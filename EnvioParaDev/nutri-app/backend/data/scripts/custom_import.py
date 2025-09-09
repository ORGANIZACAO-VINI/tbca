"""
Script para importar dados nutricionais personalizados em formato JSON para um banco de dados SQLite
Este script permite a importação de dados no formato da TBCA (Tabela Brasileira de Composição de Alimentos)
"""

import os
import json
import sqlite3
import pandas as pd
from pathlib import Path

# Configurações - ajuste conforme necessário
DATA_DIR = Path("../../dados")  # Ajuste para o diretório onde seus arquivos JSON estão
OUTPUT_DB = Path("./tbca.db")
JSON_FILE = None  # Você fornecerá o nome do arquivo durante a execução

def criar_estrutura_db():
    """Cria a estrutura inicial do banco de dados"""
    # Garantir que o diretório existe
    OUTPUT_DB.parent.mkdir(parents=True, exist_ok=True)
    
    # Conectar ao banco de dados (será criado se não existir)
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    # Limpar tabelas existentes (opcional)
    cursor.execute('DROP TABLE IF EXISTS porcoes')
    cursor.execute('DROP TABLE IF EXISTS nutrientes')
    cursor.execute('DROP TABLE IF EXISTS alimentos')
    cursor.execute('DROP TABLE IF EXISTS grupos')
    
    # Criar tabela de grupos de alimentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS grupos (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL UNIQUE
    )
    ''')
    
    # Criar tabela de alimentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alimentos (
        id INTEGER PRIMARY KEY,
        codigo TEXT UNIQUE,
        nome TEXT NOT NULL,
        nome_cientifico TEXT,
        grupo_id INTEGER,
        marca TEXT,
        FOREIGN KEY (grupo_id) REFERENCES grupos(id)
    )
    ''')
    
    # Criar tabela de nutrientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nutrientes (
        id INTEGER PRIMARY KEY,
        alimento_id INTEGER,
        nome TEXT NOT NULL,
        unidade TEXT,
        valor_por_100g REAL,
        FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
    )
    ''')
    
    # Criar tabela de porções
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS porcoes (
        id INTEGER PRIMARY KEY,
        nutriente_id INTEGER,
        descricao TEXT NOT NULL,
        quantidade TEXT,
        valor REAL,
        FOREIGN KEY (nutriente_id) REFERENCES nutrientes(id)
    )
    ''')
    
    # Criar índices para pesquisa eficiente
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alimentos_nome ON alimentos(nome)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alimentos_codigo ON alimentos(codigo)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nutrientes_nome ON nutrientes(nome)')
    
    conn.commit()
    conn.close()
    
    print(f"Estrutura do banco de dados criada em {OUTPUT_DB}")

