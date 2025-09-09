# Script para configurar ambiente Oracle para desenvolvimento
Write-Host "=== Configurando Ambiente Oracle para NutriApp ===" -ForegroundColor Cyan

# Verificar se temos o Oracle Client instalado
$oracleClientInstalled = $false
try {
    $oraclePath = Get-ItemProperty -Path "HKLM:\SOFTWARE\Oracle\*" -ErrorAction SilentlyContinue
    if ($oraclePath) {
        $oracleClientInstalled = $true
        Write-Host "[OK] Oracle Client já está instalado" -ForegroundColor Green
    }
} catch {
    $oracleClientInstalled = $false
}

if (-not $oracleClientInstalled) {
    Write-Host "[INFO] Oracle Client não encontrado." -ForegroundColor Yellow
    Write-Host "Por favor, baixe e instale o Oracle Instant Client de: https://www.oracle.com/database/technologies/instant-client/downloads.html"
    
    $installClient = Read-Host "Deseja abrir a página de download do Oracle Instant Client? (S/N)"
    if ($installClient -eq "S" -or $installClient -eq "s") {
        Start-Process "https://www.oracle.com/database/technologies/instant-client/downloads.html"
    }
}

# Criar/ativar ambiente virtual Python com suporte a cx_Oracle
cd backend
if (-not (Test-Path .\venv)) {
    Write-Host "Criando ambiente virtual Python..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Instalando cx_Oracle e outras dependências Oracle
Write-Host "Instalando dependências Oracle..." -ForegroundColor Yellow
pip install cx_Oracle sqlalchemy-oracle fastapi uvicorn sqlalchemy pydantic

# Configurar variáveis de ambiente Oracle
$env:ORACLE_HOME = $oraclePath.ORACLE_HOME
$env:TNS_ADMIN = "$env:ORACLE_HOME\network\admin"
$env:PATH = "$env:ORACLE_HOME\bin;$env:PATH"

# Criar arquivo de configuração Oracle para a aplicação
$configDir = "..\config"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir | Out-Null
}

# Criar arquivo de configuração com credenciais Oracle
$oracleConfigFile = "$configDir\oracle_config.json"
$defaultConfig = @{
    ORACLE_USER = "nutri_app"
    ORACLE_PASSWORD = "mudar_senha"
    ORACLE_HOST = "localhost"
    ORACLE_PORT = "1521"
    ORACLE_SERVICE = "XEPDB1"
    ORACLE_SCHEMA = "nutri_app"
}

$defaultConfig | ConvertTo-Json | Out-File -FilePath $oracleConfigFile

Write-Host "Arquivo de configuração Oracle criado em: $oracleConfigFile" -ForegroundColor Green
Write-Host "IMPORTANTE: Edite este arquivo com suas credenciais reais antes de conectar." -ForegroundColor Yellow

# Verificar conexão Oracle
Write-Host "`nDeseja testar a conexão com o banco Oracle? (S/N)" -ForegroundColor Cyan
$testConnection = Read-Host

