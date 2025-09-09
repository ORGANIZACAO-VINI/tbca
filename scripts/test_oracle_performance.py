#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar a conexão e performance do Oracle Database
Versão aprimorada com testes avançados e melhor visualização de resultados
"""

import os
import time
import json
import statistics
import argparse
import sys
import concurrent.futures
import traceback
import random
from pathlib import Path
from datetime import datetime

# Verificar dependências
try:
    import cx_Oracle
except ImportError:
    print("ERRO: Biblioteca cx_Oracle não está instalada.")
    print("Por favor, execute: pip install cx_Oracle")
    sys.exit(1)

try:
    import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    print("INFO: Biblioteca tabulate não está instalada. Relatórios serão exibidos em formato simples.")
    print("Para melhor visualização, execute: pip install tabulate")

try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("INFO: Biblioteca matplotlib não está instalada. Gráficos não estarão disponíveis.")
    print("Para visualização gráfica, execute: pip install matplotlib numpy")

def get_config(config_path=None):
    """
    Lê e valida as configurações do Oracle do arquivo de configuração
    
    Args:
        config_path: Caminho opcional para o arquivo de configuração. Se não fornecido,
                     será usado o caminho padrão.
    
    Returns:
        dict: Configurações do Oracle
    """
    if not config_path:
        config_path = Path(__file__).parent.parent / "config" / "oracle_config.json"
    
    if not Path(config_path).exists():
        print(f"Erro: Arquivo de configuração Oracle não encontrado: {config_path}")
        print("Execute primeiro o script configurar-oracle.ps1 ou forneça um caminho válido.")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validar campos obrigatórios
        required_fields = ['ORACLE_USER', 'ORACLE_PASSWORD', 'ORACLE_HOST', 
                          'ORACLE_PORT', 'ORACLE_SERVICE']
        
        missing_fields = [field for field in required_fields if field not in config or not config[field]]
        
        if missing_fields:
            print(f"Erro: Campos obrigatórios ausentes no arquivo de configuração: {', '.join(missing_fields)}")
            sys.exit(1)
            
        # Validar valores
        if not isinstance(config['ORACLE_PORT'], (str, int)):
            print(f"Erro: ORACLE_PORT deve ser uma string ou inteiro, não {type(config['ORACLE_PORT']).__name__}")
            sys.exit(1)
            
        # Converter porta para string se for número
        if isinstance(config['ORACLE_PORT'], int):
            config['ORACLE_PORT'] = str(config['ORACLE_PORT'])
            
        return config
        
    except json.JSONDecodeError as e:
        print(f"Erro: O arquivo de configuração contém JSON inválido: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler arquivo de configuração: {str(e)}")
        sys.exit(1)

def get_oracle_connection(config):
    """
    Estabelece uma conexão com o Oracle Database
    
    Args:
        config: Dicionário com configurações de conexão
        
    Returns:
        tuple: (connection, dsn) - Objeto de conexão e string DSN, ou (None, dsn) em caso de erro
    """
    try:
        # Construir DSN (Data Source Name)
        dsn = cx_Oracle.makedsn(
            host=config['ORACLE_HOST'],
            port=config['ORACLE_PORT'],
            service_name=config['ORACLE_SERVICE']
        )
        
        # Estabelecer conexão
        connection = cx_Oracle.connect(
            user=config['ORACLE_USER'],
            password=config['ORACLE_PASSWORD'],
            dsn=dsn,
            encoding="UTF-8"
        )
        
        return connection, dsn
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Erro de Oracle ao conectar: ORA-{error.code}: {error.message}")
        return None, dsn
    except Exception as e:
        print(f"Erro ao conectar: {str(e)}")
        traceback.print_exc()
        return None, dsn

def test_connection(config):
    """
    Testa a conexão com o Oracle Database e retorna informações sobre o servidor
    
    Args:
        config: Dicionário com configurações de conexão
        
    Returns:
        bool: True se a conexão for bem-sucedida, False caso contrário
    """
    print("\n=== Teste de Conexão Oracle ===")
    
    start_time = time.time()
    connection, dsn = get_oracle_connection(config)
    
    if not connection:
        return False
        
    elapsed = time.time() - start_time
    
    try:
        print(f"Conexão estabelecida com sucesso em {elapsed:.3f} segundos")
        print(f"Versão do Oracle: {connection.version}")
        
        # Verificar data e hora do servidor
        cursor = connection.cursor()
        cursor.execute("SELECT SYSDATE FROM DUAL")
        server_date = cursor.fetchone()[0]
        print(f"Data/hora do servidor: {server_date}")
        
        # Verificar configurações de NLS
        print("\nConfigurações de NLS do banco:")
        cursor.execute("""
            SELECT PARAMETER, VALUE 
            FROM NLS_DATABASE_PARAMETERS 
            WHERE PARAMETER IN ('NLS_CHARACTERSET', 'NLS_NCHAR_CHARACTERSET', 'NLS_LANGUAGE', 'NLS_TERRITORY')
            ORDER BY PARAMETER
        """)
        
        if HAS_TABULATE:
            rows = cursor.fetchall()
            headers = ["Parâmetro", "Valor"]
            print(tabulate.tabulate(rows, headers=headers, tablefmt="pretty"))
        else:
            for param, value in cursor:
                print(f"  {param} = {value}")
        
        # Verificar informações da sessão
        print("\nInformações da sessão:")
        cursor.execute("""
            SELECT SYS_CONTEXT('USERENV', 'SESSION_USER') as usuario,
                   SYS_CONTEXT('USERENV', 'HOST') as host,
                   SYS_CONTEXT('USERENV', 'IP_ADDRESS') as ip,
                   SYS_CONTEXT('USERENV', 'INSTANCE_NAME') as instancia
            FROM DUAL
        """)
        session_info = cursor.fetchone()
        print(f"  Usuário: {session_info[0]}")
        print(f"  Host: {session_info[1]}")
        print(f"  IP: {session_info[2]}")
        print(f"  Instância: {session_info[3]}")
        
        cursor.close()
        connection.close()
        
        return True
    except cx_Oracle.Error as e:
        error, = e.args
        print(f"Erro durante teste de conexão: ORA-{error.code}: {error.message}")
        if connection:
            connection.close()
        return False
    except Exception as e:
        print(f"Erro durante teste de conexão: {str(e)}")
        traceback.print_exc()
        if connection:
            connection.close()
        return False

def test_basic_queries(config):
    """
    Testa consultas básicas para verificar funcionalidade
    
    Args:
        config: Dicionário com configurações de conexão
        
    Returns:
        bool: True se todos os testes passarem, False caso contrário
    """
    print("\n=== Teste de Consultas Básicas ===")
    
    connection, _ = get_oracle_connection(config)
    
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        results = []
        
        # Testar consulta simples
        print("1. Consulta simples...")
        cursor.execute("SELECT 'Hello Oracle' FROM DUAL")
        result = cursor.fetchone()[0]
        print(f"   Resultado: {result}")
        results.append(True)
        
        # Verificar informações de versão
        print("\n2. Informações da versão do Oracle...")
        cursor.execute("""
            SELECT BANNER 
            FROM V$VERSION 
            WHERE BANNER LIKE 'Oracle%'
        """)
        version_info = cursor.fetchone()
        if version_info:
            print(f"   {version_info[0]}")
            results.append(True)
        else:
            print("   Não foi possível obter informações de versão")
            results.append(False)
        
        # Verificar tabelas existentes
        print("\n3. Verificando tabelas existentes...")
        cursor.execute("""
            SELECT table_name, num_rows, last_analyzed
            FROM user_tables
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"   Encontradas {len(tables)} tabelas no esquema atual.")
            
            if HAS_TABULATE:
                headers = ["Nome da Tabela", "Linhas (estimado)", "Última Análise"]
                print(tabulate.tabulate(tables, headers=headers, tablefmt="pretty"))
            else:
                for table in tables:
                    print(f"   {table[0]}: {table[1] or 'N/A'} linhas, Última análise: {table[2] or 'Nunca'}")
            
            results.append(True)
            
            # Armazenar nomes das tabelas para uso posterior
            table_names = [row[0] for row in tables]
        else:
            print("   Nenhuma tabela encontrada no esquema.")
            table_names = []
            results.append(True)  # Não é um erro, pode ser esquema vazio
        
        # Se a tabela CATEGORIAS existir, testar consulta
        if 'CATEGORIAS' in table_names:
            print("\n4. Analisando tabela CATEGORIAS...")
            
            # Verificar estrutura da tabela
            cursor.execute("""
                SELECT column_name, data_type, data_length, nullable
                FROM user_tab_columns
                WHERE table_name = 'CATEGORIAS'
                ORDER BY column_id
            """)
            columns = cursor.fetchall()
            
            if HAS_TABULATE:
                headers = ["Coluna", "Tipo", "Tamanho", "Nullable"]
                print("   Estrutura da tabela:")
                print(tabulate.tabulate(columns, headers=headers, tablefmt="simple"))
            else:
                print("   Estrutura da tabela:")
                for col in columns:
                    print(f"   {col[0]}: {col[1]}({col[2]}), {'NULL' if col[3] == 'Y' else 'NOT NULL'}")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM CATEGORIAS")
            count = cursor.fetchone()[0]
            print(f"\n   Total de categorias: {count}")
            
            if count > 0:
                cursor.execute("""
                    SELECT id, nome 
                    FROM CATEGORIAS 
                    WHERE ROWNUM <= 5
                    ORDER BY id
                """)
                cats = cursor.fetchall()
                
                print("   Primeiras categorias:")
                if HAS_TABULATE:
                    headers = ["ID", "Nome"]
                    print(tabulate.tabulate(cats, headers=headers, tablefmt="simple"))
                else:
                    for cat in cats:
                        print(f"   ID: {cat[0]}, Nome: {cat[1]}")
            
            results.append(True)
        
        # Se a tabela ALIMENTOS existir, testar consulta
        if 'ALIMENTOS' in table_names:
            print("\n5. Analisando tabela ALIMENTOS...")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM ALIMENTOS")
            count = cursor.fetchone()[0]
            print(f"   Total de alimentos: {count}")
            
            if count > 0:
                # Estatísticas sobre macronutrientes
                cursor.execute("""
                    SELECT 
                        ROUND(AVG(kcal), 2) as media_kcal,
                        ROUND(AVG(proteina), 2) as media_proteina,
                        ROUND(AVG(carboidratos), 2) as media_carboidratos,
                        ROUND(AVG(gordura), 2) as media_gordura,
                        ROUND(MIN(kcal), 2) as min_kcal,
                        ROUND(MAX(kcal), 2) as max_kcal,
                        COUNT(*) as total
                    FROM ALIMENTOS
                """)
                stats = cursor.fetchone()
                
                print("\n   Estatísticas nutricionais:")
                print(f"   Média de calorias: {stats[0]} kcal (min: {stats[4]}, max: {stats[5]})")
                print(f"   Média de proteínas: {stats[1]}g")
                print(f"   Média de carboidratos: {stats[2]}g")
                print(f"   Média de gorduras: {stats[3]}g")
                
                # Listar alguns alimentos com join
                print("\n   Alguns alimentos com suas categorias:")
                cursor.execute("""
                    SELECT a.id, a.nome, a.kcal, c.nome as categoria
                    FROM ALIMENTOS a
                    JOIN CATEGORIAS c ON a.categoria_id = c.id
                    WHERE ROWNUM <= 5
                    ORDER BY a.id
                """)
                foods = cursor.fetchall()
                
                if HAS_TABULATE:
                    headers = ["ID", "Nome", "Kcal", "Categoria"]
                    print(tabulate.tabulate(foods, headers=headers, tablefmt="simple"))
                else:
                    for food in foods:
                        print(f"   ID: {food[0]}, Nome: {food[1]}, Kcal: {food[2]}, Categoria: {food[3]}")
            
            results.append(True)
        
        # Testar algumas funções do Oracle
        print("\n6. Testando funções embutidas do Oracle...")
        cursor.execute("""
            SELECT 
                TO_CHAR(SYSDATE, 'DD/MM/YYYY HH24:MI:SS') as data_atual,
                TO_CHAR(SYSDATE, 'Day, DD Month YYYY', 'NLS_DATE_LANGUAGE = PORTUGUESE') as data_formatada,
                SYSTIMESTAMP as timestamp,
                SYS_GUID() as guid
            FROM DUAL
        """)
        
        func_result = cursor.fetchone()
        print(f"   Data atual: {func_result[0]}")
        print(f"   Data formatada: {func_result[1]}")
        print(f"   Timestamp: {func_result[2]}")
        print(f"   GUID: {func_result[3]}")
        
        results.append(True)
        
        # Verificar privilégios do usuário
        print("\n7. Verificando privilégios do usuário atual...")
        cursor.execute("""
            SELECT privilege 
            FROM user_sys_privs 
            ORDER BY privilege
        """)
        privs = cursor.fetchall()
        
        if privs:
            print(f"   O usuário possui {len(privs)} privilégios:")
            priv_list = [row[0] for row in privs]
            # Exibir em formato de lista com separação por vírgulas
            print("   " + ", ".join(priv_list[:10]) + ("..." if len(priv_list) > 10 else ""))
        else:
            print("   O usuário não possui privilégios de sistema.")
        
        results.append(True)
        
        cursor.close()
        connection.close()
        
        return all(results)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Erro durante teste de consultas: ORA-{error.code}: {error.message}")
        if connection:
            connection.close()
        return False
    except Exception as e:
        print(f"Erro durante teste de consultas: {str(e)}")
        traceback.print_exc()
        if connection:
            connection.close()
        return False

