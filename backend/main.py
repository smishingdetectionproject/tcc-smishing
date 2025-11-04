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
from io import BytesIO # Adicionado para carregar o modelo do Gist

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
GITHUB_PAT = os.environ.get("GITHUB_PAT")

FEEDBACK_FILENAME = "feedback.csv"
MODEL_FILENAME = "model.joblib"
GIST_API_URL = "https://api.github.com/gists/"

# Variáveis globais para os modelos
tfidf_vectorizer = None
model_rf = None
model_nb = None
data_df = None # Dados de treinamento para análise

def load_model_from_gist():
    """Baixa o modelo empacotado (vetorizador e classificador) do Gist."""
    global tfidf_vectorizer, model_rf, model_nb
    
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        # 1. Baixar o Gist
        response = requests.get(f"{GIST_API_URL}{GIST_MODEL_ID}", headers=headers)
        response.raise_for_status()
        gist_data = response.json()
        
        if MODEL_FILENAME in gist_data["files"]:
            # 2. Obter o URL do conteúdo binário
            content_url = gist_data["files"][MODEL_FILENAME]["raw_url"]
            content_response = requests.get(content_url, headers=headers)
            content_response.raise_for_status()
            
            # 3. Carregar o modelo do conteúdo binário
            pipeline = joblib.load(BytesIO(content_response.content))
            
            tfidf_vectorizer = pipeline['vectorizer']
            model_rf = pipeline['model']
            model_nb = pipeline['model'] # Usando o mesmo modelo para RF e NB por simplicidade no MLOps
            
            print("✓ Modelo de ML (vetorizador e classificador) carregado do Gist com sucesso.")
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
            detail="Modelo de ML não carregado"
        )
    
    # Previsão e Probabilidade
    predicao = modelo.predict(X)[0]
    probabilidades = modelo.predict_proba(X)[0]
    
    # A classe 1 é "Smishing" e a classe 0 é "Legítima"
    if predicao == 1:
        veredito = "Possível Tentativa de Smishing"
        confianca = probabilidades[1]
    else:
        veredito = "Legítima"
        confianca = probabilidades[0]
        
    return veredito, confianca


def salvar_feedback_no_gist(feedback_data: FeedbackRequest):
    """Salva o feedback no arquivo CSV do Gist."""
    
    # 1. Baixar o conteúdo atual do Gist
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        response = requests.get(f"{GIST_API_URL}{GIST_FEEDBACK_ID}", headers=headers)
        response.raise_for_status()
        gist_data = response.json()
        
        # 2. Obter o conteúdo atual do CSV
        current_content = ""
        if FEEDBACK_FILENAME in gist_data["files"]:
            current_content = gist_data["files"][FEEDBACK_FILENAME]["content"]
        
        # 3. Adicionar o novo feedback
        new_row = {
            "timestamp": datetime.now().isoformat(),
            "mensagem": feedback_data.mensagem.replace('"', '""'), # Escape aspas
            "veredito_original": feedback_data.veredito_original,
            "feedback_util": feedback_data.feedback_util,
            "comentario_usuario": feedback_data.comentario_usuario.replace('"', '""') if feedback_data.comentario_usuario else ""
        }
        
        # Formatar a nova linha CSV
        new_line = f'{new_row["timestamp"]},"{new_row["mensagem"]}","{new_row["veredito_original"]}",{new_row["feedback_util"]},"{new_row["comentario_usuario"]}"\n'
        
        # Se o conteúdo atual estiver vazio, adiciona o cabeçalho
        if not current_content:
            current_content = "timestamp,mensagem,veredito_original,feedback_util,comentario_usuario\n"
        
        updated_content = current_content + new_line
        
        # 4. Atualizar o Gist
        data = {
            "files": {
                FEEDBACK_FILENAME: {
                    "content": updated_content
                }
            }
        }
        
        response = requests.patch(f"{GIST_API_URL}{GIST_FEEDBACK_ID}", headers=headers, json=data)
        response.raise_for_status()
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao salvar feedback no Gist: {e}")
        return False


