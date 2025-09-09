#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar dados do banco SQLite
Versão 2.0: Suporte para composição avançada
"""

import sqlite3
import os
import pandas as pd
from collections import defaultdict

def check_database():
    """Verifica dados do banco SQLite com detalhes avançados"""
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
        
        print("\n" + "=" * 60)
        print("🔍 ANÁLISE COMPLETA DO BANCO DE DADOS")
        print("=" * 60)
        print(f"\nBanco: {db_path}")
        print("\nTabelas encontradas:")
        
        # Resumo de tabelas
        print("\n" + "-" * 40)
        print("📋 RESUMO DE TABELAS")
        print("-" * 40)
        
        for table in tables:
            table_name = table[0]
            
            # Contar registros
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   • {table_name}: {count} registros")
            except Exception as e:
                print(f"   • {table_name}: Erro: {e}")
        
        # Detalhes de cada tabela
        print("\n" + "=" * 60)
        print("📊 DETALHES DAS TABELAS")
        print("=" * 60)
        
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
            
            # Exemplos para tabelas específicas
            if table_name == 'alimentos' and count > 0:
                print("\n   📝 Exemplos de Alimentos:")
                cursor.execute("""
                    SELECT id, codigo, nome, grupo_id 
                    FROM alimentos 
                    ORDER BY id
                    LIMIT 5
                """)
                for row in cursor.fetchall():
                    print(f"     • ID: {row[0]}, Código: {row[1]}, Nome: {row[2]}")
                    
            elif table_name == 'nutrientes' and count > 0:
                print("\n   📝 Exemplos de Nutrientes:")
                cursor.execute("""
                    SELECT n.alimento_id, a.nome, n.nome, n.unidade, n.valor_por_100g
                    FROM nutrientes n
                    JOIN alimentos a ON n.alimento_id = a.id
                    LIMIT 10
                """)
                for row in cursor.fetchall():
                    print(f"     • Alimento: {row[1]}, {row[2]}: {row[4]} {row[3]}")
                    
            elif table_name == 'alimentos_composicao' and count > 0:
                print("\n   📝 Exemplos de Composição Detalhada:")
                cursor.execute("""
                    SELECT ac.alimento_id, a.nome, ac.componente, ac.unidade, 
                           ac.valor_por_100g, ac.porcao_nome, ac.porcao_valor
                    FROM alimentos_composicao ac
                    JOIN alimentos a ON ac.alimento_id = a.id
                    LIMIT 5
                """)
                for row in cursor.fetchall():
                    if row[5]:  # tem porção
                        print(f"     • {row[1]}, {row[2]}: {row[4]} {row[3]}/100g, {row[6]} {row[3]} em {row[5]}")
                    else:
                        print(f"     • {row[1]}, {row[2]}: {row[4]} {row[3]}/100g")

        # Estatísticas avançadas
        print("\n" + "=" * 60)
        print("📈 ESTATÍSTICAS AVANÇADAS")
        print("=" * 60)
        
        # Contar por grupo
        try:
            print("\n📊 Alimentos por Grupo:")
            cursor.execute("""
                SELECT g.nome, COUNT(a.id) as total
                FROM alimentos a
                JOIN grupos g ON a.grupo_id = g.id
                GROUP BY g.nome
                ORDER BY total DESC
            """)
            for row in cursor.fetchall():
                print(f"   • {row[0]}: {row[1]} alimentos")
        except Exception as e:
            print(f"   Erro ao obter grupos: {e}")
            
        # Top nutrientes
        try:
            print("\n📊 Alimentos com mais calorias (por 100g):")
            cursor.execute("""
                SELECT a.nome, n.valor_por_100g
                FROM nutrientes n
                JOIN alimentos a ON n.alimento_id = a.id
                WHERE n.nome = 'Energia'
                ORDER BY n.valor_por_100g DESC
                LIMIT 5
            """)
            for row in cursor.fetchall():
                print(f"   • {row[0]}: {row[1]} kcal")
        except Exception as e:
            print(f"   Erro ao obter energia: {e}")
            
        # Nutrientes médios
        try:
            print("\n📊 Valores médios de nutrientes (por 100g):")
            cursor.execute("""
                SELECT n.nome, n.unidade, AVG(n.valor_por_100g) as media
                FROM nutrientes n
                GROUP BY n.nome, n.unidade
                ORDER BY n.nome
            """)
            for row in cursor.fetchall():
                print(f"   • {row[0]}: {row[2]:.2f} {row[1]}")
        except Exception as e:
            print(f"   Erro ao calcular médias: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao acessar banco: {e}")

if __name__ == "__main__":
    print("🔍 VERIFICAÇÃO DE BANCO DE DADOS")
    print("-" * 40)
    check_database()
    print("\n✅ Verificação concluída!")
