"""
Esquemas Pydantic para validação de dados e serialização da API
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class PorcaoBase(BaseModel):
    descricao: str
    quantidade: Optional[str] = None
    valor: float
    
    class Config:
        orm_mode = True

class NutrienteBase(BaseModel):
    nome: str
    unidade: Optional[str] = None
    valor_por_100g: float
    
    class Config:
        orm_mode = True

class NutrienteCreate(NutrienteBase):
    pass

class NutrienteDetail(NutrienteBase):
    id: int
    porcoes: List[PorcaoBase] = []

class AlimentoBase(BaseModel):
    codigo: Optional[str] = None
    nome: str
    nome_cientifico: Optional[str] = None
    marca: Optional[str] = None
    
    class Config:
        orm_mode = True

class AlimentoCreate(AlimentoBase):
    grupo_id: int

class AlimentoList(AlimentoBase):
    id: int
    grupo_nome: Optional[str] = None

class AlimentoDetail(AlimentoBase):
    id: int
    grupo_nome: Optional[str] = None
    nutrientes: List[NutrienteDetail] = []

class GrupoBase(BaseModel):
    nome: str
    
    class Config:
        orm_mode = True

class GrupoCreate(GrupoBase):
    pass

class GrupoList(GrupoBase):
    id: int
    alimentos_count: int = 0

class GrupoDetail(GrupoBase):
    id: int
    alimentos: List[AlimentoList] = []

class SearchQuery(BaseModel):
    q: str = Field(..., min_length=2)
    grupo_id: Optional[int] = None
    limit: int = 20
    offset: int = 0

class ItemAlimentoCreate(BaseModel):
    alimento_id: int
    quantidade_g: float = Field(..., gt=0)

class CalculoNutricionalCreate(BaseModel):
    itens: List[ItemAlimentoCreate]

class ResultadoNutricional(BaseModel):
    kcal: float
    carboidratos: float
    proteina: float
    gordura: float
    fibras: float
    calcio: float
    ferro: float
    detalhes: List[dict]
