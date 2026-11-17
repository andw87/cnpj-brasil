# S03 — ReceitaWS

English: [../../sources/S03-receitaws.md](../../sources/S03-receitaws.md) · Todas as APIs: [sugestão por caso de uso](../ranking.md)

> Cobertura de 99,0% das empresas existentes, mas 2,5 CNPJs/min efetivos no limite documentado de 3 requisições/min, 16,0% de HTTP 429 nesse ritmo, o plano gratuito serve só o próprio cache e os termos proíbem uso comercial. Adequada a consultas ocasionais.

_Medição exploratória, uma janela de coleta em 16–17/11/2026 (UTC), um cliente. Todos os números abaixo vêm de [results/summary.json](../../../results/summary.json). Método: [metodologia](../methodology.md)._

## Ficha
| Item | Valor |
|---|---|
| Endpoint | `GET https://receitaws.com.br/v1/cnpj/{cnpj}` |
| Autenticação | nenhuma (plano gratuito) |
| Mantenedor | Empresa comercial (ReceitaWS) |
| Site | https://receitaws.com.br |
| Documentação | https://developers.receitaws.com.br |
| Código-fonte | — |
| Limite documentado | 3 requisições por minuto (plano gratuito) |
| Comportamento medido no limite | `X-RateLimit-Limit: 3`; 16% das requisições receberam 429 mesmo no ritmo de 3 req/min |
| Origem dos dados (declarada) | consultas ao site da Receita Federal guardadas em cache próprio; a API gratuita serve só o cache, um CNPJ fora do cache responde HTTP 504 ([spec](https://developers.receitaws.com.br/receitaws.yaml)) |
| Atualização (declarada) | por registro (`ultima_atualizacao`) |
| Termos de uso | apenas para benefício próprio, sem comercialização ([termos](https://receitaws.com.br/terms.pdf)) |
| CNPJ alfanumérico (medido) | aceita o formato: dígito verificador errado → HTTP 400, exemplo alfanumérico 12.ABC.345/01DE-35 → HTTP 200 |

## Como conectar
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

Erros vêm com HTTP 200 e `{"status": "ERROR", "message": ...}`. Datas em `dd/mm/aaaa`; natureza jurídica como `"206-2 - Sociedade Empresária Limitada"`.

### Respostas observadas
| Caso | HTTP | Corpo (início) |
|---|---|---|
| encontrado | 200 | — |
| dígito verificador errado | 400 | `{   "status": "ERROR",   "message": "CNPJ inválido" }` |
| exemplo alfanumérico 12.ABC.345/01DE-35 | 200 | `{   "cnpj": "12.ABC.345/01DE-35",   "ultima_atualizacao": "2026-11-10T18:44:35.100Z",   "s` |
| HTTP 429 | 429 | HTTP 429 com `X-RateLimit-Limit`, `X-RateLimit-Remaining` |

## Campos retornados (medidos)
| Campo canônico | Caminho JSON na resposta | Preenchido % | Concorda com outras fontes % |
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
| `address_city_ibge` | — | não retorna | — |
| `phones` | `telefone` | 93 | 85 |
| `email` | `email` | 79 | 100 |
| `partners` | `qsa[].nome, qsa[].qual` | 67 | 98 |
| `simples_optant` | `simples.optante` | 100 | 100 |
| `mei_optant` | `simei.optante` | 100 | 100 |

## Desempenho medido
| Item | Valor |
|---|---|
| Cobertura, onda 1 (intervalo de Wilson de 95%; n = CNPJs com resposta conclusiva) | 99,0% (97,1–99,7), n = 300 |
| Latência p50 / p95 | 238 / 287 ms |
| Vazão efetiva (ritmo usado entre parênteses) | 2,5 CNPJs/min (3 req/min) |
| Tentativas respondidas com HTTP 429 no ritmo usado | 16,0% |
| Onda 2, rampa: proporção de HTTP 429 a 1× / 2× / 4× o ritmo (requisições tentadas/min) | 15,6% @ 3 / 56,2% @ 6 / 77,8% @ 12 |
| Onda 2, rajadas sem ritmo, 4 requisições simultâneas, 2 × 100 requisições (requisições tentadas/min) | interrompida após 10 respostas HTTP 429 seguidas (regra de parada do teste) (ambas) |

## Frescor
| Item | Valor |
|---|---|
| Abertura mais recente retornada | 27/10/2026 |
| Empresas abertas de 16/10/2026 a 14/11/2026 retornadas (encontradas / existentes) | 71% (5/7) |
| Idade declarada do registro (p50 / p90) | 35 / 35 dias |

## Problemas observados
- CNAE principal ausente em 27% e quadro societário em 17% dos registros em que outras fontes os têm.
- Não retorna código IBGE do município.
- Telefone em texto livre, incluindo o fax.
- Vazão efetiva de 2,5 CNPJs por minuto.
- Empresas novas que ninguém consultou antes recebem `{"status": "ERROR", "message": "not in cache"}` (HTTP 404) no plano gratuito.

## Evidências
- Relatórios: [onda 1, qualidade](../../../results/wave1/REPORT.pt-BR.md) · [onda 2, limites](../../../results/wave2/REPORT.pt-BR.md) · [frescor](../../../results/freshness/REPORT.pt-BR.md)
- Código do conector: [s03_receitaws.py](../../../src/cnpjbench/connectors/s03_receitaws.py)
