# Script PowerShell para executar testes Oracle de forma facilitada
# Versão: 2.0 - Aprimorada com melhor interface e validações

param(
    [switch]$Setup,
    [switch]$Test,
    [switch]$Quick,
    [int]$Iterations = 5,
    [int]$PoolSize = 5,
    [int]$Concurrency = 10,
    [switch]$Help,
    [switch]$Verbose
)

# Cores para output
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Show-Help {
    Write-ColorMessage "=== ORACLE TESTING SUITE - HELP ===" $InfoColor
    Write-Host ""
    Write-ColorMessage "DESCRIÇÃO:" $InfoColor
    Write-Host "  Script para facilitar testes Oracle com interface aprimorada"
    Write-Host ""
    Write-ColorMessage "USO:" $InfoColor
    Write-Host "  .\testar-oracle-aprimorado.ps1 [OPÇÕES]"
    Write-Host ""
    Write-ColorMessage "OPÇÕES:" $InfoColor
    Write-Host "  -Setup              Configurar ambiente Oracle interativamente"
    Write-Host "  -Test               Executar todos os testes Oracle"
    Write-Host "  -Quick              Executar testes rápidos (3 iterações)"
    Write-Host "  -Iterations <num>   Número de iterações para testes (padrão: 5)"
    Write-Host "  -PoolSize <num>     Tamanho máximo do pool (padrão: 5)"
    Write-Host "  -Concurrency <num>  Operações concorrentes (padrão: 10)"
    Write-Host "  -Help               Mostrar esta ajuda"
    Write-Host ""
    Write-ColorMessage "EXEMPLOS:" $InfoColor
    Write-Host "  .\testar-oracle-aprimorado.ps1 -Setup"
    Write-Host "  .\testar-oracle-aprimorado.ps1 -Test"
    Write-Host "  .\testar-oracle-aprimorado.ps1 -Quick"
    Write-Host "  .\testar-oracle-aprimorado.ps1 -Test -Iterations 10 -PoolSize 8"
    Write-Host ""
}

function Test-PythonEnvironment {
    Write-ColorMessage "🔍 Verificando ambiente Python..." $InfoColor
    
    # Verificar se Python existe
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorMessage "✅ Python encontrado: $pythonVersion" $SuccessColor
    }
    catch {
        Write-ColorMessage "❌ Python não encontrado! Instale Python 3.8 ou superior." $ErrorColor
        return $false
    }
    
    # Verificar bibliotecas necessárias
    $libraries = @("cx_Oracle", "tabulate", "matplotlib")
    $missingLibs = @()
    
    foreach ($lib in $libraries) {
        python -c "import $lib" 2>$null
        if ($LASTEXITCODE -eq 0) {
            if ($Verbose) {
                Write-ColorMessage "✅ ${lib} - OK" $SuccessColor
            }
        } else {
            Write-ColorMessage "⚠️  ${lib} - Não instalado" $WarningColor
            $missingLibs += $lib
        }
    }
    
    if ($missingLibs.Count -gt 0) {
        Write-ColorMessage "📦 Instalando bibliotecas necessárias..." $InfoColor
        foreach ($lib in $missingLibs) {
            Write-ColorMessage "   Instalando ${lib}..." $InfoColor
            pip install $lib
        }
    }
    
    return $true
}

function Setup-OracleConfig {
    Write-ColorMessage "⚙️ CONFIGURAÇÃO INTERATIVA DO ORACLE" $InfoColor
    Write-ColorMessage "====================================" $InfoColor
    
    if (-not (Test-PythonEnvironment)) {
        Write-ColorMessage "❌ Falha na verificação do ambiente Python." $ErrorColor
        return $false
    }
    
    # Verificar se o script de configuração existe
    $configScript = "scripts\oracle_config_utils.py"
    if (-not (Test-Path $configScript)) {
        Write-ColorMessage "❌ Script de configuração não encontrado: $configScript" $ErrorColor
        return $false
    }
    
    Write-ColorMessage "🚀 Iniciando configuração interativa..." $InfoColor
    python $configScript create
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorMessage "✅ Configuração criada com sucesso!" $SuccessColor
        
        # Validar configuração criada
        Write-ColorMessage "🔍 Validando configuração..." $InfoColor
        python $configScript validate
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorMessage "✅ Configuração válida!" $SuccessColor
            return $true
        } else {
            Write-ColorMessage "❌ Configuração inválida!" $ErrorColor
            return $false
        }
    } else {
        Write-ColorMessage "❌ Falha na criação da configuração!" $ErrorColor
        return $false
    }
}

