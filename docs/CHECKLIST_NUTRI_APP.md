# Checklist de Configuração - Aplicativo Web de Nutrição TBCA

Use este checklist para acompanhar seu progresso na configuração e desenvolvimento do aplicativo web de nutrição TBCA.

## Pré-requisitos

- [x] Python 3.8+ instalado
- [x] Node.js 14+ e npm/yarn instalados
- [x] Git instalado
- [ ] Conhecimento básico de React/Next.js e FastAPI

## Configuração Inicial

### 1. Estrutura de diretórios

- [ ] Criar diretório principal do projeto (`mkdir -p nutri-app`)
- [ ] Criar estrutura para backend:
  - [ ] `backend/app/models`
  - [ ] `backend/app/routes`
  - [ ] `backend/app/services`
  - [ ] `backend/app/utils`
  - [ ] `backend/data`
  - [ ] `backend/tests`
- [ ] Criar estrutura para frontend:
  - [ ] `frontend/public`
  - [ ] `frontend/src/components`
  - [ ] `frontend/src/pages`
  - [ ] `frontend/src/styles`
  - [ ] `frontend/src/hooks`
  - [ ] `frontend/src/services`
  - [ ] `frontend/src/utils`

### 2. Ambiente Python para o backend

- [ ] Navegar para o diretório backend (`cd backend`)
- [ ] Criar ambiente virtual (`python -m venv venv`)
- [ ] Ativar ambiente virtual:
  - [ ] Windows: `venv\Scripts\activate`
  - [ ] Linux/Mac: `source venv/bin/activate`
- [ ] Instalar dependências: 
  - [ ] FastAPI (`pip install fastapi`)
  - [ ] Uvicorn (`pip install uvicorn`)
  - [ ] SQLAlchemy (`pip install sqlalchemy`)
  - [ ] Pydantic (`pip install pydantic`)
  - [ ] Pandas (`pip install pandas`)

### 3. Projeto Next.js para o frontend

- [ ] Navegar para o diretório frontend (`cd frontend`)
- [ ] Inicializar projeto Next.js (`npx create-next-app@latest . --use-npm --typescript`)
- [ ] Instalar dependências adicionais:
  - [ ] Axios (`npm install axios`)
  - [ ] Chart.js (`npm install chart.js react-chartjs-2`)
  - [ ] React Hook Form (`npm install react-hook-form`)
  - [ ] TailwindCSS (`npm install tailwindcss postcss autoprefixer`)
  - [ ] Configurar TailwindCSS

### 4. Importação de dados

- [ ] Copiar arquivo `import_csv_to_sqlite.py` para `backend/data/scripts/`
- [ ] Executar script de importação (`python data/scripts/import_csv_to_sqlite.py`)
- [ ] Verificar se o banco SQLite foi criado corretamente
- [ ] Alternativa: Usar script personalizado para importar dados JSON:
  - [ ] Copiar `custom_import.py` para `backend/data/`
  - [ ] Executar script (`python data/custom_import.py`)
  - [ ] Fornecer caminho para o arquivo JSON quando solicitado

### 5. Servidor backend

- [ ] Copiar arquivo `backend_app.py` para `backend/app/main.py`
- [ ] Iniciar servidor FastAPI (`uvicorn app.main:app --reload`)
- [ ] Verificar API em `http://localhost:8000`
- [ ] Verificar documentação da API em `http://localhost:8000/docs`

### 6. Servidor frontend

- [ ] Copiar arquivo `frontend_home_page.jsx` para `frontend/src/pages/index.js`
- [ ] Iniciar servidor Next.js (`npm run dev`)
- [ ] Verificar frontend em `http://localhost:3000`

## Fases de Desenvolvimento

### Fase 1: Backend e Dados

- [ ] Implementar modelos de dados completos
  - [ ] Definir SQLAlchemy models
  - [ ] Definir Pydantic schemas
- [ ] Desenvolver endpoints da API
  - [ ] Endpoints de busca
  - [ ] Endpoints de detalhes
  - [ ] Endpoints de cálculo nutricional
- [ ] Adicionar autenticação básica
  - [ ] Implementar JWT
  - [ ] Configurar middleware
- [ ] Implementar testes
  - [ ] Testes unitários
  - [ ] Testes de integração
- [ ] Documentar a API
  - [ ] Atualizar docstrings
  - [ ] Expandir documentação OpenAPI

### Fase 2: Frontend Básico

- [ ] Implementar componentes reutilizáveis
  - [ ] Componentes de UI
  - [ ] Componentes de formulário
  - [ ] Componentes de visualização
- [ ] Desenvolver páginas principais
  - [ ] Página de busca
  - [ ] Página de detalhes
  - [ ] Calculadora nutricional
- [ ] Integrar com a API backend
  - [ ] Configurar cliente HTTP
  - [ ] Implementar hooks de data fetching
- [ ] Implementar visualizações de dados
  - [ ] Gráficos de macronutrientes
  - [ ] Comparações de alimentos
- [ ] Adicionar responsividade para dispositivos móveis

### Fase 3: Funcionalidades Avançadas

- [ ] Implementar sistema de autenticação
  - [ ] Tela de login/registro
  - [ ] Perfil de usuário
- [ ] Desenvolver diário alimentar
  - [ ] Rastreamento de refeições
  - [ ] Histórico alimentar
- [ ] Adicionar recomendações personalizadas
  - [ ] Algoritmo de sugestões
  - [ ] Preferências do usuário
- [ ] Implementar exportação de dados
  - [ ] Exportação para PDF
  - [ ] Exportação para CSV
- [ ] Otimizar desempenho e experiência do usuário
  - [ ] Lazy loading
  - [ ] Caching

## Recursos e Referências

- [ ] Documentação do FastAPI
  - [ ] Revisar [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
  - [ ] Explorar exemplos de projetos similares
- [ ] Documentação do Next.js
  - [ ] Revisar [nextjs.org/docs](https://nextjs.org/docs)
  - [ ] Estudar exemplos de layouts responsivos
- [ ] Documentação do TailwindCSS
  - [ ] Revisar [tailwindcss.com/docs](https://tailwindcss.com/docs)
  - [ ] Configurar tema personalizado
- [ ] Referência da TBCA
  - [ ] Explorar [tbca.net.br](https://www.tbca.net.br/)
  - [ ] Entender estrutura de dados e relações

## Boas Práticas

- [ ] Desenvolvimento Incremental
  - [ ] Implementar uma funcionalidade por vez
  - [ ] Testar completamente antes de avançar
- [ ] Reutilização de Código
  - [ ] Criar utilitários compartilhados
  - [ ] Desenvolver componentes modulares
- [ ] Testes Contínuos
  - [ ] Implementar CI/CD (opcional)
  - [ ] Manter cobertura de testes adequada
- [ ] Documentação
  - [ ] Documentar código com docstrings
  - [ ] Manter README atualizado
  - [ ] Documentar decisões de arquitetura
- [ ] Controle de Versão
  - [ ] Usar branches para novas features
  - [ ] Fazer commits frequentes e descritivos

## Acompanhamento de Progresso

- [ ] Configuração Inicial Completa
- [ ] Backend Funcionando
- [ ] Frontend Funcionando
- [ ] Integração Backend-Frontend
- [ ] Fase 1 Completa (Backend e Dados)
- [ ] Fase 2 Completa (Frontend Básico)
- [ ] Fase 3 Completa (Funcionalidades Avançadas)
- [ ] Testes Implementados
- [ ] Documentação Finalizada
- [ ] Pronto para Produção
