"""
Serviços para operações relacionadas a alimentos
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from ..models.models import Alimento, Grupo, Nutriente

def get_alimento(db: Session, alimento_id: int):
    """
    Obtém um alimento pelo ID, incluindo todos os seus nutrientes e porções
    """
    return db.query(Alimento)\
        .options(
            joinedload(Alimento.grupo),
            joinedload(Alimento.nutrientes).joinedload(Nutriente.porcoes)
        )\
        .filter(Alimento.id == alimento_id)\
        .first()

def search_alimentos(db: Session, query: str, skip: int = 0, limit: int = 100, grupo_id: int = None):
    """
    Busca alimentos por nome, código ou nome científico, com filtro opcional por grupo
    """
    base_query = db.query(Alimento).join(Grupo)
    
    # Aplicar filtro de grupo se fornecido
    if grupo_id:
        base_query = base_query.filter(Alimento.grupo_id == grupo_id)
    
    # Aplicar filtro de texto se fornecido
    if query:
        base_query = base_query.filter(
            or_(
                Alimento.nome.ilike(f"%{query}%"),
                Alimento.codigo.ilike(f"%{query}%"),
                Alimento.nome_cientifico.ilike(f"%{query}%")
            )
        )
    
    return base_query.offset(skip).limit(limit).all()

def get_alimentos_by_grupo(db: Session, grupo_id: int, skip: int = 0, limit: int = 100):
    """
    Obtém todos os alimentos de um grupo específico
    """
    return db.query(Alimento)\
        .filter(Alimento.grupo_id == grupo_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
