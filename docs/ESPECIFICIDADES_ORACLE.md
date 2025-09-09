# Especificidades do Projeto de Nutrição com Oracle Database

## Visão Geral

Este documento descreve as especificidades técnicas e funcionais do aplicativo web de nutrição TBCA adaptado para utilizar o Oracle Database como sistema de gerenciamento de banco de dados.

## 1. Arquitetura do Sistema

### 1.1 Componentes Principais

- **Banco de Dados Oracle**: Núcleo do sistema, armazenando todos os dados nutricionais e informações de usuários
- **Backend API**: Desenvolvido em FastAPI, comunica-se com o Oracle Database via cx_Oracle
- **Frontend Web**: Aplicação Next.js que consome a API e apresenta interface para o usuário
- **Serviços de Autenticação**: Utilizando Oracle Advanced Security para proteção de credenciais
- **Sistema de Caching**: Oracle Coherence para caching de consultas frequentes

### 1.2 Diagrama de Arquitetura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────────┐
│                 │     │                 │     │                         │
│  Cliente Web    │◄───►│  API FastAPI    │◄───►│  Oracle Database 19c    │
│  (Next.js)      │     │  (Python)       │     │                         │
│                 │     │                 │     │                         │
└─────────────────┘     └────────┬────────┘     └─────────────────────────┘
                                 │                          ▲
                                 │                          │
                                 ▼                          │
                        ┌─────────────────┐      ┌─────────────────────┐
                        │                 │      │                     │
                        │  Cache Layer    │      │  Stored Procedures  │
                        │  (Coherence)    │      │  (PL/SQL)           │
                        │                 │      │                     │
                        └─────────────────┘      └─────────────────────┘
```

## 2. Modelo de Dados Oracle-Específico

### 2.1 Tipos de Dados Otimizados

- Utilização de `VARCHAR2` para strings de tamanho variável
- `NUMBER` para valores numéricos com precisão específica
- `TIMESTAMP` para datas com informação de hora
- `CLOB` para armazenamento de textos longos (ex: descrições detalhadas de alimentos)
- `BLOB` para armazenamento de imagens de alimentos

### 2.2 Recursos Avançados do Oracle

- **Tabelas Particionadas**: Para histórico de diário alimentar (particionamento por data)
- **Índices de Função**: Para buscas case-insensitive (ex: `UPPER(nome)`)
- **Materialized Views**: Para cálculos pré-computados de médias nutricionais
- **Virtual Columns**: Para cálculos automáticos (ex: proporção proteína/carboidrato)
- **Constraints Check**: Para validação de dados (ex: valores nutricionais não negativos)

### 2.3 Exemplo de Estrutura Estendida

```sql
-- Extensão da tabela de alimentos com informações nutricionais detalhadas
CREATE TABLE nutrientes_detalhados (
    alimento_id NUMBER PRIMARY KEY,
    sodio NUMBER(8,2),
    potassio NUMBER(8,2),
    magnesio NUMBER(8,2),
    fosforo NUMBER(8,2),
    zinco NUMBER(8,2),
    vitamina_a NUMBER(8,2),
    vitamina_c NUMBER(8,2),
    vitamina_d NUMBER(8,2),
    vitamina_e NUMBER(8,2),
    colesterol NUMBER(8,2),
    acucar NUMBER(8,2),
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alim_nutrientes FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
);

-- Tabela para informações de sazonalidade dos alimentos
CREATE TABLE sazonalidade_alimentos (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alimento_id NUMBER,
    mes NUMBER(2),
    disponibilidade VARCHAR2(20) CHECK (disponibilidade IN ('alta', 'média', 'baixa')),
    preco_medio NUMBER(6,2),
    CONSTRAINT fk_alim_sazon FOREIGN KEY (alimento_id) REFERENCES alimentos(id),
    CONSTRAINT uk_alim_mes UNIQUE (alimento_id, mes)
);