if ($testConnection -eq "S" -or $testConnection -eq "s") {
    Write-Host "Testando conexão com Oracle..." -ForegroundColor Yellow
    
    $testScript = @"
import cx_Oracle
import json
import os

try:
    # Ler configurações
    config_path = os.path.join('..', 'config', 'oracle_config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Construir string de conexão
    dsn = cx_Oracle.makedsn(
        host=config['ORACLE_HOST'],
        port=config['ORACLE_PORT'],
        service_name=config['ORACLE_SERVICE']
    )
    
    # Tentar conectar
    connection = cx_Oracle.connect(
        user=config['ORACLE_USER'],
        password=config['ORACLE_PASSWORD'],
        dsn=dsn
    )
    
    print("Conexão com Oracle estabelecida com sucesso!")
    print(f"Versão do banco: {connection.version}")
    
    # Executar query simples
    cursor = connection.cursor()
    cursor.execute("SELECT SYSDATE FROM DUAL")
    result = cursor.fetchone()
    print(f"Data e hora do servidor: {result[0]}")
    
    # Fechar conexão
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Erro ao conectar ao Oracle: {str(e)}")
    print("Verifique suas credenciais no arquivo config/oracle_config.json")
"@

    $testScript | Out-File -FilePath "test_oracle_connection.py"
    python test_oracle_connection.py
    Remove-Item "test_oracle_connection.py"
}

# Criar arquivos adaptados para Oracle
Write-Host "`nCriando arquivos de adaptação Oracle..." -ForegroundColor Yellow

# Criar modelo de banco de dados adaptado para Oracle
$modelOraclePath = "app\models\oracle_models.py"
if (-not (Test-Path $modelOraclePath)) {
    $modelOracleContent = @"
# Modelos SQLAlchemy adaptados para Oracle
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, MetaData, DateTime, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

# Tabela de categorias
class Categoria(Base):
    __tablename__ = 'categorias'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    
    alimentos = relationship("Alimento", back_populates="categoria")

# Tabela de alimentos
class Alimento(Base):
    __tablename__ = 'alimentos'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(20), unique=True)
    nome = Column(String(200), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    kcal = Column(Float)
    carboidratos = Column(Float)
    proteina = Column(Float)
    gordura = Column(Float)
    fibras = Column(Float)
    calcio = Column(Float)
    ferro = Column(Float)
    
    categoria = relationship("Categoria", back_populates="alimentos")
    
# Tabela de usuários
class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(64), nullable=False)
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    ultimo_acesso = Column(DateTime)
    perfil = Column(String(20), default='regular')
    
    diarios = relationship("DiarioAlimentar", back_populates="usuario")

# Tabela de diário alimentar
class DiarioAlimentar(Base):
    __tablename__ = 'diario_alimentar'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    data_registro = Column(DateTime, nullable=False)
    hora_registro = Column(String(5), nullable=False)
    tipo_refeicao = Column(String(20))
    descricao = Column(String(200))
    
    usuario = relationship("Usuario", back_populates="diarios")
    itens = relationship("ItemDiario", back_populates="diario")

# Tabela de itens do diário
class ItemDiario(Base):
    __tablename__ = 'itens_diario'
    
    id = Column(Integer, primary_key=True)
    diario_id = Column(Integer, ForeignKey('diario_alimentar.id'), nullable=False)
    alimento_id = Column(Integer, ForeignKey('alimentos.id'), nullable=False)
    quantidade_g = Column(Float, nullable=False)
    
    diario = relationship("DiarioAlimentar", back_populates="itens")
    alimento = relationship("Alimento")
"@

    New-Item -ItemType Directory -Path "app\models" -Force | Out-Null
    $modelOracleContent | Out-File -FilePath $modelOraclePath
    Write-Host "[OK] Arquivo de modelos Oracle criado: $modelOraclePath" -ForegroundColor Green
}

# Criar arquivo de conexão Oracle
$dbOraclePath = "app\models\oracle_database.py"
if (-not (Test-Path $dbOraclePath)) {
    $dbOracleContent = @"
# Módulo de conexão Oracle
import json
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import cx_Oracle

# Ler configurações
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

# Criar engine e sessão
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=2,
    echo=False  # Definir como True para ver SQL gerado
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para obter sessão de banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"@

    New-Item -ItemType Directory -Path "app\models" -Force | Out-Null
    $dbOracleContent | Out-File -FilePath $dbOraclePath
    Write-Host "[OK] Arquivo de conexão Oracle criado: $dbOraclePath" -ForegroundColor Green
}

