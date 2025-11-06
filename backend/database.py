import os
from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel, create_engine, Session

# URL de conexão com o banco de dados
# Usaremos uma variável de ambiente para a URL do Render PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./database.db")

# Engine do banco de dados
engine = create_engine(DATABASE_URL, echo=False)

# ============================================================================
# MODELOS DE DADOS (SQLModel)
# ============================================================================

class Dataset(SQLModel, table=True, schema="public"):
    """
    Tabela para armazenar o dataset original e os dados de feedback
    usados no treinamento.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(index=True)
    label: int = Field(index=True) # 0 = Legítima, 1 = Smishing
    source: str = Field(default="original") # 'original' ou 'feedback'
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class Feedback(SQLModel, table=True, schema="public"):
    """
    Tabela para armazenar o feedback do usuário.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    mensagem: str
    veredito_original: str # 'Legítima' ou 'Smishing'
    feedback_util: bool # True se útil, False se não útil (erro do modelo)
    comentario_usuario: Optional[str] = None
    modelo_usado: Optional[str] = None # 'naive_bayes' ou 'random_forest'

class ModelMetadata(SQLModel, table=True, schema="public"):
    """
    Tabela para armazenar os metadados do treinamento e as métricas.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    model_name: str = Field(index=True) # 'naive_bayes' ou 'random_forest'
    f1_score: float
    precision: float
    recall: float
    accuracy: float
    is_active: bool = Field(default=True) # Indica se é o modelo atualmente em uso

    # Metadados do treinamento
    dataset_size: int
    feedback_count: int
    vectorizer_max_features: int

class ModelBinary(SQLModel, table=True, schema="public"):
    """
    Tabela para armazenar o binário do modelo (joblib)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    model_name: str = Field(index=True) # 'naive_bayes' ou 'random_forest'
    model_binary: bytes # O modelo serializado em joblib
    metadata_id: int = Field(foreign_key="modelmetadata.id") # Link para os metadados

# ============================================================================
# FUNÇÕES DE INICIALIZAÇÃO
# ============================================================================

def create_db_and_tables():
    """Cria o banco de dados e as tabelas se não existirem."""
    SQLModel.metadata.create_all(engine)
    print("✓ Banco de dados e tabelas criadas com sucesso.")

def get_session():
    """Retorna uma sessão de banco de dados."""
    with Session(engine) as session:
        yield session

# ============================================================================
# FUNÇÕES DE PERSISTÊNCIA (A SEREM USADAS NO train.py)
# ============================================================================

def save_model_to_db(model_name: str, model_binary: bytes, metrics: dict, dataset_info: dict):
    """Salva o modelo treinado e seus metadados no banco de dados."""
    
    # 1. Desativa todos os modelos anteriores com o mesmo nome
    with Session(engine) as session:
        # Busca todos os modelos ativos com o mesmo nome
        active_models = session.query(ModelMetadata).filter(
            ModelMetadata.model_name == model_name,
            ModelMetadata.is_active == True
        ).all()
        
        # Desativa os modelos encontrados
        for model in active_models:
            model.is_active = False
            session.add(model)
        
        session.commit()
        
        # 2. Cria os metadados do novo modelo
        metadata = ModelMetadata(
            model_name=model_name,
            f1_score=metrics.get("f1_score", 0.0),
            precision=metrics.get("precision", 0.0),
            recall=metrics.get("recall", 0.0),
            accuracy=metrics.get("accuracy", 0.0),
            dataset_size=dataset_info.get("dataset_size", 0),
            feedback_count=dataset_info.get("feedback_count", 0),
            vectorizer_max_features=dataset_info.get("vectorizer_max_features", 0),
            is_active=True
        )
        session.add(metadata)
        session.commit()
        session.refresh(metadata)
        
        # 3. Salva o binário do modelo
        model_bin = ModelBinary(
            model_name=model_name,
            model_binary=model_binary,
            metadata_id=metadata.id
        )
        session.add(model_bin)
        session.commit()
        
        print(f"✓ Modelo {model_name} (ID: {metadata.id}) salvo e ativado no BD.")
        return metadata.id

def load_active_model_from_db(model_name: str):
    """Carrega o binário do modelo ativo do banco de dados."""
    with Session(engine) as session:
        # 1. Busca os metadados do modelo ativo
        metadata = session.query(ModelMetadata).filter(
            ModelMetadata.model_name == model_name,
            ModelMetadata.is_active == True
        ).order_by(ModelMetadata.timestamp.desc()).first()
        
        if not metadata:
            return None, None
            
        # 2. Busca o binário do modelo
        model_bin = session.query(ModelBinary).filter(
            ModelBinary.metadata_id == metadata.id
        ).first()
        
        if model_bin:
            return model_bin.model_binary, metadata
        
        return None, None
