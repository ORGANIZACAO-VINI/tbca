"""
Rotas para a calculadora nutricional
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import CalculoNutricionalCreate, ResultadoNutricional, ItemAlimentoCreate
from app.services.calculadora import calcular_nutricional

router = APIRouter()

@router.post("/", response_model=ResultadoNutricional)
def calcular(
    calculo: CalculoNutricionalCreate,
    db: Session = Depends(get_db)
):
    """
    Calcula os valores nutricionais para uma lista de alimentos e suas quantidades
    """
    return calcular_nutricional(db, calculo.itens)
