import os
import requests
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
import joblib
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from pathlib import Path

# ============================================================================
# CONFIGURAÇÕES DO GIST E VARIÁVEIS DE AMBIENTE
# ============================================================================

# Variáveis de ambiente para o Gist
GIST_MODEL_ID = os.environ.get("GIST_MODEL_ID")
GIST_FEEDBACK_ID = os.environ.get("GIST_FEEDBACK_ID")
GIST_DATASET_ID = os.environ.get("GIST_DATASET_ID") # Novo Gist para o dataset original
GITHUB_PAT = os.environ.get("GITHUB_PAT")

# Configurações de MLOps
VECTORIZER_MAX_FEATURES = 5000 # Mantenha o mesmo max_features do seu treinamento original

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

def load_original_data_from_gist():
    """Carrega o dataset original do Gist."""
    if not GIST_DATASET_ID:
        print("✗ Variável GIST_DATASET_ID não configurada. Carregando dados SIMULADOS (Fallback).")
        return load_simulated_data()

    try:
        # O arquivo CSV deve ser o dataset original
        content = get_gist_content(GIST_DATASET_ID, "dataset_original.csv")
        
        if not content:
            print("✗ Arquivo dataset_original.csv não encontrado no Gist. Carregando dados SIMULADOS (Fallback).")
            return load_simulated_data()
            
        df = pd.read_csv(StringIO(content.decode('utf-8')))
        
        # Garante que as colunas corretas estão presentes
        if 'text' not in df.columns or 'label' not in df.columns:
            print("✗ CSV do Gist não tem as colunas 'text' e 'label'. Carregando dados SIMULADOS (Fallback).")
            return load_simulated_data()
            
        print(f"✓ Dataset original carregado do Gist ({len(df)} registros).")
        return df[['text', 'label']]
        
    except Exception as e:
        print(f"✗ Erro ao carregar dataset do Gist: {e}. Carregando dados SIMULADOS (Fallback).")
        return load_simulated_data()

def load_simulated_data():
    """Carrega um dataset simulado para o primeiro treinamento (fallback)."""
    print("⚠️ Carregando dados SIMULADOS (fallback). Por favor, configure o GIST_DATASET_ID.")
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

def load_feedback_data_from_gist():
    """Carrega os dados de feedback do Gist."""
    if not GIST_FEEDBACK_ID:
        return pd.DataFrame()

    try:
        content = get_gist_content(GIST_FEEDBACK_ID, "feedback.csv")
        
        if not content:
            return pd.DataFrame()
            
        df_feedback = pd.read_csv(StringIO(content.decode('utf-8')))
        
        # Filtra apenas os feedbacks que não foram úteis (erros do modelo)
        df_feedback = df_feedback[df_feedback['feedback_util'] == False]
        
        if df_feedback.empty:
            return pd.DataFrame()
            
        # Mapeia o veredito original para a label correta (o oposto do veredito original)
        df_feedback['label_correta'] = df_feedback['veredito_original'].apply(
            lambda x: 1 if x == 'Legítima' else 0
        )
        
        # Seleciona apenas o texto e a label correta
        df_feedback = df_feedback.rename(columns={'mensagem': 'text', 'label_correta': 'label'})
        print(f"✓ Feedback de erro carregado do Gist ({len(df_feedback)} registros).")
        return df_feedback[['text', 'label']]
        
    except Exception as e:
        print(f"✗ Erro ao carregar feedback do Gist: {e}")
        return pd.DataFrame()

def save_model_to_gist(model_binary: bytes, metrics: dict):
    """Salva o modelo treinado e seus metadados no Gist."""
    if not GIST_MODEL_ID:
        print("✗ Variável GIST_MODEL_ID não configurada. Modelo não salvo.")
        return

    try:
        # 1. Salvar o binário do modelo
        update_data = {
            "files": {
                "model.joblib": {
                    "content": base64.b64encode(model_binary).decode('utf-8'),
                    "encoding": "base64"
                },
                "metrics.json": {
                    "content": json.dumps(metrics, indent=4)
                }
            }
        }
        
        headers = {"Authorization": f"token {GITHUB_PAT}"}
        response = requests.patch(f"https://api.github.com/gists/{GIST_MODEL_ID}", headers=headers, json=update_data)
        response.raise_for_status()
        print("✓ Modelos e métricas salvos no Gist com sucesso.")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro ao salvar modelo no Gist: {e}")

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

def train_and_save_model():
    """Executa o pipeline de treinamento e salva AMBOS os modelos no Gist."""
    print("Iniciando o pipeline de MLOps...")
    
    # 1. Carregar Dados do Gist
    df_original = load_original_data_from_gist()
    df_feedback = load_feedback_data_from_gist()
    
    if df_original.empty:
        print("✗ Erro: Não há dados para treinar. O Gist está vazio ou não configurado.")
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
    
    # 7. Empacotar e Salvar AMBOS os modelos e métricas no Gist
    pipeline = {
        'vectorizer': vectorizer, 
        'model_nb': model_nb,
        'model_rf': model_rf
    }
    model_binary = BytesIO()
    joblib.dump(pipeline, model_binary)
    
    all_metrics = {
        "naive_bayes": metrics_nb,
        "random_forest": metrics_rf
    }
    
    save_model_to_gist(model_binary.getvalue(), all_metrics)
    
    print("Pipeline de MLOps concluído com sucesso!")
    print(f"Resumo das métricas:")
    print(f"  - Naive Bayes F1-Score: {metrics_nb['f1_score']:.4f}")
    print(f"  - Random Forest F1-Score: {metrics_rf['f1_score']:.4f}")

if __name__ == "__main__":
    train_and_save_model()