def importar_json_para_sqlite(arquivo_json):
    """
    Importa dados do JSON para o banco SQLite
    
    Parâmetros:
    - arquivo_json: caminho para o arquivo JSON
    """
    arquivo_path = Path(arquivo_json)
    
    # Verificar se o arquivo JSON existe
    if not arquivo_path.exists():
        print(f"Arquivo JSON não encontrado: {arquivo_path}")
        return False
    
    # Ler dados do JSON
    print(f"Lendo dados de {arquivo_path}...")
    with open(arquivo_path, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    print(f"Encontrados {len(dados)} alimentos no arquivo JSON")
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    # Dicionário para mapear grupos
    grupos = {}
    
    # Contadores para estatísticas
    count_alimentos = 0
    count_nutrientes = 0
    count_porcoes = 0
    
    # Processar cada alimento
    for alimento in dados:
        count_alimentos += 1
        if count_alimentos % 100 == 0:
            print(f"Processando alimento {count_alimentos}/{len(dados)}")
        
        # Obter ou criar grupo
        grupo_nome = alimento.get('grupo', 'Não categorizado')
        if grupo_nome not in grupos:
            cursor.execute("INSERT INTO grupos (nome) VALUES (?)", (grupo_nome,))
            grupo_id = cursor.lastrowid
            grupos[grupo_nome] = grupo_id
        else:
            grupo_id = grupos[grupo_nome]
        
        # Inserir alimento
        cursor.execute("""
            INSERT INTO alimentos 
            (codigo, nome, nome_cientifico, grupo_id, marca) 
            VALUES (?, ?, ?, ?, ?)
        """, (
            alimento.get('codigo', ''),
            alimento.get('nome', 'Sem nome'),
            alimento.get('nome_cientifico', ''),
            grupo_id,
            alimento.get('marca', '')
        ))
        
        alimento_id = cursor.lastrowid
        
        # Processar nutrientes
        for nutriente in alimento.get('nutrientes', []):
            count_nutrientes += 1
            
            # Converter valor para número
            valor_str = nutriente.get('valor_por_100g', '0')
            try:
                valor = float(valor_str.replace(',', '.'))
            except (ValueError, AttributeError):
                valor = 0
            
            # Inserir nutriente
            cursor.execute("""
                INSERT INTO nutrientes 
                (alimento_id, nome, unidade, valor_por_100g) 
                VALUES (?, ?, ?, ?)
            """, (
                alimento_id,
                nutriente.get('nome', ''),
                nutriente.get('unidade', ''),
                valor
            ))
            
            nutriente_id = cursor.lastrowid
            
            # Processar porções
            for porcao in nutriente.get('porcoes', []):
                count_porcoes += 1
                
                # Converter valor para número
                valor_porcao_str = porcao.get('valor', '0')
                try:
                    valor_porcao = float(valor_porcao_str.replace(',', '.'))
                except (ValueError, AttributeError):
                    valor_porcao = 0
                
                # Inserir porção
                cursor.execute("""
                    INSERT INTO porcoes 
                    (nutriente_id, descricao, quantidade, valor) 
                    VALUES (?, ?, ?, ?)
                """, (
                    nutriente_id,
                    porcao.get('descricao', ''),
                    porcao.get('quantidade', ''),
                    valor_porcao
                ))
        
        # Commit a cada 50 alimentos para evitar perda de dados
        if count_alimentos % 50 == 0:
            conn.commit()
    
    # Commit final
    conn.commit()
    
    print(f"Importação concluída! Estatísticas:")
    print(f"- Alimentos: {count_alimentos}")
    print(f"- Nutrientes: {count_nutrientes}")
    print(f"- Porções: {count_porcoes}")
    print(f"- Grupos: {len(grupos)}")
    
    # Fechar conexão
    conn.close()
    
    return True

def main():
    """Função principal"""
    print("Iniciando importação de dados nutricionais em formato JSON para SQLite...")
    
    # Criar estrutura do banco de dados
    criar_estrutura_db()
    
    # Solicitar arquivo JSON
    arquivo_json = input("Digite o caminho completo para o arquivo JSON a ser importado: ")
    
    # Importar dados
    sucesso = importar_json_para_sqlite(arquivo_json)
    
    if sucesso:
        print("Processo concluído com sucesso!")
        
        # Estatísticas básicas
        conn = sqlite3.connect(OUTPUT_DB)
        cursor = conn.cursor()
        
        # Contar número de alimentos
        cursor.execute("SELECT COUNT(*) FROM alimentos")
        total_alimentos = cursor.fetchone()[0]
        
        # Contar número de nutrientes
        cursor.execute("SELECT COUNT(*) FROM nutrientes")
        total_nutrientes = cursor.fetchone()[0]
        
        # Contar nutrientes por alimento
        cursor.execute("""
            SELECT AVG(num_nutrientes) FROM (
                SELECT alimento_id, COUNT(*) as num_nutrientes 
                FROM nutrientes 
                GROUP BY alimento_id
            )
        """)
        media_nutrientes = cursor.fetchone()[0]
        
        # Contar por grupo
        cursor.execute("""
            SELECT g.nome, COUNT(a.id) 
            FROM alimentos a 
            JOIN grupos g ON a.grupo_id = g.id 
            GROUP BY g.nome
            ORDER BY COUNT(a.id) DESC
        """)
        grupos_count = cursor.fetchall()
        
        print(f"\nTotal de alimentos importados: {total_alimentos}")
        print(f"Total de nutrientes: {total_nutrientes}")
        print(f"Média de nutrientes por alimento: {media_nutrientes:.2f}")
        print("\nDistribuição por grupos:")
        for grupo_nome, count in grupos_count:
            print(f"  - {grupo_nome}: {count}")
        
        conn.close()
    else:
        print("Ocorreram erros durante a importação.")

if __name__ == "__main__":
    main()
