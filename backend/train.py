import os
import requests
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

# ============================================================================
# CONFIGURAÇÕES DO GIST E VARIÁVEIS DE AMBIENTE
# ============================================================================

# IDs dos Gists (Serão lidos das variáveis de ambiente no Render)
GIST_FEEDBACK_ID = os.environ.get("GIST_FEEDBACK_ID", "49f7cfb15be23bb0add2a3ddc4ef38b472")
GIST_MODEL_ID = os.environ.get("GIST_MODEL_ID", "a844905fb97f000ae20a402ff438b472")
GITHUB_PAT = os.environ.get("GITHUB_PAT")

# Nome do arquivo dentro do Gist
FEEDBACK_FILENAME = "feedback.csv"
MODEL_FILENAME = "model.joblib"

# URL base da API do GitHub Gist
GIST_API_URL = "https://api.github.com/gists/"

# ============================================================================
# FUNÇÕES DE COMUNICAÇÃO COM O GIST
# ============================================================================

def get_gist_content(gist_id, filename):
    """Baixa o conteúdo de um arquivo de um Gist."""
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        response = requests.get(f"{GIST_API_URL}{gist_id}", headers=headers)
        response.raise_for_status()
        gist_data = response.json()
        
        if filename in gist_data["files"]:
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

def update_gist_content(gist_id, filename, content_bytes):
    """Atualiza o conteúdo de um arquivo em um Gist."""
    headers = {
        "Authorization": f"token {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # O conteúdo do modelo (bytes) precisa ser codificado em base64 para a API do Gist
    import base64
    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
    
    data = {
        "files": {
            filename: {
                "content": content_base64
            }
        }
    }
    
    try:
        response = requests.patch(f"{GIST_API_URL}{gist_id}", headers=headers, json=data)
        response.raise_for_status()
        print(f"Sucesso: Arquivo {filename} atualizado no Gist {gist_id}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao atualizar o Gist {gist_id}: {e}")
        print(f"Resposta do GitHub: {response.text if 'response' in locals() else 'N/A'}")
        return False

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

def load_original_data():
    """Carrega o dataset original (simulado com dados do seu notebook)."""
    # Simulação de um dataset original (2009 legítimas, 552 smishing)
    # Na prática, você carregaria seu arquivo CSV/TXT original aqui.
    data = {
        'text': [
            "me passa seu cpf preciso urgente", # Smishing
            "olá, sua conta foi bloqueada. clique no link para desbloquear", # Smishing
            "lembrete: sua consulta é amanhã às 10h", # Legítima
            "parabéns, você ganhou um prêmio! ligue agora", # Smishing
            "confirmação de agendamento: 12345", # Legítima
            # Adicione mais dados do seu dataset original aqui
        ] * 100, # Multiplicando para simular um dataset maior
        'label': [1, 1, 0, 1, 0] * 100
    }
    df = pd.DataFrame(data)
    # Adicionando mais dados legítimos para simular o desbalanceamento
    df_legitimo_extra = pd.DataFrame({
        'text': ["mensagem legítima de teste"] * 1500,
        'label': [0] * 1500
    })
    df = pd.concat([df, df_legitimo_extra], ignore_index=True)
    
    # O seu dataset original deve ser carregado aqui.
    # Ex: df = pd.read_csv("seu_dataset_original.csv")
    
    return df

def load_feedback_data():
    """Baixa e carrega os dados de feedback do Gist."""
    feedback_content = get_gist_content(GIST_FEEDBACK_ID, FEEDBACK_FILENAME)
    if feedback_content:
        # Tenta ler o CSV, ignorando linhas mal formatadas
        try:
            df_feedback = pd.read_csv(StringIO(feedback_content), on_bad_lines='skip')
            # Filtra apenas os feedbacks que não foram úteis (erros do modelo)
            df_feedback = df_feedback[df_feedback['feedback_util'] == False]
            
            # Mapeia o veredito original para a label correta (o oposto do veredito original)
            # Se o modelo disse 'Legítima' (0) e o usuário disse 'Não Útil', a label correta é 1 (Smishing)
            # Se o modelo disse 'Smishing' (1) e o usuário disse 'Não Útil', a label correta é 0 (Legítima)
            
            # O veredito original é o que o modelo previu (0 ou 1)
            # Como o feedback é "Não Útil", a label correta é o oposto.
            
            # O seu main.py armazena o veredito como string 'Legítima' ou 'Smishing'
            # Precisamos converter para 0 ou 1
            
            # Se o veredito original foi 'Legítima', o modelo errou, então a label correta é 1 (Smishing)
            df_feedback['label_correta'] = df_feedback['veredito_original'].apply(
                lambda x: 1 if x == 'Legítima' else 0
            )
            
            # Seleciona apenas o texto e a label correta
            df_feedback = df_feedback.rename(columns={'mensagem': 'text', 'label_correta': 'label'})
            return df_feedback[['text', 'label']]
        except Exception as e:
            print(f"Erro ao processar o CSV de feedback: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def train_and_save_model():
    """Executa o pipeline de treinamento e salva o modelo no Gist."""
    print("Iniciando o pipeline de MLOps...")
    
    # 1. Carregar Dados
    df_original = load_original_data()
    df_feedback = load_feedback_data()
    
    if df_feedback.empty:
        print("Nenhum feedback de erro encontrado. Re-treinando apenas com o dataset original.")
    
    # 2. Combinar Dados
    df_combined = pd.concat([df_original, df_feedback], ignore_index=True)
    df_combined['text'] = df_combined['text'].apply(preprocess_text)
    
    X = df_combined['text']
    y = df_combined['label']
    
    # 3. Treinamento
    # Usamos todo o dataset combinado para o treinamento (sem split, pois o objetivo é ter o modelo mais atualizado)
    
    # Inicializa o vetorizador e o modelo
    vectorizer = TfidfVectorizer(max_features=5000) # Mantenha o mesmo max_features do seu treinamento original
    model = ComplementNB()
    
    # Treina o vetorizador e transforma os dados
    X_vectorized = vectorizer.fit_transform(X)
    
    # Treina o modelo
    model.fit(X_vectorized, y)
    
    # 4. Empacotar e Salvar
    # O modelo final é um pipeline que inclui o vetorizador e o classificador
    joblib.dump({'vectorizer': vectorizer, 'model': model}, 'model.joblib')
    
    # 5. Salvar no Gist
    print("Salvando o novo modelo no Gist...")
    update_gist_content(GIST_MODEL_ID, MODEL_FILENAME, pipeline)
    
    print("Pipeline de MLOps concluído com sucesso!")

if __name__ == "__main__":
    if not GITHUB_PAT:
        print("Erro: Variável de ambiente GITHUB_PAT não configurada. Não é possível acessar o Gist.")
    else:
        train_and_save_model()