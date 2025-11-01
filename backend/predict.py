import sys
import os
import json
import joblib
import numpy as np

# Configuração de caminhos
# O BASE_DIR aponta para a pasta 'backend'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Nomes dos arquivos
MODEL_FILES = {
    "Random Forest": "random_forest.pkl",
    "Naive Bayes": "complement_naive_bayes.pkl",
}
VECTORIZER_FILE = "tfidf_vectorizer.pkl"

def load_model(model_name):
    """Carrega o modelo e o vetorizador."""
    try:
        model_path = os.path.join(MODELS_DIR, MODEL_FILES[model_name])
        vectorizer_path = os.path.join(MODELS_DIR, VECTORIZER_FILE)
        
        # Usamos joblib para carregar os arquivos .pkl
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        
        return model, vectorizer
    except Exception as e:
        # Se houver erro ao carregar, retorna None
        return None, None

def predict_message(message, model_name):
    """Realiza a previsão e retorna o resultado em JSON."""
    model, vectorizer = load_model(model_name)
    
    if model is None or vectorizer is None:
        # Retorna um JSON de erro se o modelo não puder ser carregado
        return json.dumps({"error": "Failed to load model or vectorizer. Check if .pkl files are in backend/models/"})

    try:
        # 1. Vetorizar a mensagem
        message_vectorized = vectorizer.transform([message])
        
        # 2. Previsão
        # A previsão retorna 0 para não-phishing e 1 para phishing
        prediction = model.predict(message_vectorized)[0]
        
        # 3. Probabilidade (usando predict_proba se disponível)
        if hasattr(model, 'predict_proba'):
            # Pega a probabilidade da classe 1 (phishing)
            probability = model.predict_proba(message_vectorized)[0][1]
        else:
            # Se não suportar, usa uma probabilidade fixa baseada na previsão
            probability = 1.0 if prediction == 1 else 0.0
            
        # 4. Formatação do resultado
        result = {
            "label": "phishing" if prediction == 1 else "nao-phishing",
            "probability": float(probability),
        }
        
        # Retorna o resultado como uma string JSON
        return json.dumps(result)

    except Exception as e:
        # Retorna um JSON de erro se a previsão falhar
        return json.dumps({"error": f"Prediction failed: {str(e)}"})

if __name__ == "__main__":
    # O script espera 2 argumentos: a mensagem e o nome do modelo
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Invalid number of arguments. Usage: python predict.py <message> <model_name>"}))
        sys.exit(1)
        
    message = sys.argv[1]
    model_name = sys.argv[2]
    
    # Executa a função de previsão e imprime o resultado no stdout
    print(predict_message(message, model_name))
