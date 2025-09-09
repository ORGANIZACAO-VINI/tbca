# Script para iniciar a aplicação NutriApp

# Ativar ambiente virtual e instalar dependências do backend
cd backend
if (-not (Test-Path .\venv)) {
    Write-Host "Criando ambiente virtual..."
    python -m venv venv
}

Write-Host "Ativando ambiente virtual..."
.\venv\Scripts\Activate.ps1

Write-Host "Instalando dependências do backend..."
pip install fastapi uvicorn sqlalchemy pydantic

# Inicializar banco de dados e inserir dados de exemplo
Write-Host "Inicializando banco de dados com dados de exemplo..."
python data\scripts\inserir_dados_exemplo.py

# Iniciar servidor backend
Write-Host "Iniciando servidor backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $pwd; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"

# Instalar dependências do frontend e iniciar servidor
cd ..\frontend
Write-Host "Instalando dependências do frontend..."
npm install

Write-Host "Iniciando servidor frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $pwd; npm run dev"

Write-Host "Aplicação iniciada!"
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"
