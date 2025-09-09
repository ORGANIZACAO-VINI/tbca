#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gerador de consultas PL/SQL e Stored Procedures para o projeto NutriApp Oracle
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

TEMPLATES = {
    'stored_procedure': """
CREATE OR REPLACE PROCEDURE {name}(
{parameters}
) AS
BEGIN
    {body}
    
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END {name};
/
""",
    
    'function': """
CREATE OR REPLACE FUNCTION {name}(
{parameters}
) RETURN {return_type} AS
{variables}
BEGIN
    {body}
    
    RETURN {return_var};
EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END {name};
/
""",
    
    'package_spec': """
CREATE OR REPLACE PACKAGE {name} AS
    {declarations}
END {name};
/
""",
    
    'package_body': """
CREATE OR REPLACE PACKAGE BODY {name} AS
    {implementations}
END {name};
/
""",
    
    'trigger': """
CREATE OR REPLACE TRIGGER {name}
{when} {event} ON {table}
{for_each}
{declaration}
BEGIN
    {body}
EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END;
/
""",
    
    'view': """
CREATE OR REPLACE VIEW {name} AS
{query}
/
""",
    
    'materialized_view': """
CREATE MATERIALIZED VIEW {name}
{refresh_clause}
AS
{query}
/
""",
    
    'index': """
CREATE INDEX {name} ON {table}({columns});
/
""",
    
    'sequence': """
CREATE SEQUENCE {name}
    START WITH {start}
    INCREMENT BY {increment}
    {options};
/
"""
}

