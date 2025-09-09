"""
Rotas para gerenciamento de alimentos no aplicativo de nutrição TBCA
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.database import get_db
from ..models.schemas import AlimentoList, AlimentoDetail, SearchQuery
from ..services.alimentos_service import get_alimento, search_alimentos, get_alimentos_by_grupo

router = APIRouter(
    prefix="/alimentos",
    tags=["alimentos"],
    responses={404: {"description": "Alimento não encontrado"}},
)

@router.get("/", response_model=List[AlimentoList])
def listar_alimentos(
    skip: int = 0,
    limit: int = 100,
    categoria_id: Optional[int] = None,
    termo_busca: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna uma lista de alimentos, opcionalmente filtrados por grupo e termo de busca
    """
    if categoria_id:
        return get_alimentos_by_grupo(db, categoria_id, skip, limit)
    
    if termo_busca:
        return search_alimentos(db, termo_busca, skip, limit)
    
    return search_alimentos(db, "", skip, limit)

@router.get("/search", response_model=List[AlimentoList])
def buscar_alimentos(
    q: str = Query(..., min_length=2, description="Termo de busca"),
    grupo_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Busca alimentos por nome, código ou nome científico
    """
    return search_alimentos(db, q, skip, limit, grupo_id)

@router.get("/{alimento_id}", response_model=AlimentoDetail)
def obter_alimento(alimento_id: int, db: Session = Depends(get_db)):
    """
    Obtém informações detalhadas de um alimento específico
    """
    alimento = get_alimento(db, alimento_id)
    if alimento is None:
        raise HTTPException(status_code=404, detail="Alimento não encontrado")
    return alimento
