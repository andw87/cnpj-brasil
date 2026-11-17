# Metodologia

English: [../methodology.md](../methodology.md) · Resumo: [README](../../README.md) ·
Sugestão por caso de uso: [ranking.md](ranking.md)

## 1. Situação do estudo
Este é um **estudo comparativo exploratório**. Os dados foram coletados em uma noite (16–17/11/2026,
UTC), a partir de um único cliente e um único endereço IP, com amostras pequenas: 300 CNPJs para
qualidade, 196 para limites de requisição e 346 consultas (343 CNPJs distintos) para frescor. Os
resultados descrevem como as APIs se comportaram nessa janela. Não são uma certificação e não
preveem o comportamento futuro. Todos os números publicados estão em
[results/summary.json](../../results/summary.json), e a coleta pode ser repetida com o código deste
repositório ([reproduce.md](reproduce.md)).

## 2. Questões de pesquisa
| ID | Questão | Teste | Métricas (§5) |
|---|---|---|---|
| RQ1 | A API retorna um registro para CNPJs reais e válidos? | onda 1 | R2, R3, R4 |
| RQ2 | Quais campos ela entrega, e com que frequência? | onda 1 | C1, C2 |
| RQ3 | Os valores são bem formados e internamente consistentes? | onda 1 | Q1–Q4 |
| RQ4 | Os valores concordam com os das demais APIs? | onda 1 | A1 (A2 secundária) |
| RQ5 | Que vazão e latência são sustentáveis dentro dos limites, e o que acontece acima deles? | ondas 1 e 2 | T1–T7, S1–S11 |
| RQ6 | Uma empresa aberta neste mês, ou nesta semana, já aparece? | frescor | F1–F3 |
| RQ7 | O CNPJ alfanumérico (emitido desde julho de 2026) é aceito? | sonda alfanumérica | F4 |

## 3. Desenho e condições controladas
**Desenho.** Estudo comparativo de medição: a mesma lista de CNPJs é enviada a todas as APIs, pelo
mesmo cliente, na mesma janela de tempo. Toda tentativa HTTP é registrada (status, latência,
cabeçalhos, resultado). Toda resposta encontrada é guardada como recebida e convertida para um
esquema comum de 25 campos (§6), para que cada campo signifique a mesma coisa em todas as APIs.

**Condições iguais para todas as APIs.**
- Cliente HTTP `httpx`, tempo limite de 20 s por requisição, mesmo `User-Agent`
  (`cnpjbench/0.1 (research benchmark)`).
- Uma requisição por vez por API, no ritmo do limite documentado ou observado da API; 60
  requisições/min quando não há limite conhecido. As APIs rodam em paralelo entre si.
- Até 2 novas tentativas para HTTP 429, HTTP 5xx, tempo esgotado ou falha de conexão. A espera
  respeita `Retry-After` ou `X-RateLimit-Reset` quando a API os envia.
- A configuração de cada execução é gravada junto com os dados.

**Pré-registro.** As definições das métricas, a classificação dos resultados e os pesos do índice
composto (§5.5) foram fixados antes da coleta principal. Acréscimos posteriores (limites, frescor)
entraram como novas métricas; as definições anteriores não foram alteradas.

**Critérios de inclusão das APIs.** Uma API foi medida quando: (a) é gratuita ou de código aberto;
(b) é uma API HTTP que devolve JSON consultada por CNPJ; (c) pode ser usada sem contrato pago; e
(d) respondeu a uma consulta de teste em 16/11/2026 (CNPJ público 33.000.167/0001-01).

| ID | API | Acesso | Ritmo usado (req/min) e base | Situação |
|---|---|---|---|---|
| S01 | BrasilAPI | gratuito, sem chave | 60, sem limite conhecido | medida |
| S02 | Minha Receita (instância pública) | gratuito, sem chave | 60, sem limite conhecido | medida |
| S03 | ReceitaWS (plano gratuito) | gratuito, sem chave | 3, observado nos cabeçalhos | medida |
| S04 | CNPJá Open | gratuito, sem chave | 5, documentado | medida |
| S05 | CNPJ.ws (API pública) | gratuito, sem chave | 3, observado nos cabeçalhos | medida |
| S06 | OpenCNPJ.org | gratuito, sem chave | 300, documentado | medida |
| S07 | OpenCNPJ.com (API Kitana) | gratuito, sem chave | 120, ver nota | medida |
| S08 | Minha Receita auto-hospedada | instância própria | — | não medida (exige infraestrutura) |
| S09 | Arquivos de dados abertos da Receita Federal | download mensal | — | não medida (candidata a referência) |
| S10 | Invertexto | gratuito com chave | — | não medida (exige cadastro de chave) |
| S11 | Casa dos Dados | chave paga | — | excluída (paga) |
| S12 | SERPRO Consulta CNPJ | contrato pago | — | excluída (paga) |

