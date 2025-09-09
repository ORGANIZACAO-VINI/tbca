# GUIA: Como Adicionar Seus Dados ao Sistema

## 📊 FORMATOS ACEITOS

### 1. Arquivos CSV
- Coloque seus arquivos .csv na pasta `dados/`
- Formato esperado:
  ```
  codigo;nome;kcal;carboidratos;proteina;gordura;fibras;calcio;ferro
  ALM001;Arroz branco;130;28.1;2.5;0.3;1.6;10;0.8
  ```

### 2. Arquivos Excel (.xlsx)
- Coloque na pasta `dados/`
- Primeira linha deve ser o cabeçalho
- Colunas principais: nome, kcal, proteína, carboidratos, etc.

### 3. Banco de Dados Existente
- SQLite: copie o arquivo .db para `nutri-app/backend/`
- MySQL/PostgreSQL: use scripts de exportação
- Access: exporte para CSV primeiro

## 🚀 PASSOS PARA IMPORTAR

### Opção A: Dados em CSV
1. Copie seu arquivo para `dados/meus_dados.csv`
2. Execute: `python importar_csv_simples.py`
3. Ajuste o nome do arquivo no script se necessário

### Opção B: Dados em Excel
1. Coloque arquivo em `dados/meus_dados.xlsx`
2. Execute: `python importar_excel.py` (criaremos este)

### Opção C: Dados de API/Web
1. Use o script de download automático
2. Configure URLs no arquivo de configuração

## 🛠️ SCRIPTS DISPONÍVEIS

- `importar_csv_simples.py` - Para arquivos CSV
- `importar_excel.py` - Para planilhas Excel (a criar)
- `migrar_dados_completo.py` - Pipeline completo
- `check_database.py` - Verificar dados importados

## 📋 EXEMPLO DE ESTRUTURA CSV

```csv
codigo,nome,categoria,kcal,proteina,carboidratos,gordura,fibras
ALM001,"Arroz branco cozido","Cereais",130,2.5,28.1,0.3,1.6
ALM002,"Feijão preto cozido","Leguminosas",77,4.5,14.0,0.5,8.4
ALM003,"Frango grelhado","Carnes",165,31.0,0,3.6,0
```

## ⚡ IMPORTAÇÃO RÁPIDA

Para dados urgentes, use:
```bash
# Copiar arquivo
copy "C:\caminho\seus_dados.csv" "dados\meus_alimentos.csv"

# Importar
python importar_csv_simples.py
```
