# S06 — OpenCNPJ.org

English: [../../sources/S06-opencnpj-org.md](../../sources/S06-opencnpj-org.md) · Todas as APIs: [sugestão por caso de uso](../ranking.md)

> Cobertura de 99,0%; 0% de HTTP 429 até 5.209 requisições/min; uso comercial permitido pelo FAQ; base completa para download. Dados uma publicação mensal atrás: a empresa mais recente retornada abriu em 08/10/2026.

_Medição exploratória, uma janela de coleta em 16–17/11/2026 (UTC), um cliente. Todos os números abaixo vêm de [results/summary.json](../../../results/summary.json). Método: [metodologia](../methodology.md)._

## Ficha
| Item | Valor |
|---|---|
| Endpoint | `GET https://api.opencnpj.org/{cnpj}` |
| Autenticação | nenhuma |
| Mantenedor | Projeto de código aberto sem fins lucrativos (MIT) |
| Site | https://opencnpj.org |
| Documentação | https://opencnpj.org |
| Código-fonte | https://github.com/Hitmasu/OpenCNPJ |
| Limite documentado | sem cota fixa; picos acima de 100 requisições/segundo aceitos; abuso contínuo → 429 ([opencnpj.org](https://opencnpj.org)) |
| Comportamento medido no limite | nenhum 429 até ~5.200 req/min (4 simultâneas) |
| Origem dos dados (declarada) | base mensal da Receita Federal → ETL → fragmentos estáticos no Cloudflare R2; base completa também disponível para download; `/info` informa `source_snapshot_month: 2026-10` |
| Atualização (declarada) | mensal; a base de 2026-10 (publicada em 13/10/2026) foi carregada em 01/11/2026 |
| Termos de uso | código MIT; uso gratuito, inclusive comercial (FAQ do site) |
| CNPJ alfanumérico (medido) | não valida a entrada (dígito errado → 404) |

## Como conectar
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

Valide os dígitos verificadores antes: a API responde 404 para CNPJ inválido. `GET https://api.opencnpj.org/info` informa o mês da base e o número de registros.

### Respostas observadas
| Caso | HTTP | Corpo (início) |
|---|---|---|
| encontrado | 200 | — |
| dígito verificador errado | 404 | `{"error":"not found"}` |
| exemplo alfanumérico 12.ABC.345/01DE-35 | 404 | `{"error":"not found"}` |

## Campos retornados (medidos)
| Campo canônico | Caminho JSON na resposta | Preenchido % | Concorda com outras fontes % |
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
| `address_city_ibge` | — | não retorna | — |
| `phones` | `telefones[].ddd + telefones[].numero` | 93 | 99 |
| `email` | `email` | 79 | 100 |
| `partners` | `QSA[].nome_socio, QSA[].qualificacao_socio` | 81 | 96 |
| `simples_optant` | `opcao_simples` | 57 | 100 |
| `mei_optant` | `opcao_mei` | 57 | 100 |

## Desempenho medido
| Item | Valor |
|---|---|
| Cobertura, onda 1 (intervalo de Wilson de 95%; n = CNPJs com resposta conclusiva) | 99,0% (97,1–99,7), n = 300 |
| Latência p50 / p95 | 496 / 673 ms |
| Vazão efetiva (ritmo usado entre parênteses) | 121,7 CNPJs/min (300 req/min) |
| Tentativas respondidas com HTTP 429 no ritmo usado | 0,0% |
| Onda 2, rampa: proporção de HTTP 429 a 1× / 2× / 4× o ritmo (requisições tentadas/min) | 0,0% @ 308 / 0,0% @ 511 / 0,0% @ 1.091 |
| Onda 2, rajadas sem ritmo, 4 requisições simultâneas, 2 × 100 requisições (requisições tentadas/min) | 0,0% @ 5.209 / 0,0% @ 5.077 |

## Frescor
| Item | Valor |
|---|---|
| Abertura mais recente retornada | 08/10/2026 |
| Empresas abertas de 16/10/2026 a 14/11/2026 retornadas (encontradas / existentes) | 0% (0/67) |
| Idade declarada do registro (p50 / p90) | 15 / 15 dias |

## Problemas observados
- Cerca de um mês atrás da base oficial: a empresa mais recente retornada abriu em 08/10/2026; nenhuma das empresas abertas depois de 15/10/2026 foi retornada.
- Não retorna código IBGE; Simples/MEI preenchidos em 57% dos registros.
- Não valida a entrada (dígito errado → 404).

## Evidências
- Relatórios: [onda 1, qualidade](../../../results/wave1/REPORT.pt-BR.md) · [onda 2, limites](../../../results/wave2/REPORT.pt-BR.md) · [frescor](../../../results/freshness/REPORT.pt-BR.md)
- Código do conector: [s06_opencnpj_org.py](../../../src/cnpjbench/connectors/s06_opencnpj_org.py)
