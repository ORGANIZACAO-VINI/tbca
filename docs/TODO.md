# TODO - Melhorias no script de exportação TBCA

- [x] Adicionar tratamento de erros para requisições HTTP
- [x] Adicionar delay entre as requisições para evitar sobrecarga no site
- [x] Adicionar barra de progresso (tqdm)
- [x] Substituir Scrapy Selector por BeautifulSoup para simplificar dependências
- [x] Melhorar eficiência do código (opcional: paralelização segura)
- [x] Garantir que o script salve corretamente o CSV mesmo em caso de erro
- [x] Comentar e organizar o código final
- [x] Adicionar sistema de cache para links dos produtos
- [x] Implementar sistema de retentativas com backoff exponencial
- [x] Adicionar campos para mais nutrientes (fibras, cálcio, ferro)
- [x] Adicionar User-Agent e delays aleatórios para evitar bloqueios
- [x] Adicionar opções de linha de comando (argparse)
- [x] Implementar sistema de checkpoints e backups
- [x] Adicionar tratamento para interrupções do usuário
- [x] Criar documentação completa (README.md)

## Possíveis melhorias futuras:
- [ ] Implementar multi-threading seguro para coleta em paralelo
- [ ] Adicionar suporte para proxy rotativo
- [ ] Criar interface gráfica simples
- [ ] Adicionar exportação para outros formatos (JSON, SQLite)
- [ ] Implementar opção de busca por alimento específico
