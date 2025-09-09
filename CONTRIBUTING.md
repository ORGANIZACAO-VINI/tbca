# Contribuindo para o Nutri-App

Primeiramente, obrigado por dedicar seu tempo para contribuir com o projeto! 🎉👍

Este documento estabelece as diretrizes para contribuir com o Nutri-App. Seguir estas diretrizes ajuda a comunicar que você respeita o tempo dos desenvolvedores que gerenciam e desenvolvem este projeto. Em troca, eles devem retribuir esse respeito abordando seu problema, avaliando mudanças e ajudando a finalizar suas solicitações de pull.

## Índice

- [Código de Conduta](#código-de-conduta)
- [Como Posso Contribuir?](#como-posso-contribuir)
  - [Reportando Bugs](#reportando-bugs)
  - [Sugerindo Melhorias](#sugerindo-melhorias)
  - [Contribuindo com Código](#contribuindo-com-código)
  - [Pull Requests](#pull-requests)
- [Padrões de Estilo](#padrões-de-estilo)
  - [Mensagens de Commit Git](#mensagens-de-commit-git)
  - [Python](#python)
  - [JavaScript/React](#javascriptreact)
  - [Documentação](#documentação)
- [Fluxo de Trabalho de Desenvolvimento](#fluxo-de-trabalho-de-desenvolvimento)

## Código de Conduta

Este projeto e todos os participantes são regidos por um [Código de Conduta](CODE_OF_CONDUCT.md). Ao participar, espera-se que você mantenha este código. Por favor, reporte comportamento inaceitável para [seu-email@exemplo.com].

## Como Posso Contribuir?

### Reportando Bugs

Esta seção orienta você através do envio de um relatório de bug. Seguir estas diretrizes ajuda os mantenedores a entender seu relatório, reproduzir o comportamento e encontrar relatórios relacionados.

Antes de criar relatórios de bugs, verifique a [lista de issues](https://github.com/seu-usuario/nutri-app/issues) para ver se o problema já foi reportado. Se encontrar um issue aberto, adicione um comentário em vez de abrir um novo.

**Ao reportar um bug, inclua:**
* **Título claro e descritivo** para identificar o problema
* **Passos precisos para reproduzir o problema** com o máximo de detalhes possível
* **Comportamento esperado e atual**
* **Screenshots** se aplicável
* **Ambiente** (SO, navegador, versão do Python, etc)
* **Contexto adicional** como logs ou configuração

### Sugerindo Melhorias

Esta seção orienta você através do envio de uma sugestão de melhoria, incluindo recursos completamente novos e pequenas melhorias nas funcionalidades existentes.

**Ao sugerir uma melhoria, inclua:**
* **Título claro e descritivo**
* **Descrição detalhada da melhoria proposta**
* **Justificativa** por que esta melhoria seria útil
* **Possível implementação** se tiver ideias
* **Referências relacionadas** como exemplos de outras aplicações

### Contribuindo com Código

#### Configuração Local de Desenvolvimento

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/nutri-app.git
   cd nutri-app
   ```

2. Configure o ambiente de desenvolvimento:
   ```bash
   # Backend
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate no Windows
   pip install -r backend/requirements.txt
   pip install -r backend/requirements-dev.txt  # Dependências de desenvolvimento

   # Frontend
   cd frontend
   npm install
   ```

3. Execute os testes para garantir que tudo está funcionando:
   ```bash
   # Backend
   python -m pytest

   # Frontend
   npm test
   ```

### Pull Requests

* Siga todas as instruções em [template de pull request](PULL_REQUEST_TEMPLATE.md)
* Inclua screenshots e GIFs animados em seu PR quando possível
* Documente novos códigos
* Siga os padrões de estilo do projeto
* Termine todas as frases em descrições com ponto
* Faça referência a issues relacionados

## Padrões de Estilo

### Mensagens de Commit Git

* Use o presente imperativo: "Adiciona funcionalidade" não "Adicionada funcionalidade"
* Limite a primeira linha a 72 caracteres ou menos
* Referencie issues e pull requests após a primeira linha
* Considere iniciar a mensagem de commit com um emoji aplicável:
  * 🎨 `:art:` ao melhorar a formatação/estrutura do código
  * ⚡️ `:zap:` ao melhorar performance
  * 🔥 `:fire:` ao remover código ou arquivos
  * 🐛 `:bug:` ao corrigir um bug
  * ✨ `:sparkles:` ao introduzir novas funcionalidades
  * 📝 `:memo:` ao adicionar ou atualizar documentação

### Python

* Siga [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use docstrings no formato Google Python Style Guide
* Organize imports na seguinte ordem:
  1. Imports da biblioteca padrão
  2. Imports relacionados a terceiros
  3. Imports locais da aplicação/biblioteca
* Utilize tipagem estática quando possível

### JavaScript/React

* Utilize o padrão do ESLint configurado no projeto
* Prefira componentes funcionais e hooks em React
* Utilize destructuring para props
* Separe lógica de negócio de componentes de UI
* Mantenha componentes pequenos e com responsabilidade única

### Documentação

* Use Markdown para documentação
* Atualize o README.md com detalhes de mudanças na interface
* Mantenha a documentação da API atualizada

## Fluxo de Trabalho de Desenvolvimento

1. Crie um branch a partir de `main`
2. Implemente suas mudanças
3. Execute os testes (`pytest` para backend, `npm test` para frontend)
4. Atualize a documentação se necessário
5. Envie um Pull Request para `main`
6. Aguarde revisão e feedback

---

Agradecemos suas contribuições para tornar o Nutri-App melhor para todos!
