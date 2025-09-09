#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu de Importação da Base TBCA Completa
"""

import os
import sys
import subprocess
from datetime import datetime

def mostrar_cabecalho():
    """Mostra cabeçalho do menu"""
    print("\n" + "=" * 70)
    print("🍎 SISTEMA DE IMPORTAÇÃO DA BASE TBCA COMPLETA")
    print("=" * 70)
    print("\nData: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
def mostrar_menu():
    """Mostra menu principal"""
    print("\n" + "-" * 50)
    print("📋 MENU PRINCIPAL")
    print("-" * 50)
    print("1. 📥 Importar Tabela Completa (CSV → SQLite)")
    print("2. 🔍 Verificar Dados Importados (Simples)")
    print("3. 📊 Verificar Dados Importados (Avançado)")
    print("4. 🗄️ Migrar Dados para Oracle")
    print("5. 🧹 Limpar Banco de Dados Atual")
    print("6. 📚 Informações sobre o Formato CSV")
    print("0. 🚪 Sair")
    print("-" * 50)

def mostrar_info_csv():
    """Mostra informações sobre o formato do CSV"""
    print("\n" + "=" * 70)
    print("📚 INFORMAÇÕES SOBRE O FORMATO CSV")
    print("=" * 70)
    
    print("\n🔸 ESTRUTURA DO ARQUIVO:")
    print("O arquivo 'composicao_todos_alimentos.csv' contém dados da Tabela")
    print("Brasileira de Composição de Alimentos (TBCA) com mais de 230.000 linhas.")
    
    print("\n🔸 FORMATO:")
    print("• Cada linha contém um componente/nutriente para um alimento específico")
    print("• Múltiplas linhas podem se referir ao mesmo alimento (diferentes nutrientes)")
    print("• Contém valores para porções além dos valores padrão por 100g")
    
    print("\n🔸 COLUNAS PRINCIPAIS:")
    print("• componente: Nome do nutriente/componente")
    print("• unidade: Unidade de medida (g, mg, kcal, etc.)")
    print("• Valor por 100g: Quantidade do nutriente por 100g")
    print("• codigo_alimento: Código único do alimento (ex: BRC0001C)")
    print("• nome_alimento: Nome do alimento")
    print("• Demais colunas: Valores para diferentes medidas caseiras")
    
    print("\n🔸 PROCESSO DE IMPORTAÇÃO:")
    print("1. Leitura e normalização dos dados CSV")
    print("2. Identificação de alimentos únicos por código")
    print("3. Extração dos nutrientes principais")
    print("4. Organização em alimentos e componentes")
    print("5. Inserção no banco SQLite")
    
    print("\n🔸 BANCO DE DADOS:")
    print("• alimentos: Dados básicos dos alimentos")
    print("• nutrientes: Nutrientes principais (kcal, proteínas, etc.)")
    print("• alimentos_composicao: Composição detalhada com todas as medidas")
    
def executar_opcao(opcao):
    """Executa a opção escolhida"""
    python_exe = sys.executable
    
    if opcao == "1":
        print("\n🔄 Executando importação da tabela completa...")
        subprocess.run([python_exe, "importar_tbca_completo.py"])
        
    elif opcao == "2":
        print("\n🔍 Verificando dados (simples)...")
        subprocess.run([python_exe, "check_database.py"])
        
    elif opcao == "3":
        print("\n📊 Verificando dados (avançado)...")
        subprocess.run([python_exe, "check_database_avancado.py"])
        
    elif opcao == "4":
        print("\n🗄️ Migrando dados para Oracle...")
        
        # Verificar se o script existe
        if os.path.exists("scripts/migrate_sqlite_to_oracle.py"):
            subprocess.run([python_exe, "scripts/migrate_sqlite_to_oracle.py"])
        else:
            print("❌ Script de migração não encontrado: scripts/migrate_sqlite_to_oracle.py")
        
    elif opcao == "5":
        print("\n🧹 Limpando banco de dados...")
        
        confirmacao = input("⚠️ ATENÇÃO: Isso irá apagar TODOS os dados! Confirmar? (s/n): ").strip().lower()
        if confirmacao in ['s', 'sim', 'y', 'yes']:
            try:
                import sqlite3
                conn = sqlite3.connect("nutri-app/backend/tbca.db")
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM nutrientes")
                cursor.execute("DELETE FROM alimentos")
                cursor.execute("DELETE FROM grupos")
                cursor.execute("DELETE FROM categorias")
                
                # Verificar se existe a tabela de composição
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alimentos_composicao'")
                if cursor.fetchone():
                    cursor.execute("DELETE FROM alimentos_composicao")
                
                conn.commit()
                conn.close()
                
                print("✅ Banco de dados limpo com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao limpar banco: {e}")
        else:
            print("⚠️ Operação cancelada pelo usuário.")
        
    elif opcao == "6":
        mostrar_info_csv()
        
    elif opcao == "0":
        print("\n👋 Saindo...")
        return False
        
    else:
        print("❌ Opção inválida!")
    
    return True

def verificar_pre_requisitos():
    """Verifica pré-requisitos antes de executar"""
    
    # Verificar se o arquivo CSV existe
    if not os.path.exists("composicao_todos_alimentos.csv"):
        print("⚠️ Arquivo 'composicao_todos_alimentos.csv' não encontrado no diretório atual.")
        print("ℹ️ Certifique-se de que o arquivo esteja na raiz do projeto.")
        print("   Caminho esperado: " + os.path.abspath("composicao_todos_alimentos.csv"))
        return False
    
    # Verificar se o banco existe
    if not os.path.exists("nutri-app/backend/tbca.db"):
        print("⚠️ Banco de dados 'tbca.db' não encontrado.")
        print("ℹ️ Certifique-se de que o banco exista em nutri-app/backend/")
        return False
    
    # Verificar dependências Python
    try:
        import pandas
        import sqlite3
    except ImportError as e:
        print(f"⚠️ Dependência não encontrada: {e}")
        print("ℹ️ Execute: pip install pandas")
        return False
    
    return True

def main():
    """Função principal"""
    
    mostrar_cabecalho()
    
    # Verificar pré-requisitos
    if not verificar_pre_requisitos():
        print("\n❌ Pré-requisitos não atendidos. Corrija os erros e tente novamente.")
        return
    
    # Mostrar estatísticas do arquivo
    try:
        tamanho_mb = os.path.getsize("composicao_todos_alimentos.csv") / (1024 * 1024)
        num_linhas = sum(1 for _ in open("composicao_todos_alimentos.csv", 'r', encoding='utf-8'))
        
        print("\n📊 INFORMAÇÕES DO ARQUIVO:")
        print(f"   • Arquivo: composicao_todos_alimentos.csv")
        print(f"   • Tamanho: {tamanho_mb:.2f} MB")
        print(f"   • Linhas: {num_linhas:,}".replace(',', '.'))
    except Exception as e:
        print(f"⚠️ Erro ao ler estatísticas do arquivo: {e}")
    
    # Loop principal
    while True:
        mostrar_menu()
        
        opcao = input("\n➤ Digite sua opção (0-6): ").strip()
        
        if not executar_opcao(opcao):
            break
        
        if opcao != "0":
            input("\n⏎ Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