# Templates para lógica nutricional
NUTRI_TEMPLATES = {
    'calc_macros': """
-- Função para calcular macronutrientes totais de uma refeição
CREATE OR REPLACE FUNCTION calcular_macronutrientes(p_diario_id IN NUMBER)
RETURN SYS_REFCURSOR AS
    v_result SYS_REFCURSOR;
BEGIN
    OPEN v_result FOR
        SELECT 
            SUM(a.kcal * i.quantidade_g / 100) as kcal_total,
            SUM(a.proteina * i.quantidade_g / 100) as proteina_total,
            SUM(a.carboidratos * i.quantidade_g / 100) as carboidratos_total,
            SUM(a.gordura * i.quantidade_g / 100) as gordura_total,
            SUM(a.fibras * i.quantidade_g / 100) as fibras_total
        FROM 
            itens_diario i
            JOIN alimentos a ON i.alimento_id = a.id
        WHERE 
            i.diario_id = p_diario_id;
    
    RETURN v_result;
END calcular_macronutrientes;
/
""",
    
    'recomendacao_diaria': """
-- Função para calcular recomendação diária baseada em perfil
CREATE OR REPLACE FUNCTION recomendacao_diaria(
    p_peso IN NUMBER,
    p_altura IN NUMBER,
    p_idade IN NUMBER,
    p_sexo IN VARCHAR2,
    p_nivel_atividade IN NUMBER,
    p_objetivo IN VARCHAR2
) RETURN SYS_REFCURSOR AS
    v_result SYS_REFCURSOR;
    v_tmb NUMBER;
    v_necessidade_calorica NUMBER;
    v_proteina NUMBER;
    v_gordura NUMBER;
    v_carboidrato NUMBER;
BEGIN
    -- Cálculo da Taxa Metabólica Basal (TMB) pela fórmula de Harris-Benedict
    IF UPPER(p_sexo) = 'M' THEN
        v_tmb := 88.362 + (13.397 * p_peso) + (4.799 * p_altura) - (5.677 * p_idade);
    ELSE
        v_tmb := 447.593 + (9.247 * p_peso) + (3.098 * p_altura) - (4.330 * p_idade);
    END IF;
    
    -- Cálculo da necessidade calórica diária
    v_necessidade_calorica := v_tmb * p_nivel_atividade;
    
    -- Ajuste baseado no objetivo
    IF UPPER(p_objetivo) = 'EMAGRECIMENTO' THEN
        v_necessidade_calorica := v_necessidade_calorica * 0.85;
        v_proteina := p_peso * 2.0;
        v_gordura := p_peso * 1.0;
    ELSIF UPPER(p_objetivo) = 'GANHO_MUSCULAR' THEN
        v_necessidade_calorica := v_necessidade_calorica * 1.1;
        v_proteina := p_peso * 2.2;
        v_gordura := p_peso * 1.0;
    ELSE
        -- Manutenção
        v_proteina := p_peso * 1.8;
        v_gordura := p_peso * 1.0;
    END IF;
    
    -- Cálculo de carboidratos com base nas calorias restantes
    v_carboidrato := (v_necessidade_calorica - (v_proteina * 4) - (v_gordura * 9)) / 4;
    
    -- Retornar recomendações
    OPEN v_result FOR
        SELECT 
            ROUND(v_necessidade_calorica) as calorias,
            ROUND(v_proteina) as proteina,
            ROUND(v_carboidrato) as carboidratos,
            ROUND(v_gordura) as gordura,
            ROUND(v_proteina * 4) as kcal_proteina,
            ROUND(v_carboidrato * 4) as kcal_carboidratos,
            ROUND(v_gordura * 9) as kcal_gordura,
            ROUND(v_proteina / p_peso, 1) as proteina_por_kg,
            ROUND(v_proteina * 100 / v_necessidade_calorica * 4, 1) as perc_proteina,
            ROUND(v_carboidrato * 100 / v_necessidade_calorica * 4, 1) as perc_carboidratos,
            ROUND(v_gordura * 100 / v_necessidade_calorica * 9, 1) as perc_gordura
        FROM DUAL;
    
    RETURN v_result;
END recomendacao_diaria;
/
""",
    
    'analise_nutricional': """
-- Função para análise nutricional completa
CREATE OR REPLACE FUNCTION analise_nutricional(p_usuario_id IN NUMBER, p_data IN DATE)
RETURN SYS_REFCURSOR AS
    v_result SYS_REFCURSOR;
BEGIN
    OPEN v_result FOR
        WITH refeicoes AS (
            SELECT 
                d.id as diario_id,
                d.tipo_refeicao,
                SUM(a.kcal * i.quantidade_g / 100) as kcal,
                SUM(a.proteina * i.quantidade_g / 100) as proteina,
                SUM(a.carboidratos * i.quantidade_g / 100) as carboidrato,
                SUM(a.gordura * i.quantidade_g / 100) as gordura,
                SUM(a.fibras * i.quantidade_g / 100) as fibra,
                SUM(a.calcio * i.quantidade_g / 100) as calcio,
                SUM(a.ferro * i.quantidade_g / 100) as ferro
            FROM 
                diario_alimentar d
                JOIN itens_diario i ON d.id = i.diario_id
                JOIN alimentos a ON i.alimento_id = a.id
            WHERE 
                d.usuario_id = p_usuario_id
                AND TRUNC(d.data_registro) = TRUNC(p_data)
            GROUP BY 
                d.id, d.tipo_refeicao
        ),
        totais AS (
            SELECT 
                SUM(kcal) as kcal_total,
                SUM(proteina) as proteina_total,
                SUM(carboidrato) as carboidrato_total,
                SUM(gordura) as gordura_total,
                SUM(fibra) as fibra_total,
                SUM(calcio) as calcio_total,
                SUM(ferro) as ferro_total,
                COUNT(DISTINCT diario_id) as qtd_refeicoes
            FROM 
                refeicoes
        )
        SELECT 
            r.diario_id,
            r.tipo_refeicao,
            r.kcal,
            r.proteina,
            r.carboidrato,
            r.gordura,
            r.fibra,
            r.calcio,
            r.ferro,
            ROUND(r.kcal * 100 / t.kcal_total, 1) as perc_kcal,
            ROUND(r.proteina * 100 / t.proteina_total, 1) as perc_proteina,
            ROUND(r.carboidrato * 100 / t.carboidrato_total, 1) as perc_carboidrato,
            ROUND(r.gordura * 100 / t.gordura_total, 1) as perc_gordura,
            t.kcal_total,
            t.proteina_total,
            t.carboidrato_total,
            t.gordura_total,
            t.fibra_total,
            t.calcio_total,
            t.ferro_total,
            t.qtd_refeicoes,
            ROUND(r.proteina * 4 * 100 / r.kcal, 1) as perc_kcal_proteina,
            ROUND(r.carboidrato * 4 * 100 / r.kcal, 1) as perc_kcal_carboidrato,
            ROUND(r.gordura * 9 * 100 / r.kcal, 1) as perc_kcal_gordura
        FROM 
            refeicoes r
            CROSS JOIN totais t
        ORDER BY 
            r.diario_id;
    
    RETURN v_result;
END analise_nutricional;
/
""",
    
    'alimentos_recomendados': """
-- Função para recomendar alimentos baseados em objetivo nutricional
CREATE OR REPLACE FUNCTION alimentos_recomendados(
    p_objetivo IN VARCHAR2,
    p_limite_kcal IN NUMBER DEFAULT NULL,
    p_min_proteina IN NUMBER DEFAULT NULL,
    p_categoria_id IN NUMBER DEFAULT NULL
) RETURN SYS_REFCURSOR AS
    v_result SYS_REFCURSOR;
BEGIN
    -- Base query
    IF UPPER(p_objetivo) = 'EMAGRECIMENTO' THEN
        OPEN v_result FOR
            SELECT 
                a.id, a.codigo, a.nome, 
                c.nome as categoria,
                a.kcal, a.proteina, a.carboidratos, a.gordura, a.fibras,
                ROUND(a.proteina / NULLIF(a.kcal, 0) * 100, 1) as indice_proteico,
                ROUND(a.fibras / NULLIF(a.kcal, 0) * 100, 1) as indice_fibras
            FROM 
                alimentos a
                JOIN categorias c ON a.categoria_id = c.id
            WHERE 
                (p_limite_kcal IS NULL OR a.kcal <= p_limite_kcal)
                AND (p_min_proteina IS NULL OR a.proteina >= p_min_proteina)
                AND (p_categoria_id IS NULL OR a.categoria_id = p_categoria_id)
                AND a.proteina > 0
            ORDER BY 
                indice_proteico DESC, indice_fibras DESC;
    ELSIF UPPER(p_objetivo) = 'GANHO_MUSCULAR' THEN
        OPEN v_result FOR
            SELECT 
                a.id, a.codigo, a.nome, 
                c.nome as categoria,
                a.kcal, a.proteina, a.carboidratos, a.gordura, a.fibras,
                ROUND(a.proteina, 1) as proteina_total,
                ROUND(a.proteina / NULLIF(a.kcal, 0) * 100, 1) as proteina_por_caloria,
                ROUND(a.proteina * 4 * 100 / NULLIF(a.kcal, 0), 1) as perc_kcal_proteina
            FROM 
                alimentos a
                JOIN categorias c ON a.categoria_id = c.id
            WHERE 
                (p_limite_kcal IS NULL OR a.kcal <= p_limite_kcal)
                AND (p_min_proteina IS NULL OR a.proteina >= p_min_proteina)
                AND (p_categoria_id IS NULL OR a.categoria_id = p_categoria_id)
                AND a.proteina >= 5
            ORDER BY 
                proteina_total DESC, proteina_por_caloria DESC;
    ELSE
        -- Equilibrado
        OPEN v_result FOR
            SELECT 
                a.id, a.codigo, a.nome, 
                c.nome as categoria,
                a.kcal, a.proteina, a.carboidratos, a.gordura, a.fibras,
                ROUND((a.proteina * 4 + a.carboidratos * 4 + a.gordura * 9) / NULLIF(a.kcal, 0) * 100, 1) as indice_balanceamento,
                CASE 
                    WHEN a.proteina * 4 >= 0.2 * a.kcal AND a.carboidratos * 4 >= 0.4 * a.kcal AND a.gordura * 9 >= 0.2 * a.kcal THEN 'BALANCEADO'
                    ELSE 'DESBALANCEADO'
                END as classificacao
            FROM 
                alimentos a
                JOIN categorias c ON a.categoria_id = c.id
            WHERE 
                (p_limite_kcal IS NULL OR a.kcal <= p_limite_kcal)
                AND (p_min_proteina IS NULL OR a.proteina >= p_min_proteina)
                AND (p_categoria_id IS NULL OR a.categoria_id = p_categoria_id)
            ORDER BY 
                indice_balanceamento DESC, a.fibras DESC;
    END IF;
    
    RETURN v_result;
END alimentos_recomendados;
/
"""
}

