# Script simples para iniciar os serviços e testar a integração

# Configurações
$backendDir = Join-Path $PSScriptRoot "backend"
$frontendDir = Join-Path $PSScriptRoot "frontend"
$logDir = Join-Path $PSScriptRoot "logs"

# Verificar se log dir existe
if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory | Out-Null
    Write-Host "Diretório de logs criado: $logDir"
}

$logFile = Join-Path $logDir "teste_rapido_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
"Iniciando teste rápido: $(Get-Date)" | Out-File -FilePath $logFile

# Testar se o backend já está rodando
function Test-Backend {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Backend já está funcionando em http://localhost:8000" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "[INFO] Backend não está rodando ainda" -ForegroundColor Yellow
        return $false
    }
}

# Testar se o frontend já está rodando
function Test-Frontend {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Frontend já está funcionando em http://localhost:3000" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "[INFO] Frontend não está rodando ainda" -ForegroundColor Yellow
        return $false
    }
}

# Executar verificação
Write-Host "=== Verificando Serviços de Integração ===" -ForegroundColor Cyan
$backendRunning = Test-Backend
$frontendRunning = Test-Frontend

Write-Host "`n=== Resumo da Verificação ===" -ForegroundColor Cyan
if ($backendRunning -and $frontendRunning) {
    Write-Host "[OK] Backend e Frontend estão rodando!" -ForegroundColor Green
    Write-Host "Para testar a integração completa, abra o frontend no navegador: http://localhost:3000" -ForegroundColor Magenta
    
    $openBrowser = Read-Host "Deseja abrir o frontend no navegador? (S/N)"
    if ($openBrowser -eq "S" -or $openBrowser -eq "s") {
        Start-Process "http://localhost:3000"
    }
} else {
    Write-Host "[INFO] Nem todos os serviços estão rodando." -ForegroundColor Yellow
    Write-Host "Para iniciar todos os serviços, execute ./iniciar-integracao.ps1" -ForegroundColor Cyan
}

# Se desejar limpar os arquivos de teste
$cleanup = Read-Host "Deseja remover os arquivos de teste criados? (S/N)"
if ($cleanup -eq "S" -or $cleanup -eq "s") {
    # Lista de arquivos para potencialmente remover
    $testFiles = @(
        (Join-Path $PSScriptRoot "testar_estrutura.py"),
        (Join-Path $backendDir "requirements.txt")
    )
    
    foreach ($file in $testFiles) {
        if (Test-Path $file) {
            Write-Host "Removendo $file" -ForegroundColor Yellow
            Remove-Item $file -Force
        }
    }
    
    Write-Host "Arquivos de teste removidos." -ForegroundColor Green
}
