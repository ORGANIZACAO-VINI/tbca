"""
Arquivo de inicialização para o pacote de modelos
"""
from .models import Alimento, Grupo, Nutriente, Porcao
from .database import Base, get_db
