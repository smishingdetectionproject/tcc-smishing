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
import requests # Adicionado para comunicação com a API do GitHub
from datetime import datetime
from pathlib import Path
from typing import Optional

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

# Configurações do GitHub Gist para persistência do feedback
GIST_ID = "49f7cfb15be23bb0add2a3ddc4ef343a" # ID fornecido pelo usuário
GIST_FILENAME = "feedback.csv"
GIST_API_URL = f"https://api.github.com/gists/{GIST_ID}"

# Carregar o vetorizador TF-IDF
try:
    # Tentar carregar de um arquivo pickle
    import pickle
    with open(BACKEND_DIR / "tfidf_vectorizer.pkl", "rb") as f:
        tfidf_vectorizer = pickle.load(f)
    print("✓ Vetorizador TF-IDF carregado com sucesso")
except Exception as e:
    print(f"✗ Erro ao carregar vetorizador TF-IDF: {e}")
    tfidf_vectorizer = None

# Carregar o modelo Random Forest
try:
    import pickle
    with open(BACKEND_DIR / "random_forest.pkl", "rb") as f:
        model_rf = pickle.load(f)
    print("✓ Modelo Random Forest carregado com sucesso")
except Exception as e:
    print(f"✗ Erro ao carregar modelo Random Forest: {e}")
    model_rf = None

# Carregar o modelo Complement Naive Bayes (como modelo alternativo)
try:
    import pickle
    with open(BACKEND_DIR / "complement_naive_bayes.pkl", "rb") as f:
        model_nb = pickle.load(f)
    print("✓ Modelo Complement Naive Bayes carregado com sucesso")
except Exception as e:
    print(f"✗ Erro ao carregar modelo Complement Naive Bayes: {e}")
    model_nb = None

# Carregar dados de treinamento para análise
try:
    data_df = pd.read_csv(BACKEND_DIR / "data_processed.csv")
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
    comentario_usuario: Optional[str] = None # Alterado para 'comentario_usuario'


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
    # CPF (XXX.XXX.XXX-XX ou XXXXXXXXXXX)
    # RG (XX.XXX.XXX-X ou XXXXXXXXXX)
    # Cartão de Crédito (XXXX XXXX XXXX XXXX)
    # Título de Eleitor (12 dígitos)
    import re
    regex_dados = r'\bcpf\b|\brg\b|\btítulo de eleitor\b|\bcartão de crédito\b|\bcartão de débito\b|\bcartão\b|\bcvv\b|\bdata de validade\b|\bvalidade do cartão\b'
    
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
    
    # Padrão 4: Links ou números suspeitos (Heurística Aprimorada)
    # Regex para encontrar URLs
    url_pattern = re.compile(r'https?://[^\s]+|www\.[^\s]+|\bbit\.ly\b|\btinyurl\.com\b', re.IGNORECASE)
    links_encontrados = url_pattern.findall(mensagem)

    if links_encontrados:
        # Contar links HTTPS (mais seguros) e HTTP (menos seguros)
        links_http = sum(1 for link in links_encontrados if link.startswith("http://"))
        links_https = sum(1 for link in links_encontrados if link.startswith("https://"))
        
        # Focar em links HTTP ou encurtadores (bit.ly, tinyurl)
        tem_link_suspeito = links_http > 0 or any(re.search(r'\bbit\.ly\b|\btinyurl\.com\b', link, re.IGNORECASE) for link in links_encontrados)
        
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
                descricao="Contém links (HTTPS) que podem ser legítimos, mas exigem cautela.",
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
    if re.search(r'\d{8,}', mensagem):  # Sequência de 8+ dígitos
        caracteristicas.append(CaracteristicaDetectada(
            nome="Números Suspeitos",
            descricao="Contém sequências de números que podem ser contas ou telefones.",
            icone="📱",
            confianca=0.70
        ))
    
    return caracteristicas