-- Tabela para bioativos e compostos funcionais
CREATE TABLE compostos_bioativos (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alimento_id NUMBER,
    composto VARCHAR2(100),
    quantidade NUMBER(10,4),
    unidade VARCHAR2(10),
    beneficio CLOB,
    CONSTRAINT fk_alim_bioativo FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
);
```

## 3. Recursos Oracle-Específicos Utilizados

### 3.1 PL/SQL para Lógica de Negócio

#### Exemplo: Cálculo de Macronutrientes para Plano Alimentar

```sql
CREATE OR REPLACE PACKAGE nutri_calculos AS
    -- Tipo para armazenar resultados de cálculos nutricionais
    TYPE resultado_nutricional IS RECORD (
        kcal NUMBER,
        proteina NUMBER,
        carboidratos NUMBER,
        gordura NUMBER,
        fibras NUMBER
    );
    
    -- Função para calcular valores nutricionais de uma refeição
    FUNCTION calcular_refeicao(p_itens IN SYS_REFCURSOR) 
    RETURN resultado_nutricional;
    
    -- Procedimento para gerar recomendações baseadas em perfil
    PROCEDURE gerar_recomendacoes(
        p_usuario_id IN NUMBER,
        p_objetivo IN VARCHAR2,
        p_resultado OUT SYS_REFCURSOR
    );
    
    -- Função para verificar adequação nutricional
    FUNCTION verificar_adequacao(
        p_usuario_id IN NUMBER,
        p_data IN DATE
    ) RETURN NUMBER;
END nutri_calculos;
```

### 3.2 Oracle Advanced Security

- Criptografia transparente de dados (TDE) para informações pessoais de saúde
- Mascaramento de dados para limitar exposição de informações sensíveis
- Auditoria de acesso para rastrear operações em dados críticos

### 3.3 Oracle Scheduler para Processos Automáticos

```sql
-- Exemplo: Job para atualizar estatísticas de uso
BEGIN
    DBMS_SCHEDULER.CREATE_JOB (
        job_name        => 'ATUALIZAR_ESTATISTICAS_USO',
        job_type        => 'STORED_PROCEDURE',
        job_action      => 'atualizar_estatisticas_uso',
        start_date      => SYSTIMESTAMP,
        repeat_interval => 'FREQ=DAILY; BYHOUR=3',
        enabled         => TRUE,
        comments        => 'Job diário para atualizar estatísticas de uso'
    );
END;
/

-- Exemplo: Job para gerar recomendações personalizadas
BEGIN
    DBMS_SCHEDULER.CREATE_JOB (
        job_name        => 'GERAR_RECOMENDACOES_SEMANAIS',
        job_type        => 'STORED_PROCEDURE',
        job_action      => 'gerar_recomendacoes_para_usuarios',
        start_date      => SYSTIMESTAMP,
        repeat_interval => 'FREQ=WEEKLY; BYDAY=MON; BYHOUR=5',
        enabled         => TRUE,
        comments        => 'Job semanal para gerar recomendações personalizadas'
    );
END;
/
```

## 4. Adaptações da API para Oracle

### 4.1 Conexão e Pool de Conexões

```python
import cx_Oracle
from fastapi import FastAPI, Depends
from functools import lru_cache

# Configuração do pool de conexões Oracle
@lru_cache()
def get_connection_pool():
    dsn = cx_Oracle.makedsn(
        host="hostname",
        port=1521,
        service_name="service_name"
    )
    pool = cx_Oracle.SessionPool(
        user="username",
        password="password",
        dsn=dsn,
        min=2,
        max=10,
        increment=1,
        threaded=True,
        encoding="UTF-8"
    )
    return pool

# Dependency para obter conexão do pool
def get_oracle_connection():
    pool = get_connection_pool()
    connection = pool.acquire()
    try:
        yield connection
    finally:
        pool.release(connection)
