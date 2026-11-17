# Como reproduzir

English: [../reproduce.md](../reproduce.md) · Método: [methodology.md](methodology.md)

Os comandos rodam a partir da raiz do repositório. Os caminhos mostrados são do Windows; no Linux e
no macOS use `.venv/bin/python` no lugar de `.venv/Scripts/python`. Os scripts são numerados na
ordem em que rodam (o dígito das dezenas é a etapa; o das unidades, uma variante dentro da etapa).

## O que pode ser repetido sem dados privados
| Parte | Precisa de dados privados? | Como |
|---|---|---|
| Testes do código (conectores, normalização, métricas) | não; não usa rede | `pytest`, abaixo |
| Fichas por API a partir dos números publicados | não; não usa rede | passo 95 |
| Frescor e CNPJ alfanumérico | não; os CNPJs são gerados pelo código | passos 32, 33, 40, 52 |
| Qualidade (onda 1) e limites (onda 2) | precisa de uma lista de CNPJs reais | qualquer lista no formato do arquivo de semente, abaixo |

## Configuração (uma vez)
```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev,viz]"
cp .env.example .env               # configurações locais; o arquivo .env não é versionado
docker compose up -d               # MongoDB 7.0 em 127.0.0.1:27017, guarda respostas e métricas
.venv/Scripts/python -m pytest -q  # todos os testes devem passar antes de qualquer coleta
```

## Arquivo de semente (lista de CNPJs para a onda 1)
O teste de qualidade sorteia CNPJs de um arquivo `data/seed/seed_companies.jsonl` (a pasta `data/`
não é versionada). O estudo publicado usou um cadastro privado, que não está no repositório. Para
repetir com outra lista, gere um objeto JSON por linha, em UTF-8:

```json
{"cnpj": "33000167000101", "ref_duplicates": 1,
 "ref": {"legal_name": "PETROLEO BRASILEIRO S A PETROBRAS", "registered_at": "2008-02-28",
         "address_street": "AV REPUBLICA DO CHILE", "address_number": "65",
         "address_district": "CENTRO", "address_city": "Rio de Janeiro", "address_state": "RJ",
         "address_zip": "20031170", "address_city_ibge": "3304557", "phones": ["2121660000"]}}
```

Só `cnpj` é obrigatório. As chaves de `ref` são opcionais e servem apenas para a concordância com o
cadastro de referência (métrica A2); valores vazios devem ser omitidos. O passo 20 rejeita CNPJs com
dígito verificador inválido.

## Etapas
| Passo | Comando | O que conferir |
|---|---|---|
| 00 | `python scripts/00_smoke_sources.py` | cada API ativa imprime `found` |
| 10 | `python scripts/10_init_db.py` | coleções e índices listados |
| 20 | `python scripts/20_import_seed.py --replace` | `accepted` = linhas − inválidas |
| 30 | `python scripts/30_draw_sample.py --size 1100` | identificador da amostra impresso |
| 40 | `python scripts/40_run_collection.py --all-active --sample <id da amostra>` | uma execução por API, situação `finished` |
| 50 | `python scripts/50_compute_metrics.py --sample <id da amostra>` | métricas por API |
| 60 | `python scripts/60_build_report.py --sample <id da amostra>` | relatório em `data/reports/` |

O passo 40 respeita o ritmo de cada API definido em [catalog/sources.yaml](../../catalog/sources.yaml).
Com 1.100 CNPJs, a duração é limitada pela API mais lenta (3 req/min ≈ 6 h 10 min). Uma execução
interrompida continua com `--source <ID> --sample <id> --resume <run_id>`, que pula os CNPJs já
encerrados.

## Comandos usados no estudo publicado
Os identificadores exatos das amostras estão em [results/manifest.yaml](../../results/manifest.yaml).

