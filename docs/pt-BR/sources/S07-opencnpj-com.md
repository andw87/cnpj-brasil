# S07 — OpenCNPJ.com (Kitana API)

English: [../../sources/S07-opencnpj-com.md](../../sources/S07-opencnpj-com.md) · Todas as APIs: [sugestão por caso de uso](../ranking.md)

> Menor latência medida (p50 53 ms, p95 94 ms); limite documentado de 300 requisições/min. Dados cerca de dois meses atrás (a empresa mais recente retornada abriu em 11/09/2026); sem licença de reutilização.

_Medição exploratória, uma janela de coleta em 16–17/11/2026 (UTC), um cliente. Todos os números abaixo vêm de [results/summary.json](../../../results/summary.json). Método: [metodologia](../methodology.md)._

## Ficha
| Item | Valor |
|---|---|
| Endpoint | `GET https://kitana.opencnpj.com/cnpj/{cnpj}` |
| Autenticação | nenhuma |
| Mantenedor | OpenCaramelo — projeto diferente do OpenCNPJ.org, apesar do nome |
| Site | https://opencnpj.com |
| Documentação | https://opencnpj.com |
| Código-fonte | https://github.com/opencaramelo/opencnpj |
| Limite documentado | 300 requisições por minuto por IP (cabeçalhos `X-Ratelimit-Limit: 300`) |
| Comportamento medido no limite | nenhum 429 até ~4.700 req/min (4 simultâneas) |
| Origem dos dados (declarada) | 'fontes oficiais da Receita Federal'; processo não documentado |
| Atualização (declarada) | não documentada; medido: empresa mais recente retornada abriu em 11/09/2026 |
| Termos de uso | repositório sem licença; 'todos os direitos reservados' no site |
| CNPJ alfanumérico (medido) | aceita o formato: dígito verificador errado → HTTP 400, exemplo alfanumérico 12.ABC.345/01DE-35 → HTTP 404 |

## Como conectar
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

Envelope `{"success": true, "data": {...}}`; chaves em camelCase; datas `dd/mm/aaaa`; natureza jurídica como `"Texto (2062)"`; o primeiro item de `cnaes` é o CNAE principal.

### Respostas observadas
| Caso | HTTP | Corpo (início) |
|---|---|---|
| encontrado | 200 | — |
| dígito verificador errado | 400 | `{"success":false,"message":"CNPJ inválido.","data":null}` |
| exemplo alfanumérico 12.ABC.345/01DE-35 | 404 | — |

## Campos retornados (medidos)
| Campo canônico | Caminho JSON na resposta | Preenchido % | Concorda com outras fontes % |
|---|---|---|---|
| `legal_name` | `data.razaoSocial` | 100 | 99 |
| `trade_name` | `data.nomeFantasia` | 66 | 100 |
| `establishment_type` | `data.matriz` | 100 | 100 |
| `registration_status` | `data.situacaoCadastral` | 100 | 100 |
| `registration_status_date` | `data.dataSituacaoCadastral` | 98 | 100 |
| `opening_date` | `data.dataInicioAtividades` | 100 | 100 |
| `legal_nature_code` | `data.naturezaJuridica` | 100 | 99 |
| `legal_nature` | `data.naturezaJuridica` | 100 | 99 |
| `company_size` | — | não retorna | — |
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
| `address_city_ibge` | — | não retorna | — |
| `phones` | `data.telefone` | 93 | 84 |
| `email` | `data.email` | 79 | 100 |
| `partners` | `data.socios[].nomeSocio, data.socios[].descricao` | 80 | 95 |
| `simples_optant` | `data.opcaoSimples` | 100 | 100 |
| `mei_optant` | `data.opcaoMei` | 100 | 100 |

## Desempenho medido
| Item | Valor |
|---|---|
| Cobertura, onda 1 (intervalo de Wilson de 95%; n = CNPJs com resposta conclusiva) | 99,0% (97,1–99,7), n = 300 |
| Latência p50 / p95 | 53 / 94 ms |
| Vazão efetiva (ritmo usado entre parênteses) | 120,7 CNPJs/min (120 req/min) |
| Tentativas respondidas com HTTP 429 no ritmo usado | 0,0% |
| Onda 2, rampa: proporção de HTTP 429 a 1× / 2× / 4× o ritmo (requisições tentadas/min) | 0,0% @ 123 / 0,0% @ 246 / 0,0% @ 487 |
| Onda 2, rajadas sem ritmo, 4 requisições simultâneas, 2 × 100 requisições (requisições tentadas/min) | 0,0% @ 4.187 / 0,0% @ 4.718 |

## Frescor
| Item | Valor |
|---|---|
| Abertura mais recente retornada | 11/09/2026 |
| Empresas abertas de 16/10/2026 a 14/11/2026 retornadas (encontradas / existentes) | 0% (0/67) |
| Idade declarada do registro (p50 / p90) | — |

## Problemas observados
- Cerca de dois meses de atraso: metade das empresas abertas em 01–15/09/2026 e nenhuma aberta depois de 15/09/2026 foram retornadas.
- Não retorna porte nem código IBGE; retorna só o primeiro telefone.

## Evidências
- Relatórios: [onda 1, qualidade](../../../results/wave1/REPORT.pt-BR.md) · [onda 2, limites](../../../results/wave2/REPORT.pt-BR.md) · [frescor](../../../results/freshness/REPORT.pt-BR.md)
- Código do conector: [s07_opencnpj_com.py](../../../src/cnpjbench/connectors/s07_opencnpj_com.py)
