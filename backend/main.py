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
import subprocess # Para executar o train.py na rota /train_model

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
# CONFIGURAÇÕES DO GIST
# ============================================================================

# Diretório do backend
BACKEND_DIR = Path(__file__).parent
MODEL_DIR = BACKEND_DIR / "models"
DATA_DIR = BACKEND_DIR / "data"

# Criar diretórios se não existirem
MODEL_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Variáveis de ambiente para o Gist
GIST_MODEL_ID = os.environ.get("GIST_MODEL_ID")
GIST_FEEDBACK_ID = os.environ.get("GIST_FEEDBACK_ID")
GITHUB_PAT = os.environ.get("GITHUB_PAT")

# Variáveis globais para os modelos
tfidf_vectorizer = None
model_rf = None
model_nb = None
f1_score_rf = 0.0
f1_score_nb = 0.0

# ============================================================================
# FUNÇÕES DE COMUNICAÇÃO COM O GIST
# ============================================================================

def get_gist_content(gist_id: str, filename: str) -> Optional[bytes]:
    """Busca o conteúdo de um arquivo em um Gist."""
    try:
        headers = {}
        if GITHUB_PAT:
            headers["Authorization"] = f"token {GITHUB_PAT}"
            
        response = requests.get(f"https://api.github.com/gists/{gist_id}", headers=headers)
        response.raise_for_status()
        
        gist_data = response.json()
        
        if filename in gist_data['files']:
            raw_url = gist_data['files'][filename]['raw_url']
            content_response = requests.get(raw_url)
            content_response.raise_for_status()
            return content_response.content
        
        return None
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro ao buscar Gist {gist_id}: {e}")
        return None

def load_models_from_gist():
    """Carrega o vetorizador e os modelos ativos do Gist."""
    global tfidf_vectorizer, model_rf, model_nb, f1_score_rf, f1_score_nb
    
    if not GIST_MODEL_ID:
        print("✗ Variável GIST_MODEL_ID não configurada. Usando modelos locais (Fallback).")
        return load_local_models()

    try:
        # 1. Carregar o binário do modelo
        model_binary = get_gist_content(GIST_MODEL_ID, "model.joblib")
        
        if not model_binary:
            print("✗ Arquivo model.joblib não encontrado no Gist. Usando modelos locais (Fallback).")
            return load_local_models()
            
        # 2. Carregar o binário do F1-Score
        metrics_content = get_gist_content(GIST_MODEL_ID, "metrics.json")
        
        if not metrics_content:
            print("✗ Arquivo metrics.json não encontrado no Gist. Usando modelos locais (Fallback).")
            return load_local_models()
            
        metrics = json.loads(metrics_content.decode('utf-8'))
        f1_score_rf = metrics.get("random_forest", {}).get("f1_score", 0.0)
        f1_score_nb = metrics.get("naive_bayes", {}).get("f1_score", 0.0)
        
        # 3. Desempacotar o modelo
        pipeline = joblib.load(BytesIO(model_binary))
        
        tfidf_vectorizer = pipeline['vectorizer']
        model_rf = pipeline['model_rf']
        model_nb = pipeline['model_nb']
        
        print(f"✓ Modelos carregados do Gist com sucesso.")
        print(f"  - Random Forest F1-Score: {f1_score_rf:.4f}")
        print(f"  - Naive Bayes F1-Score: {f1_score_nb:.4f}")
        
    except Exception as e:
        print(f"✗ Erro ao carregar modelos do Gist: {e}. Usando modelos locais (Fallback).")
        load_local_models()

def load_local_models():
    """Carrega modelos locais (Fallback)."""
    global tfidf_vectorizer, model_rf, model_nb
    try:
        import pickle
        with open(BACKEND_DIR / "tfidf_vectorizer.pkl", "rb") as f:
            tfidf_vectorizer = pickle.load(f)
        with open(BACKEND_DIR / "random_forest.pkl", "rb") as f:
            model_rf = pickle.load(f)
        with open(BACKEND_DIR / "complement_naive_bayes.pkl", "rb") as f:
            model_nb = pickle.load(f)
        print("✓ Modelos locais carregados com sucesso (Fallback).")
    except Exception as e_local:
        print(f"✗ Erro ao carregar modelos locais: {e_local}")

