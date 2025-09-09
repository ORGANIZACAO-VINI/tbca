# Script para iniciar a aplicação NutriApp com suporte a Oracle Database

Write-Host "=== Iniciando NutriApp com Oracle Database ===" -ForegroundColor Cyan

# Verificar se o diretório de configuração existe e criar arquivo de configuração
$configDir = Join-Path -Path $PSScriptRoot -ChildPath "config"

if (-not (Test-Path $configDir)) {
    Write-Host "Criando diretório de configuração..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $configDir | Out-Null
}

# Criar ou atualizar arquivo de configuração Oracle
$oracleConfigFile = Join-Path -Path $configDir -ChildPath "oracle_config.json"

if (-not (Test-Path $oracleConfigFile)) {
    Write-Host "Criando arquivo de configuração Oracle..." -ForegroundColor Yellow
    
    # Configurações padrão
    $defaultConfig = @{
        ORACLE_USER = "nutri_app"
        ORACLE_PASSWORD = "nutri_app"
        ORACLE_HOST = "localhost"
        ORACLE_PORT = "1521"
        ORACLE_SERVICE = "XEPDB1"
        ORACLE_SCHEMA = "nutri_app"
    }
    
    # Perguntar se o usuário deseja personalizar
    $personalizar = Read-Host "Deseja personalizar as configurações Oracle? (S/N)"
    
    if ($personalizar -eq "S" -or $personalizar -eq "s") {
        $defaultConfig.ORACLE_USER = Read-Host "Usuário Oracle [$($defaultConfig.ORACLE_USER)]" -or $defaultConfig.ORACLE_USER
        $defaultConfig.ORACLE_PASSWORD = Read-Host "Senha Oracle [$($defaultConfig.ORACLE_PASSWORD)]" -or $defaultConfig.ORACLE_PASSWORD
        $defaultConfig.ORACLE_HOST = Read-Host "Host Oracle [$($defaultConfig.ORACLE_HOST)]" -or $defaultConfig.ORACLE_HOST
        $defaultConfig.ORACLE_PORT = Read-Host "Porta Oracle [$($defaultConfig.ORACLE_PORT)]" -or $defaultConfig.ORACLE_PORT
        $defaultConfig.ORACLE_SERVICE = Read-Host "Service Oracle [$($defaultConfig.ORACLE_SERVICE)]" -or $defaultConfig.ORACLE_SERVICE
        $defaultConfig.ORACLE_SCHEMA = Read-Host "Schema Oracle [$($defaultConfig.ORACLE_SCHEMA)]" -or $defaultConfig.ORACLE_SCHEMA
    }
    
    $defaultConfig | ConvertTo-Json | Out-File -FilePath $oracleConfigFile
    Write-Host "Configuração Oracle salva em: $oracleConfigFile" -ForegroundColor Green
} else {
    Write-Host "Arquivo de configuração Oracle já existe: $oracleConfigFile" -ForegroundColor Green
}

# Verificar integração Oracle
$oracleScriptsDir = Join-Path -Path $PSScriptRoot -ChildPath "backend\data\scripts\oracle"
if (-not (Test-Path $oracleScriptsDir)) {
    Write-Host "Criando diretório para scripts Oracle..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $oracleScriptsDir -Force | Out-Null
}

# Executar script de configuração Oracle se não tiver sido executado
$configOracleScript = Join-Path -Path $PSScriptRoot -ChildPath "configurar-oracle.ps1"
if (-not (Test-Path $configOracleScript)) {
    Write-Host "Erro: Script de configuração Oracle não encontrado." -ForegroundColor Red
    Write-Host "Por favor, crie primeiro o script 'configurar-oracle.ps1'" -ForegroundColor Red
    exit 1
}

# Criar ou atualizar arquivos necessários para suporte Oracle
$backendDir = Join-Path -Path $PSScriptRoot -ChildPath "backend"
$appDir = Join-Path -Path $backendDir -ChildPath "app"
$modelsDir = Join-Path -Path $appDir -ChildPath "models"
$oracleDatabaseFile = Join-Path -Path $modelsDir -ChildPath "oracle_database.py"

if (-not (Test-Path $oracleDatabaseFile)) {
    Write-Host "Configuração Oracle não encontrada. Executando script de configuração..." -ForegroundColor Yellow
    & $configOracleScript
} else {
    Write-Host "Configuração Oracle já existe." -ForegroundColor Green
}

