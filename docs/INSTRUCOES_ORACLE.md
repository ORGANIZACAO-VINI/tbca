# Instruções para Adaptação do Projeto Nutricional para Oracle Database

Este documento fornece diretrizes para adaptar o aplicativo web de nutrição TBCA para utilizar o Oracle Database como sistema de gerenciamento de banco de dados.

## 1. Considerações Iniciais

### Vantagens do Oracle Database para este projeto

- **Alta performance**: Ideal para lidar com grandes volumes de dados nutricionais e múltiplos acessos simultâneos
- **Segurança avançada**: Proteção robusta para dados pessoais de saúde dos usuários
- **Recursos analíticos**: Ferramentas integradas para análise de padrões alimentares e tendências
- **Escalabilidade**: Capacidade de crescer conforme a base de usuários aumenta
- **Recursos de particionamento**: Útil para organizar dados históricos de diários alimentares
- **Alta disponibilidade**: Recursos como Oracle RAC para garantir operação contínua

## 2. Requisitos Técnicos

### Software necessário

- **Oracle Database**: Versão Enterprise 19c ou superior (alternativa: Oracle Database XE para desenvolvimento)
- **Oracle Client**: Para conexão com o banco de dados
- **Oracle SQL Developer**: Ferramenta gráfica para desenvolvimento e administração
- **Python cx_Oracle**: Biblioteca para conectar Python ao Oracle Database
- **Oracle REST Data Services (ORDS)**: Para criar APIs RESTful sobre o banco Oracle

### Hardware recomendado

- **Servidor de banco de dados**: Mínimo de 16GB RAM, processador quad-core, 100GB SSD
- **Ambiente de desenvolvimento**: 8GB RAM, processador dual-core

## 3. Modificações na Arquitetura

### Estrutura do banco de dados

```sql
-- Exemplo de criação de tabelas no Oracle

-- Tabela de categorias
CREATE TABLE categorias (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR2(100) NOT NULL
);

-- Tabela de alimentos
CREATE TABLE alimentos (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR2(20) UNIQUE,
    nome VARCHAR2(200) NOT NULL,
    categoria_id NUMBER,
    kcal NUMBER(8,2),
    carboidratos NUMBER(8,2),
    proteina NUMBER(8,2),
    gordura NUMBER(8,2),
    fibras NUMBER(8,2),
    calcio NUMBER(8,2),
    ferro NUMBER(8,2),
    CONSTRAINT fk_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- Índices para melhorar performance
CREATE INDEX idx_alimentos_nome ON alimentos(UPPER(nome));
CREATE INDEX idx_alimentos_codigo ON alimentos(codigo);

-- Tabela de usuários
CREATE TABLE usuarios (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR2(50) UNIQUE NOT NULL,
    email VARCHAR2(100) UNIQUE NOT NULL,
    senha_hash VARCHAR2(64) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP,
    perfil VARCHAR2(20) DEFAULT 'regular'
);

-- Tabela de diário alimentar (particionada por mês)
CREATE TABLE diario_alimentar (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id NUMBER NOT NULL,
    data_registro DATE NOT NULL,
    hora_registro VARCHAR2(5) NOT NULL,
    tipo_refeicao VARCHAR2(20),
    descricao VARCHAR2(200),
    CONSTRAINT fk_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
PARTITION BY RANGE (data_registro) (
    PARTITION diario_2025_q3 VALUES LESS THAN (TO_DATE('2025-10-01', 'YYYY-MM-DD')),
    PARTITION diario_2025_q4 VALUES LESS THAN (TO_DATE('2026-01-01', 'YYYY-MM-DD')),
    PARTITION diario_max VALUES LESS THAN (MAXVALUE)
);

-- Tabela de itens do diário
CREATE TABLE itens_diario (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    diario_id NUMBER NOT NULL,
    alimento_id NUMBER NOT NULL,
    quantidade_g NUMBER(8,2) NOT NULL,
    CONSTRAINT fk_diario FOREIGN KEY (diario_id) REFERENCES diario_alimentar(id),
    CONSTRAINT fk_alimento FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
);
```

