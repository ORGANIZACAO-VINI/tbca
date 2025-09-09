#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar dados da tabela TBCA avançada
(composicao_todos_alimentos.csv) para o banco SQLite
"""

import os
import csv
import sqlite3
import pandas as pd
import re
from datetime import datetime
from collections import defaultdict

# Configurações
CSV_PATH = "composicao_todos_alimentos.csv"
DB_PATH = "nutri-app/backend/tbca.db"
LOG_FILE = f"logs/importacao_tbca_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Garantir que pasta de logs existe
os.makedirs("logs", exist_ok=True)

def log(message, level="INFO"):
    """Função para registrar logs"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {level}: {message}"
    print(log_message)
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def normalizar_texto(texto):
    """Normaliza texto removendo caracteres especiais"""
    if not texto:
        return ""
    
    # Substituir caracteres especiais
    replacements = {
        "Ã£": "ã", "Ã¡": "á", "Ã©": "é", "Ã³": "ó", "Ãª": "ê",
        "Ã§": "ç", "Ã­": "í", "Ãº": "ú", "Ã¢": "â", "Ã´": "ô"
    }
    
    for old, new in replacements.items():
        texto = texto.replace(old, new)
    
    return texto

def valor_para_float(valor):
    """Converte valor em string para float"""
    if not valor or valor == "NA" or valor == "nan":
        return None
    
    try:
        # Substituir vírgula por ponto e converter
        valor_limpo = valor.replace(",", ".")
        return float(valor_limpo)
    except (ValueError, TypeError):
        return None

def preparar_banco():
    """Preparar banco de dados para importação"""
    if not os.path.exists(DB_PATH):
        log(f"Banco não encontrado: {DB_PATH}", "ERROR")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se existem tabelas adicionais necessárias
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='alimentos_composicao'
        """)
        
        if not cursor.fetchone():
            log("Criando tabela alimentos_composicao...")
            
            # Criar tabela para composição detalhada
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alimentos_composicao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alimento_id INTEGER,
                componente TEXT,
                unidade TEXT,
                valor_por_100g REAL,
                porcao_nome TEXT,
                porcao_valor REAL,
                FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
            )
            """)
            
            # Criar índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alimentos_composicao_alimento_id ON alimentos_composicao(alimento_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alimentos_composicao_componente ON alimentos_composicao(componente)")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        log(f"Erro ao preparar banco: {e}", "ERROR")
        return False