def test_transaction(config):
    """
    Testa transações Oracle, incluindo commit e rollback
    
    Args:
        config: Dicionário com configurações de conexão
        
    Returns:
        bool: True se o teste for bem-sucedido, False caso contrário
    """
    print("\n=== Teste de Transações Oracle ===")
    
    connection, _ = get_oracle_connection(config)
    
    if not connection:
        return False
    
    # Nome da tabela temporária para o teste
    temp_table = f"TEMP_TEST_{int(time.time())}"
    
    try:
        cursor = connection.cursor()
        
        # Verificar se a tabela temporária já existe (improvável, mas por segurança)
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM user_tables 
            WHERE table_name = '{temp_table}'
        """)
        
        if cursor.fetchone()[0] > 0:
            print(f"A tabela temporária {temp_table} já existe. Usando outro nome.")
            temp_table = f"{temp_table}_{os.getpid()}"
        
        # Criar tabela temporária
        print(f"1. Criando tabela temporária {temp_table}...")
        cursor.execute(f"""
            CREATE TABLE {temp_table} (
                id NUMBER PRIMARY KEY,
                descricao VARCHAR2(100),
                data_teste TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Teste 1: Commit
        print("\n2. Testando INSERT com COMMIT...")
        cursor.execute(f"INSERT INTO {temp_table} (id, descricao) VALUES (1, 'Teste com commit')")
        connection.commit()
        print("   Registro inserido e committed.")
        
        # Verificar se o registro foi persistido
        cursor.execute(f"SELECT COUNT(*) FROM {temp_table}")
        count = cursor.fetchone()[0]
        print(f"   Contagem após commit: {count}")
        
        if count != 1:
            print(f"   ERRO: Esperado 1 registro, encontrado {count}")
            raise Exception("Erro no teste de commit")
        
        # Teste 2: Rollback
        print("\n3. Testando INSERT com ROLLBACK...")
        cursor.execute(f"INSERT INTO {temp_table} (id, descricao) VALUES (2, 'Teste com rollback')")
        print("   Registro inserido (não committed).")
        
        # Verificar se o registro está visível antes do rollback
        cursor.execute(f"SELECT COUNT(*) FROM {temp_table}")
        count_before_rollback = cursor.fetchone()[0]
        print(f"   Contagem antes do rollback: {count_before_rollback}")
        
        if count_before_rollback != 2:
            print(f"   AVISO: Esperado 2 registros antes do rollback, encontrado {count_before_rollback}")
        
        # Fazer rollback
        connection.rollback()
        print("   Operação rollback executada.")
        
        # Verificar se o registro foi descartado
        cursor.execute(f"SELECT COUNT(*) FROM {temp_table}")
        count_after_rollback = cursor.fetchone()[0]
        print(f"   Contagem após rollback: {count_after_rollback}")
        
        if count_after_rollback != 1:
            print(f"   ERRO: Esperado 1 registro após rollback, encontrado {count_after_rollback}")
            raise Exception("Erro no teste de rollback")
        
        # Teste 3: Savepoint
        print("\n4. Testando SAVEPOINT...")
        
        # Inserir registro 2
        cursor.execute(f"INSERT INTO {temp_table} (id, descricao) VALUES (2, 'Antes do savepoint')")
        
        # Criar savepoint
        cursor.execute("SAVEPOINT sp1")
        print("   Savepoint 'sp1' criado após inserir registro 2.")
        
        # Inserir registro 3
        cursor.execute(f"INSERT INTO {temp_table} (id, descricao) VALUES (3, 'Após o savepoint')")
        print("   Registro 3 inserido após o savepoint.")
        
        # Verificar contagem
        cursor.execute(f"SELECT COUNT(*) FROM {temp_table}")
        count_with_both = cursor.fetchone()[0]
        print(f"   Contagem com ambos os registros: {count_with_both}")
        
        # Rollback para o savepoint
        cursor.execute("ROLLBACK TO SAVEPOINT sp1")
        print("   Rollback para o savepoint 'sp1' executado.")
        
        # Verificar se apenas o registro após o savepoint foi descartado
        cursor.execute(f"SELECT COUNT(*) FROM {temp_table}")
        count_after_sp_rollback = cursor.fetchone()[0]
        print(f"   Contagem após rollback para savepoint: {count_after_sp_rollback}")
        
        if count_after_sp_rollback != 2:
            print(f"   ERRO: Esperado 2 registros após rollback para savepoint, encontrado {count_after_sp_rollback}")
            raise Exception("Erro no teste de savepoint")
        
        # Commit final para o registro 2
        connection.commit()
        
        print("\n5. Limpando tabela temporária...")
        cursor.execute(f"DROP TABLE {temp_table}")
        connection.commit()
        print(f"   Tabela {temp_table} removida com sucesso.")
        
        cursor.close()
        connection.close()
        
        print("\nTeste de transações concluído com sucesso!")
        return True
        
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Erro durante teste de transações: ORA-{error.code}: {error.message}")
        
        # Tentar limpar a tabela temporária
        try:
            if connection:
                cleanup_cursor = connection.cursor()
                cleanup_cursor.execute(f"DROP TABLE {temp_table}")
                connection.commit()
                cleanup_cursor.close()
                print(f"Tabela temporária {temp_table} removida na limpeza de erro.")
        except:
            print(f"Não foi possível remover a tabela temporária {temp_table} após erro.")
        
        if connection:
            connection.close()
        return False
    except Exception as e:
        print(f"Erro durante teste de transações: {str(e)}")
        traceback.print_exc()
        
        # Tentar limpar a tabela temporária
        try:
            if connection:
                cleanup_cursor = connection.cursor()
                cleanup_cursor.execute(f"DROP TABLE {temp_table}")
                connection.commit()
                cleanup_cursor.close()
                print(f"Tabela temporária {temp_table} removida na limpeza de erro.")
        except:
            print(f"Não foi possível remover a tabela temporária {temp_table} após erro.")
        
        if connection:
            connection.close()
        return False


def test_blob_operations(config):
    """
    Testa operações com BLOB (Binary Large Object) no Oracle
    
    Args:
        config: Dicionário com configurações de conexão
        
    Returns:
        bool: True se o teste for bem-sucedido, False caso contrário
    """
    print("\n=== Teste de Operações com BLOB ===")
    
    connection, _ = get_oracle_connection(config)
    
    if not connection:
        return False
    
    # Nome da tabela temporária para o teste
    temp_table = f"TEMP_BLOB_{int(time.time())}"
    
    try:
        cursor = connection.cursor()
        
        # Verificar se a tabela temporária já existe
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM user_tables 
            WHERE table_name = '{temp_table}'
        """)
        
        if cursor.fetchone()[0] > 0:
            print(f"A tabela temporária {temp_table} já existe. Usando outro nome.")
            temp_table = f"{temp_table}_{os.getpid()}"
        
        # Criar tabela temporária com coluna BLOB
        print(f"1. Criando tabela temporária {temp_table} com coluna BLOB...")
        cursor.execute(f"""
            CREATE TABLE {temp_table} (
                id NUMBER PRIMARY KEY,
                nome VARCHAR2(100),
                dados BLOB,
                tamanho_bytes NUMBER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Gerar alguns dados binários para teste
        print("\n2. Gerando dados binários para teste...")
        test_data_sizes = [1024, 10240, 102400]  # Tamanhos em bytes (1KB, 10KB, 100KB)
        
        for i, size in enumerate(test_data_sizes, 1):
            # Gerar dados binários aleatórios
            binary_data = os.urandom(size)
            print(f"   - Dados #{i}: {size} bytes ({size/1024:.2f} KB)")
            
            # Inserir registro com BLOB
            print(f"   - Inserindo registro #{i} com BLOB...")
            
            # Preparar a declaração SQL com bind variable para o BLOB
            cursor.execute(f"""
                INSERT INTO {temp_table} (id, nome, dados, tamanho_bytes) 
                VALUES (:id, :nome, EMPTY_BLOB(), :tamanho) 
                RETURNING dados INTO :blob
            """, {
                'id': i,
                'nome': f'Teste BLOB {size} bytes',
                'tamanho': size,
                'blob': cursor.var(cx_Oracle.BLOB)
            })
            
            # Obter o LOB locator
            lob = cursor.getvalue('blob')
            
            # Escrever os dados binários no LOB
            lob.write(binary_data)
            
            # Commitar a transação
            connection.commit()
            
            print(f"   - Registro #{i} inserido com sucesso.")
        
        # Ler os BLOBs da tabela e verificar integridade
        print("\n3. Lendo e verificando os dados BLOB...")
        
        for i, size in enumerate(test_data_sizes, 1):
            cursor.execute(f"""
                SELECT dados, tamanho_bytes 
                FROM {temp_table} 
                WHERE id = :id
            """, {'id': i})
            
            lob, expected_size = cursor.fetchone()
            data = lob.read()
            
            print(f"   - Registro #{i}: Lido {len(data)} bytes, esperado {expected_size} bytes")
            
            # Verificar se o tamanho corresponde ao esperado
            if len(data) == expected_size:
                print("   - Verificação OK: Tamanho corresponde ao esperado")
            else:
                print(f"   - ERRO: Tamanho não corresponde! Esperado: {expected_size}, Lido: {len(data)}")
                raise Exception("Erro na verificação de tamanho do BLOB")
        
        # Executar UPDATE em um BLOB existente
        print("\n4. Atualizando um BLOB existente...")
        new_data = b"Dados de teste atualizados - " + os.urandom(512)
        
        cursor.execute(f"""
            UPDATE {temp_table}
            SET dados = EMPTY_BLOB(), tamanho_bytes = :novo_tamanho
            WHERE id = 1
            RETURNING dados INTO :blob
        """, {
            'novo_tamanho': len(new_data),
            'blob': cursor.var(cx_Oracle.BLOB)
        })
        
        lob = cursor.getvalue('blob')
        lob.write(new_data)
        connection.commit()
        
        # Verificar se o UPDATE funcionou
        cursor.execute(f"SELECT dados, tamanho_bytes FROM {temp_table} WHERE id = 1")
        lob, updated_size = cursor.fetchone()
        data = lob.read()
        
        print(f"   - Dados atualizados: {len(data)} bytes, tamanho registrado: {updated_size}")
        
        if len(data) == len(new_data) and updated_size == len(new_data):
            print("   - Atualização do BLOB bem-sucedida!")
        else:
            print(f"   - ERRO: Atualização do BLOB falhou! Esperado: {len(new_data)}, Lido: {len(data)}")
            raise Exception("Erro na atualização do BLOB")
        
        # Testar SELECT com funções DBMS_LOB
        print("\n5. Testando consultas com funções DBMS_LOB...")
        cursor.execute(f"""
            SELECT id, nome, DBMS_LOB.GETLENGTH(dados) as tamanho_lob, 
                   tamanho_bytes, data_criacao
            FROM {temp_table}
            ORDER BY DBMS_LOB.GETLENGTH(dados)
        """)
        
        print("   - Resultados ordenados por tamanho do BLOB:")
        results = cursor.fetchall()
        for row in results:
            print(f"   - ID: {row[0]}, Nome: {row[1]}, Tamanho LOB: {row[2]}, Tamanho Registrado: {row[3]}")
        
        # Limpar a tabela temporária
        print(f"\n6. Removendo tabela temporária {temp_table}...")
        cursor.execute(f"DROP TABLE {temp_table}")
        connection.commit()
        print(f"   - Tabela {temp_table} removida com sucesso.")
        
        cursor.close()
        connection.close()
        
        print("\nTeste de operações com BLOB concluído com sucesso!")
        return True
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Erro durante teste de BLOB: ORA-{error.code}: {error.message}")
        
        # Tentar limpar a tabela temporária
        try:
            if connection:
                cleanup_cursor = connection.cursor()
                cleanup_cursor.execute(f"DROP TABLE {temp_table}")
                connection.commit()
                cleanup_cursor.close()
                print(f"Tabela temporária {temp_table} removida na limpeza de erro.")
        except:
            print(f"Não foi possível remover a tabela temporária {temp_table} após erro.")
        
        if connection:
            connection.close()
        return False
    except Exception as e:
        print(f"Erro durante teste de BLOB: {str(e)}")
        traceback.print_exc()
        
        # Tentar limpar a tabela temporária
        try:
            if connection:
                cleanup_cursor = connection.cursor()
                cleanup_cursor.execute(f"DROP TABLE {temp_table}")
                connection.commit()
                cleanup_cursor.close()
                print(f"Tabela temporária {temp_table} removida na limpeza de erro.")
        except:
            print(f"Não foi possível remover a tabela temporária {temp_table} após erro.")
        
        if connection:
            connection.close()
        return False


def test_performance(config, iterations=5):
    """
    Testa a performance do Oracle com diferentes tipos de consultas
    
    Args:
        config: Dicionário com configurações de conexão
        iterations: Número de iterações para cada teste
        
    Returns:
        tuple: (success, results) - Indicador de sucesso e resultados detalhados
    """
    print("\n=== Teste de Performance Oracle ===")
    
    connection, _ = get_oracle_connection(config)
    
    if not connection:
        return False, {}
    
    results = {
        "simple_query": [],
        "count_query": [],
        "join_query": [],
        "filter_query": [],
        "order_query": [],
        "plsql_call": []
    }
    
    try:
        cursor = connection.cursor()
        
        # Verificar se tabelas existem para teste
        cursor.execute("SELECT COUNT(*) FROM user_tables WHERE table_name = 'ALIMENTOS'")
        has_tables = cursor.fetchone()[0] > 0
        
        if not has_tables:
            print("Tabelas necessárias para teste de performance não encontradas.")
            return False, {}
        
        # Teste 1: Consulta simples
        print("\n1. Teste de consulta simples (SELECT * FROM DUAL):")
        for i in range(iterations):
            start = time.time()
            cursor.execute("SELECT * FROM DUAL")
            cursor.fetchall()
            elapsed = time.time() - start
            results["simple_query"].append(elapsed)
            print(f"   Iteração {i+1}: {elapsed:.6f} segundos")
        
        print(f"   Média: {statistics.mean(results['simple_query']):.6f} segundos")
        print(f"   Mediana: {statistics.median(results['simple_query']):.6f} segundos")
        
        # Teste 2: Contagem de registros
        print("\n2. Teste de contagem de registros (COUNT(*)):")
        for i in range(iterations):
            start = time.time()
            cursor.execute("SELECT COUNT(*) FROM ALIMENTOS")
            count = cursor.fetchone()[0]
            elapsed = time.time() - start
            results["count_query"].append(elapsed)
            print(f"   Iteração {i+1}: {elapsed:.6f} segundos (Registros: {count})")
        
        print(f"   Média: {statistics.mean(results['count_query']):.6f} segundos")
        print(f"   Mediana: {statistics.median(results['count_query']):.6f} segundos")
        
        # Teste 3: Consulta com JOIN
        print("\n3. Teste de consulta com JOIN:")
        for i in range(iterations):
            start = time.time()
            cursor.execute("""
            SELECT a.id, a.nome, c.nome as categoria
            FROM ALIMENTOS a
            JOIN CATEGORIAS c ON a.categoria_id = c.id
            """)
            rows = cursor.fetchall()
            elapsed = time.time() - start
            results["join_query"].append(elapsed)
            print(f"   Iteração {i+1}: {elapsed:.6f} segundos (Resultados: {len(rows)})")
        
        print(f"   Média: {statistics.mean(results['join_query']):.6f} segundos")
        print(f"   Mediana: {statistics.median(results['join_query']):.6f} segundos")
        
        # Teste 4: Consulta com filtro
        print("\n4. Teste de consulta com filtro (WHERE):")
        for i in range(iterations):
            start = time.time()
            cursor.execute("""
            SELECT a.id, a.nome, a.proteina, a.kcal
            FROM ALIMENTOS a
            WHERE a.proteina > 10 AND a.kcal < 300
            """)
            rows = cursor.fetchall()
            elapsed = time.time() - start
            results["filter_query"].append(elapsed)
            print(f"   Iteração {i+1}: {elapsed:.6f} segundos (Resultados: {len(rows)})")
        
        print(f"   Média: {statistics.mean(results['filter_query']):.6f} segundos")
        print(f"   Mediana: {statistics.median(results['filter_query']):.6f} segundos")
        
        # Teste 5: Consulta com ordenação
        print("\n5. Teste de consulta com ordenação (ORDER BY):")
        for i in range(iterations):
            start = time.time()
            cursor.execute("""
            SELECT a.id, a.nome, a.proteina, a.kcal
            FROM ALIMENTOS a
            ORDER BY a.proteina DESC, a.kcal ASC
            """)
            rows = cursor.fetchall()
            elapsed = time.time() - start
            results["order_query"].append(elapsed)
            print(f"   Iteração {i+1}: {elapsed:.6f} segundos (Resultados: {len(rows)})")
        
        print(f"   Média: {statistics.mean(results['order_query']):.6f} segundos")
        print(f"   Mediana: {statistics.median(results['order_query']):.6f} segundos")
        
        # Teste 6: Chamada de PL/SQL (se existir)
        print("\n6. Teste de execução de PL/SQL:")
        cursor.execute("""
        SELECT COUNT(*) FROM user_objects 
        WHERE object_type = 'PACKAGE' AND object_name = 'NUTRI_CALCULOS'
        """)
        has_package = cursor.fetchone()[0] > 0
        
        if has_package:
            for i in range(iterations):
                start = time.time()
                # Testar execução do pacote PL/SQL
                cursor.execute("""
                DECLARE
                    v_result nutri_calculos.resultado_nutricional;
                BEGIN
                    v_result := nutri_calculos.calcular_refeicao(1);
                END;
                """)
                elapsed = time.time() - start
                results["plsql_call"].append(elapsed)
                print(f"   Iteração {i+1}: {elapsed:.6f} segundos")
            
            print(f"   Média: {statistics.mean(results['plsql_call']):.6f} segundos")
            print(f"   Mediana: {statistics.median(results['plsql_call']):.6f} segundos")
        else:
            print("   Pacote PL/SQL 'NUTRI_CALCULOS' não encontrado, pulando teste.")
        
        # Teste 7: Consulta com paralelismo (se suportado)
        print("\n7. Teste de consulta com paralelismo:")
        try:
            # Verificar se o paralelismo é suportado
            cursor.execute("""
            SELECT COUNT(*) FROM v$parameter 
            WHERE name = 'parallel_max_servers' AND value > 0
            """)
            has_parallel = cursor.fetchone()[0] > 0
            
            if has_parallel:
                print("   Paralelismo suportado. Executando consulta paralela...")
                
                start = time.time()
                cursor.execute("""
                SELECT /*+ PARALLEL(a, 2) */ 
                    COUNT(*), AVG(kcal), MAX(proteina), MIN(carboidratos)
                FROM ALIMENTOS a
                """)
                result = cursor.fetchone()
                elapsed = time.time() - start
                
                print(f"   Consulta paralela executada em {elapsed:.6f} segundos")
                print(f"   Resultado: Count={result[0]}, Avg Kcal={result[1]}, Max Prot={result[2]}, Min Carb={result[3]}")
            else:
                print("   Paralelismo não suportado ou não configurado nesta instância Oracle.")
        except cx_Oracle.DatabaseError as e:
            print(f"   Erro ao testar paralelismo: {str(e)}")
            print("   Pulando teste de paralelismo.")
        
        # Resumo dos resultados
        print("\n=== Resumo dos Testes de Performance ===")
        
        # Criar tabela com os resultados
        summary_data = []
        for test_name, times in results.items():
            if times:
                summary_data.append([
                    test_name.replace("_", " ").title(), 
                    f"{statistics.mean(times):.6f}",
                    f"{statistics.median(times):.6f}",
                    f"{min(times):.6f}",
                    f"{max(times):.6f}"
                ])
        
        if HAS_TABULATE:
            headers = ["Teste", "Média (s)", "Mediana (s)", "Mínimo (s)", "Máximo (s)"]
            print(tabulate.tabulate(summary_data, headers=headers, tablefmt="grid"))
        else:
            print("Teste\t\tMédia (s)\tMediana (s)\tMínimo (s)\tMáximo (s)")
            for row in summary_data:
                print("\t".join(row))
        
        # Gerar gráfico se matplotlib estiver disponível
        if HAS_MATPLOTLIB:
            try:
                test_names = [name.replace("_", " ").title() for name in results.keys() if results[name]]
                means = [statistics.mean(times) for times in results.values() if times]
                
                plt.figure(figsize=(10, 6))
                bars = plt.bar(test_names, means)
                
                # Adicionar valores nas barras
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.6f}',
                            ha='center', va='bottom', rotation=0)
                
                plt.xlabel('Tipo de Consulta')
                plt.ylabel('Tempo Médio (segundos)')
                plt.title('Performance de Consultas Oracle')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                # Salvar gráfico
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_dir = Path(__file__).parent.parent / "logs"
                if not report_dir.exists():
                    report_dir.mkdir(parents=True)
                
                graph_file = report_dir / f"oracle_performance_{timestamp}.png"
                plt.savefig(graph_file)
                print(f"\nGráfico de performance salvo em: {graph_file}")
                
                # Fechar a figura para liberar memória
                plt.close()
            except Exception as e:
                print(f"Erro ao gerar gráfico: {str(e)}")
        
        cursor.close()
        connection.close()
        
        return True, results
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Erro durante teste de performance: ORA-{error.code}: {error.message}")
        if connection:
            connection.close()
        return False, results
    except Exception as e:
        print(f"Erro durante teste de performance: {str(e)}")
        traceback.print_exc()
        if connection:
            connection.close()
        return False, results

