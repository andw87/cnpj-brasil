# S02 — Minha Receita

English: [../../sources/S02-minhareceita.md](../../sources/S02-minhareceita.md) · Todas as APIs: [sugestão por caso de uso](../ranking.md)

> Dados mais recentes entre as sete fontes medidas (empresas abertas até 14/11/2026 presentes em 16/11/2026). Sem chave; nenhum limite documentado ou observado (0% de HTTP 429 a até 6.310 requisições/min); código aberto e auto-hospedável. Ressalvas medidas: 404 servido de cache antigo para 7,4% dos CNPJs existentes, capital social acima de R$ 16.777.216 arredondado, sem e-mail.

_Medição exploratória, uma janela de coleta em 16–17/11/2026 (UTC), um cliente. Todos os números abaixo vêm de [results/summary.json](../../../results/summary.json). Método: [metodologia](../methodology.md)._

## Ficha
| Item | Valor |
|---|---|
| Endpoint | `GET https://minhareceita.org/{cnpj}` |
| Autenticação | nenhuma |
| Mantenedor | Projeto de código aberto mantido por um desenvolvedor, financiado por doações; código migrado para o Codeberg |
| Site | https://minhareceita.org |
| Documentação | https://docs.minhareceita.org |
| Código-fonte | https://codeberg.org/cuducos/minha-receita |
| Limite documentado | sem limite por decisão de projeto ([PR #99](https://codeberg.org/cuducos/minha-receita/pulls/99)); para uso intenso recomenda-se hospedar a própria instância |
| Comportamento medido no limite | nenhum 429 a ~6.300 req/min (4 simultâneas, CNPJs em cache) |
| Origem dos dados (declarada) | base mensal de dados abertos da Receita Federal, baixada do compartilhamento oficial ([download/webdav.go](https://codeberg.org/cuducos/minha-receita/src/branch/main/download/webdav.go)); `/updated` respondeu `2026-11` |
| Atualização (declarada) | mensal, manual, 'normalmente poucos dias após a publicação' ([FAQ](https://docs.minhareceita.org/faq/)); a base de 2026-11 (extraída em 14/11/2026) estava no ar em 16/11/2026 |
| Termos de uso | código MIT; não foram encontrados termos de uso da instância pública |
| CNPJ alfanumérico (medido) | aceita o formato: dígito verificador errado → HTTP 400, exemplo alfanumérico 12.ABC.345/01DE-35 → HTTP 404 |

## Como conectar
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

A Cloudflare guarda respostas por até 5 dias (`max-age=432000`), inclusive 404. Pedir a forma pontuada (`/12.345.678%2F0001-95`) evita uma entrada antiga. `/updated` informa o mês da base. Para volume, rode sua própria instância (Docker, PostgreSQL).

### Respostas observadas
| Caso | HTTP | Corpo (início) |
|---|---|---|
| encontrado | 200 | — |
| dígito verificador errado | 400 | `{"message":"CNPJ 33.000.167/0001-02 inválido."}` |
| exemplo alfanumérico 12.ABC.345/01DE-35 | 404 | `{"message":"CNPJ 12.ABC.345/01DE-35 não encontrado."}` |

## Campos retornados (medidos)
| Campo canônico | Caminho JSON na resposta | Preenchido % | Concorda com outras fontes % |
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
| `email` | `email` | não retorna | — |
| `partners` | `qsa[].nome_socio, qsa[].qualificacao_socio` | 80 | 96 |
| `simples_optant` | `opcao_pelo_simples` | 59 | 100 |
| `mei_optant` | `opcao_pelo_mei` | 59 | 100 |

## Desempenho medido
| Item | Valor |
|---|---|
| Cobertura, onda 1 (intervalo de Wilson de 95%; n = CNPJs com resposta conclusiva) | 91,7% (88,0–94,3), n = 300 |
| Latência p50 / p95 | 297 / 343 ms |
| Vazão efetiva (ritmo usado entre parênteses) | 60,1 CNPJs/min (60 req/min) |
| Tentativas respondidas com HTTP 429 no ritmo usado | 0,0% |
| Onda 2, rampa: proporção de HTTP 429 a 1× / 2× / 4× o ritmo (requisições tentadas/min) | 0,0% @ 62 / 0,0% @ 123 / 0,0% @ 247 |
| Onda 2, rajadas sem ritmo, 4 requisições simultâneas, 2 × 100 requisições (requisições tentadas/min) | 0,0% @ 5.437 / 0,0% @ 6.310 |

## Frescor
| Item | Valor |
|---|---|
| Abertura mais recente retornada | 14/11/2026 |
| Empresas abertas de 16/10/2026 a 14/11/2026 retornadas (encontradas / existentes) | 100% (67/67) |
| Idade declarada do registro (p50 / p90) | — |

## Problemas observados
- **404 antigos em cache.** 22 dos 297 CNPJs existentes (7,4%) receberam 404 com `cf-cache-status: HIT`; os 22 foram retornados (200) na forma pontuada. Mecanismo conhecido: 404 gerados durante recargas ou quedas permanecem em cache ([#1](https://codeberg.org/cuducos/minha-receita/issues/1), [#98](https://codeberg.org/cuducos/minha-receita/issues/98)).
- Capital social acima de 16.777.216 é arredondado (float32).
- Não retorna e-mail; logradouro e número ausentes em 14% dos registros; Simples/MEI preenchidos em 59% dos registros.
- Quedas: ~99% HTTP 503 em 08–09/10/2026 ([#98](https://codeberg.org/cuducos/minha-receita/issues/98)).

## Evidências
- Relatórios: [onda 1, qualidade](../../../results/wave1/REPORT.pt-BR.md) · [onda 2, limites](../../../results/wave2/REPORT.pt-BR.md) · [frescor](../../../results/freshness/REPORT.pt-BR.md)
- Código do conector: [s02_minhareceita.py](../../../src/cnpjbench/connectors/s02_minhareceita.py)