def save_feedback_to_gist(feedback_data: dict):
    """Salva o feedback em um Gist (append)."""
    if not GIST_FEEDBACK_ID:
        print("✗ Variável GIST_FEEDBACK_ID não configurada. Feedback não salvo.")
        return

    try:
        # 1. Obter o conteúdo atual do feedback.csv
        current_content = get_gist_content(GIST_FEEDBACK_ID, "feedback.csv")
        
        # 2. Preparar o novo feedback
        new_feedback_df = pd.DataFrame([feedback_data])
        new_feedback_csv = new_feedback_df.to_csv(index=False, header=False)
        
        # 3. Se houver conteúdo, remove o cabeçalho do novo feedback
        if current_content:
            current_csv = current_content.decode('utf-8')
            # Verifica se o cabeçalho existe no conteúdo atual
            if not current_csv.strip().startswith("mensagem,veredito_original,feedback_util,comentario_usuario"):
                # Se não houver cabeçalho, adiciona
                header = "mensagem,veredito_original,feedback_util,comentario_usuario\n"
                current_csv = header + current_csv
            
            # Adiciona o novo feedback (sem cabeçalho)
            updated_content = current_csv.strip() + "\n" + new_feedback_csv.strip()
        else:
            # Se não houver conteúdo, usa o novo feedback com cabeçalho
            updated_content = new_feedback_df.to_csv(index=False, header=True)
            
        # 4. Atualizar o Gist
        headers = {"Authorization": f"token {GITHUB_PAT}"}
        update_data = {
            "files": {
                "feedback.csv": {
                    "content": updated_content
                }
            }
        }
        
        response = requests.patch(f"https://api.github.com/gists/{GIST_FEEDBACK_ID}", headers=headers, json=update_data)
        response.raise_for_status()
        print("✓ Feedback salvo no Gist com sucesso.")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro ao salvar feedback no Gist: {e}")