def analisar_com_modelo(mensagem: str, modelo_nome: str = "random_forest") -> tuple[str, float]:
    """
    Realiza a análise da mensagem usando o modelo de ML.
    
    Args:
        mensagem: Texto da mensagem SMS
        modelo_nome: Nome do modelo a usar ("random_forest" ou "naive_bayes")
        
    Returns:
        Tupla (veredito, confiança)
    """
    if tfidf_vectorizer is None:
        raise HTTPException(
            status_code=500,
            detail="Vetorizador TF-IDF não carregado"
        )
    
    # Vetorizar a mensagem
    X = tfidf_vectorizer.transform([mensagem])
    
    # Escolher modelo
    if modelo_nome == "naive_bayes" and model_nb is not None:
        modelo = model_nb
    elif model_rf is not None:
        modelo = model_rf
    else:
        raise HTTPException(
            status_code=500,
            detail="Nenhum modelo disponível para análise"
        )
    
    # Fazer predição
    predicao = modelo.predict(X)[0]
    probabilidades = modelo.predict_proba(X)[0]
    
    # Mapear predição para veredito
    # CORREÇÃO: 1 é Smishing, 0 é Legítima (conforme notebook de treinamento)
    veredito = "Smishing" if predicao == 1 else "Legítima"
    confianca = max(probabilidades)
    
    return veredito, confianca


# ============================================================================
# ENDPOINTS DA API
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raiz para verificar se a API está funcionando"""
    return {
        "nome": "Detector de Smishing",
        "versao": "1.0.0",
        "status": "ativo",
        "modelos_carregados": {
            "random_forest": model_rf is not None,
            "naive_bayes": model_nb is not None,
            "tfidf_vectorizer": tfidf_vectorizer is not None
        }
    }


@app.get("/health")
async def health_check():
    """Endpoint para verificação de saúde da API"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/analisar", response_model=AnaliseResponse)
async def analisar_mensagem(request: AnaliseRequest):
    """
    Analisa uma mensagem SMS para detectar smishing.
    
    Args:
        request: Objeto contendo a mensagem e modelo a usar
        
    Returns:
        Resposta com veredito, confiança e características detectadas
    """
    # Validar entrada
    if not request.mensagem or len(request.mensagem.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Mensagem não pode estar vazia"
        )
    
    # 1. Análise do Modelo de ML
    veredito, confianca = analisar_com_modelo(request.mensagem, request.modelo)
    modelo_usado = request.modelo
    
    # 2. Extração de Características Heurísticas
    caracteristicas = extrair_caracteristicas_smishing(request.mensagem)
    
    # 3. Regra de SOBREPOSIÇÃO (OVERRIDE) para casos críticos:
    # Se o modelo classificou como Legítima, mas há uma combinação crítica de características heurísticas,
    # forçar a classificação para Smishing.
    
    tem_urgencia = any(c.nome == "Senso de Urgência" for c in caracteristicas)
    tem_dados_pessoais = any(c.nome == "Pedido de Dados Pessoais/Documentos" for c in caracteristicas)
    tem_links = any(c.nome == "Presença de Links Suspeitos" for c in caracteristicas)
    
    # Condição de override: (Urgência + Dados Pessoais) OU (Presença de Links Suspeitos)
    if veredito == "Legítima" and ( (tem_urgencia and tem_dados_pessoais) or tem_links ):
        veredito = "Smishing"
        # Aumentar a confiança para refletir a certeza da regra de segurança
        confianca = max(confianca, 0.99) 
        explicacao = (
            "Esta mensagem foi classificada como uma **possível tentativa de smishing** por uma regra de segurança crítica. "
            "O modelo de ML a considerou legítima, mas a combinação de **Senso de Urgência** e "
            "**Pedido de Dados Pessoais/Documentos** OU a **Presença de Links Suspeitos** são indicadores fortíssimos de golpe. "
            "Recomendamos extrema cautela."
        )
    else:
        # Gerar explicação baseada no veredito do modelo (ou do override)
        if veredito == "Smishing":
            explicacao = (
                "Esta mensagem foi classificada como uma **possível tentativa de smishing** "
                "(phishing por SMS). Ela apresenta características comuns "
                "em mensagens fraudulentas. Não clique em links, não compartilhe "
                "dados pessoais e não realize transferências solicitadas."
            )
        else:
            explicacao = (
                "Esta mensagem foi classificada como legítima. No entanto, sempre "
                "mantenha a cautela com mensagens não esperadas. Se tiver dúvidas, "
                "entre em contato diretamente com a instituição."
            )
        
        # Se for legítima, mas tiver características suspeitas, adicionar um alerta
        if veredito == "Legítima" and len(caracteristicas) > 0:
            explicacao += " **ATENÇÃO:** Embora o modelo a considere legítima, foram detectadas características comuns em golpes. Prossiga com cautela."
        
        # Se for Smishing, mas a confiança for baixa, adicionar um alerta
        if veredito == "Smishing" and confianca < 0.7:
            explicacao += " **NOTA:** A confiança do modelo nesta classificação é baixa. Considere a análise das características detectadas."
            
    return AnaliseResponse(
        veredito=veredito,
        confianca=confianca,
        caracteristicas=caracteristicas,
        explicacao=explicacao,
        modelo_usado=modelo_usado
    )


