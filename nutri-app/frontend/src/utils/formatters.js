/**
 * Formata um valor numérico para exibição com 2 casas decimais
 * @param {number} value - Valor numérico para formatar
 * @returns {string} Valor formatado
 */
export function formatNumber(value) {
  if (value === null || value === undefined) return '-';
  return Number(value).toFixed(2).replace('.', ',');
}

/**
 * Formata valores nutricionais para exibição
 * @param {number} value - Valor nutricional
 * @param {string} unit - Unidade de medida (g, mg, etc)
 * @returns {string} Valor formatado com unidade
 */
export function formatNutrient(value, unit = 'g') {
  if (value === null || value === undefined) return '-';
  return `${formatNumber(value)}${unit}`;
}

/**
 * Calcula o valor energético em kcal
 * @param {number} proteina - Quantidade de proteína em gramas
 * @param {number} carboidratos - Quantidade de carboidratos em gramas
 * @param {number} gordura - Quantidade de gordura em gramas
 * @returns {number} Valor energético em kcal
 */
export function calculateEnergy(proteina, carboidratos, gordura) {
  return (proteina * 4) + (carboidratos * 4) + (gordura * 9);
}

/**
 * Gera uma cor baseada no nome de uma categoria
 * @param {string} name - Nome da categoria
 * @returns {string} Código de cor hexadecimal
 */
export function generateColorFromName(name) {
  if (!name) return '#4CAF50';
  
  // Gerar um hash simples da string
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  // Converter para uma cor hexadecimal
  let color = '#';
  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xFF;
    color += ('00' + value.toString(16)).substr(-2);
  }
  
  return color;
}
