#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar dados do banco SQLite
"""

import sqlite3
import os

def check_database():
    db_path = "nutri-app/backend/tbca.db"
    
    if not os.path.exists(db_path):
        print(f"Banco de dados não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("=== ESTRUTURA DO BANCO DE DADOS ===")
        print(f"Banco: {db_path}")
        print("\nTabelas encontradas:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n📊 Tabela: {table_name}")
            
            # Contar registros
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   Registros: {count}")
            except Exception as e:
                print(f"   Erro ao contar: {e}")
            
            # Mostrar estrutura da tabela
            try:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                print("   Colunas:")
                for col in columns:
                    print(f"     - {col[1]} ({col[2]})")
            except Exception as e:
                print(f"   Erro ao obter estrutura: {e}")
        
        # Verificar alguns dados de exemplo se houver tabela alimentos
        if any(table[0] == 'alimentos' for table in tables):
            print("\n=== DADOS DE EXEMPLO ===")
            cursor.execute("SELECT * FROM alimentos LIMIT 5;")
            samples = cursor.fetchall()
            
            cursor.execute("PRAGMA table_info(alimentos);")
            columns = [col[1] for col in cursor.fetchall()]
            
            print("Primeiros 5 alimentos:")
            for sample in samples:
                print(f"  {dict(zip(columns, sample))}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao acessar banco: {e}")

if __name__ == "__main__":
    check_database()
