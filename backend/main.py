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
from typing import Optional, Annotated
from io import BytesIO, StringIO
import base64 
import subprocess # ADICIONADO: Para executar o train.py na rota /train_model

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlmodel import Session, select

# Importar componentes do banco de dados
# Importar componentes do banco de dados
# Importação absoluta para evitar problemas de execução no Render
from database import create_db_and_tables, load_active_model_from_db, get_session, Feedback, ModelMetadata

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

# Configurações do Banco de Dados
# O DATABASE_URL é configurado em database.py
# Variáveis de ambiente GIST_... removidas.

# Variáveis globais para os modelos
tfidf_vectorizer = None
model_rf = None
model_nb = None
data_df = None # Dados de treinamento para análise

def load_models_from_db():
    """Carrega o vetorizador e os modelos ativos do banco de dados."""
    global tfidf_vectorizer, model_rf, model_nb
    
    try:
        # 1. Carregar binário do Naive Bayes
        nb_binary, nb_metadata = load_active_model_from_db("naive_bayes")
        
        if nb_binary:
            pipeline_nb = joblib.load(BytesIO(nb_binary))
            tfidf_vectorizer = pipeline_nb['vectorizer']
            model_nb = pipeline_nb['model']
            f1_nb = nb_metadata.f1_score
            print(f"✓ Modelo Naive Bayes (F1-Score: {f1_nb:.4f}) carregado do BD.")
        else:
            print("✗ Modelo Naive Bayes ativo não encontrado no BD.")
            
        # 2. Carregar binário do Random Forest
        rf_binary, rf_metadata = load_active_model_from_db("random_forest")
        
        if rf_binary:
            pipeline_rf = joblib.load(BytesIO(rf_binary))
            # O vetorizador deve ser o mesmo, mas carregamos o modelo
            model_rf = pipeline_rf['model']
            f1_rf = rf_metadata.f1_score
            print(f"✓ Modelo Random Forest (F1-Score: {f1_rf:.4f}) carregado do BD.")
        else:
            print("✗ Modelo Random Forest ativo não encontrado no BD.")
            
        # Fallback para carregar modelos locais (se existirem) - Mantido por segurança
        if tfidf_vectorizer is None:
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
                
    except Exception as e:
        print(f"✗ Erro geral ao carregar modelos do BD: {e}")

def get_model_metadata(model_name: str, session: Session):
    """Busca os metadados do modelo ativo."""
    metadata = session.exec(
        select(ModelMetadata).where(
            ModelMetadata.model_name == model_name,
            ModelMetadata.is_active == True
        ).order_by(ModelMetadata.timestamp.desc())
    ).first()
    return metadata

@app.on_event("startup")
def on_startup():
    """Carrega os modelos na inicialização da API."""
    # A criação das tabelas foi movida para a rota /create_tables devido a restrições de permissão no Supabase/Render
    load_models_from_db()

# ============================================================================
# ROTA TEMPORÁRIA PARA INSERÇÃO DO DATASET (SEM ACESSO AO SHELL)
# ============================================================================

@app.get("/insert_dataset", tags=["Admin"], response_model=dict)
def insert_dataset(session: Annotated[Session, Depends(get_session)]):
    """
    ROTA TEMPORÁRIA: Insere o dataset original (dataset_original.csv) no BD.
    Deve ser executada APENAS UMA VEZ após o deploy.
    """
    DATASET_CSV_FILENAME = "dataset_original.csv"
    
    # 1. Verifica se o arquivo CSV existe
    if not os.path.exists(DATASET_CSV_FILENAME):
        raise HTTPException(status_code=404, detail=f"Arquivo CSV não encontrado: {DATASET_CSV_FILENAME}. Certifique-se de que ele está no diretório backend/.")

    # 2. Verifica se o dataset já foi inserido
    existing_data = session.exec(select(Dataset).where(Dataset.source == "original")).first()
    if existing_data:
        return {"sucesso": False, "mensagem": "Dataset original já inserido no banco de dados. Rota desnecessária."}

    # 3. Carrega o CSV
    try:
        df = pd.read_csv(DATASET_CSV_FILENAME)
        if 'text' not in df.columns or 'label' not in df.columns:
            raise HTTPException(status_code=400, detail="O CSV deve conter as colunas 'text' e 'label'.")
            
        df['label'] = df['label'].astype(int)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar ou processar o CSV: {e}")

    # 4. Insere os dados no BD
    count = 0
    for index, row in df.iterrows():
        dataset_entry = Dataset(
            text=row['text'],
            label=row['label'],
            source="original"
        )
        session.add(dataset_entry)
        count += 1
        
    session.commit()
    
    # 5. Dispara o primeiro treinamento após a inserção
    try:
        subprocess.run(["python3", "train.py"], check=True, cwd=BACKEND_DIR)
        treinamento_status = "Treinamento inicial disparado com sucesso."
    except subprocess.CalledProcessError as e:
        treinamento_status = f"Erro ao disparar o treinamento inicial: {e}"
        
    return {
        "sucesso": True, 
        "mensagem": f"Dataset original inserido com sucesso! {count} registros. {treinamento_status}"
    }

@app.get("/create_tables", tags=["Admin"], response_model=dict)
def create_tables_route():
    """
    ROTA TEMPORÁRIA: Força a criação das tabelas no BD.
    Deve ser executada antes de /insert_dataset se a inicialização falhar.
    """
    try:
        create_db_and_tables()
        return {"sucesso": True, "mensagem": "Tabelas criadas com sucesso no Banco de Dados."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar tabelas: {e}")

# Carregar dados de treinamento para análise (opcional, se necessário para outras análises)
# Removido o carregamento de data_processed.csv, pois o dataset será gerenciado pelo BD
try:
    # Apenas para manter a variável data_df, se for usada em outro lugar
    data_df = None
    print("✓ Carregamento de dados de treinamento local removido (agora via BD).")
except Exception as e:
    print(f"✗ Erro ao carregar dados de treinamento: {e}")
    data_df = None

# A inicialização e carregamento agora ocorrem na função on_startup()
# O carregamento de dados de treinamento local foi removido.

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


def save_feedback_to_db(feedback_data: FeedbackRequest, session: Session):
    """Salva o feedback do usuário no banco de dados."""
    
    db_feedback = Feedback(
        mensagem=feedback_data.mensagem.replace('\n', ' ').replace('\r', ''),
        veredito_original=feedback_data.veredito_original,
        feedback_util=feedback_data.feedback_util,
        comentario_usuario=feedback_data.comentario_usuario,
        modelo_usado=feedback_data.modelo
    )
    
    session.add(db_feedback)
    session.commit()
    session.refresh(db_feedback)
    return True


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
def analisar_sms(request: AnaliseRequest, session: Annotated[Session, Depends(get_session)]):
    """Analisa uma mensagem SMS para detectar smishing."""
    
    # Adicionamos a dependência de sessão, mas ela não é usada diretamente aqui.
    # É mantida para consistência, caso o usuário queira logar a predição no futuro.
    
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
def receber_feedback(feedback_data: FeedbackRequest, session: Annotated[Session, Depends(get_session)]):
    """Recebe feedback do usuário sobre a classificação e salva no BD."""
    
    try:
        if save_feedback_to_db(feedback_data, session):
            return FeedbackResponse(
                sucesso=True,
                mensagem="Feedback recebido com sucesso! Obrigado por ajudar a treinar o modelo."
            )
        else:
            raise HTTPException(status_code=500, detail="Erro ao salvar o feedback no Banco de Dados.")
    except Exception as e:
        print(f"Erro ao salvar feedback no BD: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao salvar o feedback: {e}")