Nota: a OpenCNPJ.com informa 300 req/min no cabeçalho `X-Ratelimit-Limit`; o teste usou 120
req/min, o valor registrado no catálogo antes da coleta. O motivo da diferença não foi registrado.
Fonte desta tabela: [catalog/sources.yaml](../../catalog/sources.yaml).

**Conduta com os provedores.** Os limites de cada API foram respeitados em todas as etapas, exceto
na onda 2, que testou de propósito o comportamento acima do limite sob regras de segurança (§4).
Só planos gratuitos foram usados. Nenhuma página web foi raspada e nenhuma chave de acesso foi usada.

## 4. Amostras e etapas de coleta
| Amostra | Tamanho | Construção | Uso |
|---|---|---|---|
| Principal | 1.100 sorteados; os primeiros 300 coletados | amostragem aleatória simples sem reposição, semente 20261116, sobre 35.702 CNPJs válidos de um cadastro de referência privado | onda 1 (qualidade) |
| Onda 2 | 196 | CNPJs encontrados por todas as APIs na onda 1; parte A com 96 (3 blocos de 32), parte B com 100 | onda 2 (limites) |
| Fronteira | 220 + 60 + 66 | CNPJs sintéticos de matriz construídos a partir de números-base sorteados (detalhes abaixo) | frescor |
| Reteste | 42 + 107 | CNPJs que uma API respondeu como "não encontrado" enquanto outra os retornou | separar 404 de cache antigo de registro ausente |
| Sonda alfanumérica | 12 | exemplo oficial `12.ABC.345/01DE-35`, 9 CNPJs alfanuméricos sintéticos válidos e 2 controles numéricos (um existente; o mesmo com dígito verificador errado) | CNPJ alfanumérico |

**População da amostra principal.** O cadastro de referência tinha 42.688 registros. Depois de
remover dígitos verificadores inválidos (3.847) e duplicatas, restaram 35.702 CNPJs válidos e
únicos, dos quais 29.854 (83,6%) são matrizes e nenhum é alfanumérico. Das 297 empresas da amostra
que existem, 85% são matrizes. O tamanho 1.100 foi escolhido para uma margem de ±3 pontos
percentuais com 95% de confiança; com os 300 coletados, a margem é de cerca de ±6 pontos.

**Onda 1 (qualidade).** Os primeiros 100 CNPJs da amostra principal (rótulo `w1a`) e os 200
seguintes (`w1b`), nas condições do §3, de 16/11/2026 23:55 a 17/11/2026 03:00 UTC.

**Onda 2 (limites de requisição).** Na parte A, três blocos de 32 CNPJs a 1×, 2× e 4× o ritmo da
API. Na parte B, 100 CNPJs sem controle de ritmo, com 4 requisições simultâneas, enviados duas
vezes. Regras de segurança: no máximo 4 requisições simultâneas por API, nenhuma nova tentativa,
parada após 10 respostas HTTP 429 seguidas e no máximo 300 requisições por API. A onda 2 rodou
depois das medições de qualidade e de frescor das APIs rápidas, para não afetá-las.

**Frescor (amostras de fronteira).** Os números-base de CNPJ (8 primeiros dígitos) são emitidos em
ordem crescente ao longo do tempo. Uma matriz (`/0001`) construída a partir de um número-base
próximo do maior já emitido é, portanto, uma empresa aberta recentemente. Isso fornece empresas
novas **sem nenhuma lista externa**.
- `frontier`: números-base entre 66,0 e 70,4 milhões, em 22 estratos de 200.000, 10 por estrato,
  sorteio uniforme com semente 20261116 (220 CNPJs).
- `frontier2`: faixa 69,95–70,25 milhões, 6 estratos × 10 (60 CNPJs), as últimas semanas antes da
  publicação.
- `frontierlite`: mesmos 22 estratos, 3 por estrato (66 CNPJs), para as APIs lentas (S03, S04,
  S05) caberem na mesma noite.
