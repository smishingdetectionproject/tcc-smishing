"""
Script para Regenerar Modelos ML
Detector de Smishing - TCC UNIVESP

Este script reconstrói os modelos de Machine Learning usando a versão
correta do scikit-learn, garantindo compatibilidade.
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import ComplementNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

print("=" * 70)
print("REGENERADOR DE MODELOS ML - Detector de Smishing")
print("=" * 70)

# Diretório do backend
BACKEND_DIR = Path(__file__).parent
DATA_DIR = BACKEND_DIR

# ============================================================================
# PASSO 1: Carregar dados de treinamento
# ============================================================================

print("\n[1/5] Carregando dados de treinamento...")

try:
    data_df = pd.read_csv(DATA_DIR / "data_processed.csv")
    print(f"✓ Dados carregados: {len(data_df)} registros")
    print(f"  Colunas disponíveis: {list(data_df.columns)}")
except Exception as e:
    print(f"✗ Erro ao carregar dados: {e}")
    exit(1)

# ============================================================================
# PASSO 2: Preparar dados
# ============================================================================

print("\n[2/5] Preparando dados...")

try:
    # Usar a coluna 'text' para o texto
    if 'text' in data_df.columns:
        X = data_df['text'].values
        print(f"✓ Usando coluna 'text' para textos")
    elif 'texto_processado' in data_df.columns:
        X = data_df['texto_processado'].values
        print(f"✓ Usando coluna 'texto_processado' para textos")
    else:
        print(f"✗ Nenhuma coluna de texto encontrada!")
        print(f"  Colunas disponíveis: {list(data_df.columns)}")
        exit(1)
    
    # Usar a coluna 'label' para os rótulos
    if 'label' in data_df.columns:
        y_raw = data_df['label'].values
        print(f"✓ Usando coluna 'label' para rótulos")
        print(f"  Valores únicos: {np.unique(y_raw)}")
        
        # Converter rótulos de texto para números
        # "Legitimate" -> 0, "Smishing" -> 1
        y = np.zeros(len(y_raw), dtype=int)
        for i, label in enumerate(y_raw):
            if isinstance(label, str):
                if label.lower() in ['smishing', 'spam', '1']:
                    y[i] = 1
                elif label.lower() in ['legitimate', 'ham', '0']:
                    y[i] = 0
                else:
                    print(f"⚠️  Aviso: Rótulo desconhecido: '{label}'")
            else:
                # Se já é número
                y[i] = int(label)
    else:
        print(f"✗ Coluna 'label' não encontrada!")
        exit(1)
    
    # Remover valores nulos
    mask = pd.notna(X) & pd.notna(y)
    X = X[mask]
    y = y[mask]
    
    print(f"✓ Dados preparados:")
    print(f"  Total de amostras: {len(X)}")
    print(f"  Legítimas (0): {(y == 0).sum()}")
    print(f"  Smishing (1): {(y == 1).sum()}")
    
    # Verificar se temos dados de ambas as classes
    if (y == 0).sum() == 0 or (y == 1).sum() == 0:
        print(f"✗ Erro: Faltam dados de uma das classes!")
        exit(1)
except Exception as e:
    print(f"✗ Erro ao preparar dados: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================================
# PASSO 3: Criar e treinar TF-IDF Vectorizer
# ============================================================================

print("\n[3/5] Treinando TF-IDF Vectorizer...")

try:
    tfidf_vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        lowercase=True,
        stop_words=None
    )
    
    X_tfidf = tfidf_vectorizer.fit_transform(X)
    print(f"✓ TF-IDF Vectorizer treinado:")
    print(f"  Features: {X_tfidf.shape[1]}")
    print(f"  Sparsidade: {1 - (X_tfidf.nnz / (X_tfidf.shape[0] * X_tfidf.shape[1])):.2%}")
    
    # Salvar vectorizer
    with open(BACKEND_DIR / "tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(tfidf_vectorizer, f)
    print(f"✓ Vectorizer salvo em: tfidf_vectorizer.pkl")
except Exception as e:
    print(f"✗ Erro ao treinar TF-IDF: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================================
# PASSO 4: Treinar Random Forest
# ============================================================================

print("\n[4/5] Treinando Random Forest...")

try:
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(
        X_tfidf, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Treinar modelo
    model_rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    model_rf.fit(X_train, y_train)
    
    # Avaliar
    y_pred = model_rf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    print(f"✓ Random Forest treinado:")
    print(f"  Acurácia: {accuracy:.2%}")
    print(f"  Precisão: {precision:.2%}")
    print(f"  Recall: {recall:.2%}")
    print(f"  F1-Score: {f1:.2%}")
    
    # Salvar modelo
    with open(BACKEND_DIR / "random_forest.pkl", "wb") as f:
        pickle.dump(model_rf, f)
    print(f"✓ Modelo salvo em: random_forest.pkl")
except Exception as e:
    print(f"✗ Erro ao treinar Random Forest: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================================
# PASSO 5: Treinar Complement Naive Bayes
# ============================================================================

print("\n[5/5] Treinando Complement Naive Bayes...")

try:
    # Treinar modelo
    model_nb = ComplementNB()
    model_nb.fit(X_train, y_train)
    
    # Avaliar
    y_pred = model_nb.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    print(f"✓ Complement Naive Bayes treinado:")
    print(f"  Acurácia: {accuracy:.2%}")
    print(f"  Precisão: {precision:.2%}")
    print(f"  Recall: {recall:.2%}")
    print(f"  F1-Score: {f1:.2%}")
    
    # Salvar modelo
    with open(BACKEND_DIR / "complement_naive_bayes.pkl", "wb") as f:
        pickle.dump(model_nb, f)
    print(f"✓ Modelo salvo em: complement_naive_bayes.pkl")
except Exception as e:
    print(f"✗ Erro ao treinar Naive Bayes: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================================
# CONCLUSÃO
# ============================================================================

print("\n" + "=" * 70)
print("✓ TODOS OS MODELOS FORAM REGENERADOS COM SUCESSO!")
print("=" * 70)
print("\nArquivos criados:")
print("  ✓ tfidf_vectorizer.pkl")
print("  ✓ random_forest.pkl")
print("  ✓ complement_naive_bayes.pkl")
print("\nVocê pode agora executar o backend novamente:")
print("  python main.py")
print("=" * 70)
