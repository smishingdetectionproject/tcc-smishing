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
    feedback_usuario: Optional[str] = None


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
    
    # Padrão 2: Pedido de dados pessoais
    palavras_dados = ["senha", "pin", "código", "cpf", "dados bancários", 
                      "cartão", "número da conta", "confirmar dados", "verificar conta"]
    if any(palavra in mensagem_lower for palavra in palavras_dados):
        caracteristicas.append(CaracteristicaDetectada(
            nome="Pedido de Dados Pessoais",
            descricao="Solicita informações sensíveis que você nunca deve compartilhar.",
            icone="🔐",
            confianca=0.95
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
    if "http" in mensagem_lower or "www" in mensagem_lower or "bit.ly" in mensagem_lower:
        caracteristicas.append(CaracteristicaDetectada(
            nome="Presença de Links",
            descricao="Contém links que podem levar a sites maliciosos.",
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
    import re
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
    # CORREÇÃO APLICADA AQUI: 
    # 1 é Smishing, 0 é Legítima (conforme o treinamento do modelo)
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
    
    if len(request.mensagem) > 500:
        raise HTTPException(
            status_code=400,
            detail="Mensagem muito longa (máximo 500 caracteres)"
        )
    
    try:
        # Analisar com modelo
        veredito, confianca = analisar_com_modelo(request.mensagem, request.modelo)
        
        # Extrair características heurísticas
        caracteristicas = extrair_caracteristicas_smishing(request.mensagem)
        
        # Gerar explicação
        if veredito == "Smishing":
            explicacao = "Esta mensagem foi classificada como **Smishing**. Recomendamos extrema cautela. Não clique em links, não forneça dados pessoais e entre em contato diretamente com a suposta instituição por canais oficiais."
        else:
            explicacao = "Esta mensagem foi classificada como legítima. No entanto, sempre mantenha a cautela com mensagens não esperadas. Se tiver dúvidas, entre em contato diretamente com a instituição."
        
        # Se for legítima, mas tiver características suspeitas, adicionar um alerta
        if veredito == "Legítima" and len(caracteristicas) > 0:
            explicacao += " **ATENÇÃO:** Embora o modelo a considere legítima, foram detectadas características comuns em golpes. Prossiga com cautela."
        
        # Se for Smishing, mas a confiança for baixa, adicionar um alerta
        if veredito == "Smishing" and confianca < 0.7:
            explicacao += " **NOTA:** A confiança do modelo nesta classificação é baixa. Considere a análise das características detectadas."
            
        # Retornar resposta
        return AnaliseResponse(
            veredito=veredito,
            confianca=round(confianca * 100, 2),
            caracteristicas=caracteristicas,
            explicacao=explicacao,
            modelo_usado=request.modelo
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro inesperado na análise: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor: {e}"
        )


@app.post("/feedback", response_model=FeedbackResponse)
async def registrar_feedback(request: FeedbackRequest):
    """
    Registra o feedback do usuário sobre a análise.
    
    Args:
        request: Objeto contendo a mensagem, veredito original e feedback
        
    Returns:
        Resposta de sucesso
    """
    try:
        # Caminho para o arquivo de log de feedback
        feedback_file = DATA_DIR / "feedback_log.csv"
        
        # Preparar dados para o log
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "mensagem": request.mensagem,
            "veredito_original": request.veredito_original,
            "feedback_util": request.feedback_util,
            "feedback_usuario": request.feedback_usuario if request.feedback_usuario else ""
        }
        
        # Verificar se o arquivo existe para escrever o cabeçalho
        file_exists = os.path.exists(feedback_file)
        
        with open(feedback_file, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = log_data.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()  # Escreve o cabeçalho apenas se o arquivo for novo
            
            writer.writerow(log_data)
            
        return FeedbackResponse(
            sucesso=True,
            mensagem="Feedback registrado com sucesso!"
        )
        
    except Exception as e:
        print(f"Erro ao registrar feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao registrar feedback: {e}"
        )

# ============================================================================
# EXECUÇÃO LOCAL (opcional)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)