def test_pool_connections(config, pool_size=5, iterations=10):
    """Testa conexões simultâneas usando pool de conexões"""
    print(f"\n=== Teste de Pool de Conexões ({iterations} iterações) ===")

    try:
        # Configurar o pool de conexões
        dsn = cx_Oracle.makedsn(
            host=config['ORACLE_HOST'],
            port=config['ORACLE_PORT'],
            service_name=config['ORACLE_SERVICE']
        )

        # Iniciar o pool
        start_time = time.time()
        pool = cx_Oracle.SessionPool(
            user=config['ORACLE_USER'],
            password=config['ORACLE_PASSWORD'],
            dsn=dsn,
            min=2,
            max=pool_size,
            increment=1,
            threaded=True,
            getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT  # Esperar se todas as conexões estiverem em uso
        )
        pool_init_time = time.time() - start_time

        print(f"Pool de conexões inicializado em {pool_init_time:.3f} segundos")
        print(f"Tamanho do pool: min=2, max={pool_size}, increment=1")
        print(f"Conexões abertas inicialmente: {pool.opened}")

        # Testar aquisição e liberação de conexões sequenciais
        print(f"\nTestando {iterations} aquisições de conexão sequenciais...")
        sequential_times = []

        for i in range(iterations):
            start = time.time()
            connection = pool.acquire()
            acquire_time = time.time() - start

            # Executar consulta simples
            cursor = connection.cursor()
            cursor.execute("SELECT SYSDATE FROM DUAL")
            result = cursor.fetchone()[0]
            cursor.close()

            # Liberar conexão
            pool.release(connection)
            total_time = time.time() - start

            sequential_times.append(total_time)
            print(f"   Iteração {i+1}: Aquisição={acquire_time:.6f}s, Total={total_time:.6f}s")

        print(f"   Média de tempo total: {statistics.mean(sequential_times):.6f} segundos")
        print(f"   Mediana de tempo total: {statistics.median(sequential_times):.6f} segundos")

        # Testar carga com múltiplas conexões simultâneas
        print(f"\nTestando ocupação máxima do pool ({pool_size} conexões simultâneas)...")
        connections = []
        concurrent_times = []

        start = time.time()
        for i in range(pool_size):
            conn_start = time.time()
            conn = pool.acquire()
            conn_time = time.time() - conn_start
            connections.append(conn)
            concurrent_times.append(conn_time)
            print(f"   Conexão {i+1} adquirida em {conn_time:.6f}s (ocupadas={pool.busy}, disponíveis={pool.opened-pool.busy})")

        max_pool_time = time.time() - start
        print(f"Todas as {pool_size} conexões adquiridas em {max_pool_time:.3f} segundos")
        print(f"Tempo médio por conexão: {statistics.mean(concurrent_times):.6f} segundos")

        # Testar execução simultânea
        print(f"\nTestando execução simultânea em {pool_size} conexões...")

        def concurrent_query(thread_id):
            connection = connections[thread_id]
            start_time = time.time()

            try:
                cursor = connection.cursor()

                # Executar múltiplas consultas
                for j in range(3):
                    cursor.execute("SELECT SYS_CONTEXT('USERENV', 'SESSION_USER'), SYSDATE FROM DUAL")
                    user, timestamp = cursor.fetchone()

                cursor.close()
                elapsed = time.time() - start_time
                return {"thread_id": thread_id, "elapsed": elapsed, "success": True, "user": user}
            except Exception as e:
                elapsed = time.time() - start_time
                return {"thread_id": thread_id, "elapsed": elapsed, "success": False, "error": str(e)}

        # Executar consultas simultâneas
        with concurrent.futures.ThreadPoolExecutor(max_workers=pool_size) as executor:
            concurrent_results = list(executor.map(concurrent_query, range(pool_size)))

        # Analisar resultados simultâneos
        concurrent_success = sum(1 for r in concurrent_results if r["success"])
        concurrent_times = [r["elapsed"] for r in concurrent_results]

        print(f"   Consultas simultâneas concluídas: {concurrent_success}/{pool_size}")
        print(f"   Tempo médio simultâneo: {statistics.mean(concurrent_times):.6f} segundos")
        print(f"   Tempo máximo simultâneo: {max(concurrent_times):.6f} segundos")

        if concurrent_success < pool_size:
            print("   Detalhes dos erros:")
            for r in concurrent_results:
                if not r["success"]:
                    print(f"   Thread {r['thread_id']}: {r['error']}")

        # Liberar conexões
        print("\nLiberando conexões...")
        for i, conn in enumerate(connections):
            pool.release(conn)
            print(f"   Conexão {i+1} liberada (ocupadas={pool.busy})")

        # Fechar o pool
        pool.close()
        print("Pool de conexões fechado.")

        # Resumo final
        print("\n=== Resumo do Teste de Pool ===")
        print(f"- Inicialização do pool: {pool_init_time:.3f}s")
        print(f"- Média sequencial: {statistics.mean(sequential_times):.6f}s")
        print(f"- Média simultânea: {statistics.mean(concurrent_times):.6f}s")
        print(f"- Sucesso simultâneo: {concurrent_success}/{pool_size}")

        return concurrent_success == pool_size

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Erro durante teste de pool de conexões: ORA-{error.code}: {error.message}")
        return False
    except Exception as e:
        print(f"Erro durante teste de pool de conexões: {str(e)}")
        traceback.print_exc()
        return False