- Um CNPJ é considerado existente quando pelo menos uma API o retorna. Sua data de abertura é o
  valor informado pela maioria das APIs que o retornam. Números-base não usados (não encontrados em
  nenhuma API) são esperados e ficam fora do cálculo.
- Recall (proporção de empresas existentes que a API retornou) é agrupado por quinzena da data de
  abertura.

**Reteste.** Respostas "não encontrado" para CNPJs que outra API retornou foram consultadas de novo:
primeiro na forma sem pontuação e depois na forma pontuada (`12.345.678%2F0001-95`). Uma URL
diferente não usa a entrada de cache da CDN (rede de servidores intermediários que guarda respostas)
criada para a forma sem pontuação. Isso separa um 404 antigo guardado em cache de um registro que de
fato falta. Os cabeçalhos de cache da CDN foram registrados em cada tentativa.

## 5. Métricas

### 5.1 Resultado de cada CNPJ
| Resultado | Significado | Nova tentativa |
|---|---|---|
| found | registro retornado e interpretado | — |
| not_found | a API afirma que o CNPJ não está na sua base | — |
| restricted | a API retém o registro no plano gratuito: HTTP 402 "only available in commercial api" (S04) ou "not in cache" (S03) | — |
| invalid_input | a API rejeita o CNPJ como inválido | — |
| rate_limited | HTTP 429 | sim |
| server_error | HTTP 5xx | sim |
| timeout | sem resposta em 20 s | sim |
| network_error | falha de conexão | sim |
| client_error | outros 4xx | — |
| parse_error | resposta recebida, mas a conversão falhou | — |

### 5.2 Métricas por execução
| ID | Métrica | Definição |
|---|---|---|
| T1 | tentativas | número de requisições HTTP |
| T2 | CNPJs encerrados | número de CNPJs com resultado final |
| T3 | tempo total | do início da primeira ao fim da última tentativa, em segundos |
| T4 | vazão efetiva | T2 / (T3 / 60), em CNPJs por minuto |
| T5 | latência | p50, p95 e p99 das tentativas com resposta HTTP, em ms |
| T6 | proporção de HTTP 429 | tentativas `rate_limited` / T1 |
| T7 | novas tentativas por CNPJ | (T1 − T2) / T2 |
| R1 | resultados | distribuição dos resultados finais |
| R2 | taxa de encontrados | found / T2 |
| R3 | cobertura | found / (found + not_found + restricted) |
| R4 | taxa de erro | (T2 − found − not_found − restricted) / T2 |
| C1 | preenchimento | por campo: registros com valor / registros encontrados |
| Q1 | validade | por campo: valores válidos / valores preenchidos (regras de formato: CNAE com 7 dígitos, CEP com 8, UF existente, datas ISO etc.) |
| Q2 | codificação corrompida | valores de texto com caracteres corrompidos / valores de texto |
| Q3 | consistência matriz/filial | `establishment_type` corresponde ao número de ordem do CNPJ (`0001` = matriz) |
| Q4 | consistência IBGE/UF | os dois primeiros dígitos do código IBGE correspondem à UF |
| A2 | concordância com o cadastro de referência | por campo, contra o cadastro privado; sinal secundário (§7) |

### 5.3 Métricas entre APIs
| ID | Métrica | Definição |
|---|---|---|
| C2 | completude relativa | por campo: a API tem valor / CNPJs em que **alguma** API tem valor. Um campo legitimamente vazio (por exemplo, sem nome fantasia) não penaliza ninguém |
| A1 | concordância por consenso | por campo, quando pelo menos 3 APIs têm valor: proporção de vezes em que a API concorda com a maioria das demais |

Regras de igualdade: nomes, logradouro e bairro com similaridade ≥ 0,85 depois de remover acentos e
sufixos jurídicos; município, natureza jurídica e número exatos depois da normalização; porte
comparado por código (ME, EPP, DEMAIS), porque as APIs o rotulam de formas diferentes; capital
social com diferença de até 0,01; listas de CNAE, telefones e sócios comparadas como conjuntos;
e-mail sem diferenciar maiúsculas; demais campos exatos.