# Criar script para definir PL/SQL procedures
$plsqlScriptPath = "data\scripts\create_plsql_procedures.sql"
if (-not (Test-Path $plsqlScriptPath)) {
    $plsqlScriptContent = @"
-- Script para criar procedures e funções PL/SQL para a aplicação NutriApp

-- Package para cálculos nutricionais
CREATE OR REPLACE PACKAGE nutri_calculos AS
    -- Tipo para armazenar resultados de cálculos nutricionais
    TYPE resultado_nutricional IS RECORD (
        kcal NUMBER,
        proteina NUMBER,
        carboidratos NUMBER,
        gordura NUMBER,
        fibras NUMBER
    );
    
    -- Função para calcular valores nutricionais de uma refeição
    FUNCTION calcular_refeicao(p_diario_id IN NUMBER) 
    RETURN resultado_nutricional;
    
    -- Procedimento para gerar recomendações baseadas em perfil
    PROCEDURE gerar_recomendacoes(
        p_usuario_id IN NUMBER,
        p_objetivo IN VARCHAR2,
        p_resultado OUT SYS_REFCURSOR
    );
END nutri_calculos;
/

-- Implementação do package
CREATE OR REPLACE PACKAGE BODY nutri_calculos AS
    -- Função para calcular valores nutricionais de uma refeição
    FUNCTION calcular_refeicao(p_diario_id IN NUMBER) 
    RETURN resultado_nutricional IS
        v_resultado resultado_nutricional;
    BEGIN
        -- Inicializar resultado
        v_resultado.kcal := 0;
        v_resultado.proteina := 0;
        v_resultado.carboidratos := 0;
        v_resultado.gordura := 0;
        v_resultado.fibras := 0;
        
        -- Calcular totais
        SELECT 
            SUM(a.kcal * i.quantidade_g / 100),
            SUM(a.proteina * i.quantidade_g / 100),
            SUM(a.carboidratos * i.quantidade_g / 100),
            SUM(a.gordura * i.quantidade_g / 100),
            SUM(a.fibras * i.quantidade_g / 100)
        INTO 
            v_resultado.kcal,
            v_resultado.proteina,
            v_resultado.carboidratos,
            v_resultado.gordura,
            v_resultado.fibras
        FROM 
            itens_diario i
            JOIN alimentos a ON i.alimento_id = a.id
        WHERE 
            i.diario_id = p_diario_id;
            
        RETURN v_resultado;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RETURN v_resultado;
        WHEN OTHERS THEN
            RAISE;
    END calcular_refeicao;
    
    -- Procedimento para gerar recomendações
    PROCEDURE gerar_recomendacoes(
        p_usuario_id IN NUMBER,
        p_objetivo IN VARCHAR2,
        p_resultado OUT SYS_REFCURSOR
    ) IS
    BEGIN
        -- Exemplo simples de recomendação baseada em objetivo
        IF p_objetivo = 'emagrecimento' THEN
            OPEN p_resultado FOR
                SELECT 
                    a.id, a.nome, a.kcal, a.proteina, a.gordura
                FROM 
                    alimentos a
                WHERE 
                    a.kcal < 200 AND a.proteina > 10
                ORDER BY 
                    a.proteina DESC, a.kcal ASC;
        ELSIF p_objetivo = 'ganho_muscular' THEN
            OPEN p_resultado FOR
                SELECT 
                    a.id, a.nome, a.kcal, a.proteina, a.gordura
                FROM 
                    alimentos a
                WHERE 
                    a.proteina > 15
                ORDER BY 
                    a.proteina DESC;
        ELSE
            -- Recomendação padrão balanceada
            OPEN p_resultado FOR
                SELECT 
                    a.id, a.nome, a.kcal, a.proteina, a.gordura
                FROM 
                    alimentos a
                WHERE 
                    a.kcal BETWEEN 100 AND 300
                ORDER BY 
                    a.id;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE;
    END gerar_recomendacoes;
END nutri_calculos;
/

-- Criar tabela de log para auditoria
CREATE TABLE log_auditoria (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tabela VARCHAR2(50),
    operacao VARCHAR2(10),
    usuario VARCHAR2(50),
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dados_antigos CLOB,
    dados_novos CLOB
);

-- Trigger para auditoria de alimentos
CREATE OR REPLACE TRIGGER trg_audit_alimentos
AFTER INSERT OR UPDATE OR DELETE ON alimentos
FOR EACH ROW
DECLARE
    v_operacao VARCHAR2(10);
    v_dados_antigos CLOB;
    v_dados_novos CLOB;
    v_usuario VARCHAR2(50);
BEGIN
    -- Determinar operação
    IF INSERTING THEN
        v_operacao := 'INSERT';
    ELSIF UPDATING THEN
        v_operacao := 'UPDATE';
    ELSIF DELETING THEN
        v_operacao := 'DELETE';
    END IF;
    
    -- Obter usuário do banco (ou de contexto da aplicação se disponível)
    SELECT USER INTO v_usuario FROM DUAL;
    
    -- Formatar dados antigos (para UPDATE e DELETE)
    IF UPDATING OR DELETING THEN
        v_dados_antigos := 
            'ID: ' || :OLD.id || ', ' ||
            'NOME: ' || :OLD.nome || ', ' ||
            'KCAL: ' || :OLD.kcal || ', ' ||
            'PROTEINA: ' || :OLD.proteina || ', ' ||
            'CARBOIDRATOS: ' || :OLD.carboidratos || ', ' ||
            'GORDURA: ' || :OLD.gordura;
    END IF;
    
    -- Formatar novos dados (para INSERT e UPDATE)
    IF INSERTING OR UPDATING THEN
        v_dados_novos := 
            'ID: ' || :NEW.id || ', ' ||
            'NOME: ' || :NEW.nome || ', ' ||
            'KCAL: ' || :NEW.kcal || ', ' ||
            'PROTEINA: ' || :NEW.proteina || ', ' ||
            'CARBOIDRATOS: ' || :NEW.carboidratos || ', ' ||
            'GORDURA: ' || :NEW.gordura;
    END IF;
    
    -- Inserir registro de log
    INSERT INTO log_auditoria (tabela, operacao, usuario, dados_antigos, dados_novos)
    VALUES ('ALIMENTOS', v_operacao, v_usuario, v_dados_antigos, v_dados_novos);
END;
/
"@

    New-Item -ItemType Directory -Path "data\scripts" -Force | Out-Null
    $plsqlScriptContent | Out-File -FilePath $plsqlScriptPath
    Write-Host "[OK] Script PL/SQL criado: $plsqlScriptPath" -ForegroundColor Green
}

