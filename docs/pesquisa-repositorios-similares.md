# Repositórios semelhantes: o que já existe sobre consulta de CNPJ

English: [similar-repositories.md](similar-repositories.md) · Voltar ao [README](../README.md)

## Como foi feito
Busca no GitHub em 17/11/2026 (`gh search repos`, ordenado por estrelas) com os termos
"cnpj api", "consulta cnpj", "cnpj gratuito", "brasilapi", "minha receita", "receita federal cnpj",
"receita federal dados abertos cnpj", "dados abertos cnpj", "awesome brasil", "awesome brazil api",
"apis publicas brasil", "cnpj alfanumerico", "opencnpj", "cnpja", "receitaws", "benchmark cnpj" e
"comparativo api cnpj", além dos tópicos `cnpj`, `receita-federal` e `dados-abertos`. Uma busca na
web por "API de CNPJ gratuita qual usar" trouxe sobretudo páginas de fornecedores. As estrelas são
as do dia da busca e mudam com o tempo.

## Resultado

### APIs de consulta CNPJ e seus clientes oficiais
| Repositório | O que é | Estrelas | Link |
|---|---|---|---|
| BrasilAPI/BrasilAPI | API pública com vários dados do Brasil (CEP, CNPJ, bancos e outros); a rota de CNPJ consulta a Minha Receita | 11.588 | https://github.com/BrasilAPI/BrasilAPI |
| cuducos/minha-receita | API web de código aberto para consulta de CNPJ a partir dos dados abertos da Receita Federal; código hoje mantido no Codeberg | 1.611 | https://github.com/cuducos/minha-receita |
| Hitmasu/OpenCNPJ | API pública de busca e consulta de CNPJs (opencnpj.org) | 430 | https://github.com/Hitmasu/OpenCNPJ |
| cnpj-ws/consultar-cnpj | Pacote cliente da API CNPJ.ws | 60 | https://github.com/cnpj-ws/consultar-cnpj |
| opencaramelo/opencnpj | API pública e gratuita de consulta de CNPJ (opencnpj.com) | 31 | https://github.com/opencaramelo/opencnpj |
| cnpja/sdk-nodejs | SDK oficial da CNPJá para Node.js | 11 | https://github.com/cnpja/sdk-nodejs |

### Dados abertos do CNPJ (carga da base completa da Receita Federal)
| Repositório | O que é | Estrelas | Link |
|---|---|---|---|
| fabioserpa/CNPJ-full | Utilitário em Python para ler os dados públicos do CNPJ e carregá-los em banco | 509 | https://github.com/fabioserpa/CNPJ-full |
| aphonsoar/Receita_Federal_do_Brasil_-_Dados_Publicos_CNPJ | Extração e carga dos dados públicos de CNPJ da Receita Federal | 460 | https://github.com/aphonsoar/Receita_Federal_do_Brasil_-_Dados_Publicos_CNPJ |
| rictom/rede-cnpj | Visualização das relações entre sócios e empresas com dados públicos de CNPJ | 352 | https://github.com/rictom/rede-cnpj |
| caiopizzol/cnpj-data-pipeline | Pipeline que baixa e processa os dados da Receita Federal para PostgreSQL | 345 | https://github.com/caiopizzol/cnpj-data-pipeline |
| rictom/cnpj-sqlite | Carga dos arquivos públicos de CNPJ em SQLite | 246 | https://github.com/rictom/cnpj-sqlite |

### Validação de CNPJ (inclusive alfanumérico)
| Repositório | O que é | Estrelas | Link |
|---|---|---|---|
| brazilian-utils/javascript | Utilitários para dados brasileiros, inclusive validação de CNPJ | 1.687 | https://github.com/brazilian-utils/javascript |
| klawdyo/validation-br | Validação de documentos brasileiros, com CNPJ numérico e alfanumérico | 76 | https://github.com/klawdyo/validation-br |
| gabrielfroes/novo-cnpj | Validador de CNPJ alfanumérico em TypeScript | 45 | https://github.com/gabrielfroes/novo-cnpj |

### Listas de APIs públicas brasileiras
| Repositório | O que é | Estrelas | Link |
|---|---|---|---|
| Mcp-Brasil/mcp-brasil | Servidor MCP (protocolo para assistentes de IA) para 70 APIs públicas brasileiras | 1.865 | https://github.com/Mcp-Brasil/mcp-brasil |
| vinicius73/awesome-brasil | Lista de projetos de código aberto brasileiros | 232 | https://github.com/vinicius73/awesome-brasil |
| IF-TI/APIs-PublicasBrasil | Compilação de APIs públicas brasileiras | 12 | https://github.com/IF-TI/APIs-PublicasBrasil |
| LuisGustavoDev/apis-publicas-brasil | Lista de APIs públicas e gratuitas do Brasil verificada automaticamente todos os dias | 9 | https://github.com/LuisGustavoDev/apis-publicas-brasil |

## Como esses projetos se apresentam
- **Nomes:** curtos e com a palavra do domínio (`minha-receita`, `OpenCNPJ`, `BrasilAPI`, `cnpj-sqlite`).
- **Descrições:** uma frase em português que diz o que o projeto faz: "API web para consulta de
  informações do CNPJ da Receita Federal", "API pública de busca e consulta de CNPJs do Brasil".
- **Termos que se repetem:** "consulta CNPJ", "API", "pública", "gratuita", "dados abertos",
  "dados públicos", "Receita Federal", "CNPJ alfanumérico".
- **Tópicos mais usados:** `cnpj`, `receita-federal`, `dados-abertos`, `brasil`, `brazil`, `api`,
  `open-data`, `etl`.
- **Abertura do README:** o que é, um exemplo de chamada e o link do serviço.

## Onde este repositório se encaixa
Os projetos acima são APIs, clientes, cargas da base completa, validadores e listas. Nas buscas
feitas, não foi encontrado um repositório que meça as APIs gratuitas de CNPJ entre si com um mesmo
método e publique os números (as buscas "benchmark cnpj" e "comparativo api cnpj" não trouxeram
comparações de APIs de consulta). Este repositório ocupa esse espaço: é uma comparação medida, com
sugestão por caso de uso, e não uma nova API.

Ele depende do trabalho das pessoas que mantêm essas APIs e bases de dados. Os pontos fracos
apontados aqui (por exemplo, 404 em cache ou atraso de publicação) foram medidos em uma noite e
servem para orientar a integração, não para julgar os projetos. Correções dos mantenedores são
bem-vindas por issue.