### 5.4 Métricas de limite (onda 2) e de frescor
| ID | Métrica | Definição |
|---|---|---|
| S1 | ritmo tentado | tentativas por minuto |
| S2 | ritmo de encontrados | tentativas `found` por minuto |
| S3 | início do 429 | posição (a partir de 0) da primeira tentativa respondida com HTTP 429 |
| S4 | proporção de 429 | tentativas `rate_limited` / tentativas |
| S5 | uso de Retry-After | respostas 429 com `Retry-After` / respostas 429 |
| S6 | cabeçalhos de limite | nomes de cabeçalho vistos nas respostas 429 |
| S7 | outros erros | resultados que não são found, 404 nem 429 |
| S8 | latência p50 dos encontrados | ms |
| S9–S11 | consistência na repetição | rajada 1 × rajada 2: CNPJs encontrados nas duas, proporção de registros idênticos, razão das latências p50 (abaixo de 1 sugere cache) |
| F1 | registro mais recente | data de abertura mais recente nos registros que a API retornou na amostra de fronteira |
| F2 | recall por quinzena | CNPJs retornados / CNPJs existentes, entre os que a API respondeu de forma conclusiva (erros excluídos) |
| F3 | idade declarada do registro | dias entre a coleta e o carimbo "atualizado em" da própria API (p10, p50, p90), para as APIs que o expõem |
| F4 | suporte alfanumérico | resposta a CNPJs alfanuméricos válidos: encontrado, não encontrado (formato aceito) ou rejeitado como entrada inválida |

### 5.5 Estatística e índice composto
- Os percentuais são proporções sobre os CNPJs que cada API encerrou. Cobertura e recall trazem
  intervalos de confiança de Wilson de 95% (Wilson, 1927). Diferenças com intervalos sobrepostos
  não são afirmadas.
- Latência é reportada em percentis (p50, p95, p99), não como média.
- **Índice composto (QI), pré-registrado:** QI = 0,25 · cobertura + 0,25 · completude relativa +
  0,20 · validade + 0,20 · concordância + 0,10 · pontuação de vazão, em que a pontuação de vazão é
  log10(T4) reescalado para 0–1 entre as APIs comparadas. O QI é publicado por transparência em
  [results/wave1/README.md](../../results/wave1/README.md), mas **não** decide a sugestão em
  [ranking.md](ranking.md): ele não inclui frescor, e um único peso não serve a todos os usos.

### 5.6 Correspondência com modelos de qualidade de dados
| Característica (ISO/IEC 25012) | Métrica aqui |
|---|---|
| Completude | C1, C2 |
| Acurácia sintática | Q1 |
| Acurácia semântica | A1 (aproximação por consenso, §7) |
| Consistência | Q2, Q3, Q4 |
| Atualidade | F1, F2, F3 |
| Disponibilidade | R3, R4, S7 |
| Eficiência | T4, T5, S1–S6 |

As mesmas dimensões aparecem em Wang e Strong (1996) e em Pipino, Lee e Wang (2002).

## 6. Esquema comum (25 campos comparados)
Cada conector converte a resposta da API para este modelo. Um valor que a API não entrega fica
ausente: os conectores nunca deduzem nem preenchem valores. O caminho JSON de cada campo em cada API
está em [catalog/field_map.yaml](../../catalog/field_map.yaml); a implementação está em
`src/cnpjbench/schema.py` e `src/cnpjbench/normalize.py`.

| Campo | Tipo | Normalização |
|---|---|---|
| `cnpj` (chave, não comparado) | texto, 14 caracteres | maiúsculas, apenas `[0-9A-Z]` |
| `legal_name` (razão social) | texto | espaços simples, sem espaços nas pontas |
| `trade_name` (nome fantasia) | texto | idem |
| `establishment_type` (matriz ou filial) | `head_office` ou `branch` | |
| `registration_status` (situação cadastral) | `active`, `suspended`, `unfit`, `closed`, `null` | códigos da Receita 2/3/4/8/1 ou textos |
| `registration_status_date` | data `AAAA-MM-DD` | a partir de ISO ou `DD/MM/AAAA` |
| `opening_date` (início de atividade) | data | idem |
| `legal_nature_code` | texto, 4 dígitos | zeros à esquerda |
| `legal_nature` (natureza jurídica) | texto | sem o código |
| `company_size` (porte) | texto | comparado por código (ME, EPP, DEMAIS) |
| `share_capital` (capital social) | número | aceita `1234.56` e `1.234,56` |
| `main_cnae` | texto, 7 dígitos | zeros à esquerda |
| `secondary_cnaes` | lista de textos de 7 dígitos | `0000000` descartado |
| `address_street` | texto | tipo de logradouro + nome |
| `address_number`, `address_complement`, `address_district`, `address_city` | texto | |
| `address_state` | texto, 2 letras | UF |
| `address_zip` | texto, 8 dígitos | CEP |
| `address_city_ibge` | texto, 7 dígitos | código IBGE do município |
| `phones` | lista | dígitos com DDD, sem duplicatas, fax excluído |
| `email` | texto | primeiro e-mail informado |
| `partners` (quadro societário) | lista de {nome, qualificação} | qualificação sem prefixo numérico |
| `simples_optant`, `mei_optant` | verdadeiro/falso | |

