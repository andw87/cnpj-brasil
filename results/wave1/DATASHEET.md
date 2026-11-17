# Source datasheet — wave1

Sample `SMP-20261116-n1100-r20261116`, waves `w1a + w1b`, 297 CNPJs with at least one record. Generated 2026-11-17 03:06 UTC by `scripts/75_build_datasheet.py`.
Metric definitions: [docs/methodology.md](../../docs/methodology.md), section 5. Percentages without decimals unless noted.

| Attribute | S01 | S02 | S03 | S04 | S05 | S06 | S07 |
|---|---|---|---|---|---|---|---|
| **1. Identity** |  |  |  |  |  |  |  |
| Name | BrasilAPI | Minha Receita (public instance) | ReceitaWS (free tier) | CNPJa Open | CNPJ.ws Public API | OpenCNPJ (opencnpj.org) | OpenCNPJ (opencnpj.com, Kitana API) |
| Access | free_no_key | free_no_key | free_no_key | free_no_key | free_no_key | free_no_key | free_no_key |
| Open source | yes | yes | no | no | no | yes | no |
| Upstream (declared) | Receita Federal open data (via Minha Receita) | Receita Federal open data | Receita Federal | Receita Federal + Simples Nacional | Receita Federal + SINTEGRA | Receita Federal open data | Receita Federal open data |
| Pace used, rpm (basis) | 60 (assumed) | 60 (assumed) | 3 (observed) | 5 (documented) | 3 (observed) | 300 (documented) | 120 (observed) |
| **2. Judgment** |  |  |  |  |  |  |  |
| QI (pre-registered index) | 0.9347 | 0.9385 | 0.891 | 0.9221 | 0.887 | 0.9772 | 0.974 |
| Rank by QI | 4 | 3 | 6 | 5 | 7 | 1 | 2 |
| **3. Return** |  |  |  |  |  |  |  |
| CNPJs closed (T2) | 300 | 300 | 300 | 300 | 258 | 300 | 300 |
| Found rate % (R2) | 90.3 | 91.7 | 99.0 | 99.0 | 86.8 | 99.0 | 99.0 |
| Coverage % (R3) | 90.3 | 91.7 | 99.0 | 99.0 | 99.1 | 99.0 | 99.0 |
| Error rate % (R4) | 0.0 | 0.0 | 0.0 | 0.0 | 12.4 | 0.0 | 0.0 |
| Final outcomes (R1) | found: 271<br>not_found: 29 | found: 275<br>not_found: 25 | found: 297<br>not_found: 3 | found: 297<br>not_found: 3 | found: 224<br>not_found: 2<br>server_error: 25<br>timeout: 7 | found: 297<br>not_found: 3 | found: 297<br>not_found: 3 |
| **4. Fields** — fill % / agreement % (C1 / A1); † validity < 99% (Q1 in brackets) |  |  |  |  |  |  |  |
| `legal_name` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 98 | 100 / 99 |
| `trade_name` | 67 / 100 | 66 / 100 | 66 / 100 | 66 / 100 | 68 / 100 | 66 / 100 | 66 / 100 |
| `establishment_type` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| `registration_status` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| `registration_status_date` | 99 / 100 | 99 / 100 | 100 / 100 | 100 / 100 | 97 / 100 | 98 / 100 | 98 / 100 |
| `opening_date` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| `legal_nature_code` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 99 |
| `legal_nature` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 99 | 100 / 99 | 100 / 100 | 100 / 99 |
| `company_size` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | not returned |
| `share_capital` | 100 / 90 | 100 / 91 | 100 / 96 | 100 / 96 | 100 / 96 | 100 / 96 | 100 / 96 |
| `main_cnae` | 100 / 100 | 100 / 100 | 73 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| `secondary_cnaes` | 70 / 100 | 71 / 100 | 51 / 100 | 71 / 100 | 71 / 100 | 71 / 100 | 71 / 100 |
| `address_street` | 86 / 100 | 86 / 100 | 100 / 96 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| `address_number` | 86 / 100 | 86 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| `address_complement` | 44 / 100 | 45 / 100 | 48 / 100 | 48 / 100 | 47 / 100 | 48 / 100 | 49 / 100 |
| `address_district` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| `address_city` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| `address_state` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| `address_zip` | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| `address_city_ibge` | 100 / 100 | 100 / 100 | not returned | 100 / 100 | 100 / 100 | not returned | not returned |
| `phones` | 79 / 100 † [93] | 80 / 100 † [94] | 93 / 85 † [93] | 88 / 95 | 91 / 100 † [95] | 93 / 99 † [95] | 93 / 84 † [97] |
| `email` | not returned | not returned | 79 / 100 | 79 / 100 | 79 / 100 | 79 / 100 | 79 / 100 |
| `partners` | 80 / 96 | 80 / 96 | 67 / 98 | 81 / 96 | 82 / 79 | 81 / 96 | 80 / 95 |
| `simples_optant` | 57 / 100 | 59 / 100 | 100 / 100 | 100 / 100 | 61 / 100 | 57 / 100 | 100 / 100 |
| `mei_optant` | 57 / 100 | 59 / 100 | 100 / 100 | 100 / 100 | 61 / 100 | 57 / 100 | 100 / 100 |
| Mean fill % (C1) | 85.0 | 85.2 | 87.1 | 93.3 | 90.3 | 86.0 | 85.4 |
| Mean relative completeness % (C2) | 90.5 | 90.7 | 93.0 | 99.8 | 96.7 | 92.4 | 91.8 |
| Mean validity % (Q1) | 99.7 | 99.7 | 99.7 | 100.0 | 99.8 | 99.8 | 99.9 |
| Mean agreement % (A1) | 99.4 | 99.4 | 99.0 | 99.4 | 98.9 | 99.6 | 98.7 |
| **5. Time** |  |  |  |  |  |  |  |
| Latency p50 ms | 412 | 297 | 238 | 326 | 374 | 496 | 53 |
| Latency p95 ms | 488 | 343 | 287 | 538 | 15967 | 673 | 94 |
| Latency p99 ms | 616 | 416 | 395 | 2217 | 18209 | 910 | 204 |
| Effective rpm (T4) | 60.27 | 60.14 | 2.54 | 4.49 | 1.38 | 121.66 | 120.69 |
| Wall time min (T3) | 5.0 | 5.0 | 118.3 | 66.8 | 186.6 | 2.5 | 2.5 |
| Attempts (T1) | 300 | 300 | 357 | 336 | 383 | 300 | 300 |
| HTTP 429 share % (T6) | 0.0 | 0.0 | 16.0 | 10.7 | 11.0 | 0.0 | 0.0 |
| Retries per CNPJ (T7) | 0.0 | 0.0 | 0.19 | 0.12 | 0.4845 | 0.0 | 0.0 |
| **6. Consistency** |  |  |  |  |  |  |  |
| Broken encoding % of text values (Q2) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Head office/branch vs CNPJ % (Q3) | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| IBGE code vs UF % (Q4) | 100.0 | 100.0 | — | 100.0 | 100.0 | — | — |
| Agrees with internal reference: `legal_name` % (A2) | 68 (n=271) | 69 (n=275) | 69 (n=297) | 69 (n=297) | 70 (n=224) | 69 (n=297) | 69 (n=297) |
| Agrees with internal reference: `address_state` % (A2) | 97 (n=71) | 99 (n=68) | 97 (n=77) | 97 (n=77) | 96 (n=54) | 97 (n=77) | 97 (n=77) |
| Agrees with internal reference: `address_city` % (A2) | 92 (n=72) | 93 (n=70) | 92 (n=79) | 92 (n=79) | 93 (n=56) | 92 (n=79) | 92 (n=79) |
| Agrees with internal reference: `address_zip` % (A2) | 69 (n=48) | 71 (n=48) | 68 (n=53) | 68 (n=53) | 64 (n=39) | 68 (n=53) | 68 (n=53) |
| Agrees with internal reference: `address_city_ibge` % (A2) | 95 (n=42) | 98 (n=40) | — (n=0) | 96 (n=47) | 97 (n=33) | — (n=0) | — (n=0) |

Reading guide: *fill* = share of found records with the field; *agreement* = share of times the value matches the majority of the other sources holding it (judged only where ≥ 3 sources hold it); *not returned* = the source never delivered the field. The internal reference is an outdated registry, so A2 is agreement, not accuracy.
