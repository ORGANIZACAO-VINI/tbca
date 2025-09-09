"""
Script para inserir dados de exemplo no banco de dados
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path para poder importar os módulos
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.models.database import SessionLocal, init_db
from app.models.models import Grupo, Alimento, Nutriente, Porcao

def inserir_dados_exemplo():
    """
    Insere dados de exemplo no banco de dados para teste
    """
    # Inicializar banco de dados
    init_db()
    
    # Criar sessão
    db = SessionLocal()
    
    try:
        # Verificar se já há dados
        if db.query(Alimento).count() > 0:
            print("Banco de dados já contém alimentos, pulando inserção de dados de exemplo.")
            return
        
        print("Inserindo dados de exemplo no banco de dados...")
        
        # Obter grupos existentes
        grupos = {grupo.nome: grupo for grupo in db.query(Grupo).all()}
        
        # Dados de exemplo - alimentos
        alimentos_exemplo = [
            {
                "codigo": "C001",
                "nome": "Arroz, branco, cozido",
                "nome_cientifico": "Oryza sativa",
                "grupo_nome": "Cereais e Derivados",
                "kcal": 128.0,
                "carboidratos": 28.1,
                "proteina": 2.5,
                "gordura": 0.2,
                "fibras": 1.6,
                "calcio": 4.0,
                "ferro": 0.3
            },
            {
                "codigo": "C002",
                "nome": "Feijão, carioca, cozido",
                "nome_cientifico": "Phaseolus vulgaris",
                "grupo_nome": "Leguminosas e Derivados",
                "kcal": 76.0,
                "carboidratos": 13.6,
                "proteina": 4.8,
                "gordura": 0.5,
                "fibras": 8.5,
                "calcio": 27.0,
                "ferro": 1.3
            },
            {
                "codigo": "F001",
                "nome": "Banana, nanica, crua",
                "nome_cientifico": "Musa acuminata",
                "grupo_nome": "Frutas e Derivados",
                "kcal": 92.0,
                "carboidratos": 23.8,
                "proteina": 1.3,
                "gordura": 0.1,
                "fibras": 2.0,
                "calcio": 5.0,
                "ferro": 0.3
            },
            {
                "codigo": "V001",
                "nome": "Alface, crespa, crua",
                "nome_cientifico": "Lactuca sativa",
                "grupo_nome": "Verduras, Hortaliças e Derivados",
                "kcal": 14.0,
                "carboidratos": 2.4,
                "proteina": 1.3,
                "gordura": 0.2,
                "fibras": 2.3,
                "calcio": 38.0,
                "ferro": 0.4
            },
            {
                "codigo": "C003",
                "nome": "Batata, inglesa, cozida",
                "nome_cientifico": "Solanum tuberosum",
                "grupo_nome": "Verduras, Hortaliças e Derivados",
                "kcal": 52.0,
                "carboidratos": 11.9,
                "proteina": 1.2,
                "gordura": 0.1,
                "fibras": 1.0,
                "calcio": 4.0,
                "ferro": 0.2
            },
            {
                "codigo": "L001",
                "nome": "Leite, de vaca, integral",
                "nome_cientifico": "Bos taurus",
                "grupo_nome": "Leite e Derivados",
                "kcal": 61.0,
                "carboidratos": 4.7,
                "proteina": 3.2,
                "gordura": 3.3,
                "fibras": 0.0,
                "calcio": 123.0,
                "ferro": 0.1
            },
            {
                "codigo": "C004",
                "nome": "Carne, bovina, contra filé, grelhada",
                "nome_cientifico": "Bos taurus",
                "grupo_nome": "Carnes e Derivados",
                "kcal": 219.0,
                "carboidratos": 0.0,
                "proteina": 31.9,
                "gordura": 9.9,
                "fibras": 0.0,
                "calcio": 5.0,
                "ferro": 2.8
            },
            {
                "codigo": "O001",
                "nome": "Ovo, de galinha, inteiro, cozido",
                "nome_cientifico": "Gallus gallus domesticus",
                "grupo_nome": "Ovos e Derivados",
                "kcal": 146.0,
                "carboidratos": 1.2,
                "proteina": 13.3,
                "gordura": 9.5,
                "fibras": 0.0,
                "calcio": 50.0,
                "ferro": 1.9
            },
            {
                "codigo": "F002",
                "nome": "Maçã, fuji, com casca, crua",
                "nome_cientifico": "Malus domestica",
                "grupo_nome": "Frutas e Derivados",
                "kcal": 56.0,
                "carboidratos": 15.2,
                "proteina": 0.3,
                "gordura": 0.0,
                "fibras": 2.0,
                "calcio": 3.0,
                "ferro": 0.1
            },
            {
                "codigo": "G001",
                "nome": "Azeite, de oliva, extra virgem",
                "nome_cientifico": "Olea europaea",
                "grupo_nome": "Gorduras e Óleos",
                "kcal": 884.0,
                "carboidratos": 0.0,
                "proteina": 0.0,
                "gordura": 100.0,
                "fibras": 0.0,
                "calcio": 0.0,
                "ferro": 0.6
            }
        ]
        
        # Inserir alimentos
        for alimento_data in alimentos_exemplo:
            grupo_nome = alimento_data.pop("grupo_nome")
            grupo = grupos.get(grupo_nome)
            
            if not grupo:
                print(f"Grupo '{grupo_nome}' não encontrado, pulando alimento '{alimento_data['nome']}'.")
                continue
            
            alimento = Alimento(
                grupo_id=grupo.id,
                **alimento_data
            )
            db.add(alimento)
        
        # Commit para salvar as alterações
        db.commit()
        
        print("Dados de exemplo inseridos com sucesso!")
    
    except Exception as e:
        db.rollback()
        print(f"Erro ao inserir dados de exemplo: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    inserir_dados_exemplo()
