"""
Backend principal para o aplicativo web de nutrição TBCA
Utilizando FastAPI para criar uma API RESTful
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
from pathlib import Path

# Configuração do app
app = FastAPI(
    title="API de Nutrição TBCA",
    description="API para acesso aos dados nutricionais da Tabela Brasileira de Composição de Alimentos",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar apenas domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de dados
class Categoria(BaseModel):
    id: int
    nome: str

class Alimento(BaseModel):
    id: Optional[int] = None
    codigo: str
    nome: str
    categoria_id: int
    categoria_nome: Optional[str] = None
    kcal: float
    carboidratos: float
    proteina: float
    gordura: float
    fibras: float
    calcio: float
    ferro: float

# Caminho do banco de dados
DB_PATH = Path("./backend/data/tbca.db")

# Função para obter conexão com o banco de dados
def get_db():
    """Retorna uma conexão com o banco de dados"""
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail="Banco de dados não encontrado")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para retornar resultados como dicionários
    try:
        yield conn
    finally:
        conn.close()

# Rotas da API

@app.get("/", tags=["Geral"])
def read_root():
    """Endpoint raiz da API"""
    return {"message": "API de Nutrição TBCA", "version": "0.1.0"}

@app.get("/categorias", response_model=List[Categoria], tags=["Categorias"])
def listar_categorias(db: sqlite3.Connection = Depends(get_db)):
    """Lista todas as categorias de alimentos"""
    cursor = db.cursor()
    cursor.execute("SELECT id, nome FROM categorias ORDER BY nome")
    return [dict(row) for row in cursor.fetchall()]

@app.get("/alimentos", response_model=List[Alimento], tags=["Alimentos"])
def listar_alimentos(
    skip: int = 0, 
    limit: int = 100,
    categoria_id: Optional[int] = None,
    termo_busca: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Lista alimentos com paginação e filtros opcionais
    - **skip**: Número de registros para pular (para paginação)
    - **limit**: Número máximo de registros para retornar
    - **categoria_id**: Filtrar por categoria específica
    - **termo_busca**: Buscar por termo no nome do alimento
    """
    cursor = db.cursor()
    
    # Construir consulta SQL base
    query = """
    SELECT a.id, a.codigo, a.nome, a.categoria_id, c.nome as categoria_nome,
           a.kcal, a.carboidratos, a.proteina, a.gordura, a.fibras, a.calcio, a.ferro
    FROM alimentos a
    JOIN categorias c ON a.categoria_id = c.id
    """
    
    # Adicionar condições de filtro
    conditions = []
    params = []
    
    if categoria_id is not None:
        conditions.append("a.categoria_id = ?")
        params.append(categoria_id)
    
    if termo_busca:
        conditions.append("a.nome LIKE ?")
        params.append(f"%{termo_busca}%")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    # Adicionar ordenação e paginação
    query += " ORDER BY a.nome LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    # Executar consulta
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

@app.get("/alimentos/{alimento_id}", response_model=Alimento, tags=["Alimentos"])
def obter_alimento(alimento_id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    Obtém detalhes de um alimento específico pelo ID
    """
    cursor = db.cursor()
    cursor.execute("""
    SELECT a.id, a.codigo, a.nome, a.categoria_id, c.nome as categoria_nome,
           a.kcal, a.carboidratos, a.proteina, a.gordura, a.fibras, a.calcio, a.ferro
    FROM alimentos a
    JOIN categorias c ON a.categoria_id = c.id
    WHERE a.id = ?
    """, (alimento_id,))
    
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Alimento não encontrado")
    
    return dict(result)

@app.get("/alimentos/codigo/{codigo}", response_model=Alimento, tags=["Alimentos"])
def obter_alimento_por_codigo(codigo: str, db: sqlite3.Connection = Depends(get_db)):
    """
    Obtém detalhes de um alimento específico pelo código TBCA
    """
    cursor = db.cursor()
    cursor.execute("""
    SELECT a.id, a.codigo, a.nome, a.categoria_id, c.nome as categoria_nome,
           a.kcal, a.carboidratos, a.proteina, a.gordura, a.fibras, a.calcio, a.ferro
    FROM alimentos a
    JOIN categorias c ON a.categoria_id = c.id
    WHERE a.codigo = ?
    """, (codigo,))
    
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Alimento não encontrado")
    
    return dict(result)

@app.get("/alimentos/busca/{termo}", response_model=List[Alimento], tags=["Alimentos"])
def buscar_alimentos(
    termo: str,
    limit: int = 20,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Busca alimentos por termo no nome
    """
    cursor = db.cursor()
    cursor.execute("""
    SELECT a.id, a.codigo, a.nome, a.categoria_id, c.nome as categoria_nome,
           a.kcal, a.carboidratos, a.proteina, a.gordura, a.fibras, a.calcio, a.ferro
    FROM alimentos a
    JOIN categorias c ON a.categoria_id = c.id
    WHERE a.nome LIKE ?
    ORDER BY a.nome
    LIMIT ?
    """, (f"%{termo}%", limit))
    
    return [dict(row) for row in cursor.fetchall()]

# Modelo para cálculo nutricional
class ItemAlimento(BaseModel):
    alimento_id: int
    quantidade_g: float

class CalculoNutricional(BaseModel):
    itens: List[ItemAlimento]

class ResultadoNutricional(BaseModel):
    kcal: float
    carboidratos: float
    proteina: float
    gordura: float
    fibras: float
    calcio: float
    ferro: float
    detalhes: List[dict]

@app.post("/calcular", response_model=ResultadoNutricional, tags=["Calculadora"])
def calcular_nutricional(
    calculo: CalculoNutricional,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Calcula os valores nutricionais para uma lista de alimentos e suas quantidades
    """
    cursor = db.cursor()
    
    # Inicializar resultado
    resultado = {
        "kcal": 0,
        "carboidratos": 0,
        "proteina": 0,
        "gordura": 0,
        "fibras": 0,
        "calcio": 0,
        "ferro": 0,
        "detalhes": []
    }
    
    # Calcular nutrientes para cada item
    for item in calculo.itens:
        cursor.execute("""
        SELECT a.id, a.codigo, a.nome, a.categoria_id, c.nome as categoria_nome,
               a.kcal, a.carboidratos, a.proteina, a.gordura, a.fibras, a.calcio, a.ferro
        FROM alimentos a
        JOIN categorias c ON a.categoria_id = c.id
        WHERE a.id = ?
        """, (item.alimento_id,))
        
        alimento = cursor.fetchone()
        if not alimento:
            raise HTTPException(status_code=404, 
                               detail=f"Alimento com ID {item.alimento_id} não encontrado")
        
        alimento_dict = dict(alimento)
        fator = item.quantidade_g / 100  # Valores nutricionais são por 100g
        
        # Calcular valores proporcionais à quantidade
        item_resultado = {
            "alimento_id": alimento_dict["id"],
            "nome": alimento_dict["nome"],
            "quantidade_g": item.quantidade_g,
            "kcal": alimento_dict["kcal"] * fator,
            "carboidratos": alimento_dict["carboidratos"] * fator,
            "proteina": alimento_dict["proteina"] * fator,
            "gordura": alimento_dict["gordura"] * fator,
            "fibras": alimento_dict["fibras"] * fator,
            "calcio": alimento_dict["calcio"] * fator,
            "ferro": alimento_dict["ferro"] * fator,
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
    
    # Arredondar valores para facilitar leitura
    for key in ["kcal", "carboidratos", "proteina", "gordura", "fibras", "calcio", "ferro"]:
        resultado[key] = round(resultado[key], 2)
    
    return resultado

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