# Criar script para criação e população do esquema Oracle
$createSchemaPath = "data\scripts\create_oracle_schema.py"
if (-not (Test-Path $createSchemaPath)) {
    $createSchemaContent = @"
"""
Script para criar e popular o esquema Oracle para a aplicação NutriApp
"""
import os
import json
import cx_Oracle
import csv
from pathlib import Path

# Ler configurações
config_path = Path(__file__).parent.parent.parent.parent / "config" / "oracle_config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

# Construir string de conexão
dsn = cx_Oracle.makedsn(
    host=config['ORACLE_HOST'],
    port=config['ORACLE_PORT'],
    service_name=config['ORACLE_SERVICE']
)

# Estabelecer conexão
def get_connection():
    connection = cx_Oracle.connect(
        user=config['ORACLE_USER'],
        password=config['ORACLE_PASSWORD'],
        dsn=dsn
    )
    return connection

def criar_tabelas(connection):
    """Cria as tabelas no esquema Oracle"""
    cursor = connection.cursor()
    
    # Verificar se as tabelas já existem
    cursor.execute("""
    SELECT COUNT(*) FROM user_tables WHERE table_name = 'CATEGORIAS'
    """)
    tabelas_existem = cursor.fetchone()[0] > 0
    
    if tabelas_existem:
        print("Tabelas já existem, pulando criação.")
        return
    
    print("Criando tabelas...")
    
    # Script de criação das tabelas
    sql_criacao = """
    -- Tabela de categorias
    CREATE TABLE categorias (
        id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        nome VARCHAR2(100) NOT NULL
    );

    -- Tabela de alimentos
    CREATE TABLE alimentos (
        id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        codigo VARCHAR2(20) UNIQUE,
        nome VARCHAR2(200) NOT NULL,
        categoria_id NUMBER,
        kcal NUMBER(8,2),
        carboidratos NUMBER(8,2),
        proteina NUMBER(8,2),
        gordura NUMBER(8,2),
        fibras NUMBER(8,2),
        calcio NUMBER(8,2),
        ferro NUMBER(8,2),
        CONSTRAINT fk_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    );

    -- Índices para melhorar performance
    CREATE INDEX idx_alimentos_nome ON alimentos(UPPER(nome));
    CREATE INDEX idx_alimentos_codigo ON alimentos(codigo);
    """
    
    # Executar cada comando separadamente
    for comando in sql_criacao.split(";"):
        if comando.strip():
            try:
                cursor.execute(comando)
                print(f"Executado: {comando[:50]}...")
            except cx_Oracle.Error as e:
                print(f"Erro ao executar: {comando[:50]}...")
                print(f"Erro: {str(e)}")
    
    connection.commit()
    print("Tabelas criadas com sucesso!")

def importar_dados_exemplo(connection):
    """Importa dados de exemplo para o banco Oracle"""
    cursor = connection.cursor()
    
    # Verificar se já existem dados
    cursor.execute("SELECT COUNT(*) FROM categorias")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print("Já existem dados nas tabelas, pulando importação.")
        return
    
    print("Importando dados de exemplo...")
    
    # Inserir categorias
    categorias = [
        "Cereais e derivados",
        "Verduras, hortaliças e derivados",
        "Frutas e derivados",
        "Gorduras e óleos",
        "Pescados e frutos do mar",
        "Carnes e derivados",
        "Leite e derivados",
        "Bebidas",
        "Ovos e derivados",
        "Produtos açucarados",
        "Miscelâneas",
        "Outros alimentos industrializados"
    ]
    
    for categoria in categorias:
        cursor.execute(
            "INSERT INTO categorias (nome) VALUES (:nome)",
            nome=categoria
        )
    
    # Inserir alguns alimentos de exemplo
    alimentos = [
        ("A001", "Arroz, tipo 1, cozido", 1, 128.0, 28.1, 2.5, 0.2, 1.6, 4.0, 0.1),
        ("A002", "Feijão, carioca, cozido", 1, 76.0, 13.6, 4.8, 0.5, 8.5, 27.0, 1.3),
        ("A003", "Maçã, com casca", 3, 52.0, 13.8, 0.3, 0.2, 2.4, 3.0, 0.1),
        ("A004", "Banana, nanica", 3, 92.0, 23.8, 1.1, 0.1, 2.0, 5.0, 0.3),
        ("A005", "Leite, de vaca, integral", 7, 61.0, 4.5, 3.2, 3.3, 0.0, 123.0, 0.1),
        ("A006", "Frango, peito, sem pele, cozido", 6, 163.0, 0.0, 31.0, 3.6, 0.0, 11.0, 0.9),
        ("A007", "Alface, crespa, crua", 2, 11.0, 1.7, 1.3, 0.2, 1.8, 38.0, 0.4),
        ("A008", "Tomate, com semente, cru", 2, 15.0, 3.1, 0.9, 0.2, 1.2, 7.0, 0.5),
        ("A009", "Ovo, de galinha, inteiro, cozido", 9, 146.0, 0.6, 13.3, 9.5, 0.0, 50.0, 1.7),
        ("A010", "Azeite, de oliva, extra virgem", 4, 884.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.5)
    ]
    
    for alimento in alimentos:
        cursor.execute("""
        INSERT INTO alimentos 
        (codigo, nome, categoria_id, kcal, carboidratos, proteina, gordura, fibras, calcio, ferro)
        VALUES 
        (:codigo, :nome, :categoria_id, :kcal, :carboidratos, :proteina, :gordura, :fibras, :calcio, :ferro)
        """, {
            'codigo': alimento[0],
            'nome': alimento[1],
            'categoria_id': alimento[2],
            'kcal': alimento[3],
            'carboidratos': alimento[4],
            'proteina': alimento[5],
            'gordura': alimento[6],
            'fibras': alimento[7],
            'calcio': alimento[8],
            'ferro': alimento[9]
        })
    
    connection.commit()
    print("Dados de exemplo importados com sucesso!")

def executar_scripts_plsql(connection):
    """Executa os scripts PL/SQL"""
    plsql_path = Path(__file__).parent / "create_plsql_procedures.sql"
    
    if not plsql_path.exists():
        print(f"Arquivo de procedimentos PL/SQL não encontrado: {plsql_path}")
        return
    
    print("Executando scripts PL/SQL...")
    
    with open(plsql_path, 'r') as f:
        script = f.read()
    
    # Dividir o script por "/" para tratar cada bloco PL/SQL separadamente
    blocks = script.split('/')
    
    cursor = connection.cursor()
    
    for block in blocks:
        if block.strip():
            try:
                cursor.execute(block)
                print(f"Bloco PL/SQL executado com sucesso!")
            except cx_Oracle.Error as e:
                print(f"Erro ao executar bloco PL/SQL: {str(e)}")
                print(f"Bloco:\n{block[:200]}...")
    
    connection.commit()
    print("Scripts PL/SQL executados!")

if __name__ == "__main__":
    try:
        print("=== Criando esquema Oracle para NutriApp ===")
        connection = get_connection()
        
        # Criar estrutura de tabelas
        criar_tabelas(connection)
        
        # Importar dados de exemplo
        importar_dados_exemplo(connection)
        
        # Executar scripts PL/SQL
        executar_scripts_plsql(connection)
        
        print("Esquema Oracle criado e configurado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao configurar esquema Oracle: {str(e)}")
    
    finally:
        if 'connection' in locals():
            connection.close()
"@

    New-Item -ItemType Directory -Path "data\scripts" -Force | Out-Null
    $createSchemaContent | Out-File -FilePath $createSchemaPath
    Write-Host "[OK] Script de criação de esquema Oracle criado: $createSchemaPath" -ForegroundColor Green
}

