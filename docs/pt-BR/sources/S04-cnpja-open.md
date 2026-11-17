# S04 — CNPJá Open

English: [../../sources/S04-cnpja-open.md](../../sources/S04-cnpja-open.md) · Todas as APIs: [sugestão por caso de uso](../ranking.md)

> Maior completude relativa medida (99,8%; inclui código IBGE, e-mail e Simples/MEI). Limitada a 5 requisições/min por IP (4,5 CNPJs/min efetivos, 10,7% de HTTP 429 nesse ritmo); 13 de 36 empresas abertas em 01–14/11/2026 receberam HTTP 402 no plano gratuito. Adequada para completar registros individuais de empresas já estabelecidas.

_Medição exploratória, uma janela de coleta em 16–17/11/2026 (UTC), um cliente. Todos os números abaixo vêm de [results/summary.json](../../../results/summary.json). Método: [metodologia](../methodology.md)._

## Ficha
| Item | Valor |
|---|---|
| Endpoint | `GET https://open.cnpja.com/office/{cnpj}` |
| Autenticação | nenhuma |
| Mantenedor | Empresa comercial (CNPJá), plano público gratuito |
| Site | https://cnpja.com |
| Documentação | https://cnpja.com/api/open |
| Código-fonte | — |
| Limite documentado | 5 requisições por minuto por IP ([cnpja.com/api/open](https://cnpja.com/api/open)) |
| Comportamento medido no limite | 11% das requisições receberam 429 mesmo no ritmo de 5 req/min |
| Origem dos dados (declarada) | agregação própria de dados da Receita Federal e do Simples Nacional; declara não ser a fonte original ([termos](https://cnpja.com/subscription/tos)) |
| Atualização (declarada) | 'garantia de atualização de 45 dias ou menos para estabelecimentos ativos' ([cnpja.com/api/open](https://cnpja.com/api/open)); por registro (`updated`) |
| Termos de uso | ver [termos](https://cnpja.com/subscription/tos); restrições do plano gratuito não confirmadas |
| CNPJ alfanumérico (medido) | aceita o formato: dígito verificador errado → HTTP 400, exemplo alfanumérico 12.ABC.345/01DE-35 → HTTP 404 |

## Como conectar
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

JSON aninhado com chaves em inglês (`company.name`, `address.municipality`, `mainActivity.id`). Porte vem como sigla (`ME`, `EPP`, `DEMAIS`).

### Respostas observadas
| Caso | HTTP | Corpo (início) |
|---|---|---|
| encontrado | 200 | — |
| dígito verificador errado | 400 | `{"code":400,"message":"request validation failed","constraints":["taxId must be a string t` |
| exemplo alfanumérico 12.ABC.345/01DE-35 | 404 | `{"code":404,"message":"tax id not registered at revenue service"}` |
| HTTP 429 | 429 | HTTP 429; empresas recém-abertas: HTTP 402 `recently founded offices only available in commercial api` |

## Campos retornados (medidos)
| Campo canônico | Caminho JSON na resposta | Preenchido % | Concorda com outras fontes % |
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

## Desempenho medido
| Item | Valor |
|---|---|
| Cobertura, onda 1 (intervalo de Wilson de 95%; n = CNPJs com resposta conclusiva) | 99,0% (97,1–99,7), n = 300 |
| Latência p50 / p95 | 326 / 538 ms |
| Vazão efetiva (ritmo usado entre parênteses) | 4,5 CNPJs/min (5 req/min) |
| Tentativas respondidas com HTTP 429 no ritmo usado | 10,7% |
| Onda 2, rampa: proporção de HTTP 429 a 1× / 2× / 4× o ritmo (requisições tentadas/min) | 12,5% @ 5 / 46,9% @ 10 / 76,9% @ 22 |
| Onda 2, rajadas sem ritmo, 4 requisições simultâneas, 2 × 100 requisições (requisições tentadas/min) | interrompida após 10 respostas HTTP 429 seguidas (regra de parada do teste) (ambas) |

## Frescor
| Item | Valor |
|---|---|
| Abertura mais recente retornada | 10/11/2026 |
| Empresas abertas de 16/10/2026 a 14/11/2026 retornadas (encontradas / existentes) | 70% (30/43) |
| Idade declarada do registro (p50 / p90) | 38 / 38 dias |

## Problemas observados
- Vazão efetiva de 4,5 CNPJs por minuto; 11% das requisições limitadas no ritmo documentado.
- Telefones ausentes em 5% dos registros em que outras fontes os têm.
- Empresas recém-abertas: HTTP 402 `recently founded offices only available in commercial api` para 13 das 36 empresas abertas em 01–14/11/2026 consultadas.

## Evidências
- Relatórios: [onda 1, qualidade](../../../results/wave1/REPORT.pt-BR.md) · [onda 2, limites](../../../results/wave2/REPORT.pt-BR.md) · [frescor](../../../results/freshness/REPORT.pt-BR.md)
- Código do conector: [s04_cnpja_open.py](../../../src/cnpjbench/connectors/s04_cnpja_open.py)
