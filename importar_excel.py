#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar dados de Excel (.xlsx) para SQLite
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

def importar_excel_para_sqlite():
    """Importa dados de Excel para SQLite"""
    
    print("📊 IMPORTADOR DE EXCEL PARA SQLITE")
    print("=" * 40)
    
    # Procurar arquivos Excel na pasta dados
    dados_path = Path("dados")
    excel_files = list(dados_path.glob("*.xlsx")) + list(dados_path.glob("*.xls"))
    
    if not excel_files:
        print("❌ Nenhum arquivo Excel encontrado na pasta 'dados/'")
        print("   Coloque seus arquivos .xlsx ou .xls na pasta 'dados/'")
        return False
    
    print("📁 Arquivos Excel encontrados:")
    for i, file in enumerate(excel_files, 1):
        print(f"   {i}. {file.name}")
    
    # Escolher arquivo
    while True:
        try:
            escolha = int(input(f"\nEscolha um arquivo (1-{len(excel_files)}): "))
            if 1 <= escolha <= len(excel_files):
                arquivo_excel = excel_files[escolha - 1]
                break
            else:
                print("❌ Número inválido!")
        except ValueError:
            print("❌ Digite um número válido!")
    
    try:
        # Ler Excel
        print(f"\n📖 Lendo arquivo: {arquivo_excel.name}")
        df = pd.read_excel(arquivo_excel)
        
        print(f"📄 Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")
        print(f"📋 Colunas encontradas: {list(df.columns)}")
        
        # Mapear colunas
        print("\n🔗 MAPEAMENTO DE COLUNAS")
        print("Informe qual coluna corresponde a cada campo:")
        
        mapeamento = {}
        campos_obrigatorios = ["nome", "kcal"]
        campos_opcionais = ["codigo", "proteina", "carboidratos", "gordura", "fibras", "calcio", "ferro"]
        
        # Campos obrigatórios
        for campo in campos_obrigatorios:
            while True:
                coluna = input(f"   {campo.capitalize()} (obrigatório): ").strip()
                if coluna in df.columns:
                    mapeamento[campo] = coluna
                    break
                else:
                    print(f"     ❌ Coluna '{coluna}' não encontrada!")
                    print(f"     Colunas disponíveis: {list(df.columns)}")
        
        # Campos opcionais
        for campo in campos_opcionais:
            coluna = input(f"   {campo.capitalize()} (opcional, Enter para pular): ").strip()
            if coluna and coluna in df.columns:
                mapeamento[campo] = coluna
        
        # Conectar ao banco
        db_path = "nutri-app/backend/tbca.db"
        if not os.path.exists(db_path):
            print(f"❌ Banco não encontrado: {db_path}")
            return False
        
        print("\n🔗 Conectando ao banco...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Limpar dados existentes
        resposta = input("🧹 Limpar dados existentes? (s/n): ").strip().lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            cursor.execute("DELETE FROM nutrientes")
            cursor.execute("DELETE FROM alimentos")
            cursor.execute("DELETE FROM grupos")
            cursor.execute("DELETE FROM categorias")
        
        # Inserir categoria padrão
        cursor.execute("INSERT INTO categorias (nome) VALUES (?)", ("Dados Importados",))
        categoria_id = cursor.lastrowid
        
        # Inserir grupo padrão
        cursor.execute("INSERT INTO grupos (nome) VALUES (?)", ("Excel Import",))
        grupo_id = cursor.lastrowid
        
        # Processar dados
        alimentos_inseridos = 0
        nutrientes_inseridos = 0
        
        for index, row in df.iterrows():
            try:
                # Dados obrigatórios
                nome = str(row[mapeamento['nome']])
                if pd.isna(nome) or nome == 'nan':
                    continue
                
                kcal = row[mapeamento['kcal']]
                if pd.isna(kcal):
                    kcal = 0
                
                # Código (opcional)
                codigo = str(row[mapeamento.get('codigo', '')]) if 'codigo' in mapeamento else f"IMP_{index:04d}"
                if codigo == 'nan':
                    codigo = f"IMP_{index:04d}"
                
                # Inserir alimento
                cursor.execute("""
                    INSERT INTO alimentos (codigo, nome, grupo_id)
                    VALUES (?, ?, ?)
                """, (codigo, nome, grupo_id))
                
                alimento_id = cursor.lastrowid
                alimentos_inseridos += 1
                
                # Inserir kcal como nutriente
                cursor.execute("""
                    INSERT INTO nutrientes (alimento_id, nome, unidade, valor_por_100g)
                    VALUES (?, ?, ?, ?)
                """, (alimento_id, "Energia", "kcal", float(kcal)))
                nutrientes_inseridos += 1
                
                # Inserir outros nutrientes
                nutrientes_map = {
                    'proteina': ('Proteína', 'g'),
                    'carboidratos': ('Carboidratos', 'g'),
                    'gordura': ('Gordura', 'g'),
                    'fibras': ('Fibras', 'g'),
                    'calcio': ('Cálcio', 'mg'),
                    'ferro': ('Ferro', 'mg')
                }
                
                for campo, (nome_nutriente, unidade) in nutrientes_map.items():
                    if campo in mapeamento:
                        valor = row[mapeamento[campo]]
                        if not pd.isna(valor):
                            try:
                                cursor.execute("""
                                    INSERT INTO nutrientes (alimento_id, nome, unidade, valor_por_100g)
                                    VALUES (?, ?, ?, ?)
                                """, (alimento_id, nome_nutriente, unidade, float(valor)))
                                nutrientes_inseridos += 1
                            except (ValueError, TypeError):
                                continue
                
                # Progresso
                if alimentos_inseridos % 50 == 0:
                    print(f"   Processados: {alimentos_inseridos} alimentos...")
                    
            except Exception as e:
                print(f"⚠️  Erro na linha {index}: {e}")
                continue
        
        # Salvar
        conn.commit()
        conn.close()
        
        print("\n✅ IMPORTAÇÃO CONCLUÍDA!")
        print(f"   📊 Alimentos importados: {alimentos_inseridos}")
        print(f"   🥄 Nutrientes importados: {nutrientes_inseridos}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

if __name__ == "__main__":
    try:
        import pandas as pd
    except ImportError:
        print("❌ Pandas não instalado!")
        print("Execute: pip install pandas openpyxl")
        exit(1)
    
    sucesso = importar_excel_para_sqlite()
    
    if sucesso:
        print("\n🎉 Dados prontos!")
        print("   Use 'python check_database.py' para verificar")
        print("   Use 'scripts/migrate_sqlite_to_oracle.py' para migrar para Oracle")