def generate_report(config, all_tests_passed, test_results=None):
    """Gera um relatório com os resultados dos testes"""
    print("\n=== Gerando Relatório de Testes Oracle ===")
    
    # Criar diretório de logs se não existir
    logs_dir = Path(__file__).parent.parent / "logs"
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
    
    # Nome do arquivo de log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"oracle_test_{timestamp}.log"
    
    # Informações do sistema
    import platform
    
    # Criar relatório
    report = [
        "=" * 60,
        "RELATÓRIO COMPLETO DE TESTES ORACLE",
        "=" * 60,
        f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Sistema: {platform.system()} {platform.release()}",
        f"Python: {platform.python_version()}",
        f"cx_Oracle: {cx_Oracle.version if hasattr(cx_Oracle, 'version') else 'N/A'}",
        "",
        "=" * 60,
        "CONFIGURAÇÃO ORACLE",
        "=" * 60,
        f"Host: {config['ORACLE_HOST']}",
        f"Port: {config['ORACLE_PORT']}",
        f"Service: {config['ORACLE_SERVICE']}",
        f"User: {config['ORACLE_USER']}",
        "",
        "=" * 60,
        "RESULTADO DOS TESTES",
        "=" * 60,
        f"Status Geral: {'✅ SUCESSO' if all_tests_passed else '❌ FALHA'}",
        "",
        "Testes Executados:",
        "1. ✅ Teste de Conexão Oracle",
        "2. ✅ Teste de Consultas Básicas", 
        "3. ✅ Teste de Transações",
        "4. ✅ Teste de Operações BLOB",
        "5. ✅ Teste de Performance",
        "6. ✅ Teste de Pool de Conexões",
        "",
        "=" * 60,
        "DETALHES TÉCNICOS",
        "=" * 60,
    ]
    
    # Adicionar informações técnicas se disponíveis
    if test_results:
        report.extend([
            "Métricas de Performance:",
        ])
        for test_name, times in test_results.items():
            if times:
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                report.append(f"  {test_name.replace('_', ' ').title()}: Média={avg_time:.6f}s, Min={min_time:.6f}s, Max={max_time:.6f}s")
    
    report.extend([
        "",
        "=" * 60,
        "RECOMENDAÇÕES",
        "=" * 60,
    ])
    
    if all_tests_passed:
        report.extend([
            "✅ Ambiente Oracle configurado corretamente",
            "✅ Todas as funcionalidades críticas testadas com sucesso",
            "",
            "Próximos passos recomendados:",
            "1. Executar migração de dados SQLite → Oracle",
            "2. Configurar aplicação: USE_ORACLE_DB=true",
            "3. Testar aplicação completa com Oracle",
            "4. Monitorar performance em produção",
        ])
    else:
        report.extend([
            "⚠️  Alguns testes falharam - revisar configuração",
            "",
            "Ações recomendadas:",
            "1. Verificar credenciais de conexão Oracle",
            "2. Confirmar que Oracle Database está acessível",
            "3. Verificar privilégios do usuário",
            "4. Revisar configuração de rede/firewall",
        ])
    
    report.extend([
        "",
        "=" * 60,
        "FIM DO RELATÓRIO",
        "=" * 60
    ])
    
    # Salvar relatório
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print(f"📄 Relatório completo salvo em: {log_file}")
    
    return log_file

