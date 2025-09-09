# Checklist de Envio do Projeto

## 📥 Primeiro Envio (Código do Projeto)

### Arquivos Principais
- [ ] importar_tbca_completo.py
- [ ] menu_tbca_completo.py
- [ ] check_database.py
- [ ] check_database_avancado.py
- [ ] verificacao_inicial_dev.py
- [ ] README.md
- [ ] INSTRUCOES_SEGUNDO_ENVIO.md

### Diretórios
- [ ] nutri-app/ (com estrutura completa)
- [ ] scripts/ (com scripts de migração)
- [ ] dados/ (com arquivos pequenos)
- [ ] logs/ (diretório vazio para logs)

### Arquivos de Amostra
- [ ] composicao_amostra.csv (200 primeiras linhas)

### Verificações
- [ ] Executar verificar_envio.bat para testar
- [ ] Confirmar que verificacao_inicial_dev.py roda sem erros
- [ ] Confirmar que README.md tem instruções claras

## 📦 Segundo Envio (Base de Dados)

### Arquivos
- [ ] composicao_todos_alimentos.csv (arquivo completo)

### Verificações
- [ ] Verificar integridade do arquivo CSV
- [ ] Confirmar tamanho (deve ser ~40-50MB)
- [ ] Testar importação antes de enviar
- [ ] Confirmar que INSTRUCOES_SEGUNDO_ENVIO.md está atualizado

## 📧 Métodos de Envio

### Primeiro Envio
- [ ] Comprimir pasta EnvioParaDev (zip/rar)
- [ ] Enviar por e-mail (se <10MB)
- [ ] Ou usar WeTransfer/Google Drive (se >10MB)
- [ ] Confirmar recebimento com o dev

### Segundo Envio
- [ ] Comprimir arquivo CSV (opcional)
- [ ] Usar serviço de compartilhamento (Google Drive, Dropbox)
- [ ] Fornecer link com validade extendida
- [ ] Confirmar download bem-sucedido

## 📝 Comunicação com o Dev
- [ ] Explicar claramente o processo de duas etapas
- [ ] Mencionar tempo estimado para importação (5-10 min)
- [ ] Solicitar confirmação após configuração inicial
- [ ] Oferecer suporte para dúvidas durante o processo
