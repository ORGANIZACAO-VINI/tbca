"""
Serviço para cálculos nutricionais
"""
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import ItemAlimentoCreate
from app.models.models import Alimento

def calcular_nutricional(db: Session, itens: List[ItemAlimentoCreate]):
    """
    Calcula os valores nutricionais para uma lista de alimentos e quantidades
    Args:
        db: Sessão do banco de dados
        itens: Lista de itens com alimento_id e quantidade_g
    Returns:
        Dicionário com os valores nutricionais calculados
    """
    resultado = {
        "kcal": 0.0,
        "carboidratos": 0.0,
        "proteina": 0.0,
        "gordura": 0.0,
        "fibras": 0.0,
        "calcio": 0.0,
        "ferro": 0.0,
        "detalhes": []
    }
    
    # Calcular nutrientes para cada item
    for item in itens:
        alimento = db.query(Alimento).filter(Alimento.id == item.alimento_id).first()
        
        if not alimento:
            raise HTTPException(
                status_code=404, 
                detail=f"Alimento com ID {item.alimento_id} não encontrado"
            )
        
        # Calcular fator baseado na quantidade (valores nutricionais são por 100g)
        fator = item.quantidade_g / 100.0
        
        # Calcular valores proporcionais à quantidade
        item_resultado = {
            "alimento_id": alimento.id,
            "nome": alimento.nome,
            "quantidade_g": item.quantidade_g,
            "kcal": round(alimento.kcal * fator, 2),
            "carboidratos": round(alimento.carboidratos * fator, 2),
            "proteina": round(alimento.proteina * fator, 2),
            "gordura": round(alimento.gordura * fator, 2),
            "fibras": round(alimento.fibras * fator, 2),
            "calcio": round(alimento.calcio * fator, 2),
            "ferro": round(alimento.ferro * fator, 2),
        }
        
        # Adicionar ao total
        resultado["kcal"] += item_resultado["kcal"]
        resultado["carboidratos"] += item_resultado["carboidratos"]
        resultado["proteina"] += item_resultado["proteina"]
        resultado["gordura"] += item_resultado["gordura"]
        resultado["fibras"] += item_resultado["fibras"]
        resultado["calcio"] += item_resultado["calcio"]
        resultado["ferro"] += item_resultado["ferro"]
        
        # Adicionar aos detalhes
        resultado["detalhes"].append(item_resultado)
    
    # Arredondar valores finais
    for key in ["kcal", "carboidratos", "proteina", "gordura", "fibras", "calcio", "ferro"]:
        resultado[key] = round(resultado[key], 2)
    
    return resultado
