import os
import pandas as pd
from sqlmodel import Session
from database import engine, Dataset, create_db_and_tables

# ============================================================================
# SCRIPT DE INSERÇÃO DO DATASET ORIGINAL
# ============================================================================

# O Render usa o diretório raiz do projeto como /opt/render/project/src
# O arquivo CSV deve ser colocado no mesmo diretório do script (backend/)

# 1. Defina o nome do seu arquivo CSV
DATASET_CSV_FILENAME = "dataset_original.csv"

def insert_dataset_into_db():
    """
    Carrega o dataset de um CSV local e insere na tabela Dataset do PostgreSQL.
    """
    print("Iniciando a inserção do dataset original no Banco de Dados...")
    
    # 1. Cria as tabelas (se ainda não existirem)
    create_db_and_tables()
    
    # 2. Verifica se o arquivo CSV existe
    if not os.path.exists(DATASET_CSV_FILENAME):
        print(f"✗ ERRO: Arquivo CSV não encontrado: {DATASET_CSV_FILENAME}")
        print("   Por favor, coloque o seu dataset original CSV neste diretório.")
        return

    # 3. Carrega o CSV
    try:
        # O CSV deve ter as colunas 'text' e 'label'
        df = pd.read_csv(DATASET_CSV_FILENAME)
        if 'text' not in df.columns or 'label' not in df.columns:
            print("✗ ERRO: O CSV deve conter as colunas 'text' e 'label'.")
            return
            
        # Garante que a label é int
        df['label'] = df['label'].astype(int)
        
    except Exception as e:
        print(f"✗ ERRO ao carregar o CSV: {e}")
        return

    # 4. Insere os dados no BD
    with Session(engine) as session:
        # Opcional: Limpar dados anteriores com source='original'
        # session.query(Dataset).filter(Dataset.source == "original").delete()
        # session.commit()
        
        count = 0
        for index, row in df.iterrows():
            dataset_entry = Dataset(
                text=row['text'],
                label=row['label'],
                source="original"
            )
            session.add(dataset_entry)
            count += 1
            
            # Commit a cada 1000 linhas para evitar transações muito longas
            if count % 1000 == 0:
                session.commit()
                print(f"   {count} registros inseridos...")
                
        session.commit()
        print(f"✓ SUCESSO: {count} registros inseridos na tabela Dataset.")

if __name__ == "__main__":
    insert_dataset_into_db()
