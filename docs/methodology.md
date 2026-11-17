# Methodology

Português: [pt-BR/methodology.md](pt-BR/methodology.md) · Summary: [README](../README.en.md) ·
Suggestion by use case: [ranking.md](ranking.md)

## 1. Status of the study
This is an **exploratory comparative study**. The data were collected over one night (2026-11-16/17,
UTC), from a single client and a single IP address, with small samples: 300 CNPJs for quality, 196
for rate limits and 346 lookups (343 distinct CNPJs) for freshness. The results describe how the
APIs behaved in that window. They are not a certification and do not predict future behaviour.
Every published number is in [results/summary.json](../results/summary.json), and the collection can
be repeated with the code in this repository ([reproduce.md](reproduce.md)).

## 2. Research questions
| ID | Question | Test | Metrics (§5) |
|---|---|---|---|
| RQ1 | Does the API return a record for real, valid CNPJs? | wave 1 | R2, R3, R4 |
| RQ2 | Which fields does it deliver, and how often? | wave 1 | C1, C2 |
| RQ3 | Are the values well formed and internally consistent? | wave 1 | Q1–Q4 |
| RQ4 | Do the values agree with those of the other APIs? | wave 1 | A1 (A2 secondary) |
| RQ5 | What throughput and latency are sustainable within the limits, and what happens above them? | waves 1 and 2 | T1–T7, S1–S11 |
| RQ6 | Does a company opened this month, or this week, already appear? | freshness | F1–F3 |
| RQ7 | Is the alphanumeric CNPJ (issued since July 2026) accepted? | alphanumeric probe | F4 |

## 3. Design and controlled conditions
**Design.** Comparative measurement study: the same CNPJ list is sent to every API, by the same
client, in the same time window. Every HTTP attempt is logged (status, latency, headers, outcome).
Every answer found is stored as received and converted to a common 25-field schema (§6), so that
each field means the same thing for every API.

**Identical conditions for every API.**
- HTTP client `httpx`, 20 s timeout per request, same `User-Agent`
  (`cnpjbench/0.1 (research benchmark)`).
- One request at a time per API, at the API's documented or observed limit; 60 requests/min when
  no limit is known. The APIs run in parallel with each other.
- Up to 2 retries for HTTP 429, HTTP 5xx, timeout or connection failure. The wait honours
  `Retry-After` or `X-RateLimit-Reset` when the API sends them.
- The configuration of every run is stored with its data.

**Pre-registration.** Metric definitions, the outcome classification and the weights of the
composite index (§5.5) were fixed before the main collection. Later additions (rate limits,
freshness) were added as new metrics; earlier definitions were not changed.

**Inclusion criteria for APIs.** An API was measured when it (a) is free or open source, (b) is an
HTTP API returning JSON looked up by CNPJ, (c) can be used without a paid contract, and (d) answered
a test lookup on 2026-11-16 (public CNPJ 33.000.167/0001-01).

| ID | API | Access | Pace used (req/min) and basis | Status |
|---|---|---|---|---|
| S01 | BrasilAPI | free, no key | 60, no known limit | measured |
| S02 | Minha Receita (public instance) | free, no key | 60, no known limit | measured |
| S03 | ReceitaWS (free tier) | free, no key | 3, observed in headers | measured |
| S04 | CNPJá Open | free, no key | 5, documented | measured |
| S05 | CNPJ.ws (public API) | free, no key | 3, observed in headers | measured |
| S06 | OpenCNPJ.org | free, no key | 300, documented | measured |
| S07 | OpenCNPJ.com (Kitana API) | free, no key | 120, see note | measured |
| S08 | Minha Receita, self-hosted | own instance | — | not measured (needs infrastructure) |
| S09 | Receita Federal open-data files | monthly download | — | not measured (candidate reference) |
| S10 | Invertexto | free with key | — | not measured (needs key registration) |
| S11 | Casa dos Dados | paid key | — | excluded (paid) |
| S12 | SERPRO Consulta CNPJ | paid contract | — | excluded (paid) |

Note: OpenCNPJ.com reports 300 req/min in its `X-Ratelimit-Limit` header; the test used 120
req/min, the value recorded in the catalogue before the collection. The reason for the difference
was not recorded. Source of this table: [catalog/sources.yaml](../catalog/sources.yaml).