def save_script_to_file(script, filename, script_type):
    """Salva o script gerado em um arquivo"""
    scripts_dir = Path(__file__).parent.parent / "nutri-app" / "backend" / "data" / "scripts" / "oracle"
    
    if not scripts_dir.exists():
        scripts_dir.mkdir(parents=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if filename:
        file_path = scripts_dir / filename
    else:
        file_path = scripts_dir / f"{script_type}_{timestamp}.sql"
    
    with open(file_path, 'w') as f:
        f.write(f"-- Script de {script_type.upper()} gerado automaticamente\n")
        f.write(f"-- Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(script)
    
    return file_path

def generate_procedure():
    """Gera uma stored procedure básica para o projeto"""
    name = input("Nome da procedure: ")
    params = []
    
    print("Adicione parâmetros (deixe em branco para terminar):")
    while True:
        param = input("Parâmetro (nome tipo [IN/OUT/IN OUT]): ")
        if not param:
            break
        params.append(param)
    
    print("Digite o corpo da procedure:")
    body_lines = []
    while True:
        line = input("> ")
        if line == "END":
            break
        body_lines.append(line)
    
    parameters = ",\n    ".join(params)
    body = "\n    ".join(body_lines)
    
    script = TEMPLATES['stored_procedure'].format(
        name=name,
        parameters=parameters,
        body=body
    )
    
    filename = input("Nome do arquivo (ou vazio para automático): ")
    file_path = save_script_to_file(script, filename, "procedure")
    
    print(f"Procedure gerada e salva em: {file_path}")
    
    return script

def generate_function():
    """Gera uma função PL/SQL básica para o projeto"""
    name = input("Nome da função: ")
    params = []
    
    print("Adicione parâmetros (deixe em branco para terminar):")
    while True:
        param = input("Parâmetro (nome tipo [IN/OUT/IN OUT]): ")
        if not param:
            break
        params.append(param)
    
    return_type = input("Tipo de retorno: ")
    
    print("Declare variáveis (deixe em branco para terminar):")
    vars_lines = []
    while True:
        var = input("Variável (nome tipo [DEFAULT valor]): ")
        if not var:
            break
        vars_lines.append(var)
    
    print("Digite o corpo da função:")
    body_lines = []
    while True:
        line = input("> ")
        if line == "END":
            break
        body_lines.append(line)
    
    return_var = input("Variável/valor de retorno: ")
    
    parameters = ",\n    ".join(params)
    variables = "    " + ";\n    ".join(vars_lines) + ";" if vars_lines else ""
    body = "\n    ".join(body_lines)
    
    script = TEMPLATES['function'].format(
        name=name,
        parameters=parameters,
        return_type=return_type,
        variables=variables,
        body=body,
        return_var=return_var
    )
    
    filename = input("Nome do arquivo (ou vazio para automático): ")
    file_path = save_script_to_file(script, filename, "function")
    
    print(f"Função gerada e salva em: {file_path}")
    
    return script

def generate_nutritional_scripts():
    """Gera scripts nutricionais pré-definidos para o projeto"""
    print("Escolha o tipo de script nutricional:")
    print("1. Cálculo de macronutrientes")
    print("2. Recomendação diária baseada em perfil")
    print("3. Análise nutricional completa")
    print("4. Recomendação de alimentos baseada em objetivo")
    print("5. Todos os scripts nutricionais")
    
    choice = input("Opção (1-5): ")
    
    script = ""
    script_type = "nutricional"
    
    if choice == "1":
        script = NUTRI_TEMPLATES['calc_macros']
        script_type = "calculo_macros"
    elif choice == "2":
        script = NUTRI_TEMPLATES['recomendacao_diaria']
        script_type = "recomendacao_diaria"
    elif choice == "3":
        script = NUTRI_TEMPLATES['analise_nutricional']
        script_type = "analise_nutricional"
    elif choice == "4":
        script = NUTRI_TEMPLATES['alimentos_recomendados']
        script_type = "alimentos_recomendados"
    elif choice == "5":
        script = (
            NUTRI_TEMPLATES['calc_macros'] + "\n" +
            NUTRI_TEMPLATES['recomendacao_diaria'] + "\n" +
            NUTRI_TEMPLATES['analise_nutricional'] + "\n" +
            NUTRI_TEMPLATES['alimentos_recomendados']
        )
        script_type = "nutricional_completo"
    else:
        print("Opção inválida!")
        return None
    
    filename = input("Nome do arquivo (ou vazio para automático): ")
    file_path = save_script_to_file(script, filename, script_type)
    
    print(f"Script nutricional gerado e salvo em: {file_path}")
    
    return script

def generate_package():
    """Gera um package PL/SQL para o projeto"""
    name = input("Nome do package: ")
    
    print("Digite as declarações para a especificação do package:")
    spec_lines = []
    while True:
        line = input("SPEC> ")
        if line == "END":
            break
        spec_lines.append(line)
    
    print("Digite as implementações para o corpo do package:")
    body_lines = []
    while True:
        line = input("BODY> ")
        if line == "END":
            break
        body_lines.append(line)
    
    declarations = "\n    ".join(spec_lines)
    implementations = "\n    ".join(body_lines)
    
    spec_script = TEMPLATES['package_spec'].format(
        name=name,
        declarations=declarations
    )
    
    body_script = TEMPLATES['package_body'].format(
        name=name,
        implementations=implementations
    )
    
    script = spec_script + "\n" + body_script
    
    filename = input("Nome do arquivo (ou vazio para automático): ")
    file_path = save_script_to_file(script, filename, "package")
    
    print(f"Package gerado e salvo em: {file_path}")
    
    return script

def generate_trigger():
    """Gera um trigger PL/SQL para o projeto"""
    name = input("Nome do trigger: ")
    when = input("Quando (BEFORE/AFTER/INSTEAD OF): ")
    event = input("Evento (INSERT/UPDATE/DELETE/INSERT OR UPDATE OR DELETE): ")
    table = input("Tabela: ")
    for_each = input("Para cada (FOR EACH ROW/deixe em branco): ")
    
    print("Digite declarações (deixe em branco para terminar):")
    decl_lines = []
    while True:
        line = input("DECL> ")
        if not line:
            break
        decl_lines.append(line)
    
    print("Digite o corpo do trigger:")
    body_lines = []
    while True:
        line = input("BODY> ")
        if line == "END":
            break
        body_lines.append(line)
    
    declaration = "DECLARE\n    " + "\n    ".join(decl_lines) if decl_lines else ""
    body = "\n    ".join(body_lines)
    
    script = TEMPLATES['trigger'].format(
        name=name,
        when=when,
        event=event,
        table=table,
        for_each=for_each,
        declaration=declaration,
        body=body
    )
    
    filename = input("Nome do arquivo (ou vazio para automático): ")
    file_path = save_script_to_file(script, filename, "trigger")
    
    print(f"Trigger gerado e salvo em: {file_path}")
    
    return script

def generate_view():
    """Gera uma view SQL para o projeto"""
    name = input("Nome da view: ")
    
    print("Digite a consulta SQL para a view:")
    query_lines = []
    while True:
        line = input("SQL> ")
        if line == "END":
            break
        query_lines.append(line)
    
    query = "\n".join(query_lines)
    
    script = TEMPLATES['view'].format(
        name=name,
        query=query
    )
    
    filename = input("Nome do arquivo (ou vazio para automático): ")
    file_path = save_script_to_file(script, filename, "view")
    
    print(f"View gerada e salva em: {file_path}")
    
    return script

def generate_materialized_view():
    """Gera uma materialized view SQL para o projeto"""
    name = input("Nome da materialized view: ")
    
    refresh_type = input("Tipo de refresh (COMPLETE/FAST): ")
    refresh_time = input("Momento de refresh (ON DEMAND/ON COMMIT): ")
    refresh_clause = f"REFRESH {refresh_type} {refresh_time}"
    
    print("Digite a consulta SQL para a materialized view:")
    query_lines = []
    while True:
        line = input("SQL> ")
        if line == "END":
            break
        query_lines.append(line)
    
    query = "\n".join(query_lines)
    
    script = TEMPLATES['materialized_view'].format(
        name=name,
        refresh_clause=refresh_clause,
        query=query
    )
    
    filename = input("Nome do arquivo (ou vazio para automático): ")
    file_path = save_script_to_file(script, filename, "materialized_view")
    
    print(f"Materialized view gerada e salva em: {file_path}")
    
    return script

def generate_all_at_once():
    """Gera todos os scripts nutricionais em um único arquivo"""
    script = (
        "-- Scripts nutricionais completos para Oracle\n\n" +
        "-- Pacote de cálculos nutricionais\n" +
        """
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
    FUNCTION calcular_refeicao(p_diario_id IN NUMBER) 
    RETURN resultado_nutricional;
    
    -- Função para recomendação diária baseada em perfil
    FUNCTION recomendacao_diaria(
        p_peso IN NUMBER,
        p_altura IN NUMBER,
        p_idade IN NUMBER,
        p_sexo IN VARCHAR2,
        p_nivel_atividade IN NUMBER,
        p_objetivo IN VARCHAR2
    ) RETURN SYS_REFCURSOR;
    
    -- Função para análise nutricional completa
    FUNCTION analise_nutricional(p_usuario_id IN NUMBER, p_data IN DATE)
    RETURN SYS_REFCURSOR;
    
    -- Função para recomendar alimentos baseados em objetivo
    FUNCTION alimentos_recomendados(
        p_objetivo IN VARCHAR2,
        p_limite_kcal IN NUMBER DEFAULT NULL,
        p_min_proteina IN NUMBER DEFAULT NULL,
        p_categoria_id IN NUMBER DEFAULT NULL
    ) RETURN SYS_REFCURSOR;
END nutri_calculos;
/

CREATE OR REPLACE PACKAGE BODY nutri_calculos AS
    -- Função para calcular valores nutricionais de uma refeição
    FUNCTION calcular_refeicao(p_diario_id IN NUMBER) 
    RETURN resultado_nutricional IS
        v_resultado resultado_nutricional;
    BEGIN
        -- Inicializar resultado
        v_resultado.kcal := 0;
        v_resultado.proteina := 0;
        v_resultado.carboidratos := 0;
        v_resultado.gordura := 0;
        v_resultado.fibras := 0;
        
        -- Calcular totais
        SELECT 
            SUM(a.kcal * i.quantidade_g / 100),
            SUM(a.proteina * i.quantidade_g / 100),
            SUM(a.carboidratos * i.quantidade_g / 100),
            SUM(a.gordura * i.quantidade_g / 100),
            SUM(a.fibras * i.quantidade_g / 100)
        INTO 
            v_resultado.kcal,
            v_resultado.proteina,
            v_resultado.carboidratos,
            v_resultado.gordura,
            v_resultado.fibras
        FROM 
            itens_diario i
            JOIN alimentos a ON i.alimento_id = a.id
        WHERE 
            i.diario_id = p_diario_id;
            
        RETURN v_resultado;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RETURN v_resultado;
        WHEN OTHERS THEN
            RAISE;
    END calcular_refeicao;
    
    -- Função para recomendação diária baseada em perfil
    FUNCTION recomendacao_diaria(
        p_peso IN NUMBER,
        p_altura IN NUMBER,
        p_idade IN NUMBER,
        p_sexo IN VARCHAR2,
        p_nivel_atividade IN NUMBER,
        p_objetivo IN VARCHAR2
    ) RETURN SYS_REFCURSOR IS
        v_result SYS_REFCURSOR;
        v_tmb NUMBER;
        v_necessidade_calorica NUMBER;
        v_proteina NUMBER;
        v_gordura NUMBER;
        v_carboidrato NUMBER;
    BEGIN
        -- Cálculo da Taxa Metabólica Basal (TMB) pela fórmula de Harris-Benedict
        IF UPPER(p_sexo) = 'M' THEN
            v_tmb := 88.362 + (13.397 * p_peso) + (4.799 * p_altura) - (5.677 * p_idade);
        ELSE
            v_tmb := 447.593 + (9.247 * p_peso) + (3.098 * p_altura) - (4.330 * p_idade);
        END IF;
        
        -- Cálculo da necessidade calórica diária
        v_necessidade_calorica := v_tmb * p_nivel_atividade;
        
        -- Ajuste baseado no objetivo
        IF UPPER(p_objetivo) = 'EMAGRECIMENTO' THEN
            v_necessidade_calorica := v_necessidade_calorica * 0.85;
            v_proteina := p_peso * 2.0;
            v_gordura := p_peso * 1.0;
        ELSIF UPPER(p_objetivo) = 'GANHO_MUSCULAR' THEN
            v_necessidade_calorica := v_necessidade_calorica * 1.1;
            v_proteina := p_peso * 2.2;
            v_gordura := p_peso * 1.0;
        ELSE
            -- Manutenção
            v_proteina := p_peso * 1.8;
            v_gordura := p_peso * 1.0;
        END IF;
        
        -- Cálculo de carboidratos com base nas calorias restantes
        v_carboidrato := (v_necessidade_calorica - (v_proteina * 4) - (v_gordura * 9)) / 4;
        
        -- Retornar recomendações
        OPEN v_result FOR
            SELECT 
                ROUND(v_necessidade_calorica) as calorias,
                ROUND(v_proteina) as proteina,
                ROUND(v_carboidrato) as carboidratos,
                ROUND(v_gordura) as gordura,
                ROUND(v_proteina * 4) as kcal_proteina,
                ROUND(v_carboidrato * 4) as kcal_carboidratos,
                ROUND(v_gordura * 9) as kcal_gordura,
                ROUND(v_proteina / p_peso, 1) as proteina_por_kg,
                ROUND(v_proteina * 100 / v_necessidade_calorica * 4, 1) as perc_proteina,
                ROUND(v_carboidrato * 100 / v_necessidade_calorica * 4, 1) as perc_carboidratos,
                ROUND(v_gordura * 100 / v_necessidade_calorica * 9, 1) as perc_gordura
            FROM DUAL;
        
        RETURN v_result;
    END recomendacao_diaria;
    
    -- Função para análise nutricional completa
    FUNCTION analise_nutricional(p_usuario_id IN NUMBER, p_data IN DATE)
    RETURN SYS_REFCURSOR IS
        v_result SYS_REFCURSOR;
    BEGIN
        OPEN v_result FOR
            WITH refeicoes AS (
                SELECT 
                    d.id as diario_id,
                    d.tipo_refeicao,
                    SUM(a.kcal * i.quantidade_g / 100) as kcal,
                    SUM(a.proteina * i.quantidade_g / 100) as proteina,
                    SUM(a.carboidratos * i.quantidade_g / 100) as carboidrato,
                    SUM(a.gordura * i.quantidade_g / 100) as gordura,
                    SUM(a.fibras * i.quantidade_g / 100) as fibra,
                    SUM(a.calcio * i.quantidade_g / 100) as calcio,
                    SUM(a.ferro * i.quantidade_g / 100) as ferro
                FROM 
                    diario_alimentar d
                    JOIN itens_diario i ON d.id = i.diario_id
                    JOIN alimentos a ON i.alimento_id = a.id
                WHERE 
                    d.usuario_id = p_usuario_id
                    AND TRUNC(d.data_registro) = TRUNC(p_data)
                GROUP BY 
                    d.id, d.tipo_refeicao
            ),
            totais AS (
                SELECT 
                    SUM(kcal) as kcal_total,
                    SUM(proteina) as proteina_total,
                    SUM(carboidrato) as carboidrato_total,
                    SUM(gordura) as gordura_total,
                    SUM(fibra) as fibra_total,
                    SUM(calcio) as calcio_total,
                    SUM(ferro) as ferro_total,
                    COUNT(DISTINCT diario_id) as qtd_refeicoes
                FROM 
                    refeicoes
            )
            SELECT 
                r.diario_id,
                r.tipo_refeicao,
                r.kcal,
                r.proteina,
                r.carboidrato,
                r.gordura,
                r.fibra,
                r.calcio,
                r.ferro,
                ROUND(r.kcal * 100 / t.kcal_total, 1) as perc_kcal,
                ROUND(r.proteina * 100 / t.proteina_total, 1) as perc_proteina,
                ROUND(r.carboidrato * 100 / t.carboidrato_total, 1) as perc_carboidrato,
                ROUND(r.gordura * 100 / t.gordura_total, 1) as perc_gordura,
                t.kcal_total,
                t.proteina_total,
                t.carboidrato_total,
                t.gordura_total,
                t.fibra_total,
                t.calcio_total,
                t.ferro_total,
                t.qtd_refeicoes,
                ROUND(r.proteina * 4 * 100 / r.kcal, 1) as perc_kcal_proteina,
                ROUND(r.carboidrato * 4 * 100 / r.kcal, 1) as perc_kcal_carboidrato,
                ROUND(r.gordura * 9 * 100 / r.kcal, 1) as perc_kcal_gordura
            FROM 
                refeicoes r
                CROSS JOIN totais t
            ORDER BY 
                r.diario_id;
        
        RETURN v_result;
    END analise_nutricional;
    
    -- Função para recomendar alimentos baseados em objetivo
    FUNCTION alimentos_recomendados(
        p_objetivo IN VARCHAR2,
        p_limite_kcal IN NUMBER DEFAULT NULL,
        p_min_proteina IN NUMBER DEFAULT NULL,
        p_categoria_id IN NUMBER DEFAULT NULL
    ) RETURN SYS_REFCURSOR IS
        v_result SYS_REFCURSOR;
    BEGIN
        -- Base query
        IF UPPER(p_objetivo) = 'EMAGRECIMENTO' THEN
            OPEN v_result FOR
                SELECT 
                    a.id, a.codigo, a.nome, 
                    c.nome as categoria,
                    a.kcal, a.proteina, a.carboidratos, a.gordura, a.fibras,
                    ROUND(a.proteina / NULLIF(a.kcal, 0) * 100, 1) as indice_proteico,
                    ROUND(a.fibras / NULLIF(a.kcal, 0) * 100, 1) as indice_fibras
                FROM 
                    alimentos a
                    JOIN categorias c ON a.categoria_id = c.id
                WHERE 
                    (p_limite_kcal IS NULL OR a.kcal <= p_limite_kcal)
                    AND (p_min_proteina IS NULL OR a.proteina >= p_min_proteina)
                    AND (p_categoria_id IS NULL OR a.categoria_id = p_categoria_id)
                    AND a.proteina > 0
                ORDER BY 
                    indice_proteico DESC, indice_fibras DESC;
        ELSIF UPPER(p_objetivo) = 'GANHO_MUSCULAR' THEN
            OPEN v_result FOR
                SELECT 
                    a.id, a.codigo, a.nome, 
                    c.nome as categoria,
                    a.kcal, a.proteina, a.carboidratos, a.gordura, a.fibras,
                    ROUND(a.proteina, 1) as proteina_total,
                    ROUND(a.proteina / NULLIF(a.kcal, 0) * 100, 1) as proteina_por_caloria,
                    ROUND(a.proteina * 4 * 100 / NULLIF(a.kcal, 0), 1) as perc_kcal_proteina
                FROM 
                    alimentos a
                    JOIN categorias c ON a.categoria_id = c.id
                WHERE 
                    (p_limite_kcal IS NULL OR a.kcal <= p_limite_kcal)
                    AND (p_min_proteina IS NULL OR a.proteina >= p_min_proteina)
                    AND (p_categoria_id IS NULL OR a.categoria_id = p_categoria_id)
                    AND a.proteina >= 5
                ORDER BY 
                    proteina_total DESC, proteina_por_caloria DESC;
        ELSE
            -- Equilibrado
            OPEN v_result FOR
                SELECT 
                    a.id, a.codigo, a.nome, 
                    c.nome as categoria,
                    a.kcal, a.proteina, a.carboidratos, a.gordura, a.fibras,
                    ROUND((a.proteina * 4 + a.carboidratos * 4 + a.gordura * 9) / NULLIF(a.kcal, 0) * 100, 1) as indice_balanceamento,
                    CASE 
                        WHEN a.proteina * 4 >= 0.2 * a.kcal AND a.carboidratos * 4 >= 0.4 * a.kcal AND a.gordura * 9 >= 0.2 * a.kcal THEN 'BALANCEADO'
                        ELSE 'DESBALANCEADO'
                    END as classificacao
                FROM 
                    alimentos a
                    JOIN categorias c ON a.categoria_id = c.id
                WHERE 
                    (p_limite_kcal IS NULL OR a.kcal <= p_limite_kcal)
                    AND (p_min_proteina IS NULL OR a.proteina >= p_min_proteina)
                    AND (p_categoria_id IS NULL OR a.categoria_id = p_categoria_id)
                ORDER BY 
                    indice_balanceamento DESC, a.fibras DESC;
        END IF;
        
        RETURN v_result;
    END alimentos_recomendados;
END nutri_calculos;
/

-- Criação de views para análise nutricional

-- View para médias nutricionais por categoria
CREATE OR REPLACE VIEW vw_media_nutricional_categoria AS
SELECT 
    c.id as categoria_id,
    c.nome as categoria,
    COUNT(a.id) as qtd_alimentos,
    ROUND(AVG(a.kcal), 1) as kcal_media,
    ROUND(AVG(a.proteina), 1) as proteina_media,
    ROUND(AVG(a.carboidratos), 1) as carboidrato_media,
    ROUND(AVG(a.gordura), 1) as gordura_media,
    ROUND(AVG(a.fibras), 1) as fibra_media,
    ROUND(AVG(a.calcio), 1) as calcio_media,
    ROUND(AVG(a.ferro), 1) as ferro_media,
    ROUND(AVG(a.proteina * 4 * 100 / NULLIF(a.kcal, 0)), 1) as perc_kcal_proteina,
    ROUND(AVG(a.carboidratos * 4 * 100 / NULLIF(a.kcal, 0)), 1) as perc_kcal_carboidrato,
    ROUND(AVG(a.gordura * 9 * 100 / NULLIF(a.kcal, 0)), 1) as perc_kcal_gordura
FROM 
    categorias c
    JOIN alimentos a ON c.id = a.categoria_id
GROUP BY 
    c.id, c.nome
ORDER BY 
    c.nome;
/

-- View materializada para ranking de alimentos por macronutrientes
CREATE MATERIALIZED VIEW mv_ranking_alimentos
REFRESH COMPLETE ON DEMAND
START WITH SYSDATE NEXT SYSDATE + 1
AS
SELECT 
    a.id, a.nome, c.nome as categoria,
    a.kcal, a.proteina, a.carboidratos, a.gordura, a.fibras,
    
    -- Ranking por proteína
    RANK() OVER (ORDER BY a.proteina DESC) as rank_proteina,
    
    -- Ranking por proteína por caloria
    RANK() OVER (ORDER BY (a.proteina / NULLIF(a.kcal, 0)) DESC) as rank_proteina_por_kcal,
    
    -- Ranking por carboidratos
    RANK() OVER (ORDER BY a.carboidratos DESC) as rank_carboidratos,
    
    -- Ranking por fibras
    RANK() OVER (ORDER BY a.fibras DESC) as rank_fibras,
    
    -- Ranking por fibras por caloria
    RANK() OVER (ORDER BY (a.fibras / NULLIF(a.kcal, 0)) DESC) as rank_fibras_por_kcal,
    
    -- Ranking por baixo índice glicêmico (menos carboidratos por caloria)
    RANK() OVER (ORDER BY (a.carboidratos / NULLIF(a.kcal, 0)) ASC) as rank_baixo_carb,
    
    -- Ranking por baixa gordura
    RANK() OVER (ORDER BY a.gordura ASC) as rank_baixa_gordura,
    
    -- Cálculos para análise
    ROUND(a.proteina / NULLIF(a.kcal, 0) * 100, 1) as proteina_por_kcal,
    ROUND(a.fibras / NULLIF(a.kcal, 0) * 100, 1) as fibras_por_kcal,
    ROUND(a.proteina * 4 * 100 / NULLIF(a.kcal, 0), 1) as perc_kcal_proteina,
    ROUND(a.carboidratos * 4 * 100 / NULLIF(a.kcal, 0), 1) as perc_kcal_carboidrato,
    ROUND(a.gordura * 9 * 100 / NULLIF(a.kcal, 0), 1) as perc_kcal_gordura
FROM 
    alimentos a
    JOIN categorias c ON a.categoria_id = c.id
WHERE 
    a.kcal > 0;
/

-- Trigger para auditoria de alterações nos alimentos
CREATE OR REPLACE TRIGGER trg_audit_alimentos
AFTER INSERT OR UPDATE OR DELETE ON alimentos
FOR EACH ROW
DECLARE
    v_operacao VARCHAR2(10);
    v_dados_antigos CLOB;
    v_dados_novos CLOB;
    v_usuario VARCHAR2(50);
BEGIN
    -- Determinar operação
    IF INSERTING THEN
        v_operacao := 'INSERT';
    ELSIF UPDATING THEN
        v_operacao := 'UPDATE';
    ELSIF DELETING THEN
        v_operacao := 'DELETE';
    END IF;
    
    -- Obter usuário do banco (ou de contexto da aplicação se disponível)
    SELECT USER INTO v_usuario FROM DUAL;
    
    -- Formatar dados antigos (para UPDATE e DELETE)
    IF UPDATING OR DELETING THEN
        v_dados_antigos := 
            'ID: ' || :OLD.id || ', ' ||
            'NOME: ' || :OLD.nome || ', ' ||
            'KCAL: ' || :OLD.kcal || ', ' ||
            'PROTEINA: ' || :OLD.proteina || ', ' ||
            'CARBOIDRATOS: ' || :OLD.carboidratos || ', ' ||
            'GORDURA: ' || :OLD.gordura;
    END IF;
    
    -- Formatar novos dados (para INSERT e UPDATE)
    IF INSERTING OR UPDATING THEN
        v_dados_novos := 
            'ID: ' || :NEW.id || ', ' ||
            'NOME: ' || :NEW.nome || ', ' ||
            'KCAL: ' || :NEW.kcal || ', ' ||
            'PROTEINA: ' || :NEW.proteina || ', ' ||
            'CARBOIDRATOS: ' || :NEW.carboidratos || ', ' ||
            'GORDURA: ' || :NEW.gordura;
    END IF;
    
    -- Inserir registro de log
    INSERT INTO log_auditoria (tabela, operacao, usuario, dados_antigos, dados_novos)
    VALUES ('ALIMENTOS', v_operacao, v_usuario, v_dados_antigos, v_dados_novos);
END;
/
"""
    )
    
    file_path = save_script_to_file(script, "oracle_nutritional_complete.sql", "nutricional_completo")
    
    print(f"Todos os scripts nutricionais gerados e salvos em: {file_path}")
    
    return script

def main():
    parser = argparse.ArgumentParser(description='Gerador de scripts PL/SQL para Oracle')
    parser.add_argument('--type', choices=['procedure', 'function', 'nutritional', 'package', 
                                           'trigger', 'view', 'materialized_view', 'all'],
                        help='Tipo de script a ser gerado')
    args = parser.parse_args()
    
    print("=== Gerador de Scripts PL/SQL Oracle para NutriApp ===")
    
    if args.type:
        script_type = args.type
    else:
        print("Escolha o tipo de script a ser gerado:")
        print("1. Stored Procedure")
        print("2. Function")
        print("3. Scripts Nutricionais")
        print("4. Package")
        print("5. Trigger")
        print("6. View")
        print("7. Materialized View")
        print("8. Todos os scripts nutricionais")
        choice = input("Opção (1-8): ")
        
        type_map = {
            "1": "procedure",
            "2": "function",
            "3": "nutritional",
            "4": "package",
            "5": "trigger",
            "6": "view",
            "7": "materialized_view",
            "8": "all"
        }
        
        script_type = type_map.get(choice, "nutritional")
    
    try:
        if script_type == "procedure":
            generate_procedure()
        elif script_type == "function":
            generate_function()
        elif script_type == "nutritional":
            generate_nutritional_scripts()
        elif script_type == "package":
            generate_package()
        elif script_type == "trigger":
            generate_trigger()
        elif script_type == "view":
            generate_view()
        elif script_type == "materialized_view":
            generate_materialized_view()
        elif script_type == "all":
            generate_all_at_once()
        else:
            print("Tipo de script não reconhecido.")
            
    except Exception as e:
        print(f"Erro durante a geração do script: {str(e)}")

if __name__ == "__main__":
    main()