def get_gist_content() -> str:
    """Busca o conteúdo atual do Gist."""
    headers = {
        "Authorization": f"token {os.environ.get('GITHUB_PAT')}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(GIST_API_URL, headers=headers)
        response.raise_for_status()
        
        gist_data = response.json()
        
        if GIST_FILENAME in gist_data["files"]:
            return gist_data["files"][GIST_FILENAME]["content"]
        else:
            # Se o arquivo não existir no Gist, retorna apenas o cabeçalho
            return "timestamp,mensagem,veredito_original,feedback_util,comentario_usuario\n"
            
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar Gist: {e}")
        # Em caso de erro, retorna apenas o cabeçalho para evitar perda de dados
        return "timestamp,mensagem,veredito_original,feedback_util,comentario_usuario\n"


def update_gist_content(new_content: str) -> bool:
    """Atualiza o conteúdo do Gist."""
    headers = {
        "Authorization": f"token {os.environ.get('GITHUB_PAT')}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "files": {
            GIST_FILENAME: {
                "content": new_content
            }
        }
    }
    
    try:
        response = requests.patch(GIST_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao atualizar Gist: {e}")
        return False


@app.post("/feedback", response_model=FeedbackResponse)
async def receber_feedback(request: FeedbackRequest):
    """
    Recebe feedback do usuário e salva no GitHub Gist.
    
    Args:
        request: Objeto contendo o feedback do usuário
        
    Returns:
        Resposta de sucesso
    """
    # 1. Obter o conteúdo atual do Gist
    current_content = get_gist_content()
    
    # 2. Formatar o novo feedback
    novo_feedback = {
        'timestamp': datetime.now().isoformat(),
        'mensagem': request.mensagem.replace('\n', ' ').replace('\r', ''), # Remover quebras de linha para CSV
        'veredito_original': request.veredito_original,
        'feedback_util': request.feedback_util,
        'comentario_usuario': request.comentario_usuario.replace('\n', ' ').replace('\r', '') if request.comentario_usuario else ''
    }
    
    # Converter o novo feedback para a linha CSV
    fieldnames = ['timestamp', 'mensagem', 'veredito_original', 'feedback_util', 'comentario_usuario']
    
    # Usar StringIO para simular a escrita CSV e obter a linha
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writerow(novo_feedback)
    nova_linha_csv = output.getvalue().strip()
    
    # 3. Anexar a nova linha ao conteúdo
    # Se o conteúdo atual for apenas o cabeçalho, a nova linha já tem o cabeçalho.
    # Se não for, removemos o cabeçalho da nova linha (que o DictWriter adiciona)
    if current_content.endswith('\n'):
        novo_conteudo = current_content + nova_linha_csv
    else:
        # Se o arquivo não terminar com \n, adicionamos um e a nova linha
        novo_conteudo = current_content + '\n' + nova_linha_csv
    
    # 4. Atualizar o Gist
    if update_gist_content(novo_conteudo):
        return FeedbackResponse(
            sucesso=True,
            mensagem="Feedback recebido com sucesso e salvo no GitHub Gist. Obrigado por ajudar a melhorar o modelo!"
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="Erro ao salvar feedback no GitHub Gist. Verifique o GIST_ID e o GITHUB_PAT."
        )