**Conduct towards providers.** Each API's limits were respected at every stage except wave 2,
which deliberately tested behaviour above the limit under safety rules (§4). Only free tiers were
used. No web page was scraped and no access key was used.

## 4. Samples and collection stages
| Sample | Size | Construction | Use |
|---|---|---|---|
| Main | 1,100 drawn; the first 300 collected | simple random sampling without replacement, seed 20261116, over 35,702 valid CNPJs from a private reference registry | wave 1 (quality) |
| Wave 2 | 196 | CNPJs found by every API in wave 1; part A with 96 (3 blocks of 32), part B with 100 | wave 2 (limits) |
| Frontier | 220 + 60 + 66 | synthetic head-office CNPJs built from sampled base numbers (details below) | freshness |
| Retest | 42 + 107 | CNPJs one API answered as "not found" while another returned them | separate stale cached 404s from missing records |
| Alphanumeric probe | 12 | official example `12.ABC.345/01DE-35`, 9 valid synthetic alphanumeric CNPJs and 2 numeric controls (one existing; the same with a wrong check digit) | alphanumeric CNPJ |

**Population of the main sample.** The reference registry had 42,688 records. After removing
invalid check digits (3,847) and duplicates, 35,702 valid unique CNPJs remained, of which 29,854
(83.6%) are head offices and none is alphanumeric. Of the 297 sampled companies that exist, 85% are
head offices. The size 1,100 was chosen for a margin of ±3 percentage points at 95% confidence;
with the 300 collected, the margin is about ±6 points.

**Wave 1 (quality).** The first 100 CNPJs of the main sample (label `w1a`) and the next 200 (`w1b`),
under the conditions of §3, from 2026-11-16 23:55 to 2026-11-17 03:00 UTC.

**Wave 2 (rate limits).** In part A, three blocks of 32 CNPJs at 1×, 2× and 4× the API's pace. In
part B, 100 CNPJs without pacing, with 4 concurrent requests, sent twice. Safety rules: at most 4
concurrent requests per API, no retries, stop after 10 consecutive HTTP 429 answers and at most 300
requests per API. Wave 2 ran after the quality and freshness measurements of the fast APIs, so as
not to affect them.

**Freshness (frontier samples).** CNPJ base numbers (first 8 digits) are issued in increasing order
over time. A head office (`/0001`) built from a base number close to the highest one issued is
therefore a recently opened company. This yields new companies **without any external list**.
- `frontier`: base numbers between 66.0 and 70.4 million, in 22 strata of 200,000, 10 per stratum,
  drawn uniformly with seed 20261116 (220 CNPJs).
- `frontier2`: range 69.95–70.25 million, 6 strata × 10 (60 CNPJs), the last weeks before the release.
- `frontierlite`: the same 22 strata, 3 per stratum (66 CNPJs), so that the slow APIs (S03, S04, S05)
  fit in the same night.
- A CNPJ counts as existing when at least one API returns it. Its opening date is the value given by
  the majority of the APIs that return it. Unused base numbers (found by no API) are expected and are
  left out of the calculation.
- Recall (the share of existing companies the API returned) is grouped by half-month of opening date.

**Retest.** "Not found" answers for CNPJs that another API returned were queried again: first in
the bare form and then in punctuated form (`12.345.678%2F0001-95`). A different URL does not hit the
CDN cache entry (a network of intermediate servers that stores answers) created for the bare form.
This separates a stale cached 404 from a record that is really missing. CDN cache headers were
logged on every attempt.

## 5. Metrics

### 5.1 Outcome of each CNPJ
| Outcome | Meaning | Retried |
|---|---|---|
| found | record returned and parsed | — |
| not_found | the API states that the CNPJ is not in its database | — |
| restricted | the API withholds the record on its free tier: HTTP 402 "only available in commercial api" (S04) or "not in cache" (S03) | — |
| invalid_input | the API rejects the CNPJ as invalid | — |
| rate_limited | HTTP 429 | yes |
| server_error | HTTP 5xx | yes |
| timeout | no answer within 20 s | yes |
| network_error | connection failure | yes |
| client_error | other 4xx | — |
| parse_error | answer received but conversion failed | — |

