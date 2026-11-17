# S05 — CNPJ.ws (public API)

Português: [../pt-BR/sources/S05-cnpjws-public.md](../pt-BR/sources/S05-cnpjws-public.md) · All APIs: [suggestion by use case](../ranking.md)

> Returns state registrations (`inscricoes_estaduais`), which no other source in this study returns. 1.4 CNPJs/min effective at 3 requests/min; degraded during the test (12.4% of CNPJs ended in HTTP 500/504 or timeout); the terms forbid commercial use.

_Exploratory measurement, one collection window on 2026-11-16/17 (UTC), one client. Every number below comes from [results/summary.json](../../results/summary.json). Method: [methodology](../methodology.md)._

## Facts
| Item | Value |
|---|---|
| Endpoint | `GET https://publica.cnpj.ws/cnpj/{cnpj}` |
| Authentication | none |
| Operator | Commercial company (CNPJ.ws), free public tier |
| Website | https://www.cnpj.ws |
| Documentation | https://docs.cnpj.ws/referencia-de-api/api-publica |
| Source code | — |
| Documented limit | 3 requests per minute per IP; more than 360 HTTP 429 in an hour blocks the IP for 1 hour ([limits](https://docs.cnpj.ws/referencia-de-api/api-publica/limitacoes)) |
| Measured behaviour at the limit | `x-ratelimit-limit: 3`, `x-ratelimit-reset`; 11% of requests answered 429 at 3 rpm; from ~02:00 UTC on 2026-11-17 mostly HTTP 500/504 and timeouts |
| Data origin (declared) | Receita Federal, SEFAZ/SINTEGRA, Suframa, fetched periodically ([docs](https://docs.cnpj.ws)) |
| Update cadence (declared) | maximum lag 45 days ([terms](https://www.cnpj.ws/pt-BR/termos-de-uso)); per record (`atualizado_em`) |
| Terms of use | personal benefit only, no commercial use ([terms](https://www.cnpj.ws/pt-BR/termos-de-uso)) |
| Alphanumeric CNPJ (measured) | accepts the format: wrong check digit → HTTP 400, alphanumeric example 12.ABC.345/01DE-35 → HTTP 404 |

## How to connect
```bash
curl -s 'https://publica.cnpj.ws/cnpj/33000167000101'
```
```python
import requests
r = requests.get('https://publica.cnpj.ws/cnpj/{cnpj}'.format(cnpj='33000167000101'), timeout=20)
data = r.json() if r.status_code == 200 else None   # 429: wait for x-ratelimit-reset seconds
```
```javascript
const r = await fetch(`https://publica.cnpj.ws/cnpj/${cnpj}`);
const data = r.status === 200 ? await r.json() : null;
```

Establishment data is nested under `estabelecimento`; state registrations (`inscricoes_estaduais`) are included, which no other free source returns.

### Responses observed
| Case | HTTP | Body (start) |
|---|---|---|
| found | 504 | `      <!DOCTYPE html>       <html>       <head>           <meta name="viewport" content="w` |
| wrong check digit | 400 | `{"status":400,"titulo":"Requisição inválida","detalhes":"CNPJ inválido","validacao":[]}` |
| alphanumeric example 12.ABC.345/01DE-35 | 404 | `{"status":404,"titulo":"Não encontrado","detalhes":"Recurso não encontrado","validacao":[]` |
| HTTP 429 | 429 | HTTP 429 with `x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-reset` |

## Fields returned (measured)
| Canonical field | JSON path in the response | Filled % | Agrees with other sources % |
|---|---|---|---|
| `legal_name` | `razao_social` | 100 | 100 |
| `trade_name` | `estabelecimento.nome_fantasia` | 68 | 100 |
| `establishment_type` | `estabelecimento.tipo` | 100 | 100 |
| `registration_status` | `estabelecimento.situacao_cadastral` | 100 | 100 |
| `registration_status_date` | `estabelecimento.data_situacao_cadastral` | 97 | 100 |
| `opening_date` | `estabelecimento.data_inicio_atividade` | 100 | 100 |
| `legal_nature_code` | `natureza_juridica.id` | 100 | 100 |
| `legal_nature` | `natureza_juridica.descricao` | 100 | 99 |
| `company_size` | `porte.descricao` | 100 | 100 |
| `share_capital` | `capital_social` | 100 | 96 |
| `main_cnae` | `estabelecimento.atividade_principal.id` | 100 | 100 |
| `secondary_cnaes` | `estabelecimento.atividades_secundarias[].id` | 71 | 100 |
| `address_street` | `estabelecimento.tipo_logradouro + estabelecimento.logradouro` | 100 | 100 |
| `address_number` | `estabelecimento.numero` | 100 | 100 |
| `address_complement` | `estabelecimento.complemento` | 47 | 100 |
| `address_district` | `estabelecimento.bairro` | 100 | 100 |
| `address_city` | `estabelecimento.cidade.nome` | 100 | 100 |
| `address_state` | `estabelecimento.estado.sigla` | 100 | 100 |
| `address_zip` | `estabelecimento.cep` | 100 | 100 |
| `address_city_ibge` | `estabelecimento.cidade.ibge_id` | 100 | 100 |
| `phones` | `estabelecimento.ddd1 + telefone1, ddd2 + telefone2` | 91 | 100 |
| `email` | `estabelecimento.email` | 79 | 100 |
| `partners` | `socios[].nome, socios[].qualificacao_socio.descricao` | 82 | 79 |
| `simples_optant` | `simples.simples` | 61 | 100 |
| `mei_optant` | `simples.mei` | 61 | 100 |

## Measured performance
| Item | Value |
|---|---|
| Coverage, wave 1 (95% Wilson interval; n = CNPJs with a conclusive answer) | 99.1% (96.8–99.8), n = 226 |
| Latency p50 / p95 | 374 / 15,967 ms |
| Effective throughput (pace used in brackets) | 1.4 CNPJs/min (3 req/min) |
| Share of attempts answered HTTP 429 at the pace used | 11.0% |
| Wave 2 ramp: HTTP 429 share at 1× / 2× / 4× the pace (attempted requests/min) | not run: provider degraded (HTTP 500/504) |

## Freshness
| Item | Value |
|---|---|
| Newest opening date returned | 2026-10-27 |
| Companies opened 2026-10-16 to 2026-11-14 that were returned (found / existing) | 67% (2/3) |
| Declared record age (p50 / p90) | 38 / 38 days |

## Observed issues
- Degraded during the test: 12.4% of CNPJs ended in HTTP 500/504 or timeout; latency p95 16 s.
- Partner list agrees with the other sources in only 79% of records.
- Some records omit fields at the company's request.
- Freshness: the newest opening date in its own records is 2026-10-27; it also returned one company opened on 2026-11-06 (date given by the other sources) whose record had no opening date.

## Evidence
- Reports: [wave 1, quality](../../results/wave1/REPORT.md) · [wave 2, rate limits](../../results/wave2/REPORT.md) · [freshness](../../results/freshness/REPORT.md)
- Connector code: [s05_cnpjws_public.py](../../src/cnpjbench/connectors/s05_cnpjws_public.py)
