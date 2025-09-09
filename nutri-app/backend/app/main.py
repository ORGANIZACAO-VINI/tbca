"""
Backend principal para o aplicativo web de nutrição TBCA
Utilizando FastAPI para criar uma API RESTful
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

# Importar rotas dos módulos
from app.routes import alimentos, grupos, calculadora
from app.models.database import init_db

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

# Inicializar banco de dados
init_db()

# Incluir routers
app.include_router(alimentos.router, prefix="/alimentos", tags=["Alimentos"])
app.include_router(grupos.router, prefix="/grupos", tags=["Grupos"])
app.include_router(calculadora.router, prefix="/calculadora", tags=["Calculadora"])

@app.get("/", tags=["Geral"])
def read_root():
    """Endpoint raiz da API"""
    return {"message": "API de Nutrição TBCA", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