### Adaptações no backend

1. **Substituir SQLite por Oracle**:
   - Alterar conexões de banco de dados para usar cx_Oracle
   - Adaptar consultas SQL para sintaxe Oracle
   - Utilizar bind variables para queries parametrizadas

2. **Otimização de consultas**:
   - Implementar materialized views para relatórios comuns
   - Utilizar índices apropriados para consultas frequentes
   - Considerar o uso de particionamento para dados históricos

3. **PL/SQL para lógica complexa**:
   - Mover cálculos nutricionais complexos para stored procedures
   - Usar funções PL/SQL para validações de dados
   - Implementar triggers para manter histórico de alterações

## 4. Script de Importação de Dados Adaptado

```python
"""
Script para importar dados da TBCA (CSV) para Oracle Database
"""
import os
import pandas as pd
import cx_Oracle
from pathlib import Path

# Configurações Oracle
ORACLE_USER = "nutri_app"
ORACLE_PASSWORD = "sua_senha_segura"
ORACLE_DSN = "localhost:1521/XEPDB1"  # Formato: hostname:port/service_name

# Configurações de dados
DATA_DIR = Path("./dados")
CSV_FILE = DATA_DIR / "tbca_backup_20250909_122104.csv"  # Usar o backup mais recente

def conectar_oracle():
    """Estabelece conexão com o banco Oracle"""
    connection = cx_Oracle.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )
    return connection

def criar_estrutura_db():
    """Cria a estrutura inicial do banco de dados Oracle"""
    connection = conectar_oracle()
    cursor = connection.cursor()
    
    # Verificar se tabelas já existem
    cursor.execute("""
    SELECT COUNT(*) FROM user_tables WHERE table_name = 'CATEGORIAS'
    """)
    tabela_existe = cursor.fetchone()[0] > 0
    
    if not tabela_existe:
        # Criar tabela de categorias
        cursor.execute("""
        CREATE TABLE categorias (
            id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nome VARCHAR2(100) NOT NULL
        )
        """)
        
        # Criar tabela de alimentos
        cursor.execute("""
        CREATE TABLE alimentos (
            id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            codigo VARCHAR2(20) UNIQUE,
            nome VARCHAR2(200) NOT NULL,
            categoria_id NUMBER,
            kcal NUMBER(8,2),
            carboidratos NUMBER(8,2),
            proteina NUMBER(8,2),
            gordura NUMBER(8,2),
            fibras NUMBER(8,2),
            calcio NUMBER(8,2),
            ferro NUMBER(8,2),
            CONSTRAINT fk_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
        """)
        
        # Criar índices para pesquisa eficiente
        cursor.execute('CREATE INDEX idx_alimentos_nome ON alimentos(UPPER(nome))')
        cursor.execute('CREATE INDEX idx_alimentos_codigo ON alimentos(codigo)')
        
        print("Estrutura do banco de dados Oracle criada com sucesso")
    else:
        print("Estrutura do banco de dados já existe")
    
    connection.commit()
    connection.close()

def normalizar_dados(df):
    """Normaliza os dados para formato adequado ao banco de dados"""
    # Criar cópia para não modificar o original
    df_norm = df.copy()
    
    # Remover "Código:" do início e limpar espaços
    if 'codigo' in df_norm.columns:
        df_norm['codigo'] = df_norm['codigo'].str.replace('Código:', '').str.strip()
    
    # Converter vírgulas para pontos nos campos numéricos
    numeric_cols = ['kcal', 'carboidratos', 'proteina', 'gordura', 'fibras', 'calcio', 'ferro']
    for col in numeric_cols:
        if col in df_norm.columns:
            df_norm[col] = df_norm[col].astype(str).str.replace(',', '.').astype(float)
    
    return df_norm

def categorizar_alimentos(df):
    """
    Categoriza alimentos com base em padrões de nomes
    Retorna um DataFrame com uma coluna 'categoria_id' adicional
    """
    # Exemplo simplificado de categorização
    categorias = {
        1: ['arroz', 'feijão', 'grão', 'cereal'],
        2: ['carne', 'frango', 'peixe', 'boi'],
        3: ['leite', 'queijo', 'iogurte', 'lácteo'],
        4: ['fruta', 'maçã', 'banana', 'laranja'],
        5: ['legume', 'verdura', 'vegetal'],
        6: ['pão', 'bolo', 'biscoito', 'padaria'],
        7: ['óleo', 'azeite', 'gordura'],
        8: ['açúcar', 'doce', 'sobremesa'],
        9: ['bebida', 'suco', 'refrigerante'],
    }
    
    # Inicializar coluna de categoria
    df['categoria_id'] = 0  # 0 = não categorizado
    
    # Atribuir categorias com base em palavras-chave no nome
    for cat_id, keywords in categorias.items():
        for keyword in keywords:
            mask = df['alimento_pt'].str.lower().str.contains(keyword, na=False)
            df.loc[mask, 'categoria_id'] = cat_id
    
    return df

def importar_csv_para_oracle():
    """Importa dados do CSV para o banco Oracle"""
    # Verificar se o arquivo CSV existe
    if not CSV_FILE.exists():
        print(f"Arquivo CSV não encontrado: {CSV_FILE}")
        return False
    
    # Ler dados do CSV
    print(f"Lendo dados de {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE, sep=';')
    
    # Normalizar e categorizar dados
    print("Normalizando e categorizando dados...")
    df = normalizar_dados(df)
    df = categorizar_alimentos(df)
    
    # Conectar ao banco de dados
    connection = conectar_oracle()
    cursor = connection.cursor()
    
    # Inserir categorias
    print("Inserindo categorias...")
    categorias = {
        0: 'Não categorizado',
        1: 'Cereais e Leguminosas',
        2: 'Carnes e Ovos',
        3: 'Leites e Derivados',
        4: 'Frutas',
        5: 'Legumes e Verduras',
        6: 'Pães e Farináceos',
        7: 'Óleos e Gorduras',
        8: 'Açúcares e Doces',
        9: 'Bebidas',
    }
    
    for cat_id, nome in categorias.items():
        # Verificar se a categoria já existe
        cursor.execute("SELECT COUNT(*) FROM categorias WHERE id = :id", id=cat_id)
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO categorias (id, nome) VALUES (:id, :nome)",
                id=cat_id, nome=nome
            )
    
    # Inserir alimentos
    print("Inserindo alimentos no banco de dados...")
    # Usando o método executemany para inserção em lote
    alimentos_data = []
    for _, row in df.iterrows():
        alimentos_data.append((
            row['codigo'],
            row['alimento_pt'],
            int(row['categoria_id']),
            float(row['kcal']),
            float(row['carboidratos']),
            float(row['proteina']),
            float(row['gordura']),
            float(row['fibras']),
            float(row['calcio']),
            float(row['ferro'])
        ))
    
    # Limpar tabela existente
    cursor.execute("DELETE FROM alimentos")
    
    # Inserir novos dados
    cursor.executemany("""
        INSERT INTO alimentos 
        (codigo, nome, categoria_id, kcal, carboidratos, proteina, gordura, fibras, calcio, ferro)
        VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10)
    """, alimentos_data)
    
    # Commit e fechar conexão
    connection.commit()
    connection.close()
    
    print("Importação concluída para o Oracle Database!")
    return True

def main():
    """Função principal"""
    print("Iniciando importação de dados da TBCA para Oracle Database...")
    
    # Criar estrutura do banco de dados
    criar_estrutura_db()
    
    # Importar dados
    sucesso = importar_csv_para_oracle()
    
    if sucesso:
        print("Processo concluído com sucesso!")
        
        # Estatísticas básicas
        connection = conectar_oracle()
        cursor = connection.cursor()
        
        # Contar número de alimentos
        cursor.execute("SELECT COUNT(*) FROM alimentos")
        total_alimentos = cursor.fetchone()[0]
        
        # Contar por categoria
        cursor.execute("""
            SELECT c.nome, COUNT(a.id) 
            FROM alimentos a 
            JOIN categorias c ON a.categoria_id = c.id 
            GROUP BY c.nome
            ORDER BY COUNT(a.id) DESC
        """)
        categorias_count = cursor.fetchall()
        
        print(f"\nTotal de alimentos importados: {total_alimentos}")
        print("\nDistribuição por categorias:")
        for cat_nome, count in categorias_count:
            print(f"  - {cat_nome}: {count}")
        
        connection.close()
    else:
        print("Ocorreram erros durante a importação.")

if __name__ == "__main__":
    main()
```