O carimbo "atualizado em" de cada API (`source_updated_at`) é guardado como metadado e usado só em F3.

## 7. Verdade de referência
Nenhuma das APIs é uma cópia oficial do cadastro da Receita Federal. A concordância entre APIs (A1)
mede consistência, não verdade: APIs que partem da mesma cópia podem concordar no mesmo erro. Como a
maioria delas deriva da mesma publicação mensal de dados abertos, A1 detecta principalmente defeitos
de conversão (arredondamento, truncamento, codificação, prefixos ausentes). O cadastro privado usado
no sorteio é antigo e em parte desatualizado; por isso a concordância com ele (A2) aparece apenas como
sinal secundário, na [tabela por campo](../../results/wave1/DATASHEET.md).

## 8. Ameaças à validade
| Tipo | Ameaça | Tratamento e risco que resta |
|---|---|---|
| Constructo | Consenso não é acurácia | declarado no §7; A1 reportada por campo |
| Constructo | "Não encontrado" pode significar "rejeitado", "não carregado", "retido no plano gratuito", "404 antigo em cache" ou "não existe" | resultados classificados por status HTTP e corpo (`restricted` para respostas pagas ou só de cache); reteste na forma pontuada; controles numéricos na sonda alfanumérica |
| Interna | Uma única janela de coleta; incidentes nos provedores | todas as APIs rodaram na mesma janela; incidentes são reportados (S05 degradada a partir de cerca de 02:00 UTC de 17/11/2026) |
| Interna | Latência de rede do lado do cliente | mesmo cliente e local para todas as APIs; percentis reportados |
| Interna | A própria onda 2 pode mudar o comportamento do provedor depois | a onda 2 rodou depois das medições de qualidade e frescor das APIs rápidas |
| Externa | A amostra principal vem do cadastro de uma única organização (mais antigo, majoritariamente matrizes, mais sociedades anônimas) | composição reportada; as amostras de fronteira cobrem empresas novas de forma independente |
| Externa | Planos gratuitos mudam sem aviso | data de coleta registrada em todos os resultados |
| Conclusão | n pequeno | intervalos de Wilson; diferenças dentro de intervalos sobrepostos não são afirmadas |

## 9. Desvios do plano
- **Tamanho da onda 1.** Foram sorteados 1.100 CNPJs, mas só os primeiros 300 foram coletados. A
  etapa planejada de um dia inteiro sobre o restante da amostra (capacidade diária) não foi executada.
- **CNPJ.ws (S05).** O segundo lote da onda 1 foi interrompido em 158 de 200 CNPJs: a partir de
  cerca de 02:00 UTC o serviço respondeu majoritariamente HTTP 500, HTTP 504 ou esgotou o tempo. A
  execução foi mantida com situação `stopped_degraded`, e a S05 não rodou a onda 2.
- **Amostra da onda 2.** Tem 196 CNPJs em vez de 200, porque só 196 foram encontrados por todas as
  APIs na onda 1. A parte A tem 96 CNPJs (3 × 32); a parte B tem 100.
- **Frescor.** As APIs lentas (S03, S04, S05) usaram a amostra reduzida de 66 CNPJs; a S04 também
  rodou a amostra de 60. A S05 respondia cerca de 0,5 CNPJ por minuto e foi limitada aos 12 CNPJs dos
  quatro estratos mais recentes. As primeiras execuções de fronteira de S03, S04 e S05 foram
  interrompidas e estão excluídas.
- **Sonda alfanumérica.** Uma primeira versão com 10 CNPJs e sem controles foi substituída pela
  versão com 12 CNPJs e controles. A primeira versão não é reportada.

## 10. Correções feitas nesta versão
Ao reorganizar os textos para publicação, os valores divergentes entre documentos foram conferidos
contra [results/summary.json](../../results/summary.json) e os relatórios:

| Item | Antes | Agora | Fonte |
|---|---|---|---|
| Intervalo de confiança da cobertura da CNPJ.ws | 82,2–90,4% em `summary.json` e na ficha (calculado sobre os 258 CNPJs encerrados, não sobre o denominador da cobertura) | 96,8–99,8% (224 de 226) | relatório da onda 1; corrigidos `summary.json` e `scripts/90_build_summary.py` |
| 404 antigos em cache | "26 de 300 CNPJs reais (8,7%)" e "22 de 300 (7,3%)" nas fichas | 26 de 297 (8,8%) e 22 de 297 (7,4%): 3 dos 300 CNPJs não existem | relatório da onda 1 |
| Proporção de matrizes | "85% matrizes" atribuído à população de 35.702 CNPJs | população: 83,6% (29.854); empresas encontradas na amostra: 85% | protocolo original e relatório da onda 1 |
| Rampa da CNPJá a 1× | 13% no relatório, 12% na ficha | 12,5% | `summary.json` |
| Latência p50 nas rajadas (S02, S06, S07) | 31–48 ms | 31–46 ms | `summary.json` |
| Abertura mais recente da CNPJ.ws | 06/11/2026 no relatório de frescor, 27/10/2026 na ficha | 27/10/2026 nos registros da própria API; ela também retornou uma empresa aberta em 06/11/2026 sem data no registro | `summary.json` (F1 e recall por quinzena) |
| Tamanho do teste de frescor | "346 CNPJs" | 346 consultas, 343 CNPJs distintos, 298 existentes | `summary.json` (`freshness_meta`) |
| Coluna "vazão no limite" do README | misturava limite documentado e ritmo usado (OpenCNPJ.com: 300 × 120 req/min) | colunas separadas | `catalog/sources.yaml` e fichas |
| Limiar do arredondamento de capital social | "R$ 16,7 milhões" | R$ 16.777.216 (2²⁴) | relatório da onda 1 |
| APIs que aceitam e validam o CNPJ alfanumérico | "S01, S02 e S07" no ranking e no `llms.txt` | todas exceto a S06 (S01–S05 e S07) | relatório de frescor e `summary.json` (sonda F4) |
| Evidência por requisição | links para `results/*/data/*.csv` e `SHA256SUMS`, que nunca estiveram no repositório | o texto diz que só agregados são publicados | árvore do repositório |

## 11. O que é publicado
| Publicado | Onde |
|---|---|
| Todos os números agregados, por API | [results/summary.json](../../results/summary.json) |
| Amostras e rótulos de execução por trás de cada resultado | [results/manifest.yaml](../../results/manifest.yaml) |
| Relatórios, gráficos e tabela por campo | [onda 1](../../results/wave1/REPORT.pt-BR.md), [onda 2](../../results/wave2/REPORT.pt-BR.md), [frescor](../../results/freshness/REPORT.pt-BR.md), [tabela por campo](../../results/wave1/DATASHEET.md) |
| Código de coleta, conversão e métricas | [src/cnpjbench/](../../src/cnpjbench/), [scripts/](../../scripts/) |

Não são publicados: as respostas brutas das APIs, a telemetria por requisição e a lista de CNPJs da
amostra de qualidade, porque essa lista vem de um cadastro privado e revelaria as empresas. As
amostras de fronteira e alfanumérica não usam dados privados e podem ser reconstruídas exatamente
com os passos 32 e 33 e a semente 20261116 ([reproduce.md](reproduce.md)).

## 12. Referências
- ISO/IEC 25012:2008. *Software engineering — Software product Quality Requirements and Evaluation (SQuaRE) — Data quality model.*
- Wang, R. Y.; Strong, D. M. (1996). Beyond accuracy: what data quality means to data consumers. *Journal of Management Information Systems* 12(4), 5–33.
- Pipino, L. L.; Lee, Y. W.; Wang, R. Y. (2002). Data quality assessment. *Communications of the ACM* 45(4), 211–218.
- Batini, C.; Scannapieco, M. (2016). *Data and Information Quality: Dimensions, Principles and Techniques.* Springer.
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association* 22(158), 209–212.
- Wohlin, C. et al. (2012). *Experimentation in Software Engineering.* Springer (classificação das ameaças à validade).
- Receita Federal do Brasil. Instrução Normativa RFB nº 2.229/2024 (CNPJ alfanumérico).