```

### 4.2 Adaptação de Queries para Oracle

```python
# Exemplo de endpoint adaptado para Oracle
@app.get("/alimentos/avancado")
def busca_avancada(
    min_proteina: float = None,
    max_kcal: float = None,
    categoria_id: int = None,
    ordenar_por: str = "nome",
    db = Depends(get_oracle_connection)
):
    cursor = db.cursor()
    
    # Base da query
    query = """
    SELECT a.id, a.codigo, a.nome, a.kcal, a.proteina, a.carboidratos, a.gordura
    FROM alimentos a
    WHERE 1=1
    """
    
    # Parâmetros da query
    params = {}
    
    # Adicionar condições conforme parâmetros
    if min_proteina is not None:
        query += " AND a.proteina >= :min_proteina"
        params["min_proteina"] = min_proteina
        
    if max_kcal is not None:
        query += " AND a.kcal <= :max_kcal"
        params["max_kcal"] = max_kcal
    
    if categoria_id is not None:
        query += " AND a.categoria_id = :categoria_id"
        params["categoria_id"] = categoria_id
    
    # Validar e aplicar ordenação
    valid_order_columns = ["nome", "kcal", "proteina", "carboidratos", "gordura"]
    order_col = ordenar_por if ordenar_por in valid_order_columns else "nome"
    query += f" ORDER BY a.{order_col}"
    
    # Executar query
    cursor.execute(query, params)
    
    # Processar resultados
    columns = [col[0].lower() for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return results
```

### 4.3 Usando Stored Procedures Oracle

```python
@app.get("/usuario/{usuario_id}/recomendacoes")
def obter_recomendacoes(
    usuario_id: int,
    objetivo: str = "emagrecimento",
    db = Depends(get_oracle_connection)
):
    cursor = db.cursor()
    
    # Criar cursor de saída para receber resultados
    output_cursor = db.cursor()
    
    # Chamar stored procedure
    cursor.callproc(
        "nutri_calculos.gerar_recomendacoes", 
        [usuario_id, objetivo, output_cursor]
    )
    
    # Processar resultados do cursor de saída
    columns = [col[0].lower() for col in output_cursor.description]
    recommendations = [dict(zip(columns, row)) for row in output_cursor]
    
    return recommendations
```

## 5. Estratégia de Implantação e Manutenção

### 5.1 Estratégia de Backup

- Backup RMAN diário completo
- Backups incrementais a cada 6 horas
- Archive log mode habilitado para recuperação point-in-time
- Retenção de backups por 30 dias

### 5.2 Monitoramento

- Oracle Enterprise Manager para monitoramento da saúde do banco
- Alertas configurados para:
  - Uso de tablespace acima de 85%
  - Falhas em jobs agendados
  - Tempos de resposta de queries acima do limite
  - Bloqueios de longa duração

### 5.3 Manutenção

- Janela de manutenção semanal para:
  - Aplicação de patches e atualizações
  - Reorganização de índices fragmentados
  - Atualização de estatísticas
  - Validação de integridade de dados

## 6. Requisitos de Infraestrutura

### 6.1 Ambiente de Desenvolvimento

- Oracle Database 19c XE (Express Edition)
- 16GB RAM, 4 vCPUs, 100GB SSD
- Oracle SQL Developer para desenvolvimento
- Oracle Instant Client 19c para conexões cx_Oracle

### 6.2 Ambiente de Produção

- Oracle Database 19c Enterprise Edition
- 32GB RAM, 8 vCPUs, 500GB SSD
- Oracle RAC (Real Application Clusters) para alta disponibilidade
- Oracle Data Guard para disaster recovery
- Oracle GoldenGate para replicação em tempo real (opcional)

## 7. Otimizações de Performance

### 7.1 Índices Especializados

```sql
-- Índice para busca por faixa de macronutrientes (muito utilizado na aplicação)
CREATE INDEX idx_alimentos_macros ON alimentos(proteina, carboidratos, gordura);

-- Índice de texto para busca por termos no nome
CREATE INDEX idx_alimentos_nome_text ON alimentos(nome)
INDEXTYPE IS CTXSYS.CONTEXT
PARAMETERS ('LEXER my_lexer');

-- Índice para busca por múltiplos nutrientes
CREATE BITMAP INDEX idx_alimentos_nutrientes ON alimentos(
    CASE WHEN proteina > 20 THEN 'ALTO_PROT' ELSE 'NORMAL' END,
    CASE WHEN fibras > 5 THEN 'ALTO_FIBRA' ELSE 'NORMAL' END,
    CASE WHEN gordura < 3 THEN 'BAIXO_GORD' ELSE 'NORMAL' END
);
```

### 7.2 Particionamento Avançado

```sql
-- Particionamento do histórico de consumo por mês e usuário (para grandes volumes)
CREATE TABLE historico_consumo (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id NUMBER NOT NULL,
    data_consumo DATE NOT NULL,
    alimento_id NUMBER NOT NULL,
    quantidade_g NUMBER(8,2),
    refeicao VARCHAR2(20),
    CONSTRAINT fk_hist_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    CONSTRAINT fk_hist_alimento FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
)
PARTITION BY RANGE (data_consumo)
SUBPARTITION BY HASH (usuario_id) SUBPARTITIONS 8 (
    PARTITION hist_2025_q3 VALUES LESS THAN (TO_DATE('2025-10-01', 'YYYY-MM-DD')),
    PARTITION hist_2025_q4 VALUES LESS THAN (TO_DATE('2026-01-01', 'YYYY-MM-DD')),
    PARTITION hist_2026_q1 VALUES LESS THAN (TO_DATE('2026-04-01', 'YYYY-MM-DD')),
    PARTITION hist_2026_q2 VALUES LESS THAN (TO_DATE('2026-07-01', 'YYYY-MM-DD')),
    PARTITION hist_future VALUES LESS THAN (MAXVALUE)
);
```

### 7.3 Materialized Views para Análises

```sql
-- Visão materializada para estatísticas de consumo
CREATE MATERIALIZED VIEW mv_estatisticas_consumo
REFRESH COMPLETE ON DEMAND
START WITH SYSDATE NEXT SYSDATE + 1
AS
SELECT 
    a.categoria_id,
    c.nome as categoria_nome,
    TRUNC(h.data_consumo, 'MM') as mes,
    COUNT(h.id) as total_consumos,
    AVG(h.quantidade_g) as quantidade_media,
    SUM(a.kcal * h.quantidade_g / 100) as total_kcal,
    SUM(a.proteina * h.quantidade_g / 100) as total_proteina
FROM historico_consumo h
JOIN alimentos a ON h.alimento_id = a.id
JOIN categorias c ON a.categoria_id = c.id
GROUP BY a.categoria_id, c.nome, TRUNC(h.data_consumo, 'MM');
```

## 8. Integrações Externas

### 8.1 Oracle REST Data Services (ORDS)

- Exposição direta de endpoints REST a partir do banco Oracle
- Autenticação OAuth2 para acesso seguro
- Limitação de taxa para prevenir abusos

### 8.2 Oracle APEX para Dashboard Administrativo

- Dashboard para administradores gerenciarem dados
- Relatórios interativos sobre uso do sistema
- Interface para manutenção de dados nutricionais

### 8.3 Oracle Machine Learning

- Modelos preditivos para recomendações personalizadas
- Análise de padrões de consumo
- Detecção de anomalias para identificar dados inconsistentes

## 9. Roadmap de Evolução

### Fase 1: Migração para Oracle
- Adaptação da estrutura de banco de dados
- Configuração do ambiente Oracle
- Migração de dados existentes
- Adaptação do backend para cx_Oracle

### Fase 2: Otimização Oracle-Específica
- Implementação de PL/SQL para lógica de negócio complexa
- Configuração de particionamento e índices avançados
- Implementação de materialized views
- Otimização de queries para Oracle

### Fase 3: Recursos Avançados
- Implementação de Oracle Advanced Security
- Configuração de alta disponibilidade com RAC
- Integração com Oracle Machine Learning
- Desenvolvimento de dashboard APEX

### Fase 4: Escalabilidade e Analytics
- Implementação de sharding para grandes volumes
- Integração com Oracle Analytics Cloud
- Implementação de data lake para análises avançadas
- Desenvolvimento de API pública para parceiros
