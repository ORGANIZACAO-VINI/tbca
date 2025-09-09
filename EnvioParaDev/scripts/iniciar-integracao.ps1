# Script para iniciar os serviços e testar a integração frontend-backend
# Autor: GitHub Copilot
# Data: Data atual

# Configurações
$backendDir = Join-Path $PSScriptRoot "backend"
$frontendDir = Join-Path $PSScriptRoot "frontend"
$testScript = Join-Path $backendDir "tests\test_integracao.py"
$logDir = Join-Path $PSScriptRoot "logs"

# Criar diretório de logs se não existir
if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory | Out-Null
    Write-Host "Diretório de logs criado: $logDir"
}

# Registrar início da execução
$logFile = Join-Path $logDir "integracao_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
"Iniciando teste de integração: $(Get-Date)" | Out-File -FilePath $logFile

function Install-Dependencies {
    Write-Host "Verificando dependências..." -ForegroundColor Cyan
    
    # Verificar se Python está instalado
    try {
        $pythonVersion = python --version
        Write-Host "Python instalado: $pythonVersion" -ForegroundColor Green
        "Python instalado: $pythonVersion" | Out-File -FilePath $logFile -Append
    } catch {
        Write-Host "Erro: Python não encontrado. Por favor, instale o Python e tente novamente." -ForegroundColor Red
        "Erro: Python não encontrado" | Out-File -FilePath $logFile -Append
        exit 1
    }
    
    # Verificar se Node.js está instalado
    try {
        $nodeVersion = node --version
        Write-Host "Node.js instalado: $nodeVersion" -ForegroundColor Green
        "Node.js instalado: $nodeVersion" | Out-File -FilePath $logFile -Append
    } catch {
        Write-Host "Erro: Node.js não encontrado. Por favor, instale o Node.js e tente novamente." -ForegroundColor Red
        "Erro: Node.js não encontrado" | Out-File -FilePath $logFile -Append
        exit 1
    }
    
    # Instalar dependências do Python
    Write-Host "Instalando dependências do Python..." -ForegroundColor Yellow
    pip install -r "$backendDir\requirements.txt" | Out-File -FilePath $logFile -Append
    pip install requests | Out-File -FilePath $logFile -Append
    
    # Instalar dependências do Node.js
    Write-Host "Instalando dependências do Node.js..." -ForegroundColor Yellow
    Set-Location -Path $frontendDir
    npm install | Out-File -FilePath $logFile -Append
    Set-Location -Path $PSScriptRoot
}

function Start-Backend {
    Write-Host "Iniciando o servidor backend..." -ForegroundColor Cyan
    
    # Verificar se o backend já está rodando
    $backendRunning = $false
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendRunning = $true
            Write-Host "O servidor backend já está rodando!" -ForegroundColor Green
        }
    } catch {}
    
    if (-not $backendRunning) {
        Set-Location -Path $backendDir
        Start-Process -FilePath "powershell.exe" -ArgumentList "-Command cd $backendDir; uvicorn app.main:app --reload" -WindowStyle Normal
        Write-Host "Backend iniciado em http://localhost:8000" -ForegroundColor Green
        "Backend iniciado em http://localhost:8000" | Out-File -FilePath $logFile -Append
        
        # Aguardar backend iniciar
        Write-Host "Aguardando o backend iniciar..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

function Start-Frontend {
    Write-Host "Iniciando o servidor frontend..." -ForegroundColor Cyan
    
    # Verificar se o frontend já está rodando
    $frontendRunning = $false
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $frontendRunning = $true
            Write-Host "O servidor frontend já está rodando!" -ForegroundColor Green
        }
    } catch {}
    
    if (-not $frontendRunning) {
        Set-Location -Path $frontendDir
        Start-Process -FilePath "powershell.exe" -ArgumentList "-Command cd $frontendDir; npm run dev" -WindowStyle Normal
        Write-Host "Frontend iniciado em http://localhost:3000" -ForegroundColor Green
        "Frontend iniciado em http://localhost:3000" | Out-File -FilePath $logFile -Append
        
        # Aguardar frontend iniciar
        Write-Host "Aguardando o frontend iniciar..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}

function Test-Integration {
    Write-Host "Executando teste de integração..." -ForegroundColor Cyan
    
    # Aguardar alguns segundos para garantir que os serviços estão prontos
    Start-Sleep -Seconds 5
    
    # Executar o script de teste
    if (Test-Path $testScript) {
        python $testScript | Tee-Object -FilePath $logFile -Append
        
        Write-Host "`nAcesse a aplicação no navegador: http://localhost:3000" -ForegroundColor Magenta
        Write-Host "Documentação da API: http://localhost:8000/docs" -ForegroundColor Magenta
        
        # Perguntar se deseja abrir o navegador
        $openBrowser = Read-Host "Deseja abrir a aplicação no navegador? (S/N)"
        if ($openBrowser -eq "S" -or $openBrowser -eq "s") {
            Start-Process "http://localhost:3000"
        }
    } else {
        Write-Host "Erro: Script de teste não encontrado: $testScript" -ForegroundColor Red
        "Erro: Script de teste não encontrado: $testScript" | Out-File -FilePath $logFile -Append
        
        # Sugerir executar no diretório correto
        Write-Host "Dica: Certifique-se de executar este script a partir do diretório raiz do projeto." -ForegroundColor Yellow
        Write-Host "      Você pode precisar usar: cd C:\Users\vinim\Downloads\script" -ForegroundColor Yellow
    }
}

# Menu principal
function Show-Menu {
    Write-Host "`n============ MENU DE INTEGRAÇÃO NUTRI-APP ============" -ForegroundColor Cyan
    Write-Host "1. Instalar dependências"
    Write-Host "2. Iniciar Backend"
    Write-Host "3. Iniciar Frontend"
    Write-Host "4. Testar Integração"
    Write-Host "5. Iniciar tudo (1 + 2 + 3 + 4)"
    Write-Host "6. Sair"
    Write-Host "======================================================" -ForegroundColor Cyan
    
    $choice = Read-Host "Escolha uma opção"
    
    switch ($choice) {
        "1" { Install-Dependencies; Show-Menu }
        "2" { Start-Backend; Show-Menu }
        "3" { Start-Frontend; Show-Menu }
        "4" { Test-Integration; Show-Menu }
        "5" { 
            Install-Dependencies
            Start-Backend
            Start-Frontend
            Test-Integration
            Show-Menu
        }
        "6" { return }
        default { 
            Write-Host "Opção inválida. Tente novamente." -ForegroundColor Red
            Show-Menu
        }
    }
}

# Iniciar o menu
Show-Menu

# Registrar fim da execução
"Finalizado teste de integração: $(Get-Date)" | Out-File -FilePath $logFile -Append
