# Script para migrar dados de SQLite para Oracle Database
import os
import sqlite3
import cx_Oracle
import json
import argparse
from pathlib import Path
import datetime
import sys

def get_config():
    """Lê as configurações do Oracle do arquivo de configuração"""
    config_path = Path(__file__).parent.parent / "config" / "oracle_config.json"
    
    if not config_path.exists():
        print(f"Arquivo de configuração Oracle não encontrado: {config_path}")
        print("Execute primeiro o script configurar-oracle.ps1")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)

def get_oracle_connection(config):
    """Estabelece conexão com o banco Oracle"""
    dsn = cx_Oracle.makedsn(
        host=config['ORACLE_HOST'],
        port=config['ORACLE_PORT'],
        service_name=config['ORACLE_SERVICE']
    )
    
    connection = cx_Oracle.connect(
        user=config['ORACLE_USER'],
        password=config['ORACLE_PASSWORD'],
        dsn=dsn
    )
    
    return connection

def get_sqlite_connection(sqlite_path):
    """Estabelece conexão com o banco SQLite"""
    if not os.path.exists(sqlite_path):
        print(f"Banco de dados SQLite não encontrado: {sqlite_path}")
        sys.exit(1)
    
    return sqlite3.connect(sqlite_path)

def criar_estrutura_oracle(oracle_conn):
    """Cria a estrutura de tabelas no Oracle se não existir"""
    cursor = oracle_conn.cursor()
    
    # Verificar se as tabelas já existem
    cursor.execute("""
    SELECT COUNT(*) FROM user_tables WHERE table_name = 'CATEGORIAS'
    """)
    tabelas_existem = cursor.fetchone()[0] > 0
    
    if tabelas_existem:
        print("Estrutura Oracle já existe, pulando criação de tabelas.")
        return
    
    print("Criando estrutura de tabelas no Oracle...")
    
    # Comandos para criar tabelas
    commands = [
        """
        CREATE TABLE categorias (
            id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nome VARCHAR2(100) NOT NULL
        )
        """,
        """
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
        )
        """,
        """
        CREATE INDEX idx_alimentos_nome ON alimentos(UPPER(nome))
        """,
        """
        CREATE INDEX idx_alimentos_codigo ON alimentos(codigo)
        """
    ]
    
    for cmd in commands:
        try:
            cursor.execute(cmd)
            print(f"Executado: {cmd[:50]}...")
        except cx_Oracle.Error as e:
            print(f"Erro ao executar: {cmd[:50]}...")
            print(f"Erro: {str(e)}")
    
    oracle_conn.commit()
    print("Estrutura Oracle criada com sucesso!")

def migrar_categorias(sqlite_conn, oracle_conn):
    """Migra as categorias de SQLite para Oracle"""
    sqlite_cursor = sqlite_conn.cursor()
    oracle_cursor = oracle_conn.cursor()
    
    print("Migrando categorias...")
    
    # Verificar se já existem categorias no Oracle
    oracle_cursor.execute("SELECT COUNT(*) FROM categorias")
    if oracle_cursor.fetchone()[0] > 0:
        print("Já existem categorias no Oracle, pulando migração de categorias.")
        return
    
    # Obter categorias do SQLite
    sqlite_cursor.execute("SELECT id, nome FROM categorias")
    categorias = sqlite_cursor.fetchall()
    
    if not categorias:
        print("Nenhuma categoria encontrada no SQLite.")
        return
    
    # Inserir no Oracle com IDs correspondentes
    for cat_id, nome in categorias:
        try:
            # No Oracle usamos sequence para IDs, então não especificamos o ID
            oracle_cursor.execute(
                "INSERT INTO categorias (nome) VALUES (:nome)",
                nome=nome
            )
            print(f"Categoria migrada: {nome}")
        except cx_Oracle.Error as e:
            print(f"Erro ao migrar categoria '{nome}': {str(e)}")
    
    oracle_conn.commit()
    print(f"{len(categorias)} categorias migradas com sucesso!")

