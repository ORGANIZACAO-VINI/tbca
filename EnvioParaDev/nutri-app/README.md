# Aplicativo Web de Nutrição TBCA

Este é um projeto de aplicativo web para consulta e análise de dados nutricionais baseado na Tabela Brasileira de Composição de Alimentos (TBCA).

## Visão Geral

O aplicativo permite aos usuários:
- Buscar alimentos e visualizar suas informações nutricionais
- Calcular valores nutricionais de refeições
- Montar diários alimentares
- Visualizar gráficos de composição nutricional
- Exportar relatórios personalizados

## Estrutura do Projeto

O projeto segue uma arquitetura de aplicação web moderna:
- **Backend**: API REST desenvolvida com FastAPI e SQLite
- **Frontend**: Interface de usuário desenvolvida com Next.js e React

Para detalhes completos sobre a estrutura do projeto, consulte o arquivo [ESTRUTURA_WEBAPP.md](./docs/ESTRUTURA_WEBAPP.md).

## Início Rápido

Para instruções de configuração e execução do projeto, consulte o [GUIA_INICIO_RAPIDO.md](./docs/GUIA_INICIO_RAPIDO.md).

## Integração Frontend-Backend

Para testar a integração entre o frontend e o backend, siga as instruções em [INTEGRACAO_FRONTEND_BACKEND.md](./docs/INTEGRACAO_FRONTEND_BACKEND.md).

## Checklist de Desenvolvimento

Para acompanhar o progresso do desenvolvimento, utilize o [CHECKLIST_NUTRI_APP.md](./docs/CHECKLIST_NUTRI_APP.md).

## Tarefas Pendentes

Para uma lista detalhada de tarefas de implementação, consulte [TODO_WEBAPP.md](./docs/TODO_WEBAPP.md).

## Importação de Dados

O projeto inclui scripts para importação de dados:
- `import_csv_to_sqlite.py` - Para importar dados CSV da TBCA
- `custom_import.py` - Para importar dados em formato JSON

Consulte a documentação em [INSTRUCOES_IMPORTACAO.md](./backend/INSTRUCOES_IMPORTACAO.md) para detalhes sobre o processo de importação.

## Tecnologias Utilizadas

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **Frontend**: TypeScript, Next.js, React, TailwindCSS
- **Visualização de Dados**: Chart.js

## Licença

Este projeto está disponível sob a licença MIT.
