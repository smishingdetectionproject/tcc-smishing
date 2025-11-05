import os
import requests
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from sqlmodel import Session, select

# Importar modelos e funções do banco de dados
from .database import Dataset, Feedback, ModelMetadata, save_model_to_db, engine

# ============================================================================
# CONFIGURAÇÕES DO GIST E VARIÁVEIS DE AMBIENTE
# ============================================================================

# Variáveis de ambiente GIST_... removidas.
# O DATABASE_URL é configurado em database.py
# Apenas mantemos o GITHUB_PAT para o caso de precisar de fallback, mas não será usado.
GITHUB_PAT = os.environ.get("GITHUB_PAT")

# Configurações de MLOps
VECTORIZER_MAX_FEATURES = 5000 # Mantenha o mesmo max_features do seu treinamento original

# ============================================================================
# FUNÇÕES DE COMUNICAÇÃO COM O BANCO DE DADOS
# ============================================================================

def load_original_data_from_db():
    """Carrega o dataset original (fonte 'original') do banco de dados."""
    with Session(engine) as session:
        statement = select(Dataset).where(Dataset.source == "original")
        results = session.exec(statement).all()
        
        if not results:
            print("✗ Nenhum dado original encontrado no banco de dados.")
            # Fallback para simulação se o BD estiver vazio (apenas para o primeiro run)
            return load_simulated_data()
            
        df = pd.DataFrame([r.model_dump() for r in results])
        print(f"✓ Dataset original carregado do BD ({len(df)} registros).")
        return df[['text', 'label']]

def load_simulated_data():
    """Carrega um dataset simulado para o primeiro treinamento (fallback)."""
    print("⚠️ Carregando dados SIMULADOS (fallback). Por favor, insira o dataset real no BD.")
    data = {
        'text': [
            "me passa seu cpf preciso urgente", # Smishing
            "olá, sua conta foi bloqueada. clique no link para desbloquear", # Smishing
            "lembrete: sua consulta é amanhã às 10h", # Legítima
            "parabéns, você ganhou um prêmio! ligue agora", # Smishing
            "confirmação de agendamento: 12345", # Legítima
        ] * 100,
        'label': [1, 1, 0, 1, 0] * 100
    }
    df = pd.DataFrame(data)
    df_legitimo_extra = pd.DataFrame({
        'text': ["mensagem legítima de teste"] * 1500,
        'label': [0] * 1500
    })
    df = pd.concat([df, df_legitimo_extra], ignore_index=True)
    return df[['text', 'label']]

def load_feedback_data_from_db():
    """Carrega os dados de feedback (onde o modelo errou) do banco de dados."""
    with Session(engine) as session:
        # Filtra apenas os feedbacks que não foram úteis (erros do modelo)
        statement = select(Feedback).where(Feedback.feedback_util == False)
        results = session.exec(statement).all()
        
        if not results:
            return pd.DataFrame()
            
        df_feedback = pd.DataFrame([r.model_dump() for r in results])
        
        # Mapeia o veredito original para a label correta (o oposto do veredito original)
        df_feedback['label_correta'] = df_feedback['veredito_original'].apply(
            lambda x: 1 if x == 'Legítima' else 0
        )
        
        # Seleciona apenas o texto e a label correta
        df_feedback = df_feedback.rename(columns={'mensagem': 'text', 'label_correta': 'label'})
        print(f"✓ Feedback de erro carregado do BD ({len(df_feedback)} registros).")
        return df_feedback[['text', 'label']]

# ============================================================================
# FUNÇÕES DE PRÉ-PROCESSAMENTO E TREINAMENTO
# ============================================================================

def preprocess_text(text):
    """Função de pré-processamento de texto (simplificada)."""
    if pd.isna(text):
        return ""
    text = text.lower()
    # Adicione aqui mais etapas de pré-processamento se necessário (remoção de stopwords, pontuação, etc.)
    return text

# As funções load_original_data e load_feedback_data foram substituídas pelas funções de BD acima.
# load_original_data_from_db e load_feedback_data_from_db

def train_and_save_model():
    """Executa o pipeline de treinamento e salva AMBOS os modelos no Banco de Dados."""
    print("Iniciando o pipeline de MLOps...")
    
    # 1. Carregar Dados do BD
    df_original = load_original_data_from_db()
    df_feedback = load_feedback_data_from_db()
    
    if df_original.empty:
        print("✗ Erro: Não há dados para treinar. O BD está vazio.")
        return
    
    # 2. Combinar Dados
    df_combined = pd.concat([df_original, df_feedback], ignore_index=True)
    df_combined['text'] = df_combined['text'].apply(preprocess_text)
    
    X = df_combined['text']
    y = df_combined['label']
    
    # 3. Split dos dados para calcular métricas
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Inicializa o vetorizador
    vectorizer = TfidfVectorizer(max_features=VECTORIZER_MAX_FEATURES)
    
    # Treina o vetorizador e transforma os dados
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)
    
    # Informações do dataset para metadados
    dataset_info = {
        "dataset_size": len(df_combined),
        "feedback_count": len(df_feedback),
        "vectorizer_max_features": VECTORIZER_MAX_FEATURES
    }
    
    # 5. Treinar e Salvar o modelo Naive Bayes
    print("Treinando o modelo Naive Bayes...")
    model_nb = ComplementNB()
    model_nb.fit(X_train_vectorized, y_train)
    
    # Calcular Métricas
    y_pred_nb = model_nb.predict(X_test_vectorized)
    metrics_nb = {
        "f1_score": f1_score(y_test, y_pred_nb),
        "precision": precision_score(y_test, y_pred_nb),
        "recall": recall_score(y_test, y_pred_nb),
        "accuracy": accuracy_score(y_test, y_pred_nb)
    }
    print(f"F1-Score do Naive Bayes: {metrics_nb['f1_score']:.4f}")
    
    # Empacotar e Salvar no BD
    pipeline_nb = {'vectorizer': vectorizer, 'model': model_nb}
    model_binary_nb = BytesIO()
    joblib.dump(pipeline_nb, model_binary_nb)
    save_model_to_db("naive_bayes", model_binary_nb.getvalue(), metrics_nb, dataset_info)
    
    # 6. Treinar e Salvar o modelo Random Forest
    print("Treinando o modelo Random Forest...")
    model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
    model_rf.fit(X_train_vectorized, y_train)
    
    # Calcular Métricas
    y_pred_rf = model_rf.predict(X_test_vectorized)
    metrics_rf = {
        "f1_score": f1_score(y_test, y_pred_rf),
        "precision": precision_score(y_test, y_pred_rf),
        "recall": recall_score(y_test, y_pred_rf),
        "accuracy": accuracy_score(y_test, y_pred_rf)
    }
    print(f"F1-Score do Random Forest: {metrics_rf['f1_score']:.4f}")
    
    # Empacotar e Salvar no BD
    pipeline_rf = {'vectorizer': vectorizer, 'model': model_rf}
    model_binary_rf = BytesIO()
    joblib.dump(pipeline_rf, model_binary_rf)
    save_model_to_db("random_forest", model_binary_rf.getvalue(), metrics_rf, dataset_info)
    
    print("Pipeline de MLOps concluído com sucesso!")
    print(f"Resumo das métricas:")
    print(f"  - Naive Bayes F1-Score: {metrics_nb['f1_score']:.4f}")
    print(f"  - Random Forest F1-Score: {metrics_rf['f1_score']:.4f}")

if __name__ == "__main__":
    # A inicialização do BD deve ser feita antes de treinar
    from .database import create_db_and_tables
    create_db_and_tables()
    train_and_save_model()
