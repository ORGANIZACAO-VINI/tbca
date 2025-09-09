"""
Serviços para operações relacionadas a grupos de alimentos
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from ..models.models import Grupo, Alimento

def get_grupos(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtém todos os grupos de alimentos, com contagem de alimentos
    """
    return db.query(Grupo)\
        .outerjoin(Alimento)\
        .group_by(Grupo.id)\
        .order_by(Grupo.nome)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_grupo_by_id(db: Session, grupo_id: int):
    """
    Obtém um grupo específico pelo ID, incluindo seus alimentos
    """
    return db.query(Grupo)\
        .options(joinedload(Grupo.alimentos))\
        .filter(Grupo.id == grupo_id)\
        .first()