## 5. Modificações no Backend FastAPI

### Exemplo de adaptação para Oracle:

```python
from fastapi import FastAPI, HTTPException, Depends
import cx_Oracle
from pydantic import BaseModel
from typing import List, Optional

# Configuração do Oracle
ORACLE_USER = "nutri_app"
ORACLE_PASSWORD = "sua_senha_segura"
ORACLE_DSN = "localhost:1521/XEPDB1"

# Função para obter conexão
def get_db():
    connection = cx_Oracle.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )
    try:
        yield connection
    finally:
        connection.close()

# Exemplo de endpoint adaptado para Oracle
@app.get("/alimentos", response_model=List[Alimento])
def listar_alimentos(
    skip: int = 0, 
    limit: int = 100,
    categoria_id: Optional[int] = None,
    termo_busca: Optional[str] = None,
    db = Depends(get_db)
):
    cursor = db.cursor()
    
    # Consulta base
    query = """
    SELECT a.id, a.codigo, a.nome, a.categoria_id, c.nome as categoria_nome,
           a.kcal, a.carboidratos, a.proteina, a.gordura, a.fibras, a.calcio, a.ferro
    FROM alimentos a
    JOIN categorias c ON a.categoria_id = c.id
    """
    
    # Parâmetros
    params = {}
    conditions = []
    
    if categoria_id is not None:
        conditions.append("a.categoria_id = :categoria_id")
        params["categoria_id"] = categoria_id
    
    if termo_busca:
        conditions.append("UPPER(a.nome) LIKE UPPER(:termo_busca)")
        params["termo_busca"] = f"%{termo_busca}%"
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    # Ordenação e paginação (Oracle específico)
    query += " ORDER BY a.nome OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY"
    params["skip"] = skip
    params["limit"] = limit
    
    # Executar consulta
    cursor.execute(query, params)
    
    # Mapear colunas para nomes
    columns = [col[0].lower() for col in cursor.description]
    
    # Converter resultados em dicionários
    result = []
    for row in cursor:
        result.append(dict(zip(columns, row)))
    
    return result
```

