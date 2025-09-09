@echo off
REM Script para preparar o primeiro envio do projeto
REM Cria uma pasta com todos os arquivos necessários exceto a base completa

echo ===================================
echo PREPARANDO PACOTE DE ENVIO INICIAL
echo ===================================

REM Criar pasta principal se não existir
if not exist EnvioParaDev mkdir EnvioParaDev

REM Copiar scripts principais
echo Copiando scripts principais...
copy importar_tbca_completo.py EnvioParaDev\
copy menu_tbca_completo.py EnvioParaDev\
copy check_database.py EnvioParaDev\
copy check_database_avancado.py EnvioParaDev\
copy verificacao_inicial_dev.py EnvioParaDev\
copy INSTRUCOES_SEGUNDO_ENVIO.md EnvioParaDev\

REM Copiar pasta nutri-app
echo Copiando pasta nutri-app...
xcopy /E /I /Y nutri-app EnvioParaDev\nutri-app

REM Copiar pasta scripts
echo Copiando pasta scripts...
xcopy /E /I /Y scripts EnvioParaDev\scripts

REM Copiar pasta dados (exceto arquivos grandes)
echo Copiando pasta dados...
if not exist EnvioParaDev\dados mkdir EnvioParaDev\dados
copy dados\*.json EnvioParaDev\dados\
copy dados\teste_tbca.csv EnvioParaDev\dados\
copy dados\teste_completo.csv EnvioParaDev\dados\

REM Criar amostra do arquivo grande
echo Criando amostra do arquivo CSV grande...
powershell -Command "Get-Content composicao_todos_alimentos.csv -TotalCount 200 | Out-File -Encoding utf8 EnvioParaDev\composicao_amostra.csv"

REM Criar README
echo Criando arquivo README...
echo # Projeto Nutri-App > EnvioParaDev\README.md
echo. >> EnvioParaDev\README.md
echo ## Estrutura >> EnvioParaDev\README.md
echo - nutri-app/: Aplicacao principal >> EnvioParaDev\README.md
echo - scripts/: Scripts de migracao >> EnvioParaDev\README.md
echo - dados/: Arquivos de dados pequenos >> EnvioParaDev\README.md
echo. >> EnvioParaDev\README.md
echo ## Importacao da Base >> EnvioParaDev\README.md
echo 1. Execute: python verificacao_inicial_dev.py >> EnvioParaDev\README.md
echo 2. Aguarde o envio da base completa (composicao_todos_alimentos.csv) >> EnvioParaDev\README.md
echo 3. Quando receber, coloque na raiz do projeto e execute: python menu_tbca_completo.py >> EnvioParaDev\README.md
echo. >> EnvioParaDev\README.md
echo ## Notas >> EnvioParaDev\README.md
echo - Foi enviada apenas uma amostra dos dados (composicao_amostra.csv) >> EnvioParaDev\README.md
echo - A base completa sera enviada separadamente >> EnvioParaDev\README.md
echo - Veja mais detalhes em INSTRUCOES_SEGUNDO_ENVIO.md >> EnvioParaDev\README.md

REM Criar uma pasta para logs
mkdir EnvioParaDev\logs

echo.
echo ============================
echo PACOTE DE ENVIO FINALIZADO!
echo ============================
echo.
echo O pacote esta pronto na pasta: EnvioParaDev
echo.
echo Proximo passo: Comprimir a pasta e enviar para o desenvolvedor

pause