# Criar script para testar estrutura com suporte Oracle
$testOraclePath = "testar_estrutura_oracle.py"
if (-not (Test-Path $testOraclePath)) {
    $testOracleContent = @"
# Script para testar a estrutura da aplicação com suporte Oracle

def testar_estrutura_oracle():
    """Verifica se os arquivos e diretórios necessários para Oracle existem"""
    import os
    from pathlib import Path
    import sys
    
    # Diretório atual
    current_dir = Path().absolute()
    print(f"Diretório atual: {current_dir}")
    
    # Verificar estrutura
    estrutura_ok = True
    
    # Verificar arquivo de configuração Oracle
    config_path = Path("config/oracle_config.json")
    if config_path.exists():
        print("[OK] Arquivo de configuração Oracle encontrado")
    else:
        print("[ERRO] Arquivo de configuração Oracle não encontrado")
        estrutura_ok = False
    
    # Verificar dependências Python para Oracle
    try:
        import cx_Oracle
        print("[OK] Biblioteca cx_Oracle instalada")
    except ImportError:
        print("[ERRO] Biblioteca cx_Oracle não está instalada")
        estrutura_ok = False
    
    # Verificar modelos adaptados para Oracle
    oracle_models = Path("backend/app/models/oracle_models.py")
    if oracle_models.exists():
        print("[OK] Modelos Oracle encontrados")
    else:
        print("[ERRO] Modelos Oracle não encontrados")
        estrutura_ok = False
    
    # Verificar script de conexão Oracle
    oracle_db = Path("backend/app/models/oracle_database.py")
    if oracle_db.exists():
        print("[OK] Script de conexão Oracle encontrado")
    else:
        print("[ERRO] Script de conexão Oracle não encontrado")
        estrutura_ok = False
    
    # Verificar scripts PL/SQL
    plsql_script = Path("backend/data/scripts/create_plsql_procedures.sql")
    if plsql_script.exists():
        print("[OK] Scripts PL/SQL encontrados")
    else:
        print("[ERRO] Scripts PL/SQL não encontrados")
        estrutura_ok = False
    
    # Verificar script de criação de esquema
    schema_script = Path("backend/data/scripts/create_oracle_schema.py")
    if schema_script.exists():
        print("[OK] Script de criação de esquema Oracle encontrado")
    else:
        print("[ERRO] Script de criação de esquema Oracle não encontrado")
        estrutura_ok = False
    
    # Verificar Oracle client
    oracle_home = os.environ.get('ORACLE_HOME')
    if oracle_home:
        print(f"[OK] Oracle client configurado em: {oracle_home}")
    else:
        print("[AVISO] Variável ORACLE_HOME não definida")
    
    # Resultado final
    print("\n=== Resultado da Verificação Oracle ===")
    if estrutura_ok:
        print("[OK] Estrutura básica para Oracle está completa!")
    else:
        print("[AVISO] Há problemas na estrutura para Oracle.")
        print("Verifique os erros acima e corrija-os antes de continuar.")
        print("Execute o script 'configurar-oracle.ps1' para configurar o ambiente Oracle.")
    
    return estrutura_ok

if __name__ == "__main__":
    print("=== Verificando Estrutura para Oracle ===\n")
    testar_estrutura_oracle()
"@

    $testOracleContent | Out-File -FilePath $testOraclePath
    Write-Host "[OK] Script de teste de estrutura Oracle criado: $testOraclePath" -ForegroundColor Green
}

