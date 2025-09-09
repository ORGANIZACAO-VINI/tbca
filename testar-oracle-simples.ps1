# Script PowerShell para testar configuracao Oracle
# Autor: Script automatizado
# Data: 2025-01-09

param(
    [switch]$Setup,
    [switch]$Test,
    [switch]$Full,
    [switch]$Help,
    [string]$ConfigFile = "config/oracle_config.json"
)

# Cores para output formatado
$ErrorColor = "Red"
$SuccessColor = "Green"
$WarningColor = "Yellow"
$InfoColor = "Cyan"

function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Show-Help {
    Write-ColorMessage "SCRIPT DE TESTES ORACLE - VERSAO APRIMORADA" $InfoColor
    Write-ColorMessage "===========================================" $InfoColor
    Write-Host ""
    Write-ColorMessage "PARAMETROS:" $InfoColor
    Write-Host "  -Setup    : Configuracao interativa do Oracle"
    Write-Host "  -Test     : Executar testes basicos"
    Write-Host "  -Full     : Executar suite completa de testes"
    Write-Host "  -Help     : Mostrar esta ajuda"
    Write-Host ""
    Write-ColorMessage "EXEMPLOS:" $InfoColor
    Write-Host "  .\testar-oracle-simples.ps1 -Setup"
    Write-Host "  .\testar-oracle-simples.ps1 -Test"
    Write-Host "  .\testar-oracle-simples.ps1 -Full"
    Write-Host ""
}

function Test-PythonEnvironment {
    Write-ColorMessage "VERIFICANDO AMBIENTE PYTHON" $InfoColor
    Write-ColorMessage "============================" $InfoColor
    
    # Verificar se Python esta instalado
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorMessage "Python encontrado: $pythonVersion" $SuccessColor
    }
    catch {
        Write-ColorMessage "Python nao encontrado no PATH!" $ErrorColor
        Write-ColorMessage "Instale Python e adicione ao PATH do sistema" $WarningColor
        return $false
    }
    
    # Verificar bibliotecas necessarias
    $libraries = @("cx_Oracle", "tabulate", "matplotlib")
    $missingLibs = @()
    
    foreach ($lib in $libraries) {
        try {
            python -c "import $lib" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ColorMessage "$lib - OK" $SuccessColor
            } else {
                Write-ColorMessage "$lib - Nao instalado" $WarningColor
                $missingLibs += $lib
            }
        }
        catch {
            Write-ColorMessage "$lib - Nao instalado" $WarningColor
            $missingLibs += $lib
        }
    }
    
    if ($missingLibs.Count -gt 0) {
        Write-ColorMessage "Instalando bibliotecas necessarias..." $InfoColor
        foreach ($lib in $missingLibs) {
            Write-ColorMessage "   Instalando $lib..." $InfoColor
            pip install $lib
        }
    }
    
    return $true
}

function Start-OracleConfig {
    Write-ColorMessage "CONFIGURACAO INTERATIVA DO ORACLE" $InfoColor
    Write-ColorMessage "==================================" $InfoColor
    
    # Verificar se o script de configuracao existe
    if (-not (Test-Path "oracle_config_utils.py")) {
        Write-ColorMessage "Script oracle_config_utils.py nao encontrado!" $ErrorColor
        return $false
    }
    
    # Executar configuracao interativa
    try {
        Write-ColorMessage "Iniciando configuracao interativa..." $InfoColor
        python oracle_config_utils.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorMessage "Configuracao concluida com sucesso!" $SuccessColor
            return $true
        } else {
            Write-ColorMessage "Erro durante a configuracao!" $ErrorColor
            return $false
        }
    }
    catch {
        Write-ColorMessage "Erro ao executar configuracao: $_" $ErrorColor
        return $false
    }
}

function Start-OracleTests {
    param(
        [bool]$FullTest = $false
    )
    
    Write-ColorMessage "EXECUTANDO TESTES ORACLE" $InfoColor
    Write-ColorMessage "=========================" $InfoColor
    
    # Verificar se o arquivo de teste existe
    if (-not (Test-Path "test_oracle_performance.py")) {
        Write-ColorMessage "Script test_oracle_performance.py nao encontrado!" $ErrorColor
        return $false
    }
    
    # Verificar se ha configuracao
    if (-not (Test-Path $ConfigFile)) {
        Write-ColorMessage "Arquivo de configuracao nao encontrado: $ConfigFile" $WarningColor
        Write-ColorMessage "Execute primeiro: .\testar-oracle-simples.ps1 -Setup" $InfoColor
        return $false
    }
    
    try {
        Write-ColorMessage "Iniciando testes..." $InfoColor
        
        if ($FullTest) {
            Write-ColorMessage "Executando suite completa de testes..." $InfoColor
            python test_oracle_performance.py --full
        } else {
            Write-ColorMessage "Executando testes basicos..." $InfoColor
            python test_oracle_performance.py
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorMessage "Testes executados com sucesso!" $SuccessColor
            return $true
        } else {
            Write-ColorMessage "Alguns testes falharam!" $ErrorColor
            return $false
        }
    }
    catch {
        Write-ColorMessage "Erro ao executar testes: $_" $ErrorColor
        return $false
    }
}

function Main {
    Write-ColorMessage "ORACLE DATABASE TESTING SUITE" $InfoColor
    Write-ColorMessage "==============================" $InfoColor
    Write-Host ""
    
    # Mostrar ajuda se solicitado
    if ($Help) {
        Show-Help
        return
    }
    
    # Se nenhum parametro foi especificado, mostrar ajuda
    if (-not $Setup -and -not $Test -and -not $Full) {
        Write-ColorMessage "Nenhuma acao especificada!" $WarningColor
        Show-Help
        return
    }
    
    # Verificar ambiente Python primeiro
    $pythonOk = Test-PythonEnvironment
    if (-not $pythonOk) {
        Write-ColorMessage "Ambiente Python nao esta adequado!" $ErrorColor
        return
    }
    
    Write-Host ""
    
    # Verificar se estamos no diretorio correto
    if (-not (Test-Path "test_oracle_performance.py")) {
        Write-ColorMessage "Execute este script do diretorio correto!" $ErrorColor
        Write-ColorMessage "O diretorio deve conter test_oracle_performance.py" $InfoColor
        return
    }
    
    # Executar acoes solicitadas
    if ($Setup) {
        $success = Start-OracleConfig
        if ($success) {
            Write-ColorMessage "Configuracao concluida! Agora voce pode executar os testes." $SuccessColor
        }
    }
    
    if ($Test) {
        $success = Start-OracleTests -FullTest $false
        if ($success) {
            Write-ColorMessage "Testes basicos concluidos!" $SuccessColor
        }
    }
    
    if ($Full) {
        $success = Start-OracleTests -FullTest $true
        if ($success) {
            Write-ColorMessage "Suite completa de testes concluida!" $SuccessColor
        }
    }
    
    Write-Host ""
    Write-ColorMessage "Script finalizado!" $InfoColor
}

# Executar funcao principal
Main