### 5.2 Per-run metrics
| ID | Metric | Definition |
|---|---|---|
| T1 | attempts | number of HTTP requests |
| T2 | CNPJs closed | number of CNPJs with a final outcome |
| T3 | wall time | from the start of the first to the end of the last attempt, in seconds |
| T4 | effective throughput | T2 / (T3 / 60), in CNPJs per minute |
| T5 | latency | p50, p95 and p99 of the attempts with an HTTP answer, in ms |
| T6 | HTTP 429 share | `rate_limited` attempts / T1 |
| T7 | retries per CNPJ | (T1 − T2) / T2 |
| R1 | outcomes | distribution of final outcomes |
| R2 | found rate | found / T2 |
| R3 | coverage | found / (found + not_found + restricted) |
| R4 | error rate | (T2 − found − not_found − restricted) / T2 |
| C1 | fill rate | per field: records with a value / records found |
| Q1 | validity | per field: valid values / filled values (format rules: 7-digit CNAE, 8-digit ZIP, existing state, ISO dates, etc.) |
| Q2 | broken encoding | text values with corrupted characters / text values |
| Q3 | head office/branch consistency | `establishment_type` matches the CNPJ order number (`0001` = head office) |
| Q4 | IBGE/state consistency | the first two digits of the IBGE code match the state |
| A2 | agreement with the reference registry | per field, against the private registry; secondary signal (§7) |

### 5.3 Cross-API metrics
| ID | Metric | Definition |
|---|---|---|
| C2 | relative completeness | per field: the API has a value / CNPJs where **any** API has a value. A legitimately empty field (e.g. no trade name) penalises nobody |
| A1 | consensus agreement | per field, when at least 3 APIs have a value: share of times the API agrees with the majority of the others |

Equality rules: names, street and district with similarity ≥ 0.85 after removing accents and legal
suffixes; municipality, legal nature and number exact after normalisation; company size compared by
code (ME, EPP, DEMAIS), because the APIs label it differently; share capital within 0.01; CNAE,
phone and partner lists compared as sets; e-mail case-insensitive; all other fields exact.

### 5.4 Rate-limit (wave 2) and freshness metrics
| ID | Metric | Definition |
|---|---|---|
| S1 | attempted rate | attempts per minute |
| S2 | found rate | `found` attempts per minute |
| S3 | 429 onset | position (from 0) of the first attempt answered HTTP 429 |
| S4 | 429 share | `rate_limited` attempts / attempts |
| S5 | Retry-After use | 429 answers with `Retry-After` / 429 answers |
| S6 | limit headers | header names seen on 429 answers |
| S7 | other errors | outcomes other than found, 404 and 429 |
| S8 | p50 latency of found | ms |
| S9–S11 | repeat consistency | burst 1 vs burst 2: CNPJs found in both, share of identical records, ratio of p50 latencies (below 1 suggests caching) |
| F1 | newest record | most recent opening date in the records the API returned in the frontier sample |
| F2 | recall per half-month | CNPJs returned / existing CNPJs, among those the API answered conclusively (errors excluded) |
| F3 | declared record age | days between collection and the API's own "updated at" stamp (p10, p50, p90), for APIs that expose it |
| F4 | alphanumeric support | answer to valid alphanumeric CNPJs: found, not found (format accepted) or rejected as invalid input |

### 5.5 Statistics and composite index
- Percentages are proportions over the CNPJs each API closed. Coverage and recall carry 95% Wilson
  confidence intervals (Wilson, 1927). Differences with overlapping intervals are not claimed.
- Latency is reported as percentiles (p50, p95, p99), not as a mean.
- **Composite index (QI), pre-registered:** QI = 0.25 · coverage + 0.25 · relative completeness +
  0.20 · validity + 0.20 · agreement + 0.10 · throughput score, where the throughput score is
  log10(T4) rescaled to 0–1 across the APIs compared. The QI is published for transparency in
  [results/wave1/README.md](../results/wave1/README.md), but it does **not** decide the suggestion in
  [ranking.md](ranking.md): it has no freshness term, and a single weighting does not fit every use.

### 5.6 Mapping to data-quality models
| Characteristic (ISO/IEC 25012) | Metric here |
|---|---|
| Completeness | C1, C2 |
| Syntactic accuracy | Q1 |
| Semantic accuracy | A1 (consensus approximation, §7) |
| Consistency | Q2, Q3, Q4 |
| Currentness | F1, F2, F3 |
| Availability | R3, R4, S7 |
| Efficiency | T4, T5, S1–S6 |

The same dimensions appear in Wang and Strong (1996) and in Pipino, Lee and Wang (2002).