# Criar script para iniciar a aplicação com Oracle
$iniciarOraclePath = "iniciar-aplicacao-oracle.ps1"
if (-not (Test-Path $iniciarOraclePath)) {
    $iniciarOracleContent = @"
# Script para iniciar a aplicação NutriApp com Oracle Database

# Verificar estrutura Oracle
Write-Host "Verificando estrutura Oracle..." -ForegroundColor Cyan
python testar_estrutura_oracle.py

if (`$LASTEXITCODE -ne 0) {
    Write-Host "Problemas encontrados na estrutura Oracle. Executando configuração..." -ForegroundColor Yellow
    .\configurar-oracle.ps1
}

# Ativar ambiente virtual e instalar dependências do backend
cd backend
if (-not (Test-Path .\venv)) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host "Instalando dependências do backend incluindo Oracle..." -ForegroundColor Yellow
pip install cx_Oracle sqlalchemy fastapi uvicorn pydantic

# Inicializar banco de dados Oracle e inserir dados de exemplo
Write-Host "Inicializando banco de dados Oracle com dados de exemplo..." -ForegroundColor Yellow
python data\scripts\create_oracle_schema.py

# Definir variável de ambiente para usar Oracle
`$env:USE_ORACLE_DB = "true"

# Iniciar servidor backend
Write-Host "Iniciando servidor backend com suporte Oracle..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $pwd; .\venv\Scripts\Activate.ps1; `$env:USE_ORACLE_DB='true'; uvicorn app.main:app --reload"

# Instalar dependências do frontend e iniciar servidor
cd ..\frontend
Write-Host "Instalando dependências do frontend..." -ForegroundColor Yellow
npm install

Write-Host "Iniciando servidor frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $pwd; npm run dev"

Write-Host "Aplicação iniciada com suporte Oracle!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green

"@

    $iniciarOracleContent | Out-File -FilePath $iniciarOraclePath
    Write-Host "[OK] Script de inicialização Oracle criado: $iniciarOraclePath" -ForegroundColor Green
}

# Verificar dependências no arquivo requirements.txt
$requirementsPath = "backend\requirements.txt"
if (Test-Path $requirementsPath) {
    $requirementsContent = Get-Content $requirementsPath -Raw
    
    if (-not ($requirementsContent -match "cx-Oracle")) {
        Write-Host "Adicionando dependências Oracle ao requirements.txt..." -ForegroundColor Yellow
        $requirementsContent += "`ncx-Oracle>=8.3.0`nsqlalchemy-oracle>=1.1.0"
        $requirementsContent | Out-File -FilePath $requirementsPath
        Write-Host "[OK] Dependências Oracle adicionadas ao requirements.txt" -ForegroundColor Green
    } else {
        Write-Host "[OK] Dependências Oracle já constam no requirements.txt" -ForegroundColor Green
    }
}

Write-Host "`n=== Configuração Oracle Concluída! ===" -ForegroundColor Cyan
Write-Host "Para iniciar a aplicação com Oracle, execute:" -ForegroundColor Green
Write-Host ".\iniciar-aplicacao-oracle.ps1" -ForegroundColor Green