function Run-OracleTests {
    param(
        [int]$TestIterations = 5,
        [int]$TestPoolSize = 5,
        [int]$TestConcurrency = 10
    )
    
    Write-ColorMessage "🧪 EXECUTANDO TESTES ORACLE APRIMORADOS" $InfoColor
    Write-ColorMessage "=======================================" $InfoColor
    Write-ColorMessage "Iterações: $TestIterations | Pool: $TestPoolSize | Concorrência: $TestConcurrency" $InfoColor
    Write-Host ""
    
    if (-not (Test-PythonEnvironment)) {
        Write-ColorMessage "❌ Falha na verificação do ambiente Python." $ErrorColor
        return $false
    }
    
    # Verificar se arquivo de configuração existe
    $configFile = "config\oracle_config.json"
    if (-not (Test-Path $configFile)) {
        Write-ColorMessage "❌ Configuração Oracle não encontrada!" $ErrorColor
        Write-ColorMessage "💡 Execute: .\testar-oracle-aprimorado.ps1 -Setup" $InfoColor
        return $false
    }
    
    # Verificar se script de teste existe
    $testScript = "scripts\test_oracle_performance.py"
    if (-not (Test-Path $testScript)) {
        Write-ColorMessage "❌ Script de teste não encontrado: $testScript" $ErrorColor
        return $false
    }
    
    # Executar testes
    Write-ColorMessage "🚀 Iniciando bateria de testes..." $InfoColor
    Write-Host ""
    
    $startTime = Get-Date
    python $testScript --iterations $TestIterations --pool-size $TestPoolSize --concurrency $TestConcurrency
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host ""
    if ($LASTEXITCODE -eq 0) {
        Write-ColorMessage "🎉 TESTES CONCLUÍDOS COM SUCESSO!" $SuccessColor
        Write-ColorMessage "⏱️  Tempo total: $($duration.TotalSeconds) segundos" $InfoColor
        
        # Mostrar localização dos relatórios
        $logsDir = "logs"
        if (Test-Path $logsDir) {
            $latestLog = Get-ChildItem $logsDir -Filter "oracle_test_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($latestLog) {
                Write-ColorMessage "📄 Relatório detalhado: $($latestLog.FullName)" $InfoColor
            }
            
            $latestGraph = Get-ChildItem $logsDir -Filter "oracle_performance_*.png" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($latestGraph) {
                Write-ColorMessage "📊 Gráfico de performance: $($latestGraph.FullName)" $InfoColor
            }
        }
        
        return $true
    } else {
        Write-ColorMessage "❌ ALGUNS TESTES FALHARAM!" $ErrorColor
        Write-ColorMessage "🔧 Verifique os detalhes acima e corrija os problemas." $WarningColor
        return $false
    }
}

function Run-QuickTests {
    Write-ColorMessage "⚡ EXECUÇÃO RÁPIDA DE TESTES" $InfoColor
    Write-ColorMessage "===========================" $InfoColor
    
    return Run-OracleTests -TestIterations 3 -TestPoolSize 3 -TestConcurrency 5
}

function Show-Banner {
    Write-ColorMessage "╔══════════════════════════════════════════════════════════╗" $InfoColor
    Write-ColorMessage "║            🚀 ORACLE TESTING SUITE v2.0 🚀              ║" $InfoColor
    Write-ColorMessage "║                  Versão Aprimorada                       ║" $InfoColor
    Write-ColorMessage "╚══════════════════════════════════════════════════════════╝" $InfoColor
    Write-Host ""
}

# Função principal
function Main {
    Show-Banner
    
    if ($Help) {
        Show-Help
        return
    }
    
    if (-not $Setup -and -not $Test -and -not $Quick) {
        Write-ColorMessage "❓ Nenhuma ação especificada!" $WarningColor
        Write-ColorMessage "💡 Use -Help para ver as opções disponíveis" $InfoColor
        Show-Help
        return
    }
    
    # Verificar se estamos no diretório correto
    if (-not (Test-Path "scripts") -or -not (Test-Path "config")) {
        Write-ColorMessage "❌ Execute este script do diretório raiz do projeto!" $ErrorColor
        Write-ColorMessage "💡 O diretório deve conter as pastas 'scripts' e 'config'" $InfoColor
        return
    }
    
    # Executar ações solicitadas
    if ($Setup) {
        $success = Setup-OracleConfig
        if ($success) {
            Write-ColorMessage "🎯 Próximo passo: Execute .\testar-oracle-aprimorado.ps1 -Test" $InfoColor
        }
    }
    
    if ($Test) {
        $success = Run-OracleTests -TestIterations $Iterations -TestPoolSize $PoolSize -TestConcurrency $Concurrency
        if ($success) {
            Write-ColorMessage "🎯 Próximo passo: Execute a migração de dados para Oracle" $InfoColor
        }
    }
    
    if ($Quick) {
        $success = Run-QuickTests
        if ($success) {
            Write-ColorMessage "🎯 Testes rápidos OK! Para testes completos use: -Test" $InfoColor
        }
    }
}

# Executar função principal
Main
