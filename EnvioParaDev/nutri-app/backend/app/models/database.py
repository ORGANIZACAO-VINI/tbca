"""
Configuração do banco de dados para o aplicativo de nutrição TBCA
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Caminho para o banco de dados SQLite
DATABASE_URL = f"sqlite:///{BASE_DIR}/data/tbca.db"

# Criar engine SQLAlchemy
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos declarativos
Base = declarative_base()

# Função para obter sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializa o banco de dados
def init_db():
    """
    Inicializa o banco de dados criando as tabelas se não existirem
    """
    from . import models
    
    # Verificar se o diretório data existe, criar se não existir
    data_dir = BASE_DIR / "data"
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
    
    # Criar tabelas
    models.Base.metadata.create_all(bind=engine)
    
    # Verificar se há dados básicos para inserir
    with SessionLocal() as db:
        # Verificar se já existem grupos
        if db.query(models.Grupo).count() == 0:
            # Inserir grupos básicos
            grupos_iniciais = [
                models.Grupo(nome="Cereais e Derivados"),
                models.Grupo(nome="Verduras, Hortaliças e Derivados"),
                models.Grupo(nome="Frutas e Derivados"),
                models.Grupo(nome="Gorduras e Óleos"),
                models.Grupo(nome="Pescados e Frutos do Mar"),
                models.Grupo(nome="Carnes e Derivados"),
                models.Grupo(nome="Leite e Derivados"),
                models.Grupo(nome="Bebidas"),
                models.Grupo(nome="Ovos e Derivados"),
                models.Grupo(nome="Produtos Açucarados"),
                models.Grupo(nome="Miscelâneas"),
                models.Grupo(nome="Outros Alimentos Industrializados"),
                models.Grupo(nome="Alimentos Preparados"),
                models.Grupo(nome="Leguminosas e Derivados"),
            ]
            
            db.add_all(grupos_iniciais)
            db.commit()
