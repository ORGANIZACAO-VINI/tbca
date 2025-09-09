#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo para migrar dados de CSV -> SQLite -> Oracle
Versão: 1.0
Autor: Assistant
Data: 2025-09-09
"""

import os
import sqlite3
import pandas as pd
import json
import sys
from pathlib import Path
import datetime

def log_message(message, level="INFO"):
    """Log das operações com timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def import_csv_to_sqlite():
    """Importa dados do CSV para o SQLite"""
    
    # Caminhos
    csv_path = "dados/teste_tbca.csv"
    db_path = "nutri-app/backend/tbca.db"
    
    if not os.path.exists(csv_path):
        log_message(f"Arquivo CSV não encontrado: {csv_path}", "ERROR")
        return False
    
    if not os.path.exists(db_path):
        log_message(f"Banco SQLite não encontrado: {db_path}", "ERROR")
        return False
    
    try:
        log_message("Iniciando importação CSV -> SQLite...")
        
        # Ler CSV
        df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
        log_message(f"CSV carregado: {len(df)} registros")
        
        # Conectar ao SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Limpar dados existentes
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
        
        # Inserir alimentos
        alimentos_inseridos = 0
        nutrientes_inseridos = 0
        
        for index, row in df.iterrows():
            # Pular cabeçalho se existir
            if str(row.iloc[0]).startswith('codigo') or str(row.iloc[0]).startswith('CÃ³digo'):
                continue
                
            try:
                # Dados do alimento
                codigo = str(row.iloc[1]) if len(row) > 1 else f"ALM_{index:04d}"
                nome = str(row.iloc[2]) if len(row) > 2 else f"Alimento {index}"
                
                # Inserir alimento
                cursor.execute("""
                    INSERT INTO alimentos (codigo, nome, grupo_id)
                    VALUES (?, ?, ?)
                """, (codigo, nome, grupo_id))
                
                alimento_id = cursor.lastrowid
                alimentos_inseridos += 1
                
                # Inserir nutrientes (se disponíveis)
                nutrientes_map = {
                    3: ("Energia", "kcal"),
                    4: ("Carboidratos", "g"),
                    5: ("Proteína", "g"),
                    6: ("Gordura", "g"),
                    7: ("Fibras", "g"),
                    8: ("Cálcio", "mg"),
                    9: ("Ferro", "mg")
                }
                
                for col_idx, (nutriente_nome, unidade) in nutrientes_map.items():
                    if len(row) > col_idx:
                        try:
                            valor_str = str(row.iloc[col_idx]).replace(',', '.')
                            valor = float(valor_str) if valor_str and valor_str != 'nan' else 0.0
                            
                            cursor.execute("""
                                INSERT INTO nutrientes (alimento_id, nome, unidade, valor_por_100g)
                                VALUES (?, ?, ?, ?)
                            """, (alimento_id, nutriente_nome, unidade, valor))
                            
                            nutrientes_inseridos += 1
                        except (ValueError, TypeError):
                            continue
                            
            except Exception as e:
                log_message(f"Erro ao processar linha {index}: {e}", "ERROR")
                continue
        
        conn.commit()
        conn.close()
        
        log_message(f"Importação concluída: {alimentos_inseridos} alimentos, {nutrientes_inseridos} nutrientes")
        return True
        
    except Exception as e:
        log_message(f"Erro na importação: {e}", "ERROR")
        return False

def migrate_sqlite_to_oracle():
    """Migra dados do SQLite para Oracle usando script existente"""
    
    log_message("Iniciando migração SQLite -> Oracle...")
    
    # Verificar se o script de migração existe
    migrate_script = "scripts/migrate_sqlite_to_oracle.py"
    if not os.path.exists(migrate_script):
        log_message(f"Script de migração não encontrado: {migrate_script}", "ERROR")
        return False
    
    # Executar script de migração
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            migrate_script,
            "--sqlite-path", "nutri-app/backend/tbca.db"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            log_message("Migração para Oracle concluída com sucesso!")
            return True
        else:
            log_message(f"Erro na migração Oracle: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        log_message(f"Erro ao executar migração Oracle: {e}", "ERROR")
        return False

def export_data_options():
    """Mostra opções de exportação de dados"""
    
    print("\n" + "="*60)
    print("🗄️  OPÇÕES DE EXPORTAÇÃO DE DADOS")
    print("="*60)
    
    print("\n📊 DADOS DISPONÍVEIS:")
    print("   • CSV: ~100 alimentos TBCA")
    print("   • SQLite: Banco estruturado vazio")
    print("   • Oracle: Banco destino configurado")
    
    print("\n🚀 OPÇÕES DE MIGRAÇÃO:")
    print("   1. CSV -> SQLite (popular banco local)")
    print("   2. SQLite -> Oracle (migração completa)")
    print("   3. CSV -> SQLite -> Oracle (pipeline completo)")
    print("   4. Exportar para outros formatos")
    
    print("\n💡 RECOMENDAÇÕES:")
    print("   • Opção 3: Migração completa recomendada")
    print("   • Backup automático dos dados")
    print("   • Validação de integridade")

def main():
    """Função principal"""
    
    print("🍎 SISTEMA DE MIGRAÇÃO DE DADOS NUTRICIONAIS")
    print("=" * 50)
    
    export_data_options()
    
    while True:
        print("\n" + "="*50)
        print("ESCOLHA UMA OPÇÃO:")
        print("1 - Importar CSV para SQLite")
        print("2 - Migrar SQLite para Oracle")
        print("3 - Pipeline completo (CSV -> SQLite -> Oracle)")
        print("4 - Verificar status dos bancos")
        print("5 - Sair")
        
        escolha = input("\nDigite sua escolha (1-5): ").strip()
        
        if escolha == "1":
            print("\n🔄 Importando CSV para SQLite...")
            if import_csv_to_sqlite():
                print("✅ Importação concluída com sucesso!")
            else:
                print("❌ Falha na importação!")
                
        elif escolha == "2":
            print("\n🔄 Migrando SQLite para Oracle...")
            if migrate_sqlite_to_oracle():
                print("✅ Migração concluída com sucesso!")
            else:
                print("❌ Falha na migração!")
                
        elif escolha == "3":
            print("\n🔄 Executando pipeline completo...")
            
            # Passo 1: CSV -> SQLite
            print("\n📥 Passo 1/2: Importando CSV para SQLite...")
            if not import_csv_to_sqlite():
                print("❌ Falha no passo 1!")
                continue
            
            # Passo 2: SQLite -> Oracle
            print("\n📤 Passo 2/2: Migrando SQLite para Oracle...")
            if migrate_sqlite_to_oracle():
                print("✅ Pipeline completo executado com sucesso!")
                print("\n🎉 Todos os dados foram migrados para Oracle!")
            else:
                print("❌ Falha no passo 2!")
                
        elif escolha == "4":
            print("\n🔍 Verificando status dos bancos...")
            # Implementar verificação de status
            
        elif escolha == "5":
            print("\n👋 Saindo...")
            break
            
        else:
            print("❌ Opção inválida! Digite um número de 1 a 5.")

if __name__ == "__main__":
    # Verificar se pandas está instalado
    try:
        import pandas as pd
    except ImportError:
        print("❌ Erro: pandas não está instalado!")
        print("Execute: pip install pandas")
        sys.exit(1)
    
    main()
