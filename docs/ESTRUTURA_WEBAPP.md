# Estrutura do Aplicativo Web de Nutrição TBCA

Este documento descreve a estrutura de diretórios e arquivos para o aplicativo web de nutrição baseado nos dados da TBCA.

## Estrutura de Diretórios

```
nutri-app/
│
├── backend/                      # Servidor API FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # Ponto de entrada da aplicação
│   │   ├── models/               # Modelos de dados
│   │   │   ├── __init__.py
│   │   │   ├── alimento.py
│   │   │   ├── usuario.py
│   │   │   └── diario.py
│   │   ├── routes/               # Rotas da API
│   │   │   ├── __init__.py
│   │   │   ├── alimentos.py
│   │   │   ├── autenticacao.py
│   │   │   └── diario.py
│   │   ├── services/             # Lógica de negócio
│   │   │   ├── __init__.py
│   │   │   ├── alimentos_service.py
│   │   │   └── recomendacao_service.py
│   │   └── utils/                # Utilitários
│   │       ├── __init__.py
│   │       ├── database.py
│   │       └── security.py
│   ├── tests/                    # Testes unitários e de integração
│   │   ├── __init__.py
│   │   ├── test_alimentos.py
│   │   └── test_autenticacao.py
│   ├── data/                     # Dados da TBCA processados
│   │   ├── tbca.db               # Banco de dados SQLite
│   │   └── scripts/              # Scripts de importação e processamento
│   │       └── import_csv.py
│   ├── .env                      # Variáveis de ambiente
│   ├── requirements.txt          # Dependências Python
│   └── Dockerfile                # Configuração para Docker
│
├── frontend/                     # Aplicação Next.js/React
│   ├── public/                   # Arquivos estáticos
│   │   ├── favicon.ico
│   │   └── images/
│   ├── src/
│   │   ├── components/           # Componentes React
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   └── Layout.jsx
│   │   │   ├── alimentos/
│   │   │   │   ├── AlimentoCard.jsx
│   │   │   │   ├── AlimentoDetalhes.jsx
│   │   │   │   └── AlimentosLista.jsx
│   │   │   ├── calculadora/
│   │   │   │   ├── CalculadoraNutricional.jsx
│   │   │   │   └── ResultadosCalculadora.jsx
│   │   │   ├── diario/
│   │   │   │   ├── DiarioForm.jsx
│   │   │   │   └── DiarioLista.jsx
│   │   │   └── ui/
│   │   │       ├── Button.jsx
│   │   │       ├── Input.jsx
│   │   │       └── Card.jsx
│   │   ├── pages/                # Páginas da aplicação
│   │   │   ├── _app.js
│   │   │   ├── index.js          # Página inicial
│   │   │   ├── alimentos/
│   │   │   │   ├── index.js      # Lista de alimentos
│   │   │   │   └── [id].js       # Detalhes de um alimento
│   │   │   ├── calculadora.js
│   │   │   ├── diario/
│   │   │   │   ├── index.js
│   │   │   │   └── adicionar.js
│   │   │   ├── auth/
│   │   │   │   ├── login.js
│   │   │   │   └── registro.js
│   │   │   └── perfil.js
│   │   ├── hooks/                # Hooks personalizados
│   │   │   ├── useAlimentos.js
│   │   │   └── useAuth.js
│   │   ├── services/             # Serviços e API clients
│   │   │   ├── api.js
│   │   │   └── auth.js
│   │   ├── styles/               # Estilos CSS/SCSS
│   │   │   ├── globals.css
│   │   │   └── components/
│   │   └── utils/                # Funções utilitárias
│   │       ├── format.js
│   │       └── calculations.js
│   ├── .env.local                # Variáveis de ambiente do frontend
│   ├── package.json              # Dependências NPM
│   ├── tailwind.config.js        # Configuração do TailwindCSS
│   └── next.config.js            # Configuração do Next.js
│
├── docker-compose.yml            # Configuração Docker Compose
├── README.md                     # Documentação do projeto
└── .gitignore                    # Arquivos ignorados pelo Git
```

## Fluxo de Dados

1. **Importação de Dados**:
   - Os dados CSV da TBCA são processados e importados para o banco de dados SQLite
   - Categorias e taxonomias de alimentos são estabelecidas durante a importação

2. **API Backend**:
   - Fornece endpoints RESTful para acesso aos dados de alimentos
   - Gerencia autenticação de usuários e sessões
   - Calcula nutrientes para refeições e diários
   - Implementa lógica de recomendação

3. **Frontend**:
   - Interface intuitiva para busca e visualização de alimentos
   - Calculadora de nutrição para composição de refeições
   - Diário alimentar para registro e acompanhamento
   - Visualizações e gráficos para análise nutricional

## Fluxo de Usuário

1. **Visitante**:
   - Pode buscar alimentos e ver informações nutricionais
   - Pode usar a calculadora para composições simples
   - Precisa criar conta para salvar informações

2. **Usuário Registrado**:
   - Pode salvar preferências e restrições alimentares
   - Mantém diário alimentar e histórico
   - Recebe recomendações personalizadas
   - Pode exportar relatórios nutricionais

3. **Profissional/Admin**:
   - Pode criar planos alimentares para outros usuários
   - Acesso a estatísticas e análises avançadas
   - Pode adicionar anotações e recomendações personalizadas