@app.on_event("startup")
def on_startup():
    """Carrega os modelos na inicialização da API."""
    load_models_from_gist()

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
    comentario_usuario: Optional[str] = None


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
    (Função simplificada para demonstração)
    """
    caracteristicas = []
    
    # 1. Links Suspeitos
    if "http" in mensagem.lower() or "www." in mensagem.lower() or "clique aqui" in mensagem.lower():
        caracteristicas.append(CaracteristicaDetectada(
            nome="Link Suspeito",
            descricao="Presença de URL ou chamada para clique (phishing).",
            icone="🔗",
            confianca=0.8
        ))
        
    # 2. Urgência e Ameaça
    if "urgente" in mensagem.lower() or "bloqueada" in mensagem.lower() or "expira" in mensagem.lower():
        caracteristicas.append(CaracteristicaDetectada(
            nome="Urgência/Ameaça",
            descricao="Uso de palavras que forçam ação imediata (tática de smishing).",
            icone="🚨",
            confianca=0.7
        ))
        
    # 3. Pedido de Dados Pessoais
    if "cpf" in mensagem.lower() or "senha" in mensagem.lower() or "dados" in mensagem.lower():
        caracteristicas.append(CaracteristicaDetectada(
            nome="Pedido de Dados",
            descricao="Solicitação de informações pessoais ou financeiras.",
            icone="🔒",
            confianca=0.9
        ))
        
    # 4. Erros de Português (Indicador fraco, mas útil)
    # Implementação simplificada: verifica se há palavras muito curtas ou com erros óbvios
    palavras = mensagem.split()
    erros = sum(1 for p in palavras if len(p) < 3 and p.isalpha())
    if erros > 2:
        caracteristicas.append(CaracteristicaDetectada(
            nome="Erros Gramaticais",
            descricao="Possíveis erros de português ou formatação estranha.",
            icone="📝",
            confianca=0.4
        ))
        
    return caracteristicas

def preprocess_text(text):
    """Função de pré-processamento de texto (simplificada)."""
    if pd.isna(text):
        return ""
    text = text.lower()
    # Adicione aqui mais etapas de pré-processamento se necessário (remoção de stopwords, pontuação, etc.)
    return text

# ============================================================================
# ROTAS DA API
# ============================================================================

@app.get("/")
def read_root():
    """Rota de saúde da API."""
    return {
        "status": "online", 
        "modelos_carregados": model_rf is not None and model_nb is not None,
        "random_forest_f1": f1_score_rf,
        "naive_bayes_f1": f1_score_nb
    }

@app.post("/analisar", response_model=AnaliseResponse)
def analisar_sms(request: AnaliseRequest):
    """
    Analisa uma mensagem SMS e retorna o veredito de smishing.
    """
    if tfidf_vectorizer is None or model_rf is None or model_nb is None:
        raise HTTPException(status_code=503, detail="Modelos de Machine Learning não carregados. Tente novamente mais tarde.")

    # 1. Pré-processamento
    texto_processado = preprocess_text(request.mensagem)
    
    # 2. Vetorização
    texto_vetorizado = tfidf_vectorizer.transform([texto_processado])
    
    # 3. Seleção e Predição do Modelo
    modelo_usado = request.modelo.lower()
    
    if modelo_usado == "random_forest":
        model = model_rf
        f1_score_modelo = f1_score_rf
    elif modelo_usado == "naive_bayes":
        model = model_nb
        f1_score_modelo = f1_score_nb
    else:
        raise HTTPException(status_code=400, detail="Modelo inválido. Escolha 'random_forest' ou 'naive_bayes'.")

    # Predição
    predicao = model.predict(texto_vetorizado)[0]
    probabilidade = model.predict_proba(texto_vetorizado)[0]
    
    # 4. Interpretação do Resultado
    veredito = "Smishing" if predicao == 1 else "Legítima"
    confianca = probabilidade[predicao]
    
    # 5. Extração de Características
    caracteristicas = extrair_caracteristicas_smishing(request.mensagem)
    
    # 6. Explicação (simplificada)
    explicacao = f"A mensagem foi classificada como '{veredito}' com {confianca*100:.2f}% de confiança. O modelo {modelo_usado} (F1-Score: {f1_score_modelo:.4f}) foi utilizado para a predição."
    
    return AnaliseResponse(
        veredito=veredito,
        confianca=confianca,
        caracteristicas=caracteristicas,
        explicacao=explicacao,
        modelo_usado=modelo_usado
    )

@app.post("/feedback", response_model=FeedbackResponse)
def receber_feedback(request: FeedbackRequest):
    """
    Recebe feedback do usuário para aprimorar o modelo.
    """
    # 1. Preparar os dados para salvar
    feedback_data = {
        "mensagem": request.mensagem,
        "veredito_original": request.veredito_original,
        "feedback_util": request.feedback_util,
        "comentario_usuario": request.comentario_usuario
    }
    
    # 2. Salvar no Gist
    save_feedback_to_gist(feedback_data)
    
    return FeedbackResponse(
        sucesso=True,
        mensagem="Feedback recebido com sucesso. Será usado no próximo treinamento."
    )

@app.post("/train_model", response_model=dict)
def train_model_route():
    """
    Dispara o treinamento do modelo (usado pelo cronjob).
    """
    try:
        # Executa o script train.py
        result = subprocess.run(["python3", "train.py"], check=True, cwd=BACKEND_DIR, capture_output=True, text=True)
        
        # Recarrega os modelos após o treinamento
        load_models_from_gist()
        
        return {
            "sucesso": True,
            "mensagem": "Treinamento concluído e modelos recarregados com sucesso.",
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Erro no treinamento: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao disparar o treinamento: {e}")