# Ativar ambiente virtual Python
cd $backendDir
if (-not (Test-Path .\venv)) {
    Write-Host "Criando ambiente virtual Python..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Verificar e instalar dependências Oracle
$hasCxOracle = python -c "import sys; print('cx_Oracle' in sys.modules or any(m.startswith('cx_Oracle') for m in sys.modules))" 2>$null

if ($hasCxOracle -ne "True") {
    Write-Host "Instalando cx_Oracle e outras dependências Oracle..." -ForegroundColor Yellow
    pip install cx_Oracle sqlalchemy-oracle
}

# Instalar todas as dependências do backend
Write-Host "Instalando dependências do backend..." -ForegroundColor Yellow
pip install -r requirements.txt

# Verificar se o Oracle Client está instalado
$oracleClientInstalled = $false
try {
    $oraclePath = Get-ItemProperty -Path "HKLM:\SOFTWARE\Oracle\*" -ErrorAction SilentlyContinue
    if ($oraclePath) {
        $oracleClientInstalled = $true
        Write-Host "[OK] Oracle Client já está instalado" -ForegroundColor Green
        
        # Definir variáveis de ambiente Oracle
        $env:ORACLE_HOME = $oraclePath.ORACLE_HOME
        $env:TNS_ADMIN = "$env:ORACLE_HOME\network\admin"
        $env:PATH = "$env:ORACLE_HOME\bin;$env:PATH"
    }
} catch {
    $oracleClientInstalled = $false
}

if (-not $oracleClientInstalled) {
    Write-Host "[AVISO] Oracle Client não encontrado." -ForegroundColor Yellow
    Write-Host "Por favor, baixe e instale o Oracle Instant Client de: https://www.oracle.com/database/technologies/instant-client/downloads.html" -ForegroundColor Yellow
    
    $installClient = Read-Host "Deseja abrir a página de download do Oracle Instant Client? (S/N)"
    if ($installClient -eq "S" -or $installClient -eq "s") {
        Start-Process "https://www.oracle.com/database/technologies/instant-client/downloads.html"
    }
    
    Write-Host "Após instalar o Oracle Client, execute este script novamente." -ForegroundColor Yellow
    exit 1
}

# Verificar e executar script de migração SQLite para Oracle se necessário
$migrateScript = Join-Path -Path (Join-Path -Path $PSScriptRoot -ChildPath "..") -ChildPath "scripts\migrate_sqlite_to_oracle.py"
$oracleTbcaDbPath = Join-Path -Path $backendDir -ChildPath "data\oracle_tbca.db"

if (-not (Test-Path $oracleTbcaDbPath)) {
    Write-Host "Executando migração de SQLite para Oracle..." -ForegroundColor Yellow
    
    if (Test-Path $migrateScript) {
        # Construir caminho absoluto para o banco SQLite
        $sqliteDbPath = Join-Path -Path $backendDir -ChildPath "tbca.db"
        
        python $migrateScript --sqlite $sqliteDbPath
        
        # Criar um arquivo de marcação para indicar que a migração foi realizada
        "Migração realizada em $(Get-Date)" | Out-File -FilePath $oracleTbcaDbPath
    } else {
        Write-Host "Script de migração não encontrado: $migrateScript" -ForegroundColor Red
        Write-Host "Pulando etapa de migração." -ForegroundColor Yellow
    }
}

# Definir variável de ambiente para usar Oracle
$env:USE_ORACLE_DB = "true"

# Modificar o arquivo database.py para suportar Oracle de forma condicional
$databaseFilePath = Join-Path -Path $modelsDir -ChildPath "database.py"

if (Test-Path $databaseFilePath) {
    $databaseContent = Get-Content $databaseFilePath -Raw
    
    # Verificar se o arquivo já tem suporte Oracle
    if (-not ($databaseContent -match "USE_ORACLE_DB")) {
        Write-Host "Adaptando arquivo database.py para suportar Oracle..." -ForegroundColor Yellow
        
        $newDatabaseContent = @"
# Database connection setup
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Verificar se deve usar Oracle ou SQLite
USE_ORACLE = os.environ.get('USE_ORACLE_DB', '').lower() == 'true'

if USE_ORACLE:
    import json
    import cx_Oracle
    
    # Ler configurações Oracle
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'oracle_config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Construir string de conexão Oracle
    dsn = cx_Oracle.makedsn(
        host=config['ORACLE_HOST'],
        port=config['ORACLE_PORT'],
        service_name=config['ORACLE_SERVICE']
    )
    
    # URL de conexão SQLAlchemy para Oracle
    SQLALCHEMY_DATABASE_URL = f"oracle+cx_oracle://{config['ORACLE_USER']}:{config['ORACLE_PASSWORD']}@{dsn}"
    
    print("Usando Oracle Database")
else:
    # SQLite original
    SQLALCHEMY_DATABASE_URL = "sqlite:///../tbca.db"
    print("Usando SQLite Database")

# Criar engine e sessão
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False  # Definir como True para ver SQL gerado
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função para obter sessão de banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"@
        
        # Fazer backup do arquivo original
        Copy-Item -Path $databaseFilePath -Destination "${databaseFilePath}.bak"
        
        # Escrever novo conteúdo
        $newDatabaseContent | Out-File -FilePath $databaseFilePath
        
        Write-Host "Arquivo database.py adaptado com sucesso." -ForegroundColor Green
    } else {
        Write-Host "Arquivo database.py já tem suporte Oracle." -ForegroundColor Green
    }
} else {
    Write-Host "Erro: Arquivo database.py não encontrado." -ForegroundColor Red
    exit 1
}

# Iniciar servidor backend
Write-Host "Iniciando servidor backend com suporte Oracle..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $backendDir; .\venv\Scripts\Activate.ps1; `$env:USE_ORACLE_DB='true'; uvicorn app.main:app --reload"

# Iniciar frontend
$frontendDir = Join-Path -Path $PSScriptRoot -ChildPath "frontend"
cd $frontendDir

if (-not (Test-Path "node_modules")) {
    Write-Host "Instalando dependências do frontend..." -ForegroundColor Yellow
    npm install
}

Write-Host "Iniciando servidor frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $frontendDir; npm run dev"

# Voltar para o diretório original
cd $PSScriptRoot

Write-Host "`nAplicação iniciada com suporte Oracle!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "`nPara verificar o status da conexão Oracle:" -ForegroundColor Yellow
Write-Host "http://localhost:8000/status" -ForegroundColor Yellow
