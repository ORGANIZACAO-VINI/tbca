# TBCA Web - Plataforma Web para Consulta de Dados Nutricionais

Este projeto é uma aplicação web para consulta da Tabela Brasileira de Composição de Alimentos (TBCA), permitindo que usuários busquem informações nutricionais de diversos alimentos brasileiros.

## Características

- Interface web intuitiva para busca de alimentos
- Filtragem por categorias (frutas, verduras, cereais, etc.)
- Visualização detalhada dos dados nutricionais
- API REST para acesso programático aos dados
- Responsivo para uso em diferentes dispositivos

## Requisitos

- Python 3.6+
- Flask
- Pandas
- Arquivos CSV/JSON com dados da TBCA

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Crie um ambiente virtual:
   ```
   python -m venv .venv
   ```
3. Ative o ambiente virtual:
   - Windows: `.\.venv\Scripts\Activate.ps1`
   - Linux/Mac: `source .venv/bin/activate`
4. Instale as dependências:
   ```
   pip install flask pandas
   ```

## Uso

1. Inicie a aplicação:
   ```
   python tbca_web/app.py
   ```
2. Acesse a aplicação no navegador em `http://localhost:5000`

## Estrutura de Arquivos

```
tbca_web/
├── app.py                  # Aplicação Flask principal
├── static/                 # Arquivos estáticos
│   ├── css/                # Estilos CSS
│   │   └── style.css       # Estilos personalizados
│   └── js/                 # Scripts JavaScript
│       └── main.js         # Script principal
└── templates/              # Templates HTML
    ├── index.html          # Página inicial
    ├── resultados.html     # Página de resultados de busca
    ├── detalhe.html        # Página de detalhes do alimento
    └── erro.html           # Página de erro
```

## API REST

A API REST está disponível nos seguintes endpoints:

- `GET /api/alimentos`: Retorna lista de alimentos
  - Parâmetros:
    - `termo`: Termo para busca (opcional)
    - `categoria`: Categoria de alimentos (opcional)
    - `limite`: Número máximo de resultados (padrão: 50)

## Exemplo de Uso da API

```
GET /api/alimentos?termo=arroz&categoria=cereais&limite=10
```

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.
