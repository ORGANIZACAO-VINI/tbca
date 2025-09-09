#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu principal para importação de dados
"""

import os
import sys
from pathlib import Path

def mostrar_menu():
    """Mostra menu principal"""
    
    print("\n🍎 SISTEMA DE IMPORTAÇÃO DE DADOS NUTRICIONAIS")
    print("=" * 55)
    
    print("\n📁 FORMATOS SUPORTADOS:")
    print("   • CSV (separado por ; ou ,)")
    print("   • Excel (.xlsx, .xls)")
    print("   • JSON")
    print("   • Banco SQLite existente")
    
    print("\n🚀 OPÇÕES DISPONÍVEIS:")
    print("   1. Importar arquivo CSV")
    print("   2. Importar arquivo Excel")
    print("   3. Verificar dados na pasta")
    print("   4. Verificar banco atual")
    print("   5. Migrar para Oracle")
    print("   6. Ajuda - Como preparar dados")
    print("   0. Sair")

def verificar_arquivos_dados():
    """Verifica arquivos na pasta dados"""
    
    dados_path = Path("dados")
    
    if not dados_path.exists():
        print("❌ Pasta 'dados' não encontrada!")
        return
    
    print("\n📁 ARQUIVOS NA PASTA 'dados/':")
    print("-" * 40)
    
    arquivos = list(dados_path.iterdir())
    
    if not arquivos:
        print("   (pasta vazia)")
        print("\n💡 COMO ADICIONAR DADOS:")
        print("   1. Coloque seus arquivos CSV/Excel na pasta 'dados/'")
        print("   2. Execute este menu novamente")
        return
    
    for arquivo in arquivos:
        if arquivo.is_file():
            tamanho = arquivo.stat().st_size
            tamanho_mb = tamanho / (1024 * 1024)
            
            if arquivo.suffix.lower() in ['.csv', '.xlsx', '.xls']:
                print(f"   ✅ {arquivo.name} ({tamanho_mb:.1f} MB)")
            else:
                print(f"   📄 {arquivo.name} ({tamanho_mb:.1f} MB)")

def mostrar_ajuda():
    """Mostra ajuda detalhada"""
    
    print("\n📚 GUIA DE PREPARAÇÃO DE DADOS")
    print("=" * 40)
    
    print("\n🔸 ARQUIVO CSV:")
    print("   • Separador: ; (ponto e vírgula) ou , (vírgula)")
    print("   • Encoding: UTF-8")
    print("   • Primeira linha: cabeçalho")
    print("   • Exemplo:")
    print("     codigo;nome;kcal;proteina;carboidratos")
    print("     ALM001;Arroz;130;2.5;28.1")
    
    print("\n🔸 ARQUIVO EXCEL:")
    print("   • Formato: .xlsx ou .xls")
    print("   • Primeira linha: cabeçalho")
    print("   • Uma planilha por arquivo")
    
    print("\n🔸 COLUNAS OBRIGATÓRIAS:")
    print("   • nome: Nome do alimento")
    print("   • kcal: Valor energético")
    
    print("\n🔸 COLUNAS OPCIONAIS:")
    print("   • codigo: Código identificador")
    print("   • proteina: Proteínas (g)")
    print("   • carboidratos: Carboidratos (g)")
    print("   • gordura: Lipídeos (g)")
    print("   • fibras: Fibras (g)")
    print("   • calcio: Cálcio (mg)")
    print("   • ferro: Ferro (mg)")

def executar_opcao(opcao):
    """Executa a opção escolhida"""
    
    if opcao == "1":
        print("\n🔄 Executando importação CSV...")
        os.system(f"{sys.executable} importar_csv_simples.py")
        
    elif opcao == "2":
        print("\n🔄 Executando importação Excel...")
        os.system(f"{sys.executable} importar_excel.py")
        
    elif opcao == "3":
        verificar_arquivos_dados()
        
    elif opcao == "4":
        print("\n🔄 Verificando banco atual...")
        os.system(f"{sys.executable} check_database.py")
        
    elif opcao == "5":
        print("\n🔄 Migrando para Oracle...")
        os.system(f"{sys.executable} scripts/migrate_sqlite_to_oracle.py")
        
    elif opcao == "6":
        mostrar_ajuda()
        
    elif opcao == "0":
        print("\n👋 Saindo...")
        return False
        
    else:
        print("❌ Opção inválida!")
    
    return True

def main():
    """Função principal"""
    
    print("🍎 BEM-VINDO AO SISTEMA DE IMPORTAÇÃO!")
    
    while True:
        mostrar_menu()
        
        opcao = input("\n➤ Digite sua opção (0-6): ").strip()
        
        if not executar_opcao(opcao):
            break
        
        input("\n⏎ Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
