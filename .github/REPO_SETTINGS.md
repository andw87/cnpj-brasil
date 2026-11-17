# Configuração sugerida do repositório no GitHub

Valores para aplicar à mão em **Settings → General** e no painel **About** do repositório
`andw87/cnpj-brasil`. Este arquivo não é lido por nenhuma ferramenta; pode ser apagado depois de
aplicado.

## Descrição (About → Description, até 350 caracteres)

```
API de CNPJ gratuita: qual usar? Comparação medida de 7 APIs de consulta CNPJ (BrasilAPI, Minha Receita, ReceitaWS, CNPJá, CNPJ.ws, OpenCNPJ.org, OpenCNPJ.com) com dados da Receita Federal: cobertura, campos, frescor, limites e latência. Método, código e números abertos.
```

Comprimento: 271 caracteres.

## Website (About → Website)
Deixar em branco, ou apontar para o README em português.

## Tópicos (About → Topics, 20 no máximo)

```
cnpj consulta-cnpj api-cnpj cnpj-api receita-federal dados-abertos open-data brasil brazil brasilapi minha-receita opencnpj cnpja receitaws benchmark api-comparison data-quality cnpj-alfanumerico python dados-publicos
```

São 20 tópicos, todos em minúsculas e com hífen. Critério: termos que aparecem nos repositórios mais
estrelados do tema (`cnpj`, `receita-federal`, `dados-abertos`, `brasil`, `brazil`, `open-data`,
`brasilapi`) mais os termos de busca do problema (`consulta-cnpj`, `api-cnpj`, `cnpj-api`) e os nomes
das APIs medidas. Levantamento em
[docs/pesquisa-repositorios-similares.md](../docs/pesquisa-repositorios-similares.md).

## Outras opções
- **Social preview** (Settings → General → Social preview): o GitHub aceita PNG ou JPG, não SVG.
  Para usar o banner, exporte `assets/banner.svg` para PNG de 1280 × 640 (ou 1280 × 320 com margem).
- **Features:** Issues ligadas; Wiki e Projects desligados (a documentação está em `docs/`).
- **Releases:** criar a tag `v1.0.0` com a data da medição, igual à versão em `CITATION.cff`.

## Texto curto para divulgação (opcional)

```
Qual API de CNPJ gratuita usar? Medi 7 APIs (BrasilAPI, Minha Receita, ReceitaWS, CNPJá, CNPJ.ws, OpenCNPJ) com os mesmos CNPJs e publiquei uma sugestão por caso de uso, com método e números abertos: https://github.com/andw87/cnpj-brasil
```
