# Guia de Integração Frontend-Backend

Este documento descreve como testar e verificar a integração entre o frontend (Next.js) e o backend (FastAPI) do NutriApp TBCA.

## Pré-requisitos

Antes de começar, certifique-se de que você possui:

- Python 3.7+ instalado
- Node.js 14+ instalado
- npm ou yarn instalado
- Dependências do projeto instaladas (veja abaixo)

## Estrutura do Projeto

O projeto está dividido em duas partes principais:

1. **Backend (FastAPI)**:
   - Localizado na pasta `backend/`
   - Fornece APIs RESTful para acesso aos dados nutricionais
   - Gerencia o banco de dados SQLite com as informações da TBCA

2. **Frontend (Next.js)**:
   - Localizado na pasta `frontend/`
   - Interface de usuário para busca e cálculo de informações nutricionais
   - Consome as APIs do backend

## Instalação e Configuração

### Backend (FastAPI)

1. Navegue até a pasta do backend:
   ```
   cd backend
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Inicie o servidor de desenvolvimento:
   ```
   uvicorn app.main:app --reload
   ```

4. O backend estará disponível em: http://localhost:8000
   - Documentação interativa da API: http://localhost:8000/docs

### Frontend (Next.js)

1. Navegue até a pasta do frontend:
   ```
   cd frontend
   ```

2. Instale as dependências:
   ```
   npm install
   # ou
   yarn install
   ```

3. Configure o arquivo `.env.local` na raiz do frontend:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Inicie o servidor de desenvolvimento:
   ```
   npm run dev
   # ou
   yarn dev
   ```

5. O frontend estará disponível em: http://localhost:3000

## Testes de Integração

Para verificar se a integração entre frontend e backend está funcionando corretamente, você pode:

1. **Utilizar o script automatizado de teste**:
   ```
   python backend/tests/test_integracao.py
   ```
   Este script verifica se ambos os serviços estão rodando e se as APIs estão acessíveis.

2. **Usar o script PowerShell para automatizar todo o processo**:
   ```
   ./scripts/iniciar-integracao.ps1
   ```
   Este script apresenta um menu interativo para instalar dependências, iniciar os serviços e testar a integração.

## Endpoints da API

Os principais endpoints da API que o frontend utiliza são:

- `GET /grupos` - Lista todos os grupos de alimentos
- `GET /alimentos` - Lista todos os alimentos (com paginação)
  - Parâmetros: `limit`, `offset`, `grupo_id` (opcional)
- `GET /alimentos/search` - Busca alimentos por nome
  - Parâmetros: `q` (termo de busca)
- `GET /alimentos/{id}` - Obtém detalhes de um alimento específico
- `POST /calcular` - Calcula informações nutricionais com base nos alimentos e porções
  - Corpo: Array de objetos `{alimento_id, porcao}`

## Componentes Frontend

Os principais componentes do frontend que interagem com o backend são:

- `services/api.js` - Contém as funções para comunicação com o backend
- `pages/index.jsx` - Página principal que faz as chamadas para a API
- `components/SearchBar.jsx` - Componente de busca que utiliza a API de busca
- `components/NutritionalTable.jsx` - Exibe os resultados do cálculo nutricional

## Testando a Integração

Para testar manualmente a integração, siga os passos:

1. Acesse o frontend em http://localhost:3000
2. Utilize a barra de busca para procurar alimentos (ex: "arroz")
3. Selecione um alimento e adicione uma porção
4. Verifique se a tabela nutricional é atualizada corretamente

## Solução de Problemas

Se encontrar problemas na integração:

1. **Backend não está respondendo**:
   - Verifique se o servidor está rodando em http://localhost:8000
   - Consulte os logs de erro no terminal do backend
   - Verifique se o banco de dados foi inicializado corretamente

2. **Frontend não consegue se comunicar com o backend**:
   - Verifique se o arquivo `.env.local` está configurado corretamente
   - Inspecione o console do navegador para erros de rede
   - Verifique se há problemas de CORS (Cross-Origin Resource Sharing)

3. **Dados não são exibidos corretamente**:
   - Verifique a resposta da API usando a documentação interativa
   - Compare a estrutura de dados esperada pelo frontend com a fornecida pelo backend

## Logs de Integração

Os logs de teste de integração são salvos no diretório `logs/` com o formato `integracao_YYYYMMDD_HHMMSS.log`.

## Próximos Passos

Após confirmar que a integração básica está funcionando, considere:

1. Implementar testes automatizados mais abrangentes
2. Adicionar recursos de autenticação
3. Otimizar o desempenho de consultas ao banco de dados
4. Implementar cache no lado do cliente para dados frequentemente acessados
