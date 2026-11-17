# S05 — CNPJ.ws (public API)

English: [../../sources/S05-cnpjws-public.md](../../sources/S05-cnpjws-public.md) · Todas as APIs: [sugestão por caso de uso](../ranking.md)

> Retorna inscrições estaduais (`inscricoes_estaduais`), que nenhuma outra fonte deste estudo retorna. 1,4 CNPJ/min efetivo a 3 requisições/min; degradada durante o teste (12,4% dos CNPJs terminaram em HTTP 500/504 ou timeout); os termos proíbem uso comercial.

_Medição exploratória, uma janela de coleta em 16–17/11/2026 (UTC), um cliente. Todos os números abaixo vêm de [results/summary.json](../../../results/summary.json). Método: [metodologia](../methodology.md)._

## Ficha
| Item | Valor |
|---|---|
| Endpoint | `GET https://publica.cnpj.ws/cnpj/{cnpj}` |
| Autenticação | nenhuma |
| Mantenedor | Empresa comercial (CNPJ.ws), plano público gratuito |
| Site | https://www.cnpj.ws |
| Documentação | https://docs.cnpj.ws/referencia-de-api/api-publica |
| Código-fonte | — |
| Limite documentado | 3 requisições por minuto por IP; mais de 360 HTTP 429 em uma hora bloqueia o IP por 1 hora ([limitações](https://docs.cnpj.ws/referencia-de-api/api-publica/limitacoes)) |
| Comportamento medido no limite | `x-ratelimit-limit: 3`, `x-ratelimit-reset`; 11% das requisições receberam 429 a 3 req/min; a partir de ~02:00 UTC de 17/11/2026, majoritariamente HTTP 500/504 e timeouts |
| Origem dos dados (declarada) | Receita Federal, SEFAZ/SINTEGRA, Suframa, coletados periodicamente ([docs](https://docs.cnpj.ws)) |
| Atualização (declarada) | defasagem máxima de 45 dias ([termos](https://www.cnpj.ws/pt-BR/termos-de-uso)); por registro (`atualizado_em`) |
| Termos de uso | apenas para benefício próprio, sem comercialização ([termos](https://www.cnpj.ws/pt-BR/termos-de-uso)) |
| CNPJ alfanumérico (medido) | aceita o formato: dígito verificador errado → HTTP 400, exemplo alfanumérico 12.ABC.345/01DE-35 → HTTP 404 |

## Como conectar
```bash
curl -s 'https://publica.cnpj.ws/cnpj/33000167000101'
```
```python
import requests
r = requests.get('https://publica.cnpj.ws/cnpj/{cnpj}'.format(cnpj='33000167000101'), timeout=20)
data = r.json() if r.status_code == 200 else None   # 429: wait for x-ratelimit-reset seconds
```
```javascript
const r = await fetch(`https://publica.cnpj.ws/cnpj/${cnpj}`);
const data = r.status === 200 ? await r.json() : null;
```

Dados do estabelecimento ficam em `estabelecimento`; inclui inscrições estaduais (`inscricoes_estaduais`), que nenhuma outra fonte gratuita retorna.

### Respostas observadas
| Caso | HTTP | Corpo (início) |
|---|---|---|
| encontrado | 504 | `      <!DOCTYPE html>       <html>       <head>           <meta name="viewport" content="w` |
| dígito verificador errado | 400 | `{"status":400,"titulo":"Requisição inválida","detalhes":"CNPJ inválido","validacao":[]}` |
| exemplo alfanumérico 12.ABC.345/01DE-35 | 404 | `{"status":404,"titulo":"Não encontrado","detalhes":"Recurso não encontrado","validacao":[]` |
| HTTP 429 | 429 | HTTP 429 com `x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-reset` |

## Campos retornados (medidos)
| Campo canônico | Caminho JSON na resposta | Preenchido % | Concorda com outras fontes % |
|---|---|---|---|
| `legal_name` | `razao_social` | 100 | 100 |
| `trade_name` | `estabelecimento.nome_fantasia` | 68 | 100 |
| `establishment_type` | `estabelecimento.tipo` | 100 | 100 |
| `registration_status` | `estabelecimento.situacao_cadastral` | 100 | 100 |
| `registration_status_date` | `estabelecimento.data_situacao_cadastral` | 97 | 100 |
| `opening_date` | `estabelecimento.data_inicio_atividade` | 100 | 100 |
| `legal_nature_code` | `natureza_juridica.id` | 100 | 100 |
| `legal_nature` | `natureza_juridica.descricao` | 100 | 99 |
| `company_size` | `porte.descricao` | 100 | 100 |
| `share_capital` | `capital_social` | 100 | 96 |
| `main_cnae` | `estabelecimento.atividade_principal.id` | 100 | 100 |
| `secondary_cnaes` | `estabelecimento.atividades_secundarias[].id` | 71 | 100 |
| `address_street` | `estabelecimento.tipo_logradouro + estabelecimento.logradouro` | 100 | 100 |
| `address_number` | `estabelecimento.numero` | 100 | 100 |
| `address_complement` | `estabelecimento.complemento` | 47 | 100 |
| `address_district` | `estabelecimento.bairro` | 100 | 100 |
| `address_city` | `estabelecimento.cidade.nome` | 100 | 100 |
| `address_state` | `estabelecimento.estado.sigla` | 100 | 100 |
| `address_zip` | `estabelecimento.cep` | 100 | 100 |
| `address_city_ibge` | `estabelecimento.cidade.ibge_id` | 100 | 100 |
| `phones` | `estabelecimento.ddd1 + telefone1, ddd2 + telefone2` | 91 | 100 |
| `email` | `estabelecimento.email` | 79 | 100 |
| `partners` | `socios[].nome, socios[].qualificacao_socio.descricao` | 82 | 79 |
| `simples_optant` | `simples.simples` | 61 | 100 |
| `mei_optant` | `simples.mei` | 61 | 100 |

## Desempenho medido
| Item | Valor |
|---|---|
| Cobertura, onda 1 (intervalo de Wilson de 95%; n = CNPJs com resposta conclusiva) | 99,1% (96,8–99,8), n = 226 |
| Latência p50 / p95 | 374 / 15.967 ms |
| Vazão efetiva (ritmo usado entre parênteses) | 1,4 CNPJs/min (3 req/min) |
| Tentativas respondidas com HTTP 429 no ritmo usado | 11,0% |
| Onda 2, rampa: proporção de HTTP 429 a 1× / 2× / 4× o ritmo (requisições tentadas/min) | não executada: provedor degradado (HTTP 500/504) |

## Frescor
| Item | Valor |
|---|---|
| Abertura mais recente retornada | 27/10/2026 |
| Empresas abertas de 16/10/2026 a 14/11/2026 retornadas (encontradas / existentes) | 67% (2/3) |
| Idade declarada do registro (p50 / p90) | 38 / 38 dias |

## Problemas observados
- Degradou durante o teste: 12,4% dos CNPJs terminaram em HTTP 500/504 ou timeout; latência p95 de 16 s.
- Quadro societário concorda com as outras fontes em apenas 79% dos registros.
- Alguns registros omitem campos a pedido da empresa.
- Frescor: a data de abertura mais recente nos próprios registros é 27/10/2026; também retornou uma empresa aberta em 06/11/2026 (data informada pelas outras fontes) cujo registro não trazia data de abertura.

## Evidências
- Relatórios: [onda 1, qualidade](../../../results/wave1/REPORT.pt-BR.md) · [onda 2, limites](../../../results/wave2/REPORT.pt-BR.md) · [frescor](../../../results/freshness/REPORT.pt-BR.md)
- Código do conector: [s05_cnpjws_public.py](../../../src/cnpjbench/connectors/s05_cnpjws_public.py)