```bash
# onda 1: qualidade, no ritmo de cada API
python scripts/40_run_collection.py --all-active --sample SMP-20261116-n1100-r20261116 --limit 100 --label w1a
python scripts/40_run_collection.py --all-active --sample SMP-20261116-n1100-r20261116 --offset 100 --limit 200 --label w1b
python scripts/50_compute_metrics.py --sample SMP-20261116-n1100-r20261116 --labels w1a w1b
python scripts/70_build_charts.py quality --sample SMP-20261116-n1100-r20261116 --labels w1a w1b --name wave1
python scripts/75_build_datasheet.py --sample SMP-20261116-n1100-r20261116 --labels w1a w1b --name wave1

# onda 2: limites; W2 = id impresso pelo passo 31
python scripts/31_derive_sample.py --from-sample SMP-20261116-n1100-r20261116 --labels w1a w1b --size 196 --label w2
for S in S01 S02 S03 S04 S05 S06 S07; do sh scripts/wave2.sh $S $W2; done   # rampa 3x32 + 2 rajadas de 100 por API
python scripts/70_build_charts.py saturation --sample $W2 --burst-sample $W2 --name wave2

# reteste de "não encontrado": forma sem pontuação e depois pontuada; RT = id impresso pelo passo 34
python scripts/34_build_retest_sample.py --from-sample SMP-20261116-n1100-r20261116 --labels w1a w1b --sources S01 S02
python scripts/40_run_collection.py --source S01,S02 --sample $RT --label rt1
python scripts/40_run_collection.py --source S01,S02 --sample $RT --label rt2 --formatted-cnpj

# frescor e CNPJ alfanumérico: não precisam de dados privados
python scripts/32_build_frontier_sample.py --lo 66000000 --hi 70400000 --strata 22 --per-stratum 10
python scripts/32_build_frontier_sample.py --lo 69950000 --hi 70250000 --strata 6 --per-stratum 10 --label frontier2
python scripts/32_build_frontier_sample.py --lo 66000000 --hi 70400000 --strata 22 --per-stratum 3 --label frontierlite
python scripts/33_build_alphanumeric_sample.py --synthetic 9
python scripts/40_run_collection.py --all-active --sample <amostra de fronteira> --label fr   # APIs lentas: só frontierlite
python scripts/40_run_collection.py --all-active --sample <amostra alfanumérica> --label alnum
python scripts/52_compute_freshness.py --samples <frontier> <frontier2> <frontierlite> --labels fr --age-sample SMP-20261116-n1100-r20261116 --age-labels w1a w1b --alnum-sample <amostra alfanumérica>
python scripts/70_build_charts.py freshness --samples <frontier> --name freshness

# saídas consolidadas
python scripts/90_build_summary.py          # results/summary.json, a partir de results/manifest.yaml
python scripts/95_build_source_docs.py      # docs/sources/*.md e docs/pt-BR/sources/*.md; não usa rede nem banco
```

O passo 80 (`scripts/80_export_artifacts.py`) exporta a evidência por requisição com os CNPJs
substituídos por pseudônimos HMAC-SHA256 (a chave fica em `local/`, não versionada). Esses arquivos
não fazem parte deste repositório.

## API local de teste
Uma API local permite consultar cada conector e ver a resposta já convertida para o esquema comum:

```bash
.venv/Scripts/python -m uvicorn cnpjbench.api.app:app --app-dir src --port 8077
# documentação interativa em http://127.0.0.1:8077/docs
curl http://127.0.0.1:8077/sources/S06/lookup/33000167000101
```

## Como acrescentar uma API
1. Acrescente a API em [catalog/sources.yaml](../../catalog/sources.yaml) com o próximo
   identificador `S<NN>` livre. Os identificadores não são reutilizados, porque são a chave dos
   dados coletados.
2. Salve uma resposta real em `tests/fixtures/s<NN>_33000167000101.json` (anonimize nomes de pessoas).
3. Crie `src/cnpjbench/connectors/s<NN>_<slug>.py` seguindo `connectors/base.py`: `url(cnpj)` monta
   a URL, `classify(resp, payload)` classifica a resposta (§5.1 da metodologia, inclusive erros
   enviados com HTTP 200) e `parse(cnpj, payload)` converte para o esquema comum. Conectores não
   fazem I/O; transporte, ritmo, novas tentativas e telemetria ficam no executor, para que todas as
   APIs sejam medidas do mesmo jeito.
4. Acrescente o ID a `ACTIVE` em `tests/test_connectors.py`, rode `pytest` e o passo 00, e então
   defina `status: active` no catálogo.
5. Acrescente os fatos do provedor, com links, em
   [catalog/source_profiles.yaml](../../catalog/source_profiles.yaml) e o caminho de cada campo em
   [catalog/field_map.yaml](../../catalog/field_map.yaml).

Respeite os limites de cada provedor: não aumente `rate_limit_rpm` acima do valor documentado ou
observado.
