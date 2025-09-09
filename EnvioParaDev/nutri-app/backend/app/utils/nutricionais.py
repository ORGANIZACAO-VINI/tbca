"""
Utilitários para cálculos nutricionais
"""

def calcular_valores_nutricionais(alimentos, quantidades):
    """
    Calcula os valores nutricionais para uma combinação de alimentos e quantidades
    
    Args:
        alimentos (list): Lista de objetos Alimento
        quantidades (list): Lista de quantidades em gramas correspondentes aos alimentos
        
    Returns:
        dict: Dicionário com os valores nutricionais calculados
    """
    if len(alimentos) != len(quantidades):
        raise ValueError("O número de alimentos deve ser igual ao número de quantidades")
    
    # Inicializar dicionário para armazenar valores nutricionais
    valores_nutricionais = {}
    
    # Para cada alimento e sua quantidade
    for alimento, quantidade in zip(alimentos, quantidades):
        # Para cada nutriente do alimento
        for nutriente in alimento.nutrientes:
            nome = nutriente.nome
            unidade = nutriente.unidade
            
            # Calcular valor proporcional à quantidade
            valor = nutriente.valor_por_100g * (quantidade / 100)
            
            # Adicionar ao dicionário ou atualizar valor existente
            if nome not in valores_nutricionais:
                valores_nutricionais[nome] = {
                    "valor": valor,
                    "unidade": unidade
                }
            else:
                valores_nutricionais[nome]["valor"] += valor
    
    return valores_nutricionais
