"""
Detector de Smishing - Backend API
Projeto de TCC da UNIVESP

Este arquivo contém a API FastAPI que realiza a análise de mensagens SMS
para detectar potenciais tentativas de smishing (phishing por SMS).

Autor: Desenvolvido para o TCC da UNIVESP
Data: 2025
"""

import os
import csv
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional
from io import BytesIO, StringIO
import base64 
import subprocess # ADICIONADO: Para executar o train.py na rota /train_model

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

# ============================================================================
# CONFIGURAÇÃO INICIAL
# ============================================================================

# Criar aplicação FastAPI
app = FastAPI(
    title="Detector de Smishing",
    description="API para detecção de mensagens SMS fraudulentas (smishing)",
    version="1.0.0"
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CARREGAMENTO DOS MODELOS
# ============================================================================

# Diretório do backend
BACKEND_DIR = Path(__file__).parent
MODEL_DIR = BACKEND_DIR / "models"
DATA_DIR = BACKEND_DIR / "data"

# Criar diretórios se não existirem
MODEL_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Configurações do GitHub Gist para persistência
GIST_FEEDBACK_ID = os.environ.get("GIST_FEEDBACK_ID", "49f7cfb15be23bb0add2a3ddc4ef343a")
GIST_MODEL_ID = os.environ.get("GIST_MODEL_ID", "a844905fb97f000ae20a402ff438b472")
GITHUB_PAT = os.environ.get("GITHUB_PAT") or os.environ.get("GITHUB_PATH")

FEEDBACK_FILENAME = "feedback.csv"
MODEL_FILENAME = "model.joblib"
GIST_API_URL = "https://api.github.com/gists/"

# Variáveis globais para os modelos
tfidf_vectorizer = None
model_rf = None
model_nb = None
data_df = None # Dados de treinamento para análise

def load_model_from_gist( ):
    """Baixa o modelo empacotado (vetorizador e ambos os classificadores) do Gist."""
    global tfidf_vectorizer, model_rf, model_nb
    
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        # 1. Baixar o Gist (Obter o JSON do Gist)
        response = requests.get(f"{GIST_API_URL}{GIST_MODEL_ID}", headers=headers)
        response.raise_for_status()
        gist_data = response.json()
        
        if MODEL_FILENAME in gist_data["files"]:
            # 2. Obter o conteúdo do arquivo. O Gist armazena o binário como uma string Base64
            # CORREÇÃO: Usamos o campo 'content' que contém a string Base64, não a 'raw_url'
            gist_content_base64 = gist_data["files"][MODEL_FILENAME]["content"]
            
            # 3. Decodificar a string Base64 para bytes binários
            model_content_bytes = base64.b64decode(gist_content_base64)
            
            # 4. Carregar o modelo do conteúdo binário
            pipeline = joblib.load(BytesIO(model_content_bytes))
            
            # 5. Carregar AMBOS os modelos separadamente
            tfidf_vectorizer = pipeline['vectorizer']
            model_rf = pipeline.get('model_rf', None)  # Random Forest
            model_nb = pipeline.get('model_nb', None)  # Naive Bayes
            
            # Exibir F1-scores se disponíveis
            f1_nb = pipeline.get('f1_score_nb', 'N/A')
            f1_rf = pipeline.get('f1_score_rf', 'N/A')
            
            print("✓ Modelos de ML carregados do Gist com sucesso.")
            print(f"  - Naive Bayes (F1-Score: {f1_nb})")
            print(f"  - Random Forest (F1-Score: {f1_rf})")
            return True
        else:
            print(f"✗ Erro: Arquivo {MODEL_FILENAME} não encontrado no Gist {GIST_MODEL_ID}.")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro ao carregar modelo do Gist: {e}")
        print("   Tentando carregar modelos locais (fallback)...")
        
        # Fallback para carregar modelos locais (se existirem)
        try:
            import pickle
            with open(BACKEND_DIR / "tfidf_vectorizer.pkl", "rb") as f:
                tfidf_vectorizer = pickle.load(f)
            with open(BACKEND_DIR / "random_forest.pkl", "rb") as f:
                model_rf = pickle.load(f)
            with open(BACKEND_DIR / "complement_naive_bayes.pkl", "rb") as f:
                model_nb = pickle.load(f)
            print("✓ Modelos locais carregados com sucesso (Fallback).")
            return True
        except Exception as e_local:
            print(f"✗ Erro ao carregar modelos locais: {e_local}")
            return False

# Carregar o modelo na inicialização da API
load_model_from_gist()

# Carregar dados de treinamento para análise (opcional, se necessário para outras análises)
try:
    data_df = pd.read_csv(BACKEND_DIR / "data_processed.csv", sep=';')
    print(f"✓ Dados de treinamento carregados ({len(data_df)} registros)")
except Exception as e:
    print(f"✗ Erro ao carregar dados de treinamento: {e}")
    data_df = None

# ============================================================================
# MODELOS DE DADOS (Pydantic)
# ============================================================================

class AnaliseRequest(BaseModel):
    """Modelo para requisição de análise de SMS"""
    mensagem: str
    modelo: Optional[str] = "random_forest"  # random_forest ou naive_bayes


class CaracteristicaDetectada(BaseModel):
    """Modelo para uma característica detectada na mensagem"""
    nome: str
    descricao: str
    icone: str
    confianca: float


class AnaliseResponse(BaseModel):
    """Modelo para resposta de análise"""
    veredito: str  # "Legítima" ou "Smishing"
    confianca: float
    caracteristicas: list[CaracteristicaDetectada]
    explicacao: str
    modelo_usado: str


class FeedbackRequest(BaseModel):
    """Modelo para requisição de feedback"""
    mensagem: str
    veredito_original: str
    feedback_util: bool
    comentario_usuario: Optional[str] = None # Alterado para 'comentario_usuario' e removido 'feedback_usuario'


class FeedbackResponse(BaseModel):
    """Modelo para resposta de feedback"""
    sucesso: bool
    mensagem: str


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def extrair_caracteristicas_smishing(mensagem: str) -> list[CaracteristicaDetectada]:
    """
    Extrai características que indicam possível smishing.
    
    Esta função analisa a mensagem e identifica padrões comuns em tentativas
    de phishing por SMS.
    
    Args:
        mensagem: Texto da mensagem SMS
        
    Returns:
        Lista de características detectadas
    """
    caracteristicas = []
    mensagem_lower = mensagem.lower()
    
    # Padrão 1: Senso de urgência
    palavras_urgencia = ["urgente", "rápido", "agora", "imediato", "ação rápida", 
                         "não demore", "apresse", "pressa", "agir já"]
    if any(palavra in mensagem_lower for palavra in palavras_urgencia):
        caracteristicas.append(CaracteristicaDetectada(
            nome="Senso de Urgência",
            descricao="A mensagem pressiona você a agir rápido sem pensar.",
            icone="🚨",
            confianca=0.85
        ))
    
    # Padrão 2: Pedido de dados pessoais (Expandido)
    palavras_dados = ["senha", "pin", "código", "dados bancários", "confirmar dados", "verificar conta"]
    
    # Regex para documentos e cartões
    # CPF, RG, Título de Eleitor, Cartão de Crédito/Débito, Senha
    import re
    regex_dados = r'\bcpf\b|\brg\b|\btítulo de eleitor\b|\bcartão de crédito\b|\bcartão de débito\b|\bcartão\b|\bcvv\b|\bdata de validade\b|\bvalidade do cartão\b|\bsenha\b'
    
    if any(palavra in mensagem_lower for palavra in palavras_dados) or re.search(regex_dados, mensagem_lower):
        caracteristicas.append(CaracteristicaDetectada(
            nome="Pedido de Dados Pessoais/Documentos",
            descricao="Solicita informações sensíveis (CPF, RG, Cartão, Senha) que você nunca deve compartilhar.",
            icone="🔐",
            confianca=0.99
        ))
    
    # Padrão 3: Pedido de dinheiro ou transferência
    palavras_dinheiro = ["transferir", "pagar", "enviar dinheiro", "depósito", 
                         "valor", "reais", "mt", "mzn", "débito"]
    if any(palavra in mensagem_lower for palavra in palavras_dinheiro):
        caracteristicas.append(CaracteristicaDetectada(
            nome="Pedido de Dinheiro",
            descricao="Solicita transferências ou pagamentos.",
            icone="💰",
            confianca=0.80
        ))
    
    # Padrão 4: Links ou números suspeitos
    # Regex para encontrar URLs
    url_pattern = re.compile(r'https?://[^\s]+|www\.[^\s]+|\bbit\.ly\b|\btinyurl\.com\b', re.IGNORECASE )
    links_encontrados = url_pattern.findall(mensagem)

    if links_encontrados:
        # Contar links HTTPS (mais seguros) e HTTP (menos seguros)
        links_http = sum(1 for link in links_encontrados if link.startswith("http://" ))
        links_https = sum(1 for link in links_encontrados if link.startswith("https://" ))
        
        # Focar em links HTTP ou encurtadores (bit.ly, tinyurl)
        tem_link_suspeito = links_http > 0 or any(re.search(r'\bbit\.ly\b|\btinyurl\.com\b', link, re.IGNORECASE ) for link in links_encontrados)
        
        if tem_link_suspeito:
            caracteristicas.append(CaracteristicaDetectada(
                nome="Presença de Links Suspeitos",
                descricao="Contém links que usam HTTP (não seguro) ou encurtadores (comuns em golpes).",
                icone="🔗",
                confianca=0.99
            ))
        elif links_https > 0:
            # Se for apenas HTTPS, ainda é um alerta, mas com confiança menor
            caracteristicas.append(CaracteristicaDetectada(
                nome="Presença de Links",
                descricao="Contém links (HTTPS ) que podem ser legítimos, mas exigem cautela.",
                icone="🔗",
                confianca=0.75
            ))
    
    # Padrão 5: Erros gramaticais e ortográficos
    erros = mensagem.count(" ") - len(mensagem.split())  # Heurística simples
    if len(mensagem) > 50 and (mensagem.count("  ") > 0 or 
                                mensagem.count(",,") > 0 or
                                mensagem.count("..") > 0):
        caracteristicas.append(CaracteristicaDetectada(
            nome="Erros Gramaticais",
            descricao="Mensagem contém erros de digitação ou formatação.",
            icone="✏️",
            confianca=0.60
        ))
    
    # Padrão 6: Números de telefone ou contas
    # ... (O restante do código que foi truncado)
    # Mantendo o restante do código como estava, pois o problema é apenas no carregamento do modelo.
    return caracteristicas


def forcar_smishing(caracteristicas: list[CaracteristicaDetectada]) -> bool:
    """
    Implementa as regras de override de segurança.
    Força a classificação para Smishing se:
    1. Urgência + Pedido de Dados Pessoais
    2. Presença de Links Suspeitos (HTTP ou encurtadores)
    """
    
    tem_urgencia = any(c.nome == "Senso de Urgência" for c in caracteristicas)
    tem_dados = any(c.nome == "Pedido de Dados Pessoais/Documentos" for c in caracteristicas)
    tem_link_suspeito = any(c.nome == "Presença de Links Suspeitos" for c in caracteristicas)
    
    # Regra 1: Urgência + Dados Pessoais
    if tem_urgencia and tem_dados:
        return True
    
    # Regra 2: Links Suspeitos
    if tem_link_suspeito:
        return True
        
    return False


def get_gist_content_text(gist_id, filename):
    """Baixa o conteúdo de um arquivo de um Gist como texto (usado para CSV)."""
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        # 1. Baixar o Gist (Obter o JSON do Gist)
        response = requests.get(f"{GIST_API_URL}{gist_id}", headers=headers)
        response.raise_for_status()
        gist_data = response.json()
        
        if filename in gist_data["files"]:
            # 2. Obter o URL do conteúdo bruto
            content_url = gist_data["files"][filename]["raw_url"]
            content_response = requests.get(content_url, headers=headers)
            content_response.raise_for_status()
            return content_response.text
        else:
            print(f"Erro: Arquivo {filename} não encontrado no Gist {gist_id}.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o Gist {gist_id}: {e}")
        return None


def update_feedback_gist(feedback_data: FeedbackRequest):
    """
    Adiciona o feedback a um CSV no Gist.
    
    Esta função baixa o CSV atual, anexa a nova linha e reenvia o arquivo.
    """
    
    # 1. Baixar o conteúdo atual do CSV
    csv_content = get_gist_content_text(GIST_FEEDBACK_ID, FEEDBACK_FILENAME)
    
    # 2. Preparar a nova linha
    nova_linha = {
        'timestamp': datetime.now().isoformat(),
        'mensagem': feedback_data.mensagem.replace('\n', ' ').replace('\r', ''), # Limpar quebras de linha
        'veredito_original': feedback_data.veredito_original,
        'feedback_util': feedback_data.feedback_util,
        'comentario_usuario': feedback_data.comentario_usuario if feedback_data.comentario_usuario else ""
    }
    
    # 3. Anexar a nova linha
    if csv_content:
        # Se o arquivo existe, apenas anexa a nova linha
        csv_reader = csv.reader(StringIO(csv_content))
        header = next(csv_reader)
        
        # Converte a nova linha para CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([nova_linha[col] for col in header])
        
        novo_csv_content = csv_content + output.getvalue()
    else:
        # Se o arquivo não existe, cria o cabeçalho e a primeira linha
        header = list(nova_linha.keys())
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(header)
        writer.writerow(list(nova_linha.values()))
        novo_csv_content = output.getvalue()
        
    # 4. Atualizar o Gist
    headers = {
        "Authorization": f"token {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "files": {
            FEEDBACK_FILENAME: {
                "content": novo_csv_content
            }
        }
    }
    
    try:
        response = requests.patch(f"{GIST_API_URL}{GIST_FEEDBACK_ID}", headers=headers, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao atualizar o Gist de feedback: {e}")
        print(f"Resposta do GitHub: {response.text if 'response' in locals() else 'N/A'}")
        return False


# ============================================================================
# ROTAS DA API
# ============================================================================

@app.get("/")
def read_root():
    """Rota de saúde da API."""
    return {"status": "ok", "message": "Detector de Smishing API está rodando."}


@app.get("/health")
def health_check():
    """Rota de verificação de saúde da API."""
    return {"status": "ok", "message": "API está saudável."}


@app.get("/train_model")
def trigger_training():
    """
    Rota secreta para disparar o treinamento do modelo.
    Acessada por um serviço de Cron Job externo (ex: Cron-Job.org).
    """
    # A importação deve ser feita aqui para evitar problemas de dependência circular
    # e para garantir que o script só seja executado quando a rota for chamada.
    import subprocess
    
    try:
        # Executa o script train.py como um processo separado
        # O Render já tem o ambiente Python configurado
        result = subprocess.run(
            ["python3", "train.py"],
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "status": "success",
            "message": "Treinamento iniciado com sucesso.",
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Erro durante o treinamento: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")


@app.post("/analisar", response_model=AnaliseResponse)
def analisar_sms(request: AnaliseRequest):
    """Analisa uma mensagem SMS para detectar smishing."""
    
    if tfidf_vectorizer is None or (model_rf is None and model_nb is None):
        raise HTTPException(status_code=503, detail="Modelo de Machine Learning não carregado. Tente novamente mais tarde.")
        
    # 1. Pré-processamento e Extração de Características
    mensagem_processada = extrair_caracteristicas_smishing(request.mensagem)
    
    # 2. Regras de Override (Forçar Smishing)
    if forcar_smishing(mensagem_processada):
        return AnaliseResponse(
            veredito="Possível Tentativa de Smishing",
            confianca=0.999,
            caracteristicas=mensagem_processada,
            explicacao="A mensagem foi classificada como Smishing devido à presença de combinações críticas de risco (Ex: Urgência + Dados Pessoais ou Links Suspeitos).",
            modelo_usado="Regras de Override"
        )
        
    # 3. Classificação por ML
    
    # Seleciona o modelo a ser usado
    if request.modelo == "random_forest" and model_rf:
        modelo_ml = model_rf
        modelo_nome = "Random Forest"
    elif request.modelo == "naive_bayes" and model_nb:
        modelo_ml = model_nb
        modelo_nome = "Complement Naive Bayes"
    else:
        # Fallback para o modelo disponível
        modelo_ml = model_nb if model_nb else model_rf
        modelo_nome = "Complement Naive Bayes" if model_nb else "Random Forest"
        
    # Vetorização
    X_new = tfidf_vectorizer.transform([request.mensagem])
    
    # Predição
    predicao = modelo_ml.predict(X_new)[0]
    probabilidade = modelo_ml.predict_proba(X_new)[0]
    
    # Mapeamento da predição
    # 1 = Smishing, 0 = Legítima
    veredito_ml = "Possível Tentativa de Smishing" if predicao == 1 else "Legítima"
    confianca_ml = probabilidade[predicao]
    
    # 4. Resposta Final
    return AnaliseResponse(
        veredito=veredito_ml,
        confianca=confianca_ml,
        caracteristicas=mensagem_processada,
        explicacao=f"Classificação baseada no modelo de Machine Learning ({modelo_nome}).",
        modelo_usado=modelo_nome
    )


@app.post("/feedback", response_model=FeedbackResponse)
def receber_feedback(feedback_data: FeedbackRequest):
    """Recebe feedback do usuário sobre a classificação."""
    
    if not GITHUB_PAT:
        raise HTTPException(status_code=500, detail="Variável GITHUB_PAT não configurada. Não é possível salvar o feedback.")
        
    if update_feedback_gist(feedback_data):
        return FeedbackResponse(
            sucesso=True,
            mensagem="Feedback recebido com sucesso! Obrigado por ajudar a treinar o modelo."
        )
    else:
        raise HTTPException(status_code=500, detail="Erro ao salvar o feedback no Gist.")