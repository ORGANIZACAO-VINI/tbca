# Integração Frontend-Backend - Instruções

Este documento fornece instruções detalhadas para testar a integração entre o frontend (Next.js) e o backend (FastAPI) do projeto NutriApp.

## Pré-requisitos

Certifique-se de ter instalado:

- Python 3.8+
- Node.js 14+ e npm
- PowerShell (para Windows)

## Inicialização Rápida

### Opção 1: Script Automático (Recomendado)

1. Abra um terminal PowerShell na pasta raiz do projeto
2. Execute o script de inicialização:

```
.\iniciar-aplicacao.ps1
```

Este script irá:
- Configurar o ambiente virtual Python
- Instalar as dependências do backend
- Inicializar o banco de dados com dados de exemplo
- Iniciar o servidor backend
- Instalar as dependências do frontend
- Iniciar o servidor frontend

### Opção 2: Configuração Manual

#### Backend

1. Abra um terminal na pasta do backend
2. Crie e ative o ambiente virtual:
   ```
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Instale as dependências:
   ```
   pip install fastapi uvicorn sqlalchemy pydantic
   ```
4. Inicialize o banco de dados com dados de exemplo:
   ```
   python data\scripts\inserir_dados_exemplo.py
   ```
5. Inicie o servidor:
   ```
   uvicorn app.main:app --reload
   ```

#### Frontend

1. Abra outro terminal na pasta do frontend
2. Instale as dependências:
   ```
   npm install
   ```
3. Inicie o servidor de desenvolvimento:
   ```
   npm run dev
   ```

## Testando a Integração

1. Abra o navegador e acesse: http://localhost:3000
2. Você deve ver a página inicial com uma lista de alimentos
3. Tente as seguintes ações para verificar a integração:
   - Pesquisar um alimento na barra de busca (por exemplo, "arroz")
   - Filtrar por categoria
   - Clicar em um alimento para ver os detalhes
   - Navegar para a página da calculadora e adicionar alimentos

## Documentação da API

A documentação interativa da API está disponível em:
http://localhost:8000/docs

Você pode testar os endpoints diretamente nesta interface.

## Solução de Problemas

### Problema: Dados não aparecem no frontend
- Verifique se o servidor backend está rodando
- Abra o console do navegador para procurar erros
- Verifique a URL da API em `.env.local`
- Teste os endpoints diretamente na documentação Swagger

### Problema: Erro ao iniciar o backend
- Verifique se o arquivo do banco de dados foi criado
- Veja se todas as dependências foram instaladas
- Verifique se os arquivos Python foram modificados corretamente

### Problema: Erro ao iniciar o frontend
- Limpe o cache do Next.js:
  ```
  rm -rf .next
  ```
- Reinstale as dependências:
  ```
  npm install
  ```

## Recursos Adicionais

- Documentação do FastAPI: https://fastapi.tiangolo.com/
- Documentação do Next.js: https://nextjs.org/docs
- Documentação do SQLAlchemy: https://docs.sqlalchemy.org/
