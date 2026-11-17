# S02 — Minha Receita

Português: [../pt-BR/sources/S02-minhareceita.md](../pt-BR/sources/S02-minhareceita.md) · All APIs: [suggestion by use case](../ranking.md)

> Newest data among the seven sources measured (companies opened up to 2026-11-14 present on 2026-11-16). No key; no rate limit documented or observed (0% HTTP 429 at up to 6,310 requests/min); open source and self-hostable. Measured caveats: 404 served from a stale cache for 7.4% of existing CNPJs, share capital above R$ 16,777,216 rounded, no e-mail.

_Exploratory measurement, one collection window on 2026-11-16/17 (UTC), one client. Every number below comes from [results/summary.json](../../results/summary.json). Method: [methodology](../methodology.md)._

## Facts
| Item | Value |
|---|---|
| Endpoint | `GET https://minhareceita.org/{cnpj}` |
| Authentication | none |
| Operator | Open-source project maintained by an individual developer, funded by donations; code moved to Codeberg |
| Website | https://minhareceita.org |
| Documentation | https://docs.minhareceita.org |
| Source code | https://codeberg.org/cuducos/minha-receita |
| Documented limit | no rate limit by design ([PR #99](https://codeberg.org/cuducos/minha-receita/pulls/99)); self-hosting is recommended for heavy use |
| Measured behaviour at the limit | no 429 at ~6,300 rpm (4 concurrent requests, cached CNPJs) |
| Data origin (declared) | Receita Federal monthly open-data release, downloaded from the official share ([download/webdav.go](https://codeberg.org/cuducos/minha-receita/src/branch/main/download/webdav.go)); `/updated` answered `2026-11` |
| Update cadence (declared) | monthly, manually, 'normally a few days after the release' ([FAQ](https://docs.minhareceita.org/faq/)); 2026-11 release (extracted 2026-11-14) was live on 2026-11-16 |
| Terms of use | code MIT; no terms of use for the public instance found |
| Alphanumeric CNPJ (measured) | accepts the format: wrong check digit → HTTP 400, alphanumeric example 12.ABC.345/01DE-35 → HTTP 404 |

## How to connect
```bash
curl -s 'https://minhareceita.org/33000167000101'
```
```python
import requests
r = requests.get('https://minhareceita.org/{cnpj}'.format(cnpj='33000167000101'), timeout=20)
data = r.json() if r.status_code == 200 else None   # 404 = not found (may be a cached 404), 400 = invalid CNPJ
```
```javascript
const r = await fetch(`https://minhareceita.org/${cnpj}`);
const data = r.status === 200 ? await r.json() : null; // 404 may be a cached 404
```

Cloudflare caches answers for up to 5 days (`max-age=432000`), including 404. Requesting the punctuated form (`/12.345.678%2F0001-95`) bypasses a stale entry. `/updated` returns the release month. For volume, run your own instance (Docker, PostgreSQL).

### Responses observed
| Case | HTTP | Body (start) |
|---|---|---|
| found | 200 | — |
| wrong check digit | 400 | `{"message":"CNPJ 33.000.167/0001-02 inválido."}` |
| alphanumeric example 12.ABC.345/01DE-35 | 404 | `{"message":"CNPJ 12.ABC.345/01DE-35 não encontrado."}` |

## Fields returned (measured)
| Canonical field | JSON path in the response | Filled % | Agrees with other sources % |
|---|---|---|---|
| `legal_name` | `razao_social` | 100 | 100 |
| `trade_name` | `nome_fantasia` | 66 | 100 |
| `establishment_type` | `identificador_matriz_filial` | 100 | 100 |
| `registration_status` | `situacao_cadastral` | 100 | 100 |
| `registration_status_date` | `data_situacao_cadastral` | 99 | 100 |
| `opening_date` | `data_inicio_atividade` | 100 | 100 |
| `legal_nature_code` | `codigo_natureza_juridica` | 100 | 100 |
| `legal_nature` | `natureza_juridica` | 100 | 100 |
| `company_size` | `porte` | 100 | 100 |
| `share_capital` | `capital_social` | 100 | 91 |
| `main_cnae` | `cnae_fiscal` | 100 | 100 |
| `secondary_cnaes` | `cnaes_secundarios[].codigo` | 71 | 100 |
| `address_street` | `descricao_tipo_de_logradouro + logradouro` | 86 | 100 |
| `address_number` | `numero` | 86 | 100 |
| `address_complement` | `complemento` | 45 | 100 |
| `address_district` | `bairro` | 100 | 100 |
| `address_city` | `municipio` | 100 | 100 |
| `address_state` | `uf` | 100 | 100 |
| `address_zip` | `cep` | 100 | 100 |
| `address_city_ibge` | `codigo_municipio_ibge` | 100 | 100 |
| `phones` | `ddd_telefone_1, ddd_telefone_2` | 80 | 100 |
| `email` | `email` | not returned | — |
| `partners` | `qsa[].nome_socio, qsa[].qualificacao_socio` | 80 | 96 |
| `simples_optant` | `opcao_pelo_simples` | 59 | 100 |
| `mei_optant` | `opcao_pelo_mei` | 59 | 100 |

## Measured performance
| Item | Value |
|---|---|
| Coverage, wave 1 (95% Wilson interval; n = CNPJs with a conclusive answer) | 91.7% (88.0–94.3), n = 300 |
| Latency p50 / p95 | 297 / 343 ms |
| Effective throughput (pace used in brackets) | 60.1 CNPJs/min (60 req/min) |
| Share of attempts answered HTTP 429 at the pace used | 0.0% |
| Wave 2 ramp: HTTP 429 share at 1× / 2× / 4× the pace (attempted requests/min) | 0.0% @ 62 / 0.0% @ 123 / 0.0% @ 247 |
| Wave 2 unpaced bursts, 4 concurrent requests, 2 × 100 requests (attempted requests/min) | 0.0% @ 5,437 / 0.0% @ 6,310 |

## Freshness
| Item | Value |
|---|---|
| Newest opening date returned | 2026-11-14 |
| Companies opened 2026-10-16 to 2026-11-14 that were returned (found / existing) | 100% (67/67) |
| Declared record age (p50 / p90) | — |

## Observed issues
- **Stale cached 404s.** 22 of the 297 existing CNPJs (7.4%) were answered 404 with `cf-cache-status: HIT`; all 22 were returned (200) in punctuated form. Known mechanism: 404s minted during reloads or outages stay cached ([#1](https://codeberg.org/cuducos/minha-receita/issues/1), [#98](https://codeberg.org/cuducos/minha-receita/issues/98)).
- Share capital above 16,777,216 is rounded (float32).
- No e-mail address; street and number missing in 14% of records; Simples/MEI flags filled in 59% of records.
- Outages: ~99% HTTP 503 on 2026-10-08/09 ([#98](https://codeberg.org/cuducos/minha-receita/issues/98)).

## Evidence
- Reports: [wave 1, quality](../../results/wave1/REPORT.md) · [wave 2, rate limits](../../results/wave2/REPORT.md) · [freshness](../../results/freshness/REPORT.md)
- Connector code: [s02_minhareceita.py](../../src/cnpjbench/connectors/s02_minhareceita.py)
