# TODO - Aplicativo Web de Nutrição TBCA

Este documento descreve o plano de implementação para o desenvolvimento de uma aplicação web de nutrição utilizando os dados da Tabela Brasileira de Composição de Alimentos (TBCA).

## Fase 1: Configuração Inicial e Backend API

Esta fase foca na estruturação do projeto e desenvolvimento do backend que servirá os dados nutricionais.

- [ ] **Configuração do Ambiente**
  - [ ] Configurar repositório Git
  - [ ] Criar estrutura de diretórios do projeto
  - [ ] Configurar ambiente virtual Python
  - [ ] Instalar dependências básicas (FastAPI, SQLite, Pandas)

- [ ] **Preparação dos Dados**
  - [ ] Converter dados CSV para formato SQLite
  - [ ] Normalizar nomes e valores (trocar vírgula por ponto nos valores numéricos)
  - [ ] Criar índices para pesquisa eficiente
  - [ ] Implementar sistema de categorização de alimentos

- [ ] **Desenvolvimento da API REST**
  - [ ] Configurar servidor FastAPI
  - [ ] Implementar endpoints para listar todos os alimentos
  - [ ] Implementar endpoint de busca por nome/termo
  - [ ] Implementar endpoint para detalhes de um alimento específico
  - [ ] Implementar filtros (por nutrientes, categoria, etc.)
  - [ ] Documentar API com Swagger/OpenAPI

- [ ] **Segurança e Desempenho**
  - [ ] Implementar rate limiting
  - [ ] Configurar CORS
  - [ ] Adicionar caching para requisições comuns
  - [ ] Criar testes unitários e de integração

## Fase 2: Frontend Básico e Funcionalidades Essenciais

Esta fase foca na criação da interface do usuário e implementação das funcionalidades principais.

- [ ] **Configuração do Frontend**
  - [ ] Configurar projeto Next.js/React
  - [ ] Implementar sistema de rotas
  - [ ] Criar componentes reutilizáveis (cards, inputs, botões)
  - [ ] Configurar sistema de estilos (TailwindCSS ou styled-components)

- [ ] **Funcionalidades de Busca e Visualização**
  - [ ] Criar página inicial com busca de alimentos
  - [ ] Implementar exibição de resultados em cards
  - [ ] Criar página de detalhes de alimento
  - [ ] Adicionar visualizações gráficas de nutrientes
  - [ ] Implementar sistema de comparação de alimentos

- [ ] **Calculadora de Nutrição**
  - [ ] Criar interface para seleção de alimentos e porções
  - [ ] Implementar cálculo de nutrientes totais
  - [ ] Adicionar funcionalidade para salvar refeições
  - [ ] Implementar gráficos de distribuição de macronutrientes
  - [ ] Adicionar sugestões de complementos nutricionais

- [ ] **Testes e Otimização**
  - [ ] Realizar testes de usabilidade
  - [ ] Otimizar desempenho do frontend
  - [ ] Garantir responsividade para dispositivos móveis
  - [ ] Implementar feedback visual para ações do usuário

## Fase 3: Contas de Usuário e Funcionalidades Avançadas

Esta fase adiciona sistema de usuários e funcionalidades mais avançadas para personalização.

- [ ] **Sistema de Autenticação**
  - [ ] Implementar registro e login de usuários
  - [ ] Adicionar autenticação com OAuth (Google, Facebook)
  - [ ] Criar sistema de recuperação de senha
  - [ ] Implementar perfis de usuário
  - [ ] Adicionar níveis de acesso (usuário regular, profissional, admin)

- [ ] **Diário Alimentar**
  - [ ] Criar interface de diário alimentar
  - [ ] Implementar adição de refeições por data/horário
  - [ ] Adicionar cálculos de nutrientes diários
  - [ ] Criar visualizações de progresso semanal/mensal
  - [ ] Implementar sistema de metas nutricionais

- [ ] **Recomendações Personalizadas**
  - [ ] Desenvolver algoritmo de recomendação de alimentos
  - [ ] Implementar sugestões baseadas no perfil nutricional
  - [ ] Adicionar alertas para deficiências nutricionais
  - [ ] Criar planos alimentares sugeridos
  - [ ] Implementar ajustes baseados em objetivos (perda de peso, ganho de massa, etc.)

- [ ] **Exportação e Integração**
  - [ ] Adicionar exportação de relatórios em PDF
  - [ ] Implementar compartilhamento de refeições e planos
  - [ ] Criar API para integração com apps de fitness
  - [ ] Adicionar importação de dados de outras plataformas

## Tecnologias Sugeridas

- **Backend**: FastAPI, SQLite/PostgreSQL, Pandas
- **Frontend**: Next.js, React, TailwindCSS
- **Autenticação**: JWT, OAuth
- **Visualização**: Chart.js, D3.js
- **Deploy**: Docker, Vercel, AWS/GCP

## Recursos Necessários

- Servidor para hospedagem da API
- Domínio para o aplicativo web
- Armazenamento para banco de dados
- Possível integração com serviços de email para notificações