def migrar_alimentos(sqlite_conn, oracle_conn):
    """Migra os alimentos de SQLite para Oracle"""
    sqlite_cursor = sqlite_conn.cursor()
    oracle_cursor = oracle_conn.cursor()
    
    print("Migrando alimentos...")
    
    # Verificar se já existem alimentos no Oracle
    oracle_cursor.execute("SELECT COUNT(*) FROM alimentos")
    if oracle_cursor.fetchone()[0] > 0:
        print("Já existem alimentos no Oracle, pulando migração de alimentos.")
        return
    
    # Obter alimentos do SQLite
    sqlite_cursor.execute("""
    SELECT id, codigo, nome, categoria_id, kcal, carboidratos, proteina, 
           gordura, fibras, calcio, ferro
    FROM alimentos
    """)
    alimentos = sqlite_cursor.fetchall()
    
    if not alimentos:
        print("Nenhum alimento encontrado no SQLite.")
        return
    
    # Mapear IDs de categorias do SQLite para Oracle
    sqlite_cursor.execute("SELECT id, nome FROM categorias")
    cat_map = {row[0]: None for row in sqlite_cursor.fetchall()}
    
    oracle_cursor.execute("SELECT id, nome FROM categorias")
    for oracle_id, nome in oracle_cursor.fetchall():
        # Encontrar o ID SQLite correspondente
        for sqlite_id, sqlite_nome in [(id, nome) for id, nome in cat_map.items()]:
            if sqlite_nome == nome:
                cat_map[sqlite_id] = oracle_id
    
    # Inserir alimentos no Oracle
    for alimento in alimentos:
        alim_id, codigo, nome, cat_id = alimento[0:4]
        kcal, carbs, prot, gordura = alimento[4:8]
        fibras, calcio, ferro = alimento[8:11]
        
        # Obter categoria_id mapeada
        oracle_cat_id = cat_map.get(cat_id)
        
        try:
            oracle_cursor.execute("""
            INSERT INTO alimentos 
            (codigo, nome, categoria_id, kcal, carboidratos, proteina, gordura, fibras, calcio, ferro)
            VALUES 
            (:codigo, :nome, :categoria_id, :kcal, :carboidratos, :proteina, :gordura, :fibras, :calcio, :ferro)
            """, {
                'codigo': codigo,
                'nome': nome,
                'categoria_id': oracle_cat_id,
                'kcal': kcal,
                'carboidratos': carbs,
                'proteina': prot,
                'gordura': gordura,
                'fibras': fibras,
                'calcio': calcio,
                'ferro': ferro
            })
            print(f"Alimento migrado: {nome}")
        except cx_Oracle.Error as e:
            print(f"Erro ao migrar alimento '{nome}': {str(e)}")
    
    oracle_conn.commit()
    print(f"{len(alimentos)} alimentos migrados com sucesso!")

def main():
    parser = argparse.ArgumentParser(description='Migrar dados de SQLite para Oracle')
    parser.add_argument('--sqlite', help='Caminho para o banco SQLite', default='./backend/tbca.db')
    args = parser.parse_args()
    
    # Configurações
    config = get_config()
    sqlite_path = args.sqlite
    
    print(f"=== Migrando dados de {sqlite_path} para Oracle ===")
    
    try:
        # Conectar aos bancos
        oracle_conn = get_oracle_connection(config)
        sqlite_conn = get_sqlite_connection(sqlite_path)
        
        # Criar estrutura no Oracle
        criar_estrutura_oracle(oracle_conn)
        
        # Migrar dados
        migrar_categorias(sqlite_conn, oracle_conn)
        migrar_alimentos(sqlite_conn, oracle_conn)
        
        print("Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        
    finally:
        if 'oracle_conn' in locals():
            oracle_conn.close()
        if 'sqlite_conn' in locals():
            sqlite_conn.close()

if __name__ == "__main__":
    main()
