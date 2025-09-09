#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para demonstração inicial com amostra de dados
"""

import os
import sys
import sqlite3
import datetime

def demonstracao_inicial():
    """Demonstração com amostra reduzida dos dados"""
    
    print("\n" + "=" * 60)
    print("🔍 DEMONSTRAÇÃO COM AMOSTRA DE DADOS")
    print("=" * 60)
    
    # Verificar se o arquivo de amostra existe
    amostra_path = "composicao_amostra.csv"
    if not os.path.exists(amostra_path):
        print(f"❌ Arquivo de amostra não encontrado: {amostra_path}")
        print("   Este script deve ser executado com o arquivo de amostra")
        print("   incluído no primeiro envio do projeto.")
        return False
    
    # Verificar tamanho do arquivo
    try:
        tamanho_kb = os.path.getsize(amostra_path) / 1024
        print(f"\n📄 Arquivo de amostra: {tamanho_kb:.1f}KB")
        print("   (Base completa terá aproximadamente 40-50MB)")
    except Exception as e:
        print(f"⚠️ Erro ao verificar tamanho: {e}")
    
    print("\n🔄 Analisando estrutura do arquivo de amostra...")
    
    # Contar linhas na amostra
    try:
        num_linhas = sum(1 for _ in open(amostra_path, "r", encoding="utf-8"))
        print(f"   Linhas na amostra: {num_linhas}")
        print("   (Base completa terá aproximadamente 230.000 linhas)")
    except Exception as e:
        print(f"⚠️ Erro ao contar linhas: {e}")
    
    # Verificar banco de dados
    db_path = "nutri-app/backend/tbca.db"
    if not os.path.exists(db_path):
        print(f"\n⚠️ Banco de dados não encontrado: {db_path}")
        print("   Você precisa configurar o ambiente primeiro.")
        return False
    
    # Mostrar estrutura do banco
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        
        print("\n📊 Estrutura do banco de dados:")
        for tabela in tabelas:
            print(f"   • {tabela[0]}")
        
        conn.close()
    except Exception as e:
        print(f"⚠️ Erro ao verificar banco: {e}")
    
    print("\n" + "-" * 60)
    print("🚀 PARA CONTINUAR APÓS RECEBER A BASE COMPLETA:")
    print("-" * 60)
    print("1. Coloque o arquivo 'composicao_todos_alimentos.csv' na raiz do projeto")
    print("2. Execute: python menu_tbca_completo.py")
    print("3. Selecione a opção 1 para importar")
    print("\nℹ️ O processo de importação completo pode levar 5-10 minutos")
    print("   dependendo do hardware disponível.")
    
    return True

def verificar_ambiente():
    """Verifica se o ambiente está configurado corretamente"""
    
    print("🔧 VERIFICAÇÃO DE AMBIENTE")
    print("-" * 40)
    
    # Verificar Python e dependências
    print("\n📦 Dependências Python:")
    dependencias = ["sqlite3", "pandas"]
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"   ✅ {dep}: Instalado")
        except ImportError:
            print(f"   ❌ {dep}: Não encontrado")
            print(f"      Execute: pip install {dep}")
    
    # Verificar estrutura de pastas
    print("\n📁 Estrutura de pastas:")
    pastas = ["nutri-app", "scripts", "dados"]
    for pasta in pastas:
        if os.path.exists(pasta) and os.path.isdir(pasta):
            print(f"   ✅ {pasta}/: Encontrada")
        else:
            print(f"   ❌ {pasta}/: Não encontrada")
    
    # Verificar scripts principais
    print("\n📄 Scripts principais:")
    scripts = ["menu_tbca_completo.py", "importar_tbca_completo.py", "check_database_avancado.py"]
    for script in scripts:
        if os.path.exists(script):
            print(f"   ✅ {script}: Encontrado")
        else:
            print(f"   ❌ {script}: Não encontrado")
    
    print("\n" + "=" * 60)
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 PROJETO NUTRI-APP - VERIFICAÇÃO INICIAL")
    print("=" * 60)
    print("\nData: " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    verificar_ambiente()
    demonstracao_inicial()
    
    print("\n✨ Para configurar o ambiente completo, aguarde o envio da base completa.")
    print("   Entre em contato em caso de dúvidas ou problemas na configuração.")
    print("=" * 60)