## 6. Considerações de Desempenho

### Otimizações específicas do Oracle

1. **Materialized Views**: Para consultas frequentes de agregação
   ```sql
   CREATE MATERIALIZED VIEW mv_nutrientes_por_categoria AS
   SELECT c.nome as categoria, 
          AVG(a.kcal) as media_kcal, 
          AVG(a.proteina) as media_proteina,
          AVG(a.carboidratos) as media_carboidratos,
          AVG(a.gordura) as media_gordura
   FROM alimentos a
   JOIN categorias c ON a.categoria_id = c.id
   GROUP BY c.nome;
   ```

2. **Particionamento**: Para dados de diário alimentar
   ```sql
   -- Exemplo já incluído na criação da tabela diario_alimentar
   ```

3. **Índices específicos**: Para otimizar consultas comuns
   ```sql
   -- Índice para buscas por nome com case-insensitive
   CREATE INDEX idx_alimentos_nome_upper ON alimentos(UPPER(nome));
   
   -- Índice para filtro de macronutrientes
   CREATE INDEX idx_alimentos_macro ON alimentos(proteina, carboidratos, gordura);
   ```

4. **Stored Procedures**: Para cálculos complexos
   ```sql
   CREATE OR REPLACE PROCEDURE calcular_nutricao_refeicao(
       p_usuario_id IN NUMBER,
       p_data IN DATE,
       p_resultado OUT SYS_REFCURSOR
   )
   AS
   BEGIN
       OPEN p_resultado FOR
       SELECT d.data_registro, d.tipo_refeicao,
              SUM(a.kcal * i.quantidade_g / 100) as total_kcal,
              SUM(a.proteina * i.quantidade_g / 100) as total_proteina,
              SUM(a.carboidratos * i.quantidade_g / 100) as total_carboidratos,
              SUM(a.gordura * i.quantidade_g / 100) as total_gordura,
              SUM(a.fibras * i.quantidade_g / 100) as total_fibras,
              SUM(a.calcio * i.quantidade_g / 100) as total_calcio,
              SUM(a.ferro * i.quantidade_g / 100) as total_ferro
       FROM diario_alimentar d
       JOIN itens_diario i ON d.id = i.diario_id
       JOIN alimentos a ON i.alimento_id = a.id
       WHERE d.usuario_id = p_usuario_id
       AND d.data_registro = p_data
       GROUP BY d.data_registro, d.tipo_refeicao;
   END;
   ```