def processar_csv():
    """Processa o arquivo CSV e extrai dados"""
    log(f"Iniciando processamento do arquivo: {CSV_PATH}")
    
    if not os.path.exists(CSV_PATH):
        log(f"Arquivo CSV não encontrado: {CSV_PATH}", "ERROR")
        return False
    
    try:
        # Inicializar estruturas de dados
        alimentos = {}  # código -> {dados do alimento}
        composicao = defaultdict(list)  # código -> [{componente, valor, ...}]
        
        # Primeira passagem - identificar todos os alimentos
        log("Primeira passagem: identificando alimentos únicos...")
        
        with open(CSV_PATH, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            cabecalho = next(reader)  # Pular cabeçalho
            
            # Encontrar índices importantes
            try:
                idx_componente = cabecalho.index('componente')
                idx_unidade = cabecalho.index('unidade')
                idx_valor_100g = cabecalho.index('Valor por 100g')
                idx_codigo = cabecalho.index('codigo_alimento')
                idx_nome = cabecalho.index('nome_alimento')
            except ValueError as e:
                log(f"Formato de CSV inválido. Erro: {e}", "ERROR")
                return False
            
            # Processar linhas
            linha_count = 0
            for linha in reader:
                linha_count += 1
                
                if linha_count % 10000 == 0:
                    log(f"Processando linha {linha_count}...")
                
                if len(linha) <= max(idx_componente, idx_unidade, idx_valor_100g, idx_codigo, idx_nome):
                    continue  # Pular linhas incompletas
                
                codigo = linha[idx_codigo].strip()
                nome = normalizar_texto(linha[idx_nome].strip())
                
                # Adicionar alimento se ainda não existe e tem um código válido
                if codigo and codigo not in alimentos and nome and nome != "Nome não encontrado":
                    alimentos[codigo] = {
                        'codigo': codigo,
                        'nome': nome,
                        'nutrientes_principais': {}
                    }
                
                # Adicionar componente à composição
                if codigo and codigo in alimentos:
                    componente = linha[idx_componente].strip()
                    unidade = linha[idx_unidade].strip()
                    valor_100g = valor_para_float(linha[idx_valor_100g])
                    
                    if componente and unidade and valor_100g is not None:
                        # Guardar nutrientes principais diretamente no alimento
                        nutrientes_principais = {
                            'Energia': 'kcal', 
                            'Carboidrato total': 'g',
                            'Proteína': 'g',
                            'Lipídeos': 'g',
                            'Fibra alimentar': 'g',
                            'Cálcio': 'mg',
                            'Ferro': 'mg'
                        }
                        
                        if componente in nutrientes_principais:
                            alimentos[codigo]['nutrientes_principais'][componente] = valor_100g
                        
                        # Adicionar à lista de composição
                        item_composicao = {
                            'componente': componente,
                            'unidade': unidade,
                            'valor_por_100g': valor_100g
                        }
                        
                        # Adicionar porções
                        for i, coluna in enumerate(cabecalho):
                            if i > idx_nome and "Pedaço" in coluna or "Colher" in coluna or "Xícara" in coluna or "Porção" in coluna:
                                if i < len(linha) and linha[i]:
                                    valor_porcao = valor_para_float(linha[i])
                                    if valor_porcao is not None:
                                        item_composicao[coluna] = valor_porcao
                        
                        composicao[codigo].append(item_composicao)
        
        log(f"Encontrados {len(alimentos)} alimentos únicos")
        log(f"Componentes totais: {sum(len(comps) for comps in composicao.values())}")
        
        return {
            'alimentos': alimentos,
            'composicao': composicao
        }
        
    except Exception as e:
        log(f"Erro ao processar CSV: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return False

def importar_para_sqlite(dados):
    """Importa dados processados para o SQLite"""
    log("Iniciando importação para SQLite...")
    
    if not dados or 'alimentos' not in dados:
        log("Dados inválidos para importação", "ERROR")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Iniciar transação
        conn.execute("BEGIN TRANSACTION")
        
        # Confirmar com usuário
        resposta = input("\nATENÇÃO: Isso irá substituir todos os dados no banco. Continuar? (s/n): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            log("Importação cancelada pelo usuário")
            return False
        
        # Limpar dados existentes
        log("Limpando dados existentes...")
        cursor.execute("DELETE FROM nutrientes")
        cursor.execute("DELETE FROM alimentos")
        cursor.execute("DELETE FROM grupos")
        cursor.execute("DELETE FROM categorias")
        cursor.execute("DELETE FROM alimentos_composicao")
        
        # Inserir categorias e grupos
        log("Inserindo categorias e grupos...")
        cursor.execute("INSERT INTO categorias (nome) VALUES (?)", ("TBCA - Tabela Brasileira de Composição de Alimentos",))
        categoria_id = cursor.lastrowid
        
        # Criar grupos
        grupos = {
            "Cereais": None,
            "Leguminosas": None, 
            "Hortaliças": None,
            "Frutas": None, 
            "Carnes": None,
            "Leite": None,
            "Bebidas": None,
            "Ovos": None,
            "Óleos": None,
            "Açúcares": None,
            "Diversos": None
        }
        
        for grupo_nome in grupos:
            cursor.execute("INSERT INTO grupos (nome) VALUES (?)", (grupo_nome,))
            grupos[grupo_nome] = cursor.lastrowid
        
        grupo_default = grupos["Diversos"]
        
        # Inserir alimentos
        log("Inserindo alimentos...")
        alimentos_inseridos = 0
        alimentos_ids = {}  # Mapear código -> id
        
        for codigo, alimento in dados['alimentos'].items():
            nome = alimento['nome']
            
            # Determinar grupo (implementação básica)
            grupo_id = grupo_default
            nome_lower = nome.lower()
            
            if any(termo in nome_lower for termo in ['arroz', 'trigo', 'aveia', 'milho', 'pão', 'macarrão']):
                grupo_id = grupos["Cereais"]
            elif any(termo in nome_lower for termo in ['feijão', 'lentilha', 'ervilha', 'grão de bico']):
                grupo_id = grupos["Leguminosas"]
            elif any(termo in nome_lower for termo in ['alface', 'tomate', 'cenoura', 'abobrinha', 'espinafre']):
                grupo_id = grupos["Hortaliças"]
            elif any(termo in nome_lower for termo in ['maçã', 'banana', 'laranja', 'uva', 'manga']):
                grupo_id = grupos["Frutas"]
            elif any(termo in nome_lower for termo in ['carne', 'bovina', 'frango', 'peixe', 'suína']):
                grupo_id = grupos["Carnes"]
            elif any(termo in nome_lower for termo in ['leite', 'queijo', 'iogurte', 'requeijão']):
                grupo_id = grupos["Leite"]
            elif any(termo in nome_lower for termo in ['suco', 'refrigerante', 'água', 'bebida']):
                grupo_id = grupos["Bebidas"]
            elif any(termo in nome_lower for termo in ['ovo']):
                grupo_id = grupos["Ovos"]
            elif any(termo in nome_lower for termo in ['óleo', 'azeite', 'manteiga', 'margarina']):
                grupo_id = grupos["Óleos"]
            elif any(termo in nome_lower for termo in ['açúcar', 'mel', 'doce']):
                grupo_id = grupos["Açúcares"]
            
            # Inserir alimento
            cursor.execute("""
                INSERT INTO alimentos (codigo, nome, grupo_id)
                VALUES (?, ?, ?)
            """, (codigo, nome, grupo_id))
            
            alimento_id = cursor.lastrowid
            alimentos_ids[codigo] = alimento_id
            alimentos_inseridos += 1
            
            # Mostrar progresso
            if alimentos_inseridos % 100 == 0:
                log(f"Alimentos inseridos: {alimentos_inseridos}/{len(dados['alimentos'])}")
        
        # Inserir nutrientes principais
        log("Inserindo nutrientes principais...")
        nutrientes_inseridos = 0
        
        for codigo, alimento_id in alimentos_ids.items():
            nutrientes_principais = dados['alimentos'][codigo].get('nutrientes_principais', {})
            
            # Mapeamento de nutrientes
            mapeamento = {
                'Energia': ('Energia', 'kcal'),
                'Carboidrato total': ('Carboidratos', 'g'),
                'Proteína': ('Proteína', 'g'),
                'Lipídeos': ('Gordura', 'g'),
                'Fibra alimentar': ('Fibras', 'g'),
                'Cálcio': ('Cálcio', 'mg'),
                'Ferro': ('Ferro', 'mg')
            }
            
            for comp_original, (nome_nutriente, unidade) in mapeamento.items():
                if comp_original in nutrientes_principais:
                    valor = nutrientes_principais[comp_original]
                    
                    cursor.execute("""
                        INSERT INTO nutrientes (alimento_id, nome, unidade, valor_por_100g)
                        VALUES (?, ?, ?, ?)
                    """, (alimento_id, nome_nutriente, unidade, valor))
                    
                    nutrientes_inseridos += 1
        
        # Inserir composição completa
        log("Inserindo composição detalhada...")
        composicao_inserida = 0
        
        for codigo, componentes in dados['composicao'].items():
            if codigo in alimentos_ids:
                alimento_id = alimentos_ids[codigo]
                
                for componente in componentes:
                    nome_comp = componente['componente']
                    unidade = componente['unidade']
                    valor_100g = componente['valor_por_100g']
                    
                    # Inserir composição básica
                    cursor.execute("""
                        INSERT INTO alimentos_composicao (
                            alimento_id, componente, unidade, valor_por_100g
                        ) VALUES (?, ?, ?, ?)
                    """, (alimento_id, nome_comp, unidade, valor_100g))
                    
                    composicao_inserida += 1
                    
                    # Inserir porções
                    for chave, valor in componente.items():
                        if chave not in ['componente', 'unidade', 'valor_por_100g'] and valor is not None:
                            cursor.execute("""
                                INSERT INTO alimentos_composicao (
                                    alimento_id, componente, unidade, 
                                    valor_por_100g, porcao_nome, porcao_valor
                                ) VALUES (?, ?, ?, ?, ?, ?)
                            """, (alimento_id, nome_comp, unidade, valor_100g, chave, valor))
                            
                            composicao_inserida += 1
            
            # Mostrar progresso
            if composicao_inserida % 10000 == 0:
                log(f"Registros de composição inseridos: {composicao_inserida}")
        
        # Commit
        conn.commit()
        conn.close()
        
        log("✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        log(f"   Alimentos inseridos: {alimentos_inseridos}")
        log(f"   Nutrientes principais: {nutrientes_inseridos}")
        log(f"   Composição detalhada: {composicao_inserida}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        log(f"Erro ao importar para SQLite: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Função principal"""
    log("=" * 50)
    log("IMPORTAÇÃO DE BASE COMPLETA TBCA")
    log("=" * 50)
    
    # Preparar banco
    if not preparar_banco():
        log("Falha ao preparar banco de dados", "ERROR")
        return
    
    # Processar CSV
    log("Processando arquivo CSV...")
    dados = processar_csv()
    
    if not dados:
        log("Falha ao processar arquivo CSV", "ERROR")
        return
    
    # Importar para SQLite
    log("Importando dados para SQLite...")
    if importar_para_sqlite(dados):
        log("\n🎉 IMPORTAÇÃO FINALIZADA COM SUCESSO!")
        log("   Para verificar os dados, execute:")
        log("   python check_database.py")
    else:
        log("❌ Falha na importação", "ERROR")

if __name__ == "__main__":
    main()
