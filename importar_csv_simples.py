#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script SIMPLES para importar dados CSV para SQLite
"""

import sqlite3
import csv
import os

def importar_csv_para_sqlite():
    """Importa dados do CSV para SQLite de forma simples"""
    
    # Caminhos
    csv_path = "dados/teste_tbca.csv"
    db_path = "nutri-app/backend/tbca.db"
    
    print("🍎 IMPORTADOR DE DADOS TBCA")
    print("=" * 40)
    
    # Verificações
    if not os.path.exists(csv_path):
        print(f"❌ CSV não encontrado: {csv_path}")
        return False
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return False
    
    try:
        # Conectar ao banco
        print("🔗 Conectando ao banco SQLite...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Limpar dados existentes
        print("🧹 Limpando dados existentes...")
        cursor.execute("DELETE FROM nutrientes")
        cursor.execute("DELETE FROM alimentos")
        cursor.execute("DELETE FROM grupos")
        cursor.execute("DELETE FROM categorias")
        
        # Inserir categoria padrão
        cursor.execute("INSERT INTO categorias (nome) VALUES (?)", ("TBCA - Tabela Brasileira",))
        categoria_id = cursor.lastrowid
        
        # Inserir grupo padrão
        cursor.execute("INSERT INTO grupos (nome) VALUES (?)", ("Alimentos TBCA",))
        grupo_id = cursor.lastrowid
        
        # Ler e processar CSV
        print("📖 Lendo arquivo CSV...")
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            linhas = list(reader)
        
        print(f"📄 Arquivo CSV lido: {len(linhas)} linhas")
        
        # Processar dados
        alimentos_inseridos = 0
        nutrientes_inseridos = 0
        
        for i, linha in enumerate(linhas):
            # Pular cabeçalho
            if i == 0 or (len(linha) > 0 and linha[0].lower().startswith('codigo')):
                continue
            
            if len(linha) < 3:
                continue
                
            try:
                # Extrair dados da linha
                codigo = linha[1] if len(linha) > 1 else f"ALM_{i:04d}"
                nome = linha[2] if len(linha) > 2 else f"Alimento {i}"
                
                # Limpar nome (remover caracteres especiais)
                nome = nome.replace('Ã³', 'ó').replace('Ã¡', 'á').replace('Ã©', 'é')
                
                # Inserir alimento
                cursor.execute("""
                    INSERT INTO alimentos (codigo, nome, grupo_id)
                    VALUES (?, ?, ?)
                """, (codigo, nome, grupo_id))
                
                alimento_id = cursor.lastrowid
                alimentos_inseridos += 1
                
                # Inserir nutrientes (posições no CSV)
                nutrientes = [
                    (3, "Energia", "kcal"),
                    (4, "Carboidratos", "g"),
                    (5, "Proteína", "g"),
                    (6, "Gordura", "g"),
                    (7, "Fibras", "g"),
                    (8, "Cálcio", "mg"),
                    (9, "Ferro", "mg")
                ]
                
                for pos, nome_nutriente, unidade in nutrientes:
                    if len(linha) > pos and linha[pos]:
                        try:
                            # Converter valor (trocar vírgula por ponto)
                            valor_str = linha[pos].replace(',', '.')
                            valor = float(valor_str)
                            
                            cursor.execute("""
                                INSERT INTO nutrientes (alimento_id, nome, unidade, valor_por_100g)
                                VALUES (?, ?, ?, ?)
                            """, (alimento_id, nome_nutriente, unidade, valor))
                            
                            nutrientes_inseridos += 1
                            
                        except (ValueError, TypeError):
                            continue
                
                # Mostrar progresso
                if alimentos_inseridos % 10 == 0:
                    print(f"   Processados: {alimentos_inseridos} alimentos...")
                    
            except Exception as e:
                print(f"⚠️  Erro na linha {i}: {e}")
                continue
        
        # Salvar mudanças
        conn.commit()
        conn.close()
        
        print("\n✅ IMPORTAÇÃO CONCLUÍDA!")
        print(f"   📊 Alimentos importados: {alimentos_inseridos}")
        print(f"   🥄 Nutrientes importados: {nutrientes_inseridos}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def verificar_dados():
    """Verifica os dados importados"""
    
    db_path = "nutri-app/backend/tbca.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 VERIFICAÇÃO DOS DADOS:")
        print("-" * 30)
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM alimentos")
        total_alimentos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM nutrientes")
        total_nutrientes = cursor.fetchone()[0]
        
        print(f"📊 Alimentos: {total_alimentos}")
        print(f"🥄 Nutrientes: {total_nutrientes}")
        
        # Mostrar alguns exemplos
        if total_alimentos > 0:
            print("\n📋 EXEMPLOS DE ALIMENTOS:")
            cursor.execute("""
                SELECT a.codigo, a.nome, COUNT(n.id) as total_nutrientes
                FROM alimentos a
                LEFT JOIN nutrientes n ON a.id = n.alimento_id
                GROUP BY a.id
                LIMIT 5
            """)
            
            for codigo, nome, total_nut in cursor.fetchall():
                print(f"   {codigo}: {nome} ({total_nut} nutrientes)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")

if __name__ == "__main__":
    print("🍎 IMPORTADOR SIMPLES DE DADOS TBCA")
    print("=" * 50)
    
    resposta = input("Deseja importar os dados do CSV para SQLite? (s/n): ").strip().lower()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        sucesso = importar_csv_para_sqlite()
        
        if sucesso:
            verificar_dados()
            print("\n🎉 Dados prontos para migração para Oracle!")
            print("   Use o script 'migrate_sqlite_to_oracle.py' para migrar para Oracle.")
        else:
            print("\n❌ Falha na importação!")
    else:
        print("👋 Operação cancelada.")