## 7. Considerações de Segurança

### Práticas recomendadas para Oracle

1. **Usuários e Privilégios**:
   - Criar usuários específicos com privilégios mínimos necessários
   - Evitar uso do usuário SYS ou SYSTEM para a aplicação
   - Utilizar roles para gerenciar permissões

2. **Proteção de dados sensíveis**:
   - Implementar Oracle Advanced Security para criptografia de dados
   - Utilizar Virtual Private Database para controle de acesso por linha
   - Considerar Data Redaction para mascaramento de dados sensíveis

3. **Auditoria**:
   - Configurar Oracle Audit para monitorar atividades suspeitas
   - Habilitar auditoria para operações críticas (ex: mudanças em tabelas importantes)

4. **Conexões seguras**:
   - Configurar SSL/TLS para conexões com o banco de dados
   - Utilizar Oracle Wallet para gerenciamento de credenciais

## 8. Ambiente de Desenvolvimento

### Configuração local

1. **Oracle Database XE**:
   - Download: https://www.oracle.com/database/technologies/xe-downloads.html
   - Instalação mais leve para desenvolvimento

2. **Oracle SQL Developer**:
   - Para gerenciamento e desenvolvimento no banco de dados
   - Download: https://www.oracle.com/database/sqldeveloper/technologies/download/

3. **Python cx_Oracle**:
   - Instalação: `pip install cx_Oracle`
   - Também instalar Oracle Instant Client

4. **Oracle Instant Client**:
   - Necessário para cx_Oracle funcionar
   - Download: https://www.oracle.com/database/technologies/instant-client/downloads.html

### Ambiente de produção

1. **Oracle Cloud Infrastructure (OCI)**:
   - Utilizar Autonomous Database para menor custo de gerenciamento
   - Ou configurar Oracle Database em instâncias computacionais

2. **Oracle REST Data Services (ORDS)**:
   - Para expor endpoints REST diretamente do banco Oracle
   - Útil para operações simples sem necessidade de API intermediária

## 9. Processo de Implantação

### Pipeline de CI/CD adaptado para Oracle

1. **Versionamento de Esquema**:
   - Utilizar ferramentas como Flyway ou Liquibase para migração de esquema
   - Manter scripts SQL de migração no controle de versão

2. **Testes de Integração**:
   - Configurar banco Oracle de teste em container Docker
   - Executar testes automatizados contra este banco

3. **Implantação**:
   - Scripts para backup automático pré-implantação
   - Procedimentos de rollback em caso de falha
   - Validação pós-implantação

## 10. Recursos Adicionais

### Documentação e referências

- [Oracle Database Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/index.html)
- [Python cx_Oracle Documentation](https://cx-oracle.readthedocs.io/)
- [Oracle SQL Language Reference](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/index.html)
- [Oracle PL/SQL Language Reference](https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/index.html)
- [Oracle REST Data Services](https://www.oracle.com/database/technologies/appdev/rest.html)

### Ferramentas recomendadas

- **Toad for Oracle**: Ferramenta avançada para desenvolvimento Oracle
- **Oracle SQL Developer Data Modeler**: Para modelagem de dados
- **Oracle Enterprise Manager**: Para monitoramento e administração
- **SQLcl**: Interface de linha de comando para Oracle