def main():
    parser = argparse.ArgumentParser(description='Testar conexão e performance do Oracle Database')
    parser.add_argument('--iterations', type=int, default=5, help='Número de iterações para testes de performance')
    parser.add_argument('--pool-size', type=int, default=5, help='Tamanho máximo do pool de conexões')
    parser.add_argument('--concurrency', type=int, default=10, help='Número de operações concorrentes para teste de pool')
    args = parser.parse_args()
    
    print("=== Teste Completo de Ambiente Oracle ===")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Iterações de performance: {args.iterations}")
    print(f"Tamanho do pool: {args.pool_size}")
    print(f"Operações concorrentes: {args.concurrency}")
    print("=" * 50)
    
    try:
        # Obter configurações
        config = get_config()
        
        # Executar todos os testes
        print("\n[1/6] Teste de Conexão Oracle...")
        connection_ok = test_connection(config)
        
        if not connection_ok:
            print("\n❌ FALHA: Teste de conexão falhou. Verifique suas configurações Oracle.")
            generate_report(config, False)
            return
        
        print("\n[2/6] Teste de Consultas Básicas...")
        queries_ok = test_basic_queries(config)
        
        print("\n[3/6] Teste de Transações...")
        transaction_ok = test_transaction(config)
        
        print("\n[4/6] Teste de Operações BLOB...")
        blob_ok = test_blob_operations(config)
        
        print("\n[5/6] Teste de Performance...")
        performance_ok, performance_results = test_performance(config, args.iterations)
        
        print("\n[6/6] Teste de Pool de Conexões...")
        pool_ok = test_pool_connections(config, args.pool_size, args.iterations)
        
        # Verificar resultado geral
        all_passed = connection_ok and queries_ok and transaction_ok and blob_ok and performance_ok and pool_ok
        
        # Mostrar resumo dos testes
        print("\n" + "=" * 50)
        print("RESUMO DOS TESTES REALIZADOS:")
        print("=" * 50)
        
        test_results = [
            ("Conexão Oracle", connection_ok),
            ("Consultas Básicas", queries_ok),
            ("Transações", transaction_ok),
            ("Operações BLOB", blob_ok),
            ("Performance", performance_ok),
            ("Pool de Conexões", pool_ok)
        ]
        
        if HAS_TABULATE:
            table_data = []
            for test_name, result in test_results:
                status = "✅ SUCESSO" if result else "❌ FALHA"
                table_data.append([test_name, status])
            
            print(tabulate.tabulate(table_data, headers=["Teste", "Resultado"], tablefmt="simple"))
        else:
            for test_name, result in test_results:
                status = "✅ SUCESSO" if result else "❌ FALHA"
                print(f"{test_name:20} : {status}")
        
        # Estatísticas de performance se disponível
        if performance_ok and performance_results:
            print("\n📊 ESTATÍSTICAS DE PERFORMANCE:")
            print("-" * 30)
            for test_name, times in performance_results.items():
                if times:
                    avg_time = statistics.mean(times)
                    print(f"   {test_name.replace('_', ' ').title()}: {avg_time:.6f}s")
        
        # Gerar relatório detalhado
        report_file = generate_report(config, all_passed, performance_results if performance_ok else None)
        
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 RESULTADO FINAL: TODOS OS TESTES FORAM APROVADOS!")
            print("✅ O ambiente Oracle está configurado corretamente.")
            print("✅ Todas as funcionalidades testadas estão funcionando.")
        else:
            failed_tests = [name for name, result in test_results if not result]
            print(f"⚠️  RESULTADO FINAL: {len(failed_tests)} TESTE(S) FALHARAM:")
            for test in failed_tests:
                print(f"   - {test}")
            print("\n🔧 Verifique os detalhes acima para diagnosticar os problemas.")
        
        print(f"\n📄 Relatório detalhado salvo em: {report_file}")
        
        # Próximos passos
        print("\n🚀 PRÓXIMOS PASSOS:")
        if all_passed:
            print("1. ✅ Execute o script de migração para transferir dados de SQLite para Oracle")
            print("2. ✅ Configure a aplicação para usar Oracle (USE_ORACLE_DB=true)")
            print("3. ✅ Teste a aplicação completa com o banco Oracle")
        else:
            print("1. 🔧 Corrija os problemas identificados nos testes que falharam")
            print("2. 🔄 Execute novamente os testes após as correções")
            print("3. ✅ Prossiga com a migração apenas após todos os testes passarem")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ ERRO durante execução dos testes: {str(e)}")
        traceback.print_exc()
        try:
            config = get_config()
            generate_report(config, False)
        except:
            print("Não foi possível gerar relatório de erro.")

if __name__ == "__main__":
    main()
