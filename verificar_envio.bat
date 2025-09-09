@echo off
REM Script para testar se o pacote de envio está completo e funcional

echo =======================================
echo VERIFICACAO DO PACOTE DE ENVIO INICIAL
echo =======================================

cd EnvioParaDev

echo.
echo Verificando arquivos essenciais...
set MISSING=0

REM Verificar scripts principais
if not exist menu_tbca_completo.py (
    echo [ERRO] Arquivo nao encontrado: menu_tbca_completo.py
    set MISSING=1
)
if not exist importar_tbca_completo.py (
    echo [ERRO] Arquivo nao encontrado: importar_tbca_completo.py
    set MISSING=1
)
if not exist check_database_avancado.py (
    echo [ERRO] Arquivo nao encontrado: check_database_avancado.py
    set MISSING=1
)
if not exist verificacao_inicial_dev.py (
    echo [ERRO] Arquivo nao encontrado: verificacao_inicial_dev.py
    set MISSING=1
)
if not exist composicao_amostra.csv (
    echo [ERRO] Arquivo nao encontrado: composicao_amostra.csv
    set MISSING=1
)

REM Verificar pastas principais
if not exist nutri-app (
    echo [ERRO] Pasta nao encontrada: nutri-app
    set MISSING=1
)
if not exist scripts (
    echo [ERRO] Pasta nao encontrada: scripts
    set MISSING=1
)
if not exist dados (
    echo [ERRO] Pasta nao encontrada: dados
    set MISSING=1
)
if not exist logs (
    echo [ERRO] Pasta nao encontrada: logs
    set MISSING=1
)

REM Verificar banco de dados
if not exist nutri-app\backend\tbca.db (
    echo [ERRO] Banco de dados nao encontrado: nutri-app\backend\tbca.db
    set MISSING=1
)

REM Mostrar resultado
echo.
if %MISSING%==0 (
    echo [OK] Todos os arquivos essenciais estao presentes!
) else (
    echo [ATENCAO] Faltam arquivos essenciais! Verifique os erros acima.
)

echo.
echo Executando verificacao inicial...
echo.
python verificacao_inicial_dev.py

echo.
echo =======================================
echo VERIFICACAO CONCLUIDA!
echo =======================================
echo.
echo Se todos os testes passaram, o pacote esta pronto para envio.
echo Caso contrario, corrija os problemas e execute este script novamente.

cd ..
pause
