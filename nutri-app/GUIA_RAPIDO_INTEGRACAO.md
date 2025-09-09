# NutriApp TBCA - Guia Rápido de Integração

## Scripts de Integração Adicionados

1. **Script de Teste de Integração:**
   ```
   backend/tests/test_integracao.py
   ```
   Teste automatizado para verificar a conexão entre frontend e backend

2. **Script PowerShell de Integração:**
   ```
   ./iniciar-integracao.ps1
   ```
   Menu interativo para instalar dependências, iniciar serviços e testar a integração

## Como Usar

Execute o script de integração para iniciar facilmente todo o ambiente:

```powershell
./iniciar-integracao.ps1
```

### Opções do Menu

1. **Instalar dependências** - Configura o ambiente Python e Node.js
2. **Iniciar Backend** - Inicia o servidor FastAPI
3. **Iniciar Frontend** - Inicia o servidor Next.js
4. **Testar Integração** - Executa o script de teste
5. **Iniciar tudo** - Executa todas as etapas acima
6. **Sair** - Encerra o script

## Endpoints Principais

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Documentação API: http://localhost:8000/docs

## Recursos

- Documentação completa: [docs/INTEGRACAO_FRONTEND_BACKEND.md](./docs/INTEGRACAO_FRONTEND_BACKEND.md)
- Logs de integração: diretório `logs/`

## Solução de Problemas

Se encontrar dificuldades, verifique os logs de integração gerados durante a execução do script. Eles contêm informações detalhadas sobre cada etapa do processo.
