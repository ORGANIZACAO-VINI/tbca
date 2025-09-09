# Instruções para Importação da Base Completa

## 📥 Passos para Importação

1. **Coloque o arquivo CSV na raiz do projeto**
   - Certifique-se de que o arquivo está com o nome exato: `composicao_todos_alimentos.csv`
   - Deve estar no mesmo nível que os arquivos Python principais

2. **Execute o menu de importação**
   ```
   python menu_tbca_completo.py
   ```

3. **Selecione a opção 1 para importar**
   - O processo pode levar 5-10 minutos
   - Será criada uma tabela especial `alimentos_composicao` além das tabelas padrão

4. **Verifique a importação**
   - Use a opção 3 do menu para verificação avançada
   - Você deve ver cerca de 3.000-4.000 alimentos únicos
   - E aproximadamente 230.000 registros de composição detalhada

## ⚠️ Requisitos de Hardware

- **Espaço em disco**: ~100MB (banco + CSV)
- **Memória RAM**: Mínimo 4GB (recomendado 8GB)
- **Processador**: Qualquer processador moderno (2015+)

## 🛠️ Solução de Problemas

Se encontrar erros durante a importação:

1. **Erro de memória**: 
   - Feche outros aplicativos para liberar RAM
   - Ou modifique o script para processar em lotes menores

2. **Erro de codificação**:
   - Verifique se o arquivo está em UTF-8
   - Use o parâmetro `encoding='utf-8'` ao abrir o arquivo

3. **Banco corrompido**:
   - Use a opção 5 do menu para limpar o banco
   - Execute a importação novamente

## 📞 Suporte

Em caso de dúvidas, entre em contato pelo e-mail fornecido anteriormente.
