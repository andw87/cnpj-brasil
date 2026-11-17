# S03 — ReceitaWS

Português: [../pt-BR/sources/S03-receitaws.md](../pt-BR/sources/S03-receitaws.md) · All APIs: [suggestion by use case](../ranking.md)

> Coverage 99.0% of existing companies, but 2.5 CNPJs/min effective at the documented 3 requests/min, 16.0% HTTP 429 at that pace, the free tier serves only its own cache, and the terms forbid commercial use. Suited to occasional lookups.

_Exploratory measurement, one collection window on 2026-11-16/17 (UTC), one client. Every number below comes from [results/summary.json](../../results/summary.json). Method: [methodology](../methodology.md)._

## Facts
| Item | Value |
|---|---|
| Endpoint | `GET https://receitaws.com.br/v1/cnpj/{cnpj}` |
| Authentication | none (free tier) |
| Operator | Commercial company (ReceitaWS) |
| Website | https://receitaws.com.br |
| Documentation | https://developers.receitaws.com.br |
| Source code | — |
| Documented limit | 3 requests per minute (free tier) |
| Measured behaviour at the limit | `X-RateLimit-Limit: 3`; 16% of requests answered 429 even when paced at 3 rpm |
| Data origin (declared) | lookups of the Receita Federal website, stored in its own cache; the free API serves the cache only, a CNPJ not cached answers HTTP 504 ([spec](https://developers.receitaws.com.br/receitaws.yaml)) |
| Update cadence (declared) | per record (`ultima_atualizacao`) |
| Terms of use | personal benefit only, no commercial use ([terms](https://receitaws.com.br/terms.pdf)) |
| Alphanumeric CNPJ (measured) | accepts the format: wrong check digit → HTTP 400, alphanumeric example 12.ABC.345/01DE-35 → HTTP 200 |

## How to connect
```bash
curl -s 'https://receitaws.com.br/v1/cnpj/33000167000101'
```
```python
import requests
r = requests.get('https://receitaws.com.br/v1/cnpj/{cnpj}'.format(cnpj='33000167000101'), timeout=20)
data = r.json(); ok = r.status_code == 200 and data.get('status') != 'ERROR'   # errors come as HTTP 200
```
```javascript
const r = await fetch(`https://receitaws.com.br/v1/cnpj/${cnpj}`);
const data = await r.json(); const ok = r.status === 200 && data.status !== 'ERROR'; // errors come as HTTP 200
```

Errors are returned with HTTP 200 and `{"status": "ERROR", "message": ...}`. Dates are `dd/mm/yyyy`; legal nature is `"206-2 - Sociedade Empresária Limitada"`.

### Responses observed
| Case | HTTP | Body (start) |
|---|---|---|
| found | 200 | — |
| wrong check digit | 400 | `{   "status": "ERROR",   "message": "CNPJ inválido" }` |
| alphanumeric example 12.ABC.345/01DE-35 | 200 | `{   "cnpj": "12.ABC.345/01DE-35",   "ultima_atualizacao": "2026-11-10T18:44:35.100Z",   "s` |
| HTTP 429 | 429 | HTTP 429 with `X-RateLimit-Limit`, `X-RateLimit-Remaining` |

## Fields returned (measured)
| Canonical field | JSON path in the response | Filled % | Agrees with other sources % |
|---|---|---|---|
| `legal_name` | `nome` | 100 | 100 |
| `trade_name` | `fantasia` | 66 | 100 |
| `establishment_type` | `tipo` | 100 | 100 |
| `registration_status` | `situacao` | 100 | 100 |
| `registration_status_date` | `data_situacao` | 100 | 100 |
| `opening_date` | `abertura` | 100 | 100 |
| `legal_nature_code` | `natureza_juridica` | 100 | 100 |
| `legal_nature` | `natureza_juridica` | 100 | 100 |
| `company_size` | `porte` | 100 | 100 |
| `share_capital` | `capital_social` | 100 | 96 |
| `main_cnae` | `atividade_principal[0].code` | 73 | 100 |
| `secondary_cnaes` | `atividades_secundarias[].code` | 51 | 100 |
| `address_street` | `logradouro` | 100 | 96 |
| `address_number` | `numero` | 100 | 100 |
| `address_complement` | `complemento` | 48 | 100 |
| `address_district` | `bairro` | 100 | 100 |
| `address_city` | `municipio` | 100 | 100 |
| `address_state` | `uf` | 100 | 100 |
| `address_zip` | `cep` | 100 | 100 |
| `address_city_ibge` | — | not returned | — |
| `phones` | `telefone` | 93 | 85 |
| `email` | `email` | 79 | 100 |
| `partners` | `qsa[].nome, qsa[].qual` | 67 | 98 |
| `simples_optant` | `simples.optante` | 100 | 100 |
| `mei_optant` | `simei.optante` | 100 | 100 |

## Measured performance
| Item | Value |
|---|---|
| Coverage, wave 1 (95% Wilson interval; n = CNPJs with a conclusive answer) | 99.0% (97.1–99.7), n = 300 |
| Latency p50 / p95 | 238 / 287 ms |
| Effective throughput (pace used in brackets) | 2.5 CNPJs/min (3 req/min) |
| Share of attempts answered HTTP 429 at the pace used | 16.0% |
| Wave 2 ramp: HTTP 429 share at 1× / 2× / 4× the pace (attempted requests/min) | 15.6% @ 3 / 56.2% @ 6 / 77.8% @ 12 |
| Wave 2 unpaced bursts, 4 concurrent requests, 2 × 100 requests (attempted requests/min) | stopped after 10 consecutive HTTP 429 (test stop rule) (both) |

## Freshness
| Item | Value |
|---|---|
| Newest opening date returned | 2026-10-27 |
| Companies opened 2026-10-16 to 2026-11-14 that were returned (found / existing) | 71% (5/7) |
| Declared record age (p50 / p90) | 35 / 35 days |

## Observed issues
- Main CNAE missing in 27% and partner list in 17% of the records where other sources have them.
- No IBGE municipality code.
- Phone field is free text and includes the fax number.
- Effective throughput 2.5 CNPJs per minute.
- New companies nobody has queried before are answered `{"status": "ERROR", "message": "not in cache"}` (HTTP 404) on the free tier.

## Evidence
- Reports: [wave 1, quality](../../results/wave1/REPORT.md) · [wave 2, rate limits](../../results/wave2/REPORT.md) · [freshness](../../results/freshness/REPORT.md)
- Connector code: [s03_receitaws.py](../../src/cnpjbench/connectors/s03_receitaws.py)