## 6. Common schema (25 fields compared)
Every connector converts the API answer to this model. A value the API does not deliver stays
absent: connectors never infer or default values. The JSON path of each field in each API is in
[catalog/field_map.yaml](../catalog/field_map.yaml); the implementation is in
`src/cnpjbench/schema.py` and `src/cnpjbench/normalize.py`.

| Field | Type | Normalisation |
|---|---|---|
| `cnpj` (key, not compared) | text, 14 characters | upper case, only `[0-9A-Z]` |
| `legal_name` (razão social) | text | single spaces, trimmed |
| `trade_name` (nome fantasia) | text | same |
| `establishment_type` (head office or branch) | `head_office` or `branch` | |
| `registration_status` (situação cadastral) | `active`, `suspended`, `unfit`, `closed`, `null` | Receita codes 2/3/4/8/1 or texts |
| `registration_status_date` | date `YYYY-MM-DD` | from ISO or `DD/MM/YYYY` |
| `opening_date` (início de atividade) | date | same |
| `legal_nature_code` | text, 4 digits | zero-padded |
| `legal_nature` (natureza jurídica) | text | without the code |
| `company_size` (porte) | text | compared by code (ME, EPP, DEMAIS) |
| `share_capital` (capital social) | number | accepts `1234.56` and `1.234,56` |
| `main_cnae` | text, 7 digits | zero-padded |
| `secondary_cnaes` | list of 7-digit texts | `0000000` dropped |
| `address_street` | text | street type + name |
| `address_number`, `address_complement`, `address_district`, `address_city` | text | |
| `address_state` | text, 2 letters | state (UF) |
| `address_zip` | text, 8 digits | ZIP (CEP) |
| `address_city_ibge` | text, 7 digits | IBGE municipality code |
| `phones` | list | digits with area code, deduplicated, fax excluded |
| `email` | text | first e-mail given |
| `partners` (quadro societário) | list of {name, role} | role without numeric prefix |
| `simples_optant`, `mei_optant` | true/false | |

Each API's "updated at" stamp (`source_updated_at`) is kept as metadata and used only in F3.

## 7. Reference truth
None of the APIs is an official copy of the Receita Federal registry. Agreement between APIs (A1)
measures consistency, not truth: APIs that start from the same copy can agree on the same error.
Since most of them derive from the same monthly open-data release, A1 mainly detects conversion
defects (rounding, truncation, encoding, missing prefixes). The private registry used for sampling
is old and partly outdated, so agreement with it (A2) appears only as a secondary signal, in the
[per-field table](../results/wave1/DATASHEET.md).

## 8. Threats to validity
| Type | Threat | Treatment and remaining risk |
|---|---|---|
| Construct | Consensus is not accuracy | stated in §7; A1 reported per field |
| Construct | "Not found" can mean "rejected", "not loaded", "withheld on the free tier", "stale cached 404" or "does not exist" | outcomes classified by HTTP status and body (`restricted` for paid-only or cache-only answers); retest in punctuated form; numeric controls in the alphanumeric probe |
| Internal | One collection window; provider incidents | every API ran in the same window; incidents are reported (S05 degraded from about 02:00 UTC on 2026-11-17) |
| Internal | Client-side network latency | same client and location for every API; percentiles reported |
| Internal | Wave 2 itself may change provider behaviour afterwards | wave 2 ran after the quality and freshness measurements of the fast APIs |
| External | The main sample comes from one organisation's registry (older, mostly head offices, more corporations) | composition reported; the frontier samples cover new companies independently |
| External | Free tiers change without notice | collection date recorded on every result |
| Conclusion | Small n | Wilson intervals; differences within overlapping intervals are not claimed |

## 9. Deviations from the plan
- **Wave 1 size.** 1,100 CNPJs were drawn, but only the first 300 were collected. The planned
  full-day stage over the rest of the sample (daily capacity) was not run.
- **CNPJ.ws (S05).** The second batch of wave 1 was stopped at 158 of 200 CNPJs: from about
  02:00 UTC the service mostly answered HTTP 500, HTTP 504 or timed out. The run is kept with status
  `stopped_degraded`, and S05 did not run wave 2.
- **Wave 2 sample.** It has 196 CNPJs instead of 200, because only 196 were found by every API in
  wave 1. Part A has 96 CNPJs (3 × 32); part B has 100.
