# Similar repositories: what already exists for CNPJ lookup

Português: [pesquisa-repositorios-similares.md](pesquisa-repositorios-similares.md) · Back to the [README](../README.en.md)

## How it was done
GitHub search on 2026-11-17 (`gh search repos`, sorted by stars) with the terms "cnpj api",
"consulta cnpj", "cnpj gratuito", "brasilapi", "minha receita", "receita federal cnpj",
"receita federal dados abertos cnpj", "dados abertos cnpj", "awesome brasil", "awesome brazil api",
"apis publicas brasil", "cnpj alfanumerico", "opencnpj", "cnpja", "receitaws", "benchmark cnpj" and
"comparativo api cnpj", plus the topics `cnpj`, `receita-federal` and `dados-abertos`. A web search
for "API de CNPJ gratuita qual usar" returned mostly vendor pages. Star counts are those of the
search date and change over time.

## Result

### CNPJ lookup APIs and their official clients
| Repository | What it is | Stars | Link |
|---|---|---|---|
| BrasilAPI/BrasilAPI | Public API with many Brazilian datasets (postal codes, CNPJ, banks and others); its CNPJ route queries Minha Receita | 11,588 | https://github.com/BrasilAPI/BrasilAPI |
| cuducos/minha-receita | Open-source web API for CNPJ lookups from Receita Federal open data; code now maintained on Codeberg | 1,611 | https://github.com/cuducos/minha-receita |
| Hitmasu/OpenCNPJ | Public CNPJ search and lookup API (opencnpj.org) | 430 | https://github.com/Hitmasu/OpenCNPJ |
| cnpj-ws/consultar-cnpj | Client package for the CNPJ.ws API | 60 | https://github.com/cnpj-ws/consultar-cnpj |
| opencaramelo/opencnpj | Free public CNPJ lookup API (opencnpj.com) | 31 | https://github.com/opencaramelo/opencnpj |
| cnpja/sdk-nodejs | Official CNPJá SDK for Node.js | 11 | https://github.com/cnpja/sdk-nodejs |

### CNPJ open data (loading the full Receita Federal release)
| Repository | What it is | Stars | Link |
|---|---|---|---|
| fabioserpa/CNPJ-full | Python utility that reads the public CNPJ data and loads it into a database | 509 | https://github.com/fabioserpa/CNPJ-full |
| aphonsoar/Receita_Federal_do_Brasil_-_Dados_Publicos_CNPJ | Extraction and loading of the Receita Federal public CNPJ data | 460 | https://github.com/aphonsoar/Receita_Federal_do_Brasil_-_Dados_Publicos_CNPJ |
| rictom/rede-cnpj | Visualisation of partner–company relationships from public CNPJ data | 352 | https://github.com/rictom/rede-cnpj |
| caiopizzol/cnpj-data-pipeline | Pipeline that downloads and processes Receita Federal data into PostgreSQL | 345 | https://github.com/caiopizzol/cnpj-data-pipeline |
| rictom/cnpj-sqlite | Loads the public CNPJ files into SQLite | 246 | https://github.com/rictom/cnpj-sqlite |

### CNPJ validation (including alphanumeric)
| Repository | What it is | Stars | Link |
|---|---|---|---|
| brazilian-utils/javascript | Utilities for Brazilian data, including CNPJ validation | 1,687 | https://github.com/brazilian-utils/javascript |
| klawdyo/validation-br | Validation of Brazilian documents, with numeric and alphanumeric CNPJ | 76 | https://github.com/klawdyo/validation-br |
| gabrielfroes/novo-cnpj | Alphanumeric CNPJ validator in TypeScript | 45 | https://github.com/gabrielfroes/novo-cnpj |

### Lists of Brazilian public APIs
| Repository | What it is | Stars | Link |
|---|---|---|---|
| Mcp-Brasil/mcp-brasil | MCP server (a protocol for AI assistants) for 70 Brazilian public APIs | 1,865 | https://github.com/Mcp-Brasil/mcp-brasil |
| vinicius73/awesome-brasil | List of Brazilian open-source projects | 232 | https://github.com/vinicius73/awesome-brasil |
| IF-TI/APIs-PublicasBrasil | Compilation of Brazilian public APIs | 12 | https://github.com/IF-TI/APIs-PublicasBrasil |
| LuisGustavoDev/apis-publicas-brasil | List of free Brazilian public APIs, checked automatically every day | 9 | https://github.com/LuisGustavoDev/apis-publicas-brasil |

## How these projects present themselves
- **Names:** short and containing the domain word (`minha-receita`, `OpenCNPJ`, `BrasilAPI`, `cnpj-sqlite`).
- **Descriptions:** one sentence in Portuguese saying what the project does: "API web para consulta
  de informações do CNPJ da Receita Federal", "API pública de busca e consulta de CNPJs do Brasil".
- **Recurring terms:** "consulta CNPJ", "API", "pública", "gratuita", "dados abertos",
  "dados públicos", "Receita Federal", "CNPJ alfanumérico".
- **Most used topics:** `cnpj`, `receita-federal`, `dados-abertos`, `brasil`, `brazil`, `api`,
  `open-data`, `etl`.
- **README opening:** what it is, a sample call and the link to the service.

## Where this repository fits
The projects above are APIs, clients, full-release loaders, validators and lists. In the searches
made, no repository was found that measures the free CNPJ APIs against each other with one method
and publishes the numbers (the searches "benchmark cnpj" and "comparativo api cnpj" returned no
comparisons of lookup APIs). This repository fills that gap: it is a measured comparison with a
suggestion by use case, not a new API.

It depends on the work of the people who maintain these APIs and datasets. The weak points reported
here (for example, cached 404s or release lag) were measured over one night and are meant to guide
integration, not to judge the projects. Corrections from maintainers are welcome through issues.