# ============================================================================
# ENDPOINTS DA API
# ============================================================================

@app.post("/analisar", response_model=AnaliseResponse)
async def analisar_sms(request: AnaliseRequest):
    """Endpoint para analisar uma mensagem SMS."""
    
    mensagem = request.mensagem
    modelo_nome = request.modelo
    
    # 1. Extrair Características Heurísticas
    caracteristicas = extrair_caracteristicas_smishing(mensagem)
    
    # 2. Análise do Modelo de ML
    veredito_ml, confianca_ml = analisar_com_modelo(mensagem, modelo_nome)
    
    # 3. Lógica de Override (Regra de Segurança Crítica)
    
    # Verificar se há Urgência + Pedido de Dados OU Links Suspeitos
    tem_urgencia = any(c.nome == "Senso de Urgência" for c in caracteristicas)
    tem_dados = any(c.nome == "Pedido de Dados Pessoais/Documentos" for c in caracteristicas)
    tem_link_suspeito = any(c.nome == "Presença de Links Suspeitos" for c in caracteristicas)
    
    # Se o modelo disse que é legítima, mas há indicadores críticos, forçamos o Smishing
    if veredito_ml == "Legítima" and ((tem_urgencia and tem_dados) or tem_link_suspeito):
        
        veredito_final = "Possível Tentativa de Smishing"
        confianca_final = max(confianca_ml, 0.90) # Aumenta a confiança para refletir a regra
        
        # Construir a explicação do Override
        explicacao = (
            f"Esta mensagem foi classificada como **{veredito_final}** por uma regra de "
            f"segurança crítica. O modelo de ML a considerou **{veredito_ml}**, mas a combinação de "
            f"**Senso de Urgência** e **Pedido de Dados Pessoais/Documentos** OU **Presença de "
            f"Links Suspeitos** são indicadores fortíssimos de golpe. Recomendamos extrema cautela."
        )
        
    else:
        # Se não houver override, usamos o resultado do modelo
        veredito_final = veredito_ml
        confianca_final = confianca_ml
        
        if veredito_final == "Possível Tentativa de Smishing":
            explicacao = (
                f"Esta mensagem foi classificada como **{veredito_final}** com **{confianca_final:.2%}** de confiança pelo modelo **{modelo_nome.replace('_', ' ').title()}**. "
                f"Foram detectadas características comuns em golpes. Prossiga com cautela."
            )
        else:
            explicacao = (
                f"Esta mensagem foi classificada como **{veredito_final}** com **{confianca_final:.2%}** de confiança pelo modelo **{modelo_nome.replace('_', ' ').title()}**. "
                f"No entanto, sempre mantenha a cautela com mensagens não esperadas. Se tiver dúvidas, entre em contato diretamente com a instituição."
            )

    return AnaliseResponse(
        veredito=veredito_final,
        confianca=confianca_final,
        caracteristicas=caracteristicas,
        explicacao=explicacao,
        modelo_usado=modelo_nome.replace('_', ' ').title()
    )


@app.post("/feedback", response_model=FeedbackResponse)
async def receber_feedback(feedback: FeedbackRequest):
    """Endpoint para receber feedback do usuário e salvar no Gist."""
    
    if not GITHUB_PAT:
        return FeedbackResponse(sucesso=False, mensagem="Erro: Variável GITHUB_PAT não configurada no servidor.")
        
    if salvar_feedback_no_gist(feedback):
        return FeedbackResponse(sucesso=True, mensagem="Feedback recebido com sucesso! Obrigado por ajudar a treinar o modelo.")
    else:
        return FeedbackResponse(sucesso=False, mensagem="Erro ao salvar o feedback. Tente novamente mais tarde.")

@app.get("/status")
async def get_status():
    """Endpoint de saúde da API."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}