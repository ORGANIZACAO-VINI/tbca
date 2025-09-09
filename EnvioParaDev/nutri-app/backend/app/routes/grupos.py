"""
Rotas para gerenciamento de grupos de alimentos
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models.database import get_db
from ..models.schemas import GrupoList, GrupoDetail
from ..services.grupos_service import get_grupos, get_grupo_by_id

router = APIRouter(
    prefix="/grupos",
    tags=["grupos"],
    responses={404: {"description": "Grupo não encontrado"}},
)

@router.get("/", response_model=List[GrupoList])
def listar_grupos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retorna uma lista de todos os grupos de alimentos
    """
    return get_grupos(db, skip, limit)

@router.get("/{grupo_id}", response_model=GrupoDetail)
def obter_grupo(grupo_id: int, db: Session = Depends(get_db)):
    """
    Obtém informações detalhadas de um grupo específico, incluindo seus alimentos
    """
    grupo = get_grupo_by_id(db, grupo_id)
    if grupo is None:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return grupo
