/**
 * Serviço para comunicação com a API do backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Busca alimentos com filtragem e paginação
 * @param {string} termo - Termo de busca opcional
 * @param {number} categoriaId - ID da categoria para filtrar
 * @param {number} pagina - Número da página para paginação
 * @param {number} itensPorPagina - Quantidade de itens por página
 * @returns {Promise<Array>} Lista de alimentos
 */
export async function fetchAlimentos(termo = '', categoriaId = null, pagina = 1, itensPorPagina = 12) {
  const skip = (pagina - 1) * itensPorPagina;
  
  let url = `${API_URL}/alimentos?skip=${skip}&limit=${itensPorPagina}`;
  
  if (termo) {
    url += `&termo_busca=${encodeURIComponent(termo)}`;
  }
  
  if (categoriaId) {
    url += `&categoria_id=${categoriaId}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error('Erro ao buscar alimentos');
  }
  
  return response.json();
}

/**
 * Busca um alimento pelo ID
 * @param {number} id - ID do alimento
 * @returns {Promise<Object>} Dados do alimento
 */
export async function fetchAlimento(id) {
  const response = await fetch(`${API_URL}/alimentos/${id}`);
  
  if (!response.ok) {
    throw new Error('Erro ao buscar alimento');
  }
  
  return response.json();
}

/**
 * Busca todas as categorias de alimentos
 * @returns {Promise<Array>} Lista de categorias
 */
export async function fetchCategorias() {
  const response = await fetch(`${API_URL}/grupos`);
  
  if (!response.ok) {
    throw new Error('Erro ao buscar categorias');
  }
  
  return response.json();
}

/**
 * Calcula informações nutricionais para uma lista de alimentos e quantidades
 * @param {Array} itens - Lista de objetos {alimento_id, quantidade_g}
 * @returns {Promise<Object>} Resultado do cálculo nutricional
 */
export async function calcularNutricional(itens) {
  const response = await fetch(`${API_URL}/calculadora`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ itens }),
  });
  
  if (!response.ok) {
    throw new Error('Erro ao calcular valores nutricionais');
  }
  
  return response.json();
}
