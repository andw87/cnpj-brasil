# S01 — BrasilAPI

Português: [../pt-BR/sources/S01-brasilapi.md](../pt-BR/sources/S01-brasilapi.md) · All APIs: [suggestion by use case](../ranking.md)

> Proxy of Minha Receita (S02): same data and same freshness (2026-11 release online on 2026-11-16, two days after publication), no key. Measured caveats: 404 served from a stale cache for 8.8% of existing CNPJs (retry in punctuated form), share capital above R$ 16,777,216 rounded, HTTP 429 to a second unpaced burst.

_Exploratory measurement, one collection window on 2026-11-16/17 (UTC), one client. Every number below comes from [results/summary.json](../../results/summary.json). Method: [methodology](../methodology.md)._

## Facts
| Item | Value |
|---|---|
| Endpoint | `GET https://brasilapi.com.br/api/cnpj/v1/{cnpj}` |
| Authentication | none |
| Operator | Community open-source project (MIT), hosted on Vercel |
| Website | https://brasilapi.com.br |
| Documentation | https://brasilapi.com.br/docs#tag/CNPJ |
| Source code | https://github.com/BrasilAPI/BrasilAPI |
| Documented limit | not documented; the Vercel firewall answers 403/429 to empty or generic User-Agents ([#826](https://github.com/BrasilAPI/BrasilAPI/issues/826), [#835](https://github.com/BrasilAPI/BrasilAPI/issues/835)) |
| Measured behaviour at the limit | no 429 up to ~190 rpm; a second unpaced burst within one minute was answered 100% HTTP 429 (no Retry-After) |
| Data origin (declared) | **proxy of Minha Receita (S02)**: the CNPJ route calls `https://minhareceita.org/{cnpj}` with a 5 s timeout ([services/cnpj.js](https://github.com/BrasilAPI/BrasilAPI/blob/main/services/cnpj.js)) |
| Update cadence (declared) | same as Minha Receita, plus Vercel edge cache (404 answers are cached too) |
| Terms of use | code MIT; no usage terms for the API found |
| Alphanumeric CNPJ (measured) | accepts the format: wrong check digit → HTTP 400, alphanumeric example 12.ABC.345/01DE-35 → HTTP 404 |

## How to connect
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

Send a descriptive `User-Agent`. A 404 can be a stale cached answer: requesting the punctuated form (`/api/cnpj/v1/12.345.678%2F0001-95`) bypasses the cache entry of the bare form.

### Responses observed
| Case | HTTP | Body (start) |
|---|---|---|
| found | 200 | — |
| wrong check digit | 400 | `{"message":"CNPJ 33.000.167/0001-02 inválido.","type":"bad_request","name":"BadRequestErro` |
| alphanumeric example 12.ABC.345/01DE-35 | 404 | `{"message":"CNPJ 12.ABC.345/01DE-35 não encontrado.","type":"not_found","name":"NotFoundEr` |
| HTTP 429 | 429 | HTTP 429, no rate-limit headers |

## Fields returned (measured)
| Canonical field | JSON path in the response | Filled % | Agrees with other sources % |
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
| `email` | `email` | not returned | — |
| `partners` | `qsa[].nome_socio, qsa[].qualificacao_socio` | 80 | 96 |
| `simples_optant` | `opcao_pelo_simples` | 57 | 100 |
| `mei_optant` | `opcao_pelo_mei` | 57 | 100 |

## Measured performance
| Item | Value |
|---|---|
| Coverage, wave 1 (95% Wilson interval; n = CNPJs with a conclusive answer) | 90.3% (86.5–93.2), n = 300 |
| Latency p50 / p95 | 412 / 488 ms |
| Effective throughput (pace used in brackets) | 60.3 CNPJs/min (60 req/min) |
| Share of attempts answered HTTP 429 at the pace used | 0.0% |
| Wave 2 ramp: HTTP 429 share at 1× / 2× / 4× the pace (attempted requests/min) | 0.0% @ 61 / 0.0% @ 115 / 0.0% @ 189 |
| Wave 2 unpaced bursts, 4 concurrent requests, 2 × 100 requests (attempted requests/min) | 0.0% @ 858 / stopped after 10 consecutive HTTP 429 (test stop rule) |

## Freshness
| Item | Value |
|---|---|
| Newest opening date returned | 2026-11-14 |
| Companies opened 2026-10-16 to 2026-11-14 that were returned (found / existing) | 96% (64/67) |
| Declared record age (p50 / p90) | — |

## Observed issues
- **Stale cached 404s.** 26 of the 297 existing CNPJs (8.8%) were answered 404; BrasilAPI forwards the bare CNPJ to Minha Receita, whose CDN served old cached 404s. All 26 were returned (200) when requested in punctuated form, which bypasses the cache. The skew towards S.A. companies matches the hypothesis that frequently queried CNPJs were cached during upstream outages; the cause was not determined.
- Share capital above 16,777,216 is rounded (float32): 26 of 39 such values differ from the other sources, e.g. 4,443,409,696.10 → 4,443,410,000.
- No e-mail address; street and number missing in 14% of records; Simples/MEI flags filled in 57% of records.
- Inherits Minha Receita outages: 503 errors reported in October 2026 ([#916](https://github.com/BrasilAPI/BrasilAPI/issues/916), [#920](https://github.com/BrasilAPI/BrasilAPI/issues/920)).

## Evidence
- Reports: [wave 1, quality](../../results/wave1/REPORT.md) · [wave 2, rate limits](../../results/wave2/REPORT.md) · [freshness](../../results/freshness/REPORT.md)
- Connector code: [s01_brasilapi.py](../../src/cnpjbench/connectors/s01_brasilapi.py)
