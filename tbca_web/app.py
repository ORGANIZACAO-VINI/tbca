from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import json

app = Flask(__name__)

# Caminho para os arquivos de dados
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Lista de categorias disponíveis (baseadas nos arquivos CSV)
CATEGORIAS = []

# Função para carregar as categorias disponíveis baseadas nos arquivos existentes
def carregar_categorias():
    global CATEGORIAS
    if CATEGORIAS:
        return CATEGORIAS
        
    # Busca por arquivos de categorias
    arquivos = [f for f in os.listdir(DATA_DIR) if f.startswith('alimentos_') and f.endswith('.csv')]
    
    # Extrai nomes das categorias a partir dos nomes de arquivos
    for arquivo in arquivos:
        nome = arquivo.replace('alimentos_', '').replace('.csv', '')
        if nome not in ['3paginas', 'multipaginas', 'pagina1', 'pagina2', 'pagina3', 'tbca']:
            CATEGORIAS.append(nome)
    
    return CATEGORIAS

# Cache para armazenar os dados já carregados
dados_cache = {}

def carregar_dados(categoria=None):
    """
    Carrega os dados do arquivo JSON principal (tbca_dados_completos.json)
    """
    # Primeiro tenta carregar do cache
    cache_key = categoria if categoria else 'todos'
    if cache_key in dados_cache:
        return dados_cache[cache_key]
    
    # Carrega dados do arquivo JSON principal
    arquivo_json = os.path.join(DATA_DIR, 'tbca_dados_completos.json')
    
    if os.path.exists(arquivo_json):
        try:
            print(f"Carregando dados do arquivo JSON: {arquivo_json}")
            
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                dados_json = json.load(f)
            
            # Processa os dados JSON (é uma lista de alimentos)
            if isinstance(dados_json, list):
                alimentos_processados = []
                
                for alimento in dados_json:
                    # Extrai informações básicas
                    item = {
                        'codigo': alimento.get('codigo', ''),
                        'alimento': alimento.get('nome', ''),
                        'nome': alimento.get('nome', ''),
                        'nome_cientifico': alimento.get('nome_cientifico', ''),
                        'grupo': alimento.get('grupo', ''),
                        'marca': alimento.get('marca', ''),
                        'categoria': alimento.get('grupo', '').lower().replace(' ', '_')
                    }
                    
                    # Processa nutrientes se existirem
                    nutrientes = alimento.get('nutrientes', {})
                    if nutrientes:
                        # Mapeia nutrientes comuns
                        mapeamento_nutrientes = {
                            'energia_kcal': ['energia', 'kcal', 'energia_kcal', 'calorias'],
                            'energia_kj': ['energia_kj', 'kj'],
                            'proteina': ['proteina', 'proteinas', 'protein'],
                            'lipideos': ['lipideos', 'lipídeos', 'gorduras', 'fat'],
                            'carboidratos': ['carboidratos', 'carboidrato', 'carbohydrates'],
                            'fibra': ['fibra', 'fibras', 'fiber'],
                            'calcio': ['calcio', 'cálcio', 'calcium'],
                            'ferro': ['ferro', 'iron']
                        }
                        
                        for nutriente_nome, possiveis_chaves in mapeamento_nutrientes.items():
                            for chave in possiveis_chaves:
                                if chave in nutrientes:
                                    valor = nutrientes[chave]
                                    # Tenta converter para número
                                    try:
                                        if isinstance(valor, str):
                                            # Remove unidades e caracteres especiais
                                            valor_limpo = valor.replace(',', '.').replace('g', '').replace('mg', '').replace('kcal', '').replace('kJ', '').strip()
                                            if valor_limpo and valor_limpo != 'tr' and valor_limpo != '-':
                                                item[nutriente_nome] = float(valor_limpo)
                                        else:
                                            item[nutriente_nome] = float(valor)
                                    except (ValueError, TypeError):
                                        pass
                                    break
                    
                    alimentos_processados.append(item)
                
                df = pd.DataFrame(alimentos_processados)
                
                # Garante que temos pelo menos a coluna energia
                if 'energia' not in df.columns and 'energia_kcal' in df.columns:
                    df['energia'] = df['energia_kcal']
                
            else:
                print(f"Formato de dados JSON não reconhecido")
                return pd.DataFrame()
            
            # Se uma categoria específica foi solicitada, filtra os dados
            if categoria:
                if 'categoria' in df.columns:
                    df_filtrado = df[df['categoria'].str.contains(categoria.replace('_', ' '), case=False, na=False)]
                    if not df_filtrado.empty:
                        df = df_filtrado
                elif 'grupo' in df.columns:
                    df_filtrado = df[df['grupo'].str.contains(categoria.replace('_', ' '), case=False, na=False)]
                    if not df_filtrado.empty:
                        df = df_filtrado
            
            print(f"Dados carregados com sucesso:")
            print(f"   - Total de registros: {len(df)}")
            print(f"   - Colunas disponíveis: {list(df.columns)}")
            
            if len(df) > 0:
                print(f"   - Exemplo de alimento: {df.iloc[0].get('alimento', 'N/A')}")
                # Mostra algumas colunas numéricas se existirem
                colunas_nutrientes = ['energia', 'proteina', 'lipideos', 'carboidratos']
                nutrientes_disponiveis = [col for col in colunas_nutrientes if col in df.columns and not df[col].isna().all()]
                if nutrientes_disponiveis:
                    print(f"   - Nutrientes disponíveis: {nutrientes_disponiveis}")
            
            # Salva no cache
            dados_cache[cache_key] = df
            return df
            
        except Exception as e:
            print(f"Erro ao carregar arquivo JSON {arquivo_json}: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    else:
        print(f"Arquivo JSON não encontrado: {arquivo_json}")
        # Fallback para arquivos CSV se JSON não existir
        return carregar_dados_csv(categoria)

def carregar_dados_csv(categoria=None):
    """
    Método de fallback para carregar dados de arquivos CSV
    """
    # Garantir que as categorias estejam carregadas
    categorias = carregar_categorias()
    
    if categoria and categoria in categorias:
        arquivo = os.path.join(DATA_DIR, f'alimentos_{categoria}.csv')
        if os.path.exists(arquivo):
            try:
                df = pd.read_csv(arquivo, encoding='utf-8', low_memory=False)
                if 'nome' in df.columns:
                    df = df.rename(columns={'nome': 'alimento'})
                if 'categoria' not in df.columns:
                    df['categoria'] = categoria
                return df
            except Exception as e:
                print(f"Erro ao carregar arquivo CSV {arquivo}: {e}")
                return pd.DataFrame()
    
    return pd.DataFrame()  # Retorna DataFrame vazio se não encontrar dados

@app.route('/')
def index():
    """Página inicial"""
    categorias = carregar_categorias()
    return render_template('index.html', categorias=categorias)

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    """Endpoint para buscar alimentos"""
    categorias = carregar_categorias()
    
    if request.method == 'POST':
        termo_busca = request.form.get('termo', '')
        categoria = request.form.get('categoria', '')
        # Novos parâmetros de filtro
        busca_exata = request.form.get('exatamente') == '1'
        min_energia = request.form.get('minEnergia', '')
        max_energia = request.form.get('maxEnergia', '')
        min_proteina = request.form.get('minProteina', '')
        max_proteina = request.form.get('maxProteina', '')
        min_carboidrato = request.form.get('minCarboidrato', '')
        max_carboidrato = request.form.get('maxCarboidrato', '')
        min_lipideos = request.form.get('minLipideos', '')
        max_lipideos = request.form.get('maxLipideos', '')
        ordenar = request.form.get('ordenar', 'relevancia')
    else:
        termo_busca = request.args.get('termo', '')
        categoria = request.args.get('categoria', '')
        # Novos parâmetros de filtro
        busca_exata = request.args.get('exatamente') == '1'
        min_energia = request.args.get('minEnergia', '')
        max_energia = request.args.get('maxEnergia', '')
        min_proteina = request.args.get('minProteina', '')
        max_proteina = request.args.get('maxProteina', '')
        min_carboidrato = request.args.get('minCarboidrato', '')
        max_carboidrato = request.args.get('maxCarboidrato', '')
        min_lipideos = request.args.get('minLipideos', '')
        max_lipideos = request.args.get('maxLipideos', '')
        ordenar = request.args.get('ordenar', 'relevancia')
    
    # Carrega os dados da categoria selecionada ou todos os dados
    df = carregar_dados(categoria if categoria else None)
    
    if df.empty:
        return render_template('resultados.html', resultados=[], termo=termo_busca, categorias=categorias)
    
    # Realiza a busca pelo termo em várias colunas
    if termo_busca:
        # Divide o termo de busca em palavras individuais para busca mais precisa
        if busca_exata:
            termos = [termo_busca.lower()]
        else:
            termos = termo_busca.lower().split()
        
        # Verifica quais colunas estão disponíveis para busca
        colunas_busca = ['alimento', 'nome', 'descricao', 'nomeIngles', 'nomeCientifico'] 
        colunas_busca = [col for col in colunas_busca if col in df.columns]
        
        # Criar coluna de pontuação para classificar os resultados por relevância
        df['relevancia'] = 0
        
        if colunas_busca:
            # Atribui pesos para diferentes tipos de correspondência
            # Correspondência exata tem peso maior que correspondência parcial
            for termo in termos:
                for col in colunas_busca:
                    if col in df.columns:
                        # Correspondência exata (termo completo)
                        mask_exata = df[col].str.lower().str.contains(rf'\b{termo}\b', regex=True, case=False, na=False)
                        df.loc[mask_exata, 'relevancia'] += 10
                        
                        # Se não for busca exata, também considera correspondências parciais
                        if not busca_exata:
                            # Correspondência parcial (termo como substring)
                            mask_parcial = df[col].str.lower().str.contains(termo, regex=False, case=False, na=False)
                            df.loc[mask_parcial, 'relevancia'] += 5
                            
                            # Correspondência no início do texto (maior relevância)
                            mask_inicio = df[col].str.lower().str.startswith(termo, na=False)
                            df.loc[mask_inicio, 'relevancia'] += 3
            
            # Filtra apenas resultados com alguma relevância
            resultados = df[df['relevancia'] > 0]
            
            # Se não houver resultados exatos e não for busca exata, tenta busca mais flexível
            if resultados.empty and not busca_exata:
                for termo in termos:
                    # Busca com tolerância a erros (permitindo variações no termo)
                    for col in colunas_busca:
                        if col in df.columns:
                            # Usa regex com padrão mais flexível
                            pattern = ''.join(f'[{c}{c.upper()}].*?' for c in termo)
                            mask_fuzzy = df[col].str.contains(pattern, regex=True, na=False)
                            df.loc[mask_fuzzy, 'relevancia'] += 2
                
                # Filtra resultados da busca fuzzy
                resultados = df[df['relevancia'] > 0]
        else:
            resultados = pd.DataFrame()
    else:
        # Se não houver termo de busca, retorna todos os resultados
        resultados = df.copy()
        resultados['relevancia'] = 1
    
    # Aplica filtros nutricionais
    # Energia
    if min_energia and min_energia.isdigit():
        min_val = float(min_energia)
        if 'energia' in resultados.columns:
            resultados = resultados[resultados['energia'] >= min_val]
        elif 'Energia' in resultados.columns:
            resultados = resultados[resultados['Energia'] >= min_val]
    
    if max_energia and max_energia.isdigit():
        max_val = float(max_energia)
        if 'energia' in resultados.columns:
            resultados = resultados[resultados['energia'] <= max_val]
        elif 'Energia' in resultados.columns:
            resultados = resultados[resultados['Energia'] <= max_val]
    
    # Proteína
    if min_proteina:
        try:
            min_val = float(min_proteina)
            if 'proteina' in resultados.columns:
                resultados = resultados[resultados['proteina'] >= min_val]
            elif 'Proteina' in resultados.columns:
                resultados = resultados[resultados['Proteina'] >= min_val]
        except ValueError:
            pass
    
    if max_proteina:
        try:
            max_val = float(max_proteina)
            if 'proteina' in resultados.columns:
                resultados = resultados[resultados['proteina'] <= max_val]
            elif 'Proteina' in resultados.columns:
                resultados = resultados[resultados['Proteina'] <= max_val]
        except ValueError:
            pass
    
    # Carboidratos
    if min_carboidrato:
        try:
            min_val = float(min_carboidrato)
            if 'carboidratos' in resultados.columns:
                resultados = resultados[resultados['carboidratos'] >= min_val]
            elif 'Carboidratos' in resultados.columns:
                resultados = resultados[resultados['Carboidratos'] >= min_val]
            elif 'carboidrato' in resultados.columns:
                resultados = resultados[resultados['carboidrato'] >= min_val]
        except ValueError:
            pass
    
    if max_carboidrato:
        try:
            max_val = float(max_carboidrato)
            if 'carboidratos' in resultados.columns:
                resultados = resultados[resultados['carboidratos'] <= max_val]
            elif 'Carboidratos' in resultados.columns:
                resultados = resultados[resultados['Carboidratos'] <= max_val]
            elif 'carboidrato' in resultados.columns:
                resultados = resultados[resultados['carboidrato'] <= max_val]
        except ValueError:
            pass
    
    # Lipídeos
    if min_lipideos:
        try:
            min_val = float(min_lipideos)
            if 'lipideos' in resultados.columns:
                resultados = resultados[resultados['lipideos'] >= min_val]
            elif 'Lipideos' in resultados.columns:
                resultados = resultados[resultados['Lipideos'] >= min_val]
        except ValueError:
            pass
    
    if max_lipideos:
        try:
            max_val = float(max_lipideos)
            if 'lipideos' in resultados.columns:
                resultados = resultados[resultados['lipideos'] <= max_val]
            elif 'Lipideos' in resultados.columns:
                resultados = resultados[resultados['Lipideos'] <= max_val]
        except ValueError:
            pass
    
    # Ordenação dos resultados
    if ordenar:
        campo_ordenacao = ordenar
        ordem_crescente = True
        
        if ordenar.startswith('-'):
            campo_ordenacao = ordenar[1:]
            ordem_crescente = False
        
        # Verifica se o campo existe
        if campo_ordenacao in resultados.columns:
            resultados = resultados.sort_values(campo_ordenacao, ascending=ordem_crescente)
        else:
            # Ordenação padrão por relevância
            resultados = resultados.sort_values('relevancia', ascending=False)
    else:
        # Ordenação padrão por relevância
        resultados = resultados.sort_values('relevancia', ascending=False)
    
    # Converte para dicionário para enviar ao template
    resultados_dict = resultados.to_dict('records')
    
    return render_template('resultados.html', 
                          resultados=resultados_dict, 
                          termo=termo_busca,
                          categorias=categorias)

@app.route('/api/alimentos', methods=['GET'])
def api_alimentos():
    """API para buscar alimentos"""
    categorias = carregar_categorias()
    termo_busca = request.args.get('termo', '')
    categoria = request.args.get('categoria', '')
    limite = int(request.args.get('limite', 50))
    
    # Carrega os dados da categoria selecionada ou todos os dados
    df = carregar_dados(categoria if categoria else None)
    
    if df.empty:
        return jsonify([])
    
    # Realiza a busca pelo termo em várias colunas
    if termo_busca:
        # Divide o termo de busca em palavras individuais para busca mais precisa
        termos = termo_busca.lower().split()
        
        # Verifica quais colunas estão disponíveis para busca
        colunas_busca = ['alimento', 'nome', 'descricao', 'nomeIngles', 'nomeCientifico'] 
        colunas_busca = [col for col in colunas_busca if col in df.columns]
        
        # Criar coluna de pontuação para classificar os resultados por relevância
        df['relevancia'] = 0
        
        if colunas_busca:
            # Inicializa DataFrame vazio para os resultados
            resultados = pd.DataFrame()
            
            # Atribui pesos para diferentes tipos de correspondência
            # Correspondência exata tem peso maior que correspondência parcial
            for termo in termos:
                for col in colunas_busca:
                    if col in df.columns:
                        # Correspondência exata (termo completo)
                        mask_exata = df[col].str.lower().str.contains(rf'\b{termo}\b', regex=True, case=False, na=False)
                        df.loc[mask_exata, 'relevancia'] += 10
                        
                        # Correspondência parcial (termo como substring)
                        mask_parcial = df[col].str.lower().str.contains(termo, regex=False, case=False, na=False)
                        df.loc[mask_parcial, 'relevancia'] += 5
                        
                        # Correspondência no início do texto (maior relevância)
                        mask_inicio = df[col].str.lower().str.startswith(termo, na=False)
                        df.loc[mask_inicio, 'relevancia'] += 3
            
            # Filtra apenas resultados com alguma relevância
            resultados = df[df['relevancia'] > 0].sort_values('relevancia', ascending=False)
            
            # Se não houver resultados exatos, tenta busca mais flexível
            if resultados.empty:
                for termo in termos:
                    # Busca com tolerância a erros (permitindo variações no termo)
                    for col in colunas_busca:
                        if col in df.columns:
                            # Usa regex com padrão mais flexível
                            pattern = ''.join(f'[{c}{c.upper()}].*?' for c in termo)
                            mask_fuzzy = df[col].str.contains(pattern, regex=True, na=False)
                            df.loc[mask_fuzzy, 'relevancia'] += 2
                
                # Filtra resultados da busca fuzzy
                resultados = df[df['relevancia'] > 0].sort_values('relevancia', ascending=False)
        else:
            resultados = pd.DataFrame()
    else:
        # Se não houver termo de busca, retorna os primeiros N resultados
        resultados = df.head(limite)
    
    # Limita o número de resultados
    resultados = resultados.head(limite)
    
    # Converte para dicionário e depois para JSON
    return jsonify(resultados.to_dict('records'))

@app.route('/alimento/<id>')
def detalhe_alimento(id):
    """Página de detalhes de um alimento específico"""
    categorias = carregar_categorias()
    
    # Carrega todos os dados
    df = carregar_dados()
    
    if df.empty:
        return render_template('erro.html', mensagem="Dados não encontrados", categorias=categorias), 404
    
    # Busca o alimento pelo ID
    if 'codigo' in df.columns:
        alimento = df[df['codigo'] == id]
    elif 'id' in df.columns:
        alimento = df[df['id'] == id]
    else:
        # Se não houver coluna ID, usa o índice como ID
        try:
            id_num = int(id)
            if id_num < len(df):
                alimento = df.iloc[[id_num]]
            else:
                alimento = pd.DataFrame()
        except:
            alimento = pd.DataFrame()
    
    if alimento.empty:
        return render_template('erro.html', mensagem="Alimento não encontrado", categorias=categorias), 404
    
    # Converte para dicionário
    alimento_dict = alimento.iloc[0].to_dict()
    
    return render_template('detalhe.html', alimento=alimento_dict, categorias=categorias)

if __name__ == '__main__':
    # Carrega as categorias no início da aplicação
    categorias = carregar_categorias()
    print(f"Categorias disponíveis: {categorias}")
    app.run(debug=True, host='0.0.0.0', port=5000)