- **Freshness.** The slow APIs (S03, S04, S05) used the reduced 66-CNPJ sample; S04 also ran the
  60-CNPJ sample. S05 answered about 0.5 CNPJ per minute and was limited to the 12 CNPJs of the four
  newest strata. The first frontier runs of S03, S04 and S05 were interrupted and are excluded.
- **Alphanumeric probe.** A first version with 10 CNPJs and no controls was replaced by the version
  with 12 CNPJs and controls. The first version is not reported.

## 10. Corrections made in this version
While reorganising the texts for publication, values that differed between documents were checked
against [results/summary.json](../results/summary.json) and the reports:

| Item | Before | Now | Source |
|---|---|---|---|
| CNPJ.ws coverage confidence interval | 82.2–90.4% in `summary.json` and on its page (computed over the 258 CNPJs closed, not over the coverage denominator) | 96.8–99.8% (224 of 226) | wave 1 report; `summary.json` and `scripts/90_build_summary.py` corrected |
| Stale cached 404s | "26 of 300 real CNPJs (8.7%)" and "22 of 300 (7.3%)" on the pages | 26 of 297 (8.8%) and 22 of 297 (7.4%): 3 of the 300 CNPJs do not exist | wave 1 report |
| Share of head offices | "85% head offices" attributed to the 35,702-CNPJ population | population: 83.6% (29,854); companies found in the sample: 85% | original protocol and wave 1 report |
| CNPJá ramp at 1× | 13% in the report, 12% on the page | 12.5% | `summary.json` |
| p50 latency in bursts (S02, S06, S07) | 31–48 ms | 31–46 ms | `summary.json` |
| CNPJ.ws newest opening date | 2026-11-06 in the freshness report, 2026-10-27 on its page | 2026-10-27 in the API's own records; it also returned a company opened on 2026-11-06 with no date in the record | `summary.json` (F1 and recall per half-month) |
| Size of the freshness test | "346 CNPJs" | 346 lookups, 343 distinct CNPJs, 298 existing | `summary.json` (`freshness_meta`) |
| README "rate at limit" column | mixed documented limit and pace used (OpenCNPJ.com: 300 vs 120 req/min) | separate columns | `catalog/sources.yaml` and pages |
| Share-capital rounding threshold | "R$ 16.7 million" | R$ 16,777,216 (2²⁴) | wave 1 report |
| APIs that accept and validate the alphanumeric CNPJ | "S01, S02 and S07" in the ranking and `llms.txt` | all except S06 (S01–S05 and S07) | freshness report and `summary.json` (F4 probe) |
| Per-request evidence | links to `results/*/data/*.csv` and `SHA256SUMS`, which were never in the repository | the text says only aggregates are published | repository tree |

## 11. What is published
| Published | Where |
|---|---|
| Every aggregate number, per API | [results/summary.json](../results/summary.json) |
| Samples and run labels behind each result | [results/manifest.yaml](../results/manifest.yaml) |
| Reports, charts and per-field table | [wave 1](../results/wave1/REPORT.md), [wave 2](../results/wave2/REPORT.md), [freshness](../results/freshness/REPORT.md), [per-field table](../results/wave1/DATASHEET.md) |
| Collection, conversion and metric code | [src/cnpjbench/](../src/cnpjbench/), [scripts/](../scripts/) |

Not published: the raw API answers, the per-request telemetry and the CNPJ list of the quality
sample, because that list comes from a private registry and would reveal the companies. The frontier
and alphanumeric samples use no private data and can be rebuilt exactly with steps 32 and 33 and
seed 20261116 ([reproduce.md](reproduce.md)).

## 12. References
- ISO/IEC 25012:2008. *Software engineering — Software product Quality Requirements and Evaluation (SQuaRE) — Data quality model.*
- Wang, R. Y.; Strong, D. M. (1996). Beyond accuracy: what data quality means to data consumers. *Journal of Management Information Systems* 12(4), 5–33.
- Pipino, L. L.; Lee, Y. W.; Wang, R. Y. (2002). Data quality assessment. *Communications of the ACM* 45(4), 211–218.
- Batini, C.; Scannapieco, M. (2016). *Data and Information Quality: Dimensions, Principles and Techniques.* Springer.
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association* 22(158), 209–212.
- Wohlin, C. et al. (2012). *Experimentation in Software Engineering.* Springer (threats-to-validity classification).
- Receita Federal do Brasil. Instrução Normativa RFB nº 2.229/2024 (alphanumeric CNPJ).
