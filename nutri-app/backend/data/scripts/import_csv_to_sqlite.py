"""
Script para importar dados da TBCA (CSV) para um banco de dados SQLite
Este script faz parte da Fase 1 da implementação do aplicativo web de nutrição
"""

import os
import sqlite3
import pandas as pd
from pathlib import Path

# Configurações
DATA_DIR = Path("./dados")
OUTPUT_DB = Path("./backend/data/tbca.db")
CSV_FILE = DATA_DIR / "tbca_backup_20250909_122104.csv"  # Usar o backup mais recente

def criar_estrutura_db():
    """Cria a estrutura inicial do banco de dados"""
    # Garantir que o diretório existe
    OUTPUT_DB.parent.mkdir(parents=True, exist_ok=True)
    
    # Conectar ao banco de dados (será criado se não existir)
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    # Criar tabela de categorias de alimentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL
    )
    ''')
    
    # Criar tabela de alimentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alimentos (
        id INTEGER PRIMARY KEY,
        codigo TEXT UNIQUE,
        nome TEXT NOT NULL,
        categoria_id INTEGER,
        kcal REAL,
        carboidratos REAL,
        proteina REAL,
        gordura REAL,
        fibras REAL,
        calcio REAL,
        ferro REAL,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    )
    ''')
    
    # Criar índices para pesquisa eficiente
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alimentos_nome ON alimentos(nome)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alimentos_codigo ON alimentos(codigo)')
    
    conn.commit()
    conn.close()
    
    print(f"Estrutura do banco de dados criada em {OUTPUT_DB}")

def categorizar_alimentos(df):
    """
    Categoriza alimentos com base em padrões de nomes
    Retorna um DataFrame com uma coluna 'categoria_id' adicional
    """
    # Exemplo simplificado de categorização
    categorias = {
        1: ['arroz', 'feijão', 'grão', 'cereal'],
        2: ['carne', 'frango', 'peixe', 'boi'],
        3: ['leite', 'queijo', 'iogurte', 'lácteo'],
        4: ['fruta', 'maçã', 'banana', 'laranja'],
        5: ['legume', 'verdura', 'vegetal'],
        6: ['pão', 'bolo', 'biscoito', 'padaria'],
        7: ['óleo', 'azeite', 'gordura'],
        8: ['açúcar', 'doce', 'sobremesa'],
        9: ['bebida', 'suco', 'refrigerante'],
    }
    
    # Inicializar coluna de categoria
    df['categoria_id'] = 0  # 0 = não categorizado
    
    # Atribuir categorias com base em palavras-chave no nome
    for cat_id, keywords in categorias.items():
        for keyword in keywords:
            mask = df['alimento_pt'].str.lower().str.contains(keyword, na=False)
            df.loc[mask, 'categoria_id'] = cat_id
    
    return df

def normalizar_dados(df):
    """Normaliza os dados para formato adequado ao banco de dados"""
    # Criar cópia para não modificar o original
    df_norm = df.copy()
    
    # Remover "Código:" do início e limpar espaços
    if 'codigo' in df_norm.columns:
        df_norm['codigo'] = df_norm['codigo'].str.replace('Código:', '').str.strip()
    
    # Converter vírgulas para pontos nos campos numéricos
    numeric_cols = ['kcal', 'carboidratos', 'proteina', 'gordura', 'fibras', 'calcio', 'ferro']
    for col in numeric_cols:
        if col in df_norm.columns:
            df_norm[col] = df_norm[col].astype(str).str.replace(',', '.').astype(float)
    
    return df_norm

def importar_csv_para_sqlite():
    """Importa dados do CSV para o banco SQLite"""
    # Verificar se o arquivo CSV existe
    if not CSV_FILE.exists():
        print(f"Arquivo CSV não encontrado: {CSV_FILE}")
        return False
    
    # Ler dados do CSV
    print(f"Lendo dados de {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE, sep=';')
    
    # Normalizar e categorizar dados
    print("Normalizando e categorizando dados...")
    df = normalizar_dados(df)
    df = categorizar_alimentos(df)
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(OUTPUT_DB)
    
    # Inserir categorias
    print("Inserindo categorias...")
    categorias = {
        0: 'Não categorizado',
        1: 'Cereais e Leguminosas',
        2: 'Carnes e Ovos',
        3: 'Leites e Derivados',
        4: 'Frutas',
        5: 'Legumes e Verduras',
        6: 'Pães e Farináceos',
        7: 'Óleos e Gorduras',
        8: 'Açúcares e Doces',
        9: 'Bebidas',
    }
    
    for cat_id, nome in categorias.items():
        conn.execute("INSERT OR IGNORE INTO categorias (id, nome) VALUES (?, ?)", 
                    (cat_id, nome))
    
    # Inserir alimentos
    print("Inserindo alimentos no banco de dados...")
    # Selecionar apenas as colunas relevantes
    df_to_insert = df[['codigo', 'alimento_pt', 'categoria_id', 'kcal', 
                       'carboidratos', 'proteina', 'gordura', 'fibras', 
                       'calcio', 'ferro']]
    
    # Renomear colunas para corresponder à tabela
    df_to_insert = df_to_insert.rename(columns={'alimento_pt': 'nome'})
    
    # Inserir no banco de dados
    df_to_insert.to_sql('alimentos', conn, if_exists='replace', index=False, 
                        index_label='id', method='multi')
    
    # Commit e fechar conexão
    conn.commit()
    conn.close()
    
    print(f"Importação concluída! Banco de dados em {OUTPUT_DB}")
    return True

def main():
    """Função principal"""
    print("Iniciando importação de dados da TBCA para SQLite...")
    
    # Criar estrutura do banco de dados
    criar_estrutura_db()
    
    # Importar dados
    sucesso = importar_csv_para_sqlite()
    
    if sucesso:
        print("Processo concluído com sucesso!")
        
        # Estatísticas básicas
        conn = sqlite3.connect(OUTPUT_DB)
        cursor = conn.cursor()
        
        # Contar número de alimentos
        cursor.execute("SELECT COUNT(*) FROM alimentos")
        total_alimentos = cursor.fetchone()[0]
        
        # Contar por categoria
        cursor.execute("""
            SELECT c.nome, COUNT(a.id) 
            FROM alimentos a 
            JOIN categorias c ON a.categoria_id = c.id 
            GROUP BY c.nome
            ORDER BY COUNT(a.id) DESC
        """)
        categorias_count = cursor.fetchall()
        
        print(f"\nTotal de alimentos importados: {total_alimentos}")
        print("\nDistribuição por categorias:")
        for cat_nome, count in categorias_count:
            print(f"  - {cat_nome}: {count}")
        
        conn.close()
    else:
        print("Ocorreram erros durante a importação.")

if __name__ == "__main__":
    main()
