# Instruções para Importação de Dados da TBCA em Formato JSON

Este documento fornece instruções para utilizar o script `custom_import.py`, que importa dados nutricionais no formato JSON para um banco de dados SQLite.

## Visão Geral

O script foi projetado para importar dados nutricionais no formato da Tabela Brasileira de Composição de Alimentos (TBCA), estruturados como um arquivo JSON. Os dados são organizados em um banco SQLite com uma estrutura relacional que preserva todos os detalhes dos alimentos, nutrientes e porções.

## Estrutura do Banco de Dados

O banco de dados criado possui a seguinte estrutura:

1. **Tabela `grupos`**:
   - Armazena os grupos de alimentos (ex: "Frutas e derivados", "Carnes e derivados")

2. **Tabela `alimentos`**:
   - Contém informações básicas sobre cada alimento
   - Campos: código, nome, nome científico, grupo, marca

3. **Tabela `nutrientes`**:
   - Armazena os nutrientes de cada alimento
   - Campos: nome do nutriente, unidade, valor por 100g

4. **Tabela `porcoes`**:
   - Contém informações sobre porções específicas para cada nutriente
   - Campos: descrição da porção, quantidade, valor

## Como Usar o Script

1. **Execução do Script**:
   ```bash
   cd C:\Users\vinim\Downloads\script\nutri-app\backend
   python data\custom_import.py
   ```

2. **Quando solicitado**, forneça o caminho completo para o arquivo JSON:
   ```
   Digite o caminho completo para o arquivo JSON a ser importado: C:\caminho\para\seu\arquivo\alimentos_tbca.json
   ```

3. **O script irá**:
   - Criar uma nova estrutura de banco de dados (excluindo qualquer versão anterior)
   - Importar todos os alimentos do arquivo JSON
   - Processar cada nutriente e porção
   - Exibir estatísticas sobre os dados importados

## Formato de Dados Esperado

O script espera um arquivo JSON com a seguinte estrutura:

```json
[
  {
    "codigo": "BRC0001C",
    "nome": "Abacate, polpa, in natura, Brasil",
    "nome_cientifico": "Persea americana Mill",
    "grupo": "Frutas e derivados",
    "marca": "",
    "nutrientes": [
      {
        "nome": "Alfa-tocoferol (Vitamina E)",
        "unidade": "mg",
        "valor_por_100g": "0,02",
        "porcoes": [
          {
            "descricao": "Colher sopa cheia (45 g)",
            "quantidade": "45g",
            "valor": "0,01"
          }
        ]
      }
    ]
  }
]
```

## Notas Importantes

1. **Limpeza de Dados**: O script automaticamente limpa o banco de dados antes de cada importação. Se você quiser preservar dados anteriores, faça um backup do arquivo `tbca.db` antes de executar o script novamente.

2. **Conversão de Valores**: Os valores numéricos em formato de texto (com vírgula como separador decimal) são automaticamente convertidos para o formato adequado.

3. **Erros de Importação**: Se ocorrerem erros durante a importação, verifique se o formato do seu arquivo JSON corresponde exatamente ao formato esperado.

4. **Importações Repetidas**: Você pode executar o script várias vezes para importar dados de diferentes arquivos. No entanto, cada execução sobrescreverá os dados anteriores.

## Estatísticas

Após a importação, o script fornece as seguintes estatísticas:

- Total de alimentos importados
- Total de nutrientes importados
- Média de nutrientes por alimento
- Distribuição de alimentos por grupo

Estas estatísticas são úteis para verificar se a importação foi bem-sucedida e para obter uma visão geral dos dados importados.

## Solução de Problemas

Se encontrar problemas durante a importação:

1. Verifique se o arquivo JSON está no formato correto
2. Certifique-se de que o caminho para o arquivo está correto
3. Verifique se você tem permissões para ler o arquivo e escrever no diretório de saída

Para problemas mais complexos, examine o código-fonte do script para entender como os dados são processados e faça ajustes conforme necessário.
