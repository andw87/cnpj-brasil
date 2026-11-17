# S07 — OpenCNPJ.com (Kitana API)

Português: [../pt-BR/sources/S07-opencnpj-com.md](../pt-BR/sources/S07-opencnpj-com.md) · All APIs: [suggestion by use case](../ranking.md)

> Lowest latency measured (p50 53 ms, p95 94 ms); documented limit 300 requests/min. Data about two months behind (the newest company returned opened on 2026-09-11); no license for reuse.

_Exploratory measurement, one collection window on 2026-11-16/17 (UTC), one client. Every number below comes from [results/summary.json](../../results/summary.json). Method: [methodology](../methodology.md)._

## Facts
| Item | Value |
|---|---|
| Endpoint | `GET https://kitana.opencnpj.com/cnpj/{cnpj}` |
| Authentication | none |
| Operator | OpenCaramelo — a different project from OpenCNPJ.org despite the name |
| Website | https://opencnpj.com |
| Documentation | https://opencnpj.com |
| Source code | https://github.com/opencaramelo/opencnpj |
| Documented limit | 300 requests per minute per IP (response headers `X-Ratelimit-Limit: 300`) |
| Measured behaviour at the limit | no 429 up to ~4,700 rpm (4 concurrent requests) |
| Data origin (declared) | 'official Receita Federal sources'; pipeline not documented |
| Update cadence (declared) | not documented; measured: newest company returned opened on 2026-09-11 |
| Terms of use | no license in the repository; 'all rights reserved' on the site |
| Alphanumeric CNPJ (measured) | accepts the format: wrong check digit → HTTP 400, alphanumeric example 12.ABC.345/01DE-35 → HTTP 404 |

## How to connect
```bash
curl -s 'https://kitana.opencnpj.com/cnpj/33000167000101'
```
```python
import requests
r = requests.get('https://kitana.opencnpj.com/cnpj/{cnpj}'.format(cnpj='33000167000101'), timeout=20)
body = r.json() if r.status_code == 200 else {}; data = body.get('data') if body.get('success') else None
```
```javascript
const r = await fetch(`https://kitana.opencnpj.com/cnpj/${cnpj}`);
const body = r.status === 200 ? await r.json() : {}; const data = body.success ? body.data : null;
```

Envelope `{"success": true, "data": {...}}`; camelCase keys; dates `dd/mm/yyyy`; legal nature as `"Text (2062)"`; the first item of `cnaes` is the main CNAE.

### Responses observed
| Case | HTTP | Body (start) |
|---|---|---|
| found | 200 | — |
| wrong check digit | 400 | `{"success":false,"message":"CNPJ inválido.","data":null}` |
| alphanumeric example 12.ABC.345/01DE-35 | 404 | — |

## Fields returned (measured)
| Canonical field | JSON path in the response | Filled % | Agrees with other sources % |
|---|---|---|---|
| `legal_name` | `data.razaoSocial` | 100 | 99 |
| `trade_name` | `data.nomeFantasia` | 66 | 100 |
| `establishment_type` | `data.matriz` | 100 | 100 |
| `registration_status` | `data.situacaoCadastral` | 100 | 100 |
| `registration_status_date` | `data.dataSituacaoCadastral` | 98 | 100 |
| `opening_date` | `data.dataInicioAtividades` | 100 | 100 |
| `legal_nature_code` | `data.naturezaJuridica` | 100 | 99 |
| `legal_nature` | `data.naturezaJuridica` | 100 | 99 |
| `company_size` | — | not returned | — |
| `share_capital` | `data.capitalSocial` | 100 | 96 |
| `main_cnae` | `data.cnaes[0].cnae` | 100 | 100 |
| `secondary_cnaes` | `data.cnaes[1:].cnae` | 71 | 100 |
| `address_street` | `data.logradouro` | 100 | 100 |
| `address_number` | `data.numero` | 100 | 100 |
| `address_complement` | `data.complemento` | 49 | 100 |
| `address_district` | `data.bairro` | 100 | 100 |
| `address_city` | `data.municipio` | 100 | 100 |
| `address_state` | `data.uf` | 100 | 100 |
| `address_zip` | `data.cep` | 100 | 100 |
| `address_city_ibge` | — | not returned | — |
| `phones` | `data.telefone` | 93 | 84 |
| `email` | `data.email` | 79 | 100 |
| `partners` | `data.socios[].nomeSocio, data.socios[].descricao` | 80 | 95 |
| `simples_optant` | `data.opcaoSimples` | 100 | 100 |
| `mei_optant` | `data.opcaoMei` | 100 | 100 |

## Measured performance
| Item | Value |
|---|---|
| Coverage, wave 1 (95% Wilson interval; n = CNPJs with a conclusive answer) | 99.0% (97.1–99.7), n = 300 |
| Latency p50 / p95 | 53 / 94 ms |
| Effective throughput (pace used in brackets) | 120.7 CNPJs/min (120 req/min) |
| Share of attempts answered HTTP 429 at the pace used | 0.0% |
| Wave 2 ramp: HTTP 429 share at 1× / 2× / 4× the pace (attempted requests/min) | 0.0% @ 123 / 0.0% @ 246 / 0.0% @ 487 |
| Wave 2 unpaced bursts, 4 concurrent requests, 2 × 100 requests (attempted requests/min) | 0.0% @ 4,187 / 0.0% @ 4,718 |

## Freshness
| Item | Value |
|---|---|
| Newest opening date returned | 2026-09-11 |
| Companies opened 2026-10-16 to 2026-11-14 that were returned (found / existing) | 0% (0/67) |
| Declared record age (p50 / p90) | — |

## Observed issues
- About two months behind: half of the companies opened in 2026-09-01..15 and none opened after 2026-09-15 were returned.
- No company size and no IBGE code; returns only the first phone number.

## Evidence
- Reports: [wave 1, quality](../../results/wave1/REPORT.md) · [wave 2, rate limits](../../results/wave2/REPORT.md) · [freshness](../../results/freshness/REPORT.md)
- Connector code: [s07_opencnpj_com.py](../../src/cnpjbench/connectors/s07_opencnpj_com.py)
