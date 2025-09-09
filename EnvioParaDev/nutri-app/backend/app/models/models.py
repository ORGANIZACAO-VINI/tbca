"""
Modelos SQLAlchemy para o aplicativo de nutrição TBCA
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Grupo(Base):
    """Modelo para grupos de alimentos"""
    __tablename__ = 'grupos'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False, unique=True)
    
    alimentos = relationship("Alimento", back_populates="grupo")
    
    def __repr__(self):
        return f"<Grupo(id={self.id}, nome='{self.nome}')>"

class Alimento(Base):
    """Modelo para alimentos"""
    __tablename__ = 'alimentos'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String, unique=True)
    nome = Column(String, nullable=False)
    nome_cientifico = Column(String)
    grupo_id = Column(Integer, ForeignKey('grupos.id'))
    marca = Column(String)
    
    # Valores nutricionais por 100g
    kcal = Column(Float, default=0.0)
    carboidratos = Column(Float, default=0.0)
    proteina = Column(Float, default=0.0)
    gordura = Column(Float, default=0.0)
    fibras = Column(Float, default=0.0)
    calcio = Column(Float, default=0.0)
    ferro = Column(Float, default=0.0)
    
    grupo = relationship("Grupo", back_populates="alimentos")
    nutrientes = relationship("Nutriente", back_populates="alimento", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Alimento(id={self.id}, nome='{self.nome}')>"

class Nutriente(Base):
    """Modelo para nutrientes"""
    __tablename__ = 'nutrientes'
    
    id = Column(Integer, primary_key=True)
    alimento_id = Column(Integer, ForeignKey('alimentos.id'))
    nome = Column(String, nullable=False)
    unidade = Column(String)
    valor_por_100g = Column(Float)
    
    alimento = relationship("Alimento", back_populates="nutrientes")
    porcoes = relationship("Porcao", back_populates="nutriente", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Nutriente(id={self.id}, nome='{self.nome}', valor='{self.valor_por_100g} {self.unidade}')>"

class Porcao(Base):
    """Modelo para porções de alimentos"""
    __tablename__ = 'porcoes'
    
    id = Column(Integer, primary_key=True)
    nutriente_id = Column(Integer, ForeignKey('nutrientes.id'))
    descricao = Column(String, nullable=False)
    quantidade = Column(String)
    valor = Column(Float)
    
    nutriente = relationship("Nutriente", back_populates="porcoes")
    
    def __repr__(self):
        return f"<Porcao(id={self.id}, descricao='{self.descricao}', quantidade='{self.quantidade}')>"
