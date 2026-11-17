# S04 — CNPJá Open

Português: [../pt-BR/sources/S04-cnpja-open.md](../pt-BR/sources/S04-cnpja-open.md) · All APIs: [suggestion by use case](../ranking.md)

> Highest relative completeness measured (99.8%; IBGE code, e-mail and Simples/MEI included). Limited to 5 requests/min per IP (4.5 CNPJs/min effective, 10.7% HTTP 429 at that pace); 13 of 36 companies opened on 2026-11-01..14 were answered HTTP 402 on the free tier. Suited to enriching individual records of established companies.

_Exploratory measurement, one collection window on 2026-11-16/17 (UTC), one client. Every number below comes from [results/summary.json](../../results/summary.json). Method: [methodology](../methodology.md)._

## Facts
| Item | Value |
|---|---|
| Endpoint | `GET https://open.cnpja.com/office/{cnpj}` |
| Authentication | none |
| Operator | Commercial company (CNPJá), free public tier |
| Website | https://cnpja.com |
| Documentation | https://cnpja.com/api/open |
| Source code | — |
| Documented limit | 5 requests per minute per IP ([cnpja.com/api/open](https://cnpja.com/api/open)) |
| Measured behaviour at the limit | 11% of requests answered 429 even when paced at 5 rpm |
| Data origin (declared) | own aggregation of Receita Federal and Simples Nacional data; states that it is not the original source ([terms](https://cnpja.com/subscription/tos)) |
| Update cadence (declared) | 'update guarantee of 45 days or less for active establishments' ([cnpja.com/api/open](https://cnpja.com/api/open)); per record (`updated`) |
| Terms of use | see [terms](https://cnpja.com/subscription/tos); restrictions for the free tier not confirmed |
| Alphanumeric CNPJ (measured) | accepts the format: wrong check digit → HTTP 400, alphanumeric example 12.ABC.345/01DE-35 → HTTP 404 |

## How to connect
```bash
curl -s 'https://open.cnpja.com/office/33000167000101'
```
```python
import requests
r = requests.get('https://open.cnpja.com/office/{cnpj}'.format(cnpj='33000167000101'), timeout=20)
data = r.json() if r.status_code == 200 else None   # 404 = not found, 429 = wait 60 s
```
```javascript
const r = await fetch(`https://open.cnpja.com/office/${cnpj}`);
const data = r.status === 200 ? await r.json() : null;
```

Nested English-keyed JSON (`company.name`, `address.municipality`, `mainActivity.id`). Company size comes as an acronym (`ME`, `EPP`, `DEMAIS`).

### Responses observed
| Case | HTTP | Body (start) |
|---|---|---|
| found | 200 | — |
| wrong check digit | 400 | `{"code":400,"message":"request validation failed","constraints":["taxId must be a string t` |
| alphanumeric example 12.ABC.345/01DE-35 | 404 | `{"code":404,"message":"tax id not registered at revenue service"}` |
| HTTP 429 | 429 | HTTP 429; recently founded companies: HTTP 402 `recently founded offices only available in commercial api` |

## Fields returned (measured)
| Canonical field | JSON path in the response | Filled % | Agrees with other sources % |
|---|---|---|---|
| `legal_name` | `company.name` | 100 | 100 |
| `trade_name` | `alias` | 66 | 100 |
| `establishment_type` | `head` | 100 | 100 |
| `registration_status` | `status.id` | 100 | 100 |
| `registration_status_date` | `statusDate` | 100 | 100 |
| `opening_date` | `founded` | 100 | 100 |
| `legal_nature_code` | `company.nature.id` | 100 | 100 |
| `legal_nature` | `company.nature.text` | 100 | 99 |
| `company_size` | `company.size.acronym` | 100 | 100 |
| `share_capital` | `company.equity` | 100 | 96 |
| `main_cnae` | `mainActivity.id` | 100 | 100 |
| `secondary_cnaes` | `sideActivities[].id` | 71 | 100 |
| `address_street` | `address.street` | 100 | 100 |
| `address_number` | `address.number` | 100 | 100 |
| `address_complement` | `address.details` | 48 | 100 |
| `address_district` | `address.district` | 100 | 100 |
| `address_city` | `address.city` | 100 | 100 |
| `address_state` | `address.state` | 100 | 100 |
| `address_zip` | `address.zip` | 100 | 100 |
| `address_city_ibge` | `address.municipality` | 100 | 100 |
| `phones` | `phones[].area + phones[].number` | 88 | 95 |
| `email` | `emails[0].address` | 79 | 100 |
| `partners` | `company.members[].person.name, company.members[].role.text` | 81 | 96 |
| `simples_optant` | `company.simples.optant` | 100 | 100 |
| `mei_optant` | `company.simei.optant` | 100 | 100 |

## Measured performance
| Item | Value |
|---|---|
| Coverage, wave 1 (95% Wilson interval; n = CNPJs with a conclusive answer) | 99.0% (97.1–99.7), n = 300 |
| Latency p50 / p95 | 326 / 538 ms |
| Effective throughput (pace used in brackets) | 4.5 CNPJs/min (5 req/min) |
| Share of attempts answered HTTP 429 at the pace used | 10.7% |
| Wave 2 ramp: HTTP 429 share at 1× / 2× / 4× the pace (attempted requests/min) | 12.5% @ 5 / 46.9% @ 10 / 76.9% @ 22 |
| Wave 2 unpaced bursts, 4 concurrent requests, 2 × 100 requests (attempted requests/min) | stopped after 10 consecutive HTTP 429 (test stop rule) (both) |

## Freshness
| Item | Value |
|---|---|
| Newest opening date returned | 2026-11-10 |
| Companies opened 2026-10-16 to 2026-11-14 that were returned (found / existing) | 70% (30/43) |
| Declared record age (p50 / p90) | 38 / 38 days |

## Observed issues
- Effective throughput 4.5 CNPJs per minute; 11% of requests rate-limited at the documented pace.
- Phones missing in 5% of the records where other sources have them.
- Recently founded companies: HTTP 402 `recently founded offices only available in commercial api` for 13 of the 36 companies opened in 2026-11-01..14 that it was asked about.

## Evidence
- Reports: [wave 1, quality](../../results/wave1/REPORT.md) · [wave 2, rate limits](../../results/wave2/REPORT.md) · [freshness](../../results/freshness/REPORT.md)
- Connector code: [s04_cnpja_open.py](../../src/cnpjbench/connectors/s04_cnpja_open.py)
