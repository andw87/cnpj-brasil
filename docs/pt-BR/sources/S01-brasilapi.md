# S01 — BrasilAPI

English: [../../sources/S01-brasilapi.md](../../sources/S01-brasilapi.md) · Todas as APIs: [sugestão por caso de uso](../ranking.md)

> Proxy da Minha Receita (S02): mesmos dados e mesmo frescor (base de 2026-11 no ar em 16/11/2026, dois dias após a publicação), sem chave. Ressalvas medidas: 404 servido de cache antigo para 8,8% dos CNPJs existentes (repita na forma pontuada), capital social acima de R$ 16.777.216 arredondado, HTTP 429 para uma segunda rajada sem ritmo.

_Medição exploratória, uma janela de coleta em 16–17/11/2026 (UTC), um cliente. Todos os números abaixo vêm de [results/summary.json](../../../results/summary.json). Método: [metodologia](../methodology.md)._

## Ficha
| Item | Valor |
|---|---|
| Endpoint | `GET https://brasilapi.com.br/api/cnpj/v1/{cnpj}` |
| Autenticação | nenhuma |
| Mantenedor | Projeto comunitário de código aberto (MIT), hospedado na Vercel |
| Site | https://brasilapi.com.br |
| Documentação | https://brasilapi.com.br/docs#tag/CNPJ |
| Código-fonte | https://github.com/BrasilAPI/BrasilAPI |
| Limite documentado | não documentado; o firewall da Vercel responde 403/429 para User-Agent vazio ou genérico ([#826](https://github.com/BrasilAPI/BrasilAPI/issues/826), [#835](https://github.com/BrasilAPI/BrasilAPI/issues/835)) |
| Comportamento medido no limite | nenhum 429 até ~190 req/min; uma segunda rajada sem ritmo no mesmo minuto recebeu 100% HTTP 429 (sem Retry-After) |
| Origem dos dados (declarada) | **proxy da Minha Receita (S02)**: a rota de CNPJ chama `https://minhareceita.org/{cnpj}` com timeout de 5 s ([services/cnpj.js](https://github.com/BrasilAPI/BrasilAPI/blob/main/services/cnpj.js)) |
| Atualização (declarada) | a mesma da Minha Receita, mais o cache de borda da Vercel (respostas 404 também ficam em cache) |
| Termos de uso | código MIT; não foram encontrados termos de uso da API |
| CNPJ alfanumérico (medido) | aceita o formato: dígito verificador errado → HTTP 400, exemplo alfanumérico 12.ABC.345/01DE-35 → HTTP 404 |

## Como conectar
```bash
curl -s 'https://brasilapi.com.br/api/cnpj/v1/33000167000101'
```
```python
import requests
r = requests.get('https://brasilapi.com.br/api/cnpj/v1/{cnpj}'.format(cnpj='33000167000101'), timeout=20)
data = r.json() if r.status_code == 200 else None   # 404 = not found (may be a cached 404), 400 = invalid CNPJ
```
```javascript
const r = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${cnpj}`);
const data = r.status === 200 ? await r.json() : null; // 404 may be a cached 404
```

Envie um `User-Agent` descritivo. Um 404 pode ser resposta antiga em cache: pedir a forma pontuada (`/api/cnpj/v1/12.345.678%2F0001-95`) evita a entrada de cache da forma sem pontuação.

### Respostas observadas
| Caso | HTTP | Corpo (início) |
|---|---|---|
| encontrado | 200 | — |
| dígito verificador errado | 400 | `{"message":"CNPJ 33.000.167/0001-02 inválido.","type":"bad_request","name":"BadRequestErro` |
| exemplo alfanumérico 12.ABC.345/01DE-35 | 404 | `{"message":"CNPJ 12.ABC.345/01DE-35 não encontrado.","type":"not_found","name":"NotFoundEr` |
| HTTP 429 | 429 | HTTP 429, sem cabeçalhos de limite |

## Campos retornados (medidos)
| Campo canônico | Caminho JSON na resposta | Preenchido % | Concorda com outras fontes % |
|---|---|---|---|
| `legal_name` | `razao_social` | 100 | 100 |
| `trade_name` | `nome_fantasia` | 67 | 100 |
| `establishment_type` | `identificador_matriz_filial` | 100 | 100 |
| `registration_status` | `situacao_cadastral` | 100 | 100 |
| `registration_status_date` | `data_situacao_cadastral` | 99 | 100 |
| `opening_date` | `data_inicio_atividade` | 100 | 100 |
| `legal_nature_code` | `codigo_natureza_juridica` | 100 | 100 |
| `legal_nature` | `natureza_juridica` | 100 | 100 |
| `company_size` | `porte` | 100 | 100 |
| `share_capital` | `capital_social` | 100 | 90 |
| `main_cnae` | `cnae_fiscal` | 100 | 100 |
| `secondary_cnaes` | `cnaes_secundarios[].codigo` | 70 | 100 |
| `address_street` | `descricao_tipo_de_logradouro + logradouro` | 86 | 100 |
| `address_number` | `numero` | 86 | 100 |
| `address_complement` | `complemento` | 44 | 100 |
| `address_district` | `bairro` | 100 | 100 |
| `address_city` | `municipio` | 100 | 100 |
| `address_state` | `uf` | 100 | 100 |
| `address_zip` | `cep` | 100 | 100 |
| `address_city_ibge` | `codigo_municipio_ibge` | 100 | 100 |
| `phones` | `ddd_telefone_1, ddd_telefone_2` | 79 | 100 |
| `email` | `email` | não retorna | — |
| `partners` | `qsa[].nome_socio, qsa[].qualificacao_socio` | 80 | 96 |
| `simples_optant` | `opcao_pelo_simples` | 57 | 100 |
| `mei_optant` | `opcao_pelo_mei` | 57 | 100 |

## Desempenho medido
| Item | Valor |
|---|---|
| Cobertura, onda 1 (intervalo de Wilson de 95%; n = CNPJs com resposta conclusiva) | 90,3% (86,5–93,2), n = 300 |
| Latência p50 / p95 | 412 / 488 ms |
| Vazão efetiva (ritmo usado entre parênteses) | 60,3 CNPJs/min (60 req/min) |
| Tentativas respondidas com HTTP 429 no ritmo usado | 0,0% |
| Onda 2, rampa: proporção de HTTP 429 a 1× / 2× / 4× o ritmo (requisições tentadas/min) | 0,0% @ 61 / 0,0% @ 115 / 0,0% @ 189 |
| Onda 2, rajadas sem ritmo, 4 requisições simultâneas, 2 × 100 requisições (requisições tentadas/min) | 0,0% @ 858 / interrompida após 10 respostas HTTP 429 seguidas (regra de parada do teste) |

## Frescor
| Item | Valor |
|---|---|
| Abertura mais recente retornada | 14/11/2026 |
| Empresas abertas de 16/10/2026 a 14/11/2026 retornadas (encontradas / existentes) | 96% (64/67) |
| Idade declarada do registro (p50 / p90) | — |

## Problemas observados
- **404 antigos em cache.** 26 dos 297 CNPJs existentes (8,8%) receberam 404; a BrasilAPI repassa o CNPJ sem pontuação à Minha Receita, cuja CDN serviu 404 antigos em cache. Os 26 foram retornados (200) quando pedidos na forma pontuada, que escapa do cache. A concentração em sociedades anônimas é compatível com a hipótese de CNPJs muito consultados terem entrado no cache durante falhas da origem; a causa não foi determinada.
- Capital social acima de 16.777.216 é arredondado (float32): 26 de 39 valores nessa faixa diferem das outras fontes, ex.: 4.443.409.696,10 → 4.443.410.000.
- Não retorna e-mail; logradouro e número ausentes em 14% dos registros; Simples/MEI preenchidos em 57% dos registros.
- Herda as quedas da Minha Receita: erros 503 relatados em outubro de 2026 ([#916](https://github.com/BrasilAPI/BrasilAPI/issues/916), [#920](https://github.com/BrasilAPI/BrasilAPI/issues/920)).

## Evidências
- Relatórios: [onda 1, qualidade](../../../results/wave1/REPORT.pt-BR.md) · [onda 2, limites](../../../results/wave2/REPORT.pt-BR.md) · [frescor](../../../results/freshness/REPORT.pt-BR.md)
- Código do conector: [s01_brasilapi.py](../../../src/cnpjbench/connectors/s01_brasilapi.py)
