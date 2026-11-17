# S06 — OpenCNPJ.org

Português: [../pt-BR/sources/S06-opencnpj-org.md](../pt-BR/sources/S06-opencnpj-org.md) · All APIs: [suggestion by use case](../ranking.md)

> Coverage 99.0%; 0% HTTP 429 up to 5,209 requests/min; commercial use allowed by its FAQ; full dataset downloadable. Data one monthly release behind: the newest company returned opened on 2026-10-08.

_Exploratory measurement, one collection window on 2026-11-16/17 (UTC), one client. Every number below comes from [results/summary.json](../../results/summary.json). Method: [methodology](../methodology.md)._

## Facts
| Item | Value |
|---|---|
| Endpoint | `GET https://api.opencnpj.org/{cnpj}` |
| Authentication | none |
| Operator | Non-profit open-source project (MIT) |
| Website | https://opencnpj.org |
| Documentation | https://opencnpj.org |
| Source code | https://github.com/Hitmasu/OpenCNPJ |
| Documented limit | no fixed quota; bursts above 100 requests/second accepted; sustained abuse → 429 ([opencnpj.org](https://opencnpj.org)) |
| Measured behaviour at the limit | no 429 up to ~5,200 rpm (4 concurrent requests) |
| Data origin (declared) | Receita Federal monthly release → ETL → static shards on Cloudflare R2; full dataset also downloadable; `/info` reports `source_snapshot_month: 2026-10` |
| Update cadence (declared) | monthly; the 2026-10 release (published 2026-10-13) was loaded on 2026-11-01 |
| Terms of use | code MIT; free use including commercial (site FAQ) |
| Alphanumeric CNPJ (measured) | no input validation (wrong check digit → 404) |

## How to connect
```bash
curl -s 'https://api.opencnpj.org/33000167000101'
```
```python
import requests
r = requests.get('https://api.opencnpj.org/{cnpj}'.format(cnpj='33000167000101'), timeout=20)
data = r.json() if r.status_code == 200 else None   # 404 = not found OR invalid CNPJ (no validation)
```
```javascript
const r = await fetch(`https://api.opencnpj.org/${cnpj}`);
const data = r.status === 200 ? await r.json() : null;
```

Validate the check digits yourself: the API answers 404 for an invalid CNPJ. `GET https://api.opencnpj.org/info` returns the release month and record count.

### Responses observed
| Case | HTTP | Body (start) |
|---|---|---|
| found | 200 | — |
| wrong check digit | 404 | `{"error":"not found"}` |
| alphanumeric example 12.ABC.345/01DE-35 | 404 | `{"error":"not found"}` |

## Fields returned (measured)
| Canonical field | JSON path in the response | Filled % | Agrees with other sources % |
|---|---|---|---|
| `legal_name` | `razao_social` | 100 | 98 |
| `trade_name` | `nome_fantasia` | 66 | 100 |
| `establishment_type` | `matriz_filial` | 100 | 100 |
| `registration_status` | `situacao_cadastral` | 100 | 100 |
| `registration_status_date` | `data_situacao_cadastral` | 98 | 100 |
| `opening_date` | `data_inicio_atividade` | 100 | 100 |
| `legal_nature_code` | `codigo_natureza_juridica` | 100 | 100 |
| `legal_nature` | `natureza_juridica` | 100 | 100 |
| `company_size` | `porte_empresa` | 100 | 100 |
| `share_capital` | `capital_social` | 100 | 96 |
| `main_cnae` | `cnae_principal` | 100 | 100 |
| `secondary_cnaes` | `cnaes_secundarios[]` | 71 | 100 |
| `address_street` | `tipo_logradouro + logradouro` | 100 | 100 |
| `address_number` | `numero` | 100 | 100 |
| `address_complement` | `complemento` | 48 | 100 |
| `address_district` | `bairro` | 100 | 100 |
| `address_city` | `municipio` | 100 | 100 |
| `address_state` | `uf` | 100 | 100 |
| `address_zip` | `cep` | 100 | 100 |
| `address_city_ibge` | — | not returned | — |
| `phones` | `telefones[].ddd + telefones[].numero` | 93 | 99 |
| `email` | `email` | 79 | 100 |
| `partners` | `QSA[].nome_socio, QSA[].qualificacao_socio` | 81 | 96 |
| `simples_optant` | `opcao_simples` | 57 | 100 |
| `mei_optant` | `opcao_mei` | 57 | 100 |

## Measured performance
| Item | Value |
|---|---|
| Coverage, wave 1 (95% Wilson interval; n = CNPJs with a conclusive answer) | 99.0% (97.1–99.7), n = 300 |
| Latency p50 / p95 | 496 / 673 ms |
| Effective throughput (pace used in brackets) | 121.7 CNPJs/min (300 req/min) |
| Share of attempts answered HTTP 429 at the pace used | 0.0% |
| Wave 2 ramp: HTTP 429 share at 1× / 2× / 4× the pace (attempted requests/min) | 0.0% @ 308 / 0.0% @ 511 / 0.0% @ 1,091 |
| Wave 2 unpaced bursts, 4 concurrent requests, 2 × 100 requests (attempted requests/min) | 0.0% @ 5,209 / 0.0% @ 5,077 |

## Freshness
| Item | Value |
|---|---|
| Newest opening date returned | 2026-10-08 |
| Companies opened 2026-10-16 to 2026-11-14 that were returned (found / existing) | 0% (0/67) |
| Declared record age (p50 / p90) | 15 / 15 days |

## Observed issues
- About one month behind the official release: newest company returned opened on 2026-10-08; none of the companies opened after 2026-10-15 were returned.
- No IBGE municipality code; Simples/MEI flags filled in 57% of records.
- No input validation (wrong check digit → 404).

## Evidence
- Reports: [wave 1, quality](../../results/wave1/REPORT.md) · [wave 2, rate limits](../../results/wave2/REPORT.md) · [freshness](../../results/freshness/REPORT.md)
- Connector code: [s06_opencnpj_org.py](../../src/cnpjbench/connectors/s06_opencnpj_org.py)
