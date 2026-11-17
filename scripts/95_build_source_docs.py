"""Step 95 — one standardized page per source, in English and Portuguese.

Inputs: results/summary.json (step 90), catalog/source_profiles.yaml (facts from provider docs),
catalog/field_map.yaml (JSON path per canonical field). Output: docs/sources/<ID>-<slug>.md and
docs/pt-BR/sources/<ID>-<slug>.md. Every measured number comes from summary.json.
Usage: python scripts/95_build_source_docs.py
"""
import _bootstrap  # noqa: F401

import json

import yaml

from cnpjbench.config import PROJECT_ROOT
from cnpjbench.metrics import wilson
from cnpjbench.schema import SCORED_FIELDS

SUMMARY = json.loads((PROJECT_ROOT / "results" / "summary.json").read_text(encoding="utf-8"))
PROFILES = yaml.safe_load((PROJECT_ROOT / "catalog" / "source_profiles.yaml").read_text(encoding="utf-8"))
FIELDS = yaml.safe_load((PROJECT_ROOT / "catalog" / "field_map.yaml").read_text(encoding="utf-8"))
EXAMPLE = "33000167000101"

T = {
    "en": {
        "facts": "Facts", "item": "Item", "value": "Value", "operator": "Operator", "website": "Website",
        "docs": "Documentation", "code": "Source code", "auth": "Authentication", "endpoint": "Endpoint",
        "limit_doc": "Documented limit", "limit_obs": "Measured behaviour at the limit", "upstream": "Data origin (declared)",
        "cadence": "Update cadence (declared)", "terms": "Terms of use", "alnum": "Alphanumeric CNPJ (measured)",
        "connect": "How to connect", "responses": "Responses observed", "case": "Case", "http": "HTTP",
        "body": "Body (start)", "fields": "Fields returned (measured)", "field": "Canonical field",
        "path": "JSON path in the response", "fill": "Filled %", "agree": "Agrees with other sources %",
        "notret": "not returned", "perf": "Measured performance", "fresh": "Freshness",
        "issues": "Observed issues", "verdict": "Summary", "evidence": "Evidence",
        "status_note": "Exploratory measurement, one collection window on 2026-11-16/17 (UTC), one client. Every number below "
                       "comes from [results/summary.json](../../results/summary.json). Method: [methodology](../methodology.md).",
        "coverage": "Coverage, wave 1 (95% Wilson interval; n = CNPJs with a conclusive answer)", "latency": "Latency p50 / p95", "rpm": "Effective throughput (pace used in brackets)", "cpm": "CNPJs/min",
        "r429": "Share of attempts answered HTTP 429 at the pace used", "ramp": "Wave 2 ramp: HTTP 429 share at 1× / 2× / 4× the pace (attempted requests/min)",
        "burst": "Wave 2 unpaced bursts, 4 concurrent requests, 2 × 100 requests (attempted requests/min)", "newest": "Newest opening date returned",
        "recent": "Companies opened 2026-10-16 to 2026-11-14 that were returned (found / existing)", "age": "Declared record age (p50 / p90)",
        "days": "days", "none": "—", "found": "found", "notfound": "not found", "badcd": "wrong check digit",
        "alex": "alphanumeric example 12.ABC.345/01DE-35", "accepts": "accepts the format",
        "rejects": "rejects the format", "novalidate": "no input validation (wrong check digit → 404)",
        "unknown": "not determined", "stopped": "stopped after 10 consecutive HTTP 429 (test stop rule)",
        "noerr": "no 429", "lang": "Português: [../pt-BR/sources/{f}](../pt-BR/sources/{f})",
        "summary_link": "All APIs: [suggestion by use case](../ranking.md)",
    },
    "pt": {
        "facts": "Ficha", "item": "Item", "value": "Valor", "operator": "Mantenedor", "website": "Site",
        "docs": "Documentação", "code": "Código-fonte", "auth": "Autenticação", "endpoint": "Endpoint",
        "limit_doc": "Limite documentado", "limit_obs": "Comportamento medido no limite", "upstream": "Origem dos dados (declarada)",
        "cadence": "Atualização (declarada)", "terms": "Termos de uso", "alnum": "CNPJ alfanumérico (medido)",
        "connect": "Como conectar", "responses": "Respostas observadas", "case": "Caso", "http": "HTTP",
        "body": "Corpo (início)", "fields": "Campos retornados (medidos)", "field": "Campo canônico",
        "path": "Caminho JSON na resposta", "fill": "Preenchido %", "agree": "Concorda com outras fontes %",
        "notret": "não retorna", "perf": "Desempenho medido", "fresh": "Frescor",
        "issues": "Problemas observados", "verdict": "Resumo", "evidence": "Evidências",
        "status_note": "Medição exploratória, uma janela de coleta em 16–17/11/2026 (UTC), um cliente. Todos os números abaixo "
                       "vêm de [results/summary.json](../../../results/summary.json). Método: [metodologia](../methodology.md).",
        "coverage": "Cobertura, onda 1 (intervalo de Wilson de 95%; n = CNPJs com resposta conclusiva)", "latency": "Latência p50 / p95", "rpm": "Vazão efetiva (ritmo usado entre parênteses)", "cpm": "CNPJs/min",
        "r429": "Tentativas respondidas com HTTP 429 no ritmo usado", "ramp": "Onda 2, rampa: proporção de HTTP 429 a 1× / 2× / 4× o ritmo (requisições tentadas/min)",
        "burst": "Onda 2, rajadas sem ritmo, 4 requisições simultâneas, 2 × 100 requisições (requisições tentadas/min)", "newest": "Abertura mais recente retornada",
        "recent": "Empresas abertas de 16/10/2026 a 14/11/2026 retornadas (encontradas / existentes)", "age": "Idade declarada do registro (p50 / p90)",
        "days": "dias", "none": "—", "found": "encontrado", "notfound": "não encontrado", "badcd": "dígito verificador errado",
        "alex": "exemplo alfanumérico 12.ABC.345/01DE-35", "accepts": "aceita o formato",
        "rejects": "rejeita o formato", "novalidate": "não valida a entrada (dígito errado → 404)",
        "unknown": "não determinado", "stopped": "interrompida após 10 respostas HTTP 429 seguidas (regra de parada do teste)",
        "noerr": "sem 429", "lang": "English: [../../sources/{f}](../../sources/{f})",
        "summary_link": "Todas as APIs: [sugestão por caso de uso](../ranking.md)",
    },
}


LANG = "en"


def num(x, d=1):
    t = f"{x:,.{d}f}"
    return t if LANG == "en" else t.replace(",", "_").replace(".", ",").replace("_", ".")


def pct(v, d=0):
    return "—" if v is None else num(100 * v, d)


def day(iso):
    return "—" if not iso else (iso if LANG == "en" else f"{iso[8:10]}/{iso[5:7]}/{iso[:4]}")


def alnum_verdict(probe, t):
    if not probe:
        return t["unknown"]
    ex, bad = probe.get("12ABC34501DE35"), probe.get("33000167000102")
    if not ex or not bad:
        return t["unknown"]
    if ex["outcome"] == "invalid_input":
        return f"{t['rejects']} (HTTP {ex['http_status']})"
    if bad["outcome"] == "invalid_input" and ex["outcome"] == "not_found":
        return f"{t['accepts']}: {t['badcd']} → HTTP {bad['http_status']}, {t['alex']} → HTTP {ex['http_status']}"
    if bad["outcome"] == "not_found":
        return t["novalidate"]
    return f"{t['unknown']} (HTTP {ex['http_status']} {ex['outcome']})"


def recent_recall(fr, computed_on):
    if not fr:
        return None, 0, 0
    bins = sorted(b for b in fr["recall_by_half_month"] if b != "older")[-2:]
    k = sum((fr["recall_by_half_month"][b] or {}).get("found", 0) for b in bins)
    n = sum((fr["recall_by_half_month"][b] or {}).get("closed", 0) for b in bins)
    return (k / n if n else None), k, n


def page(sid, lang):
    global LANG
    LANG = lang
    t = T[lang]
    s = SUMMARY["sources"][sid]
    cat = s["catalog"]
    prof = PROFILES[sid]
    fname = f"{sid}-{cat['slug'].replace('_', '-')}.md"
    w1, w2, fr = s.get("wave1"), s.get("wave2"), s.get("freshness")
    url = cat["url_template"].format(cnpj=EXAMPLE)
    L = [f"# {sid} — {prof['display_name']}", "",
         f"{t['lang'].format(f=fname)} · {t['summary_link']}", "",
         f"> {prof['verdict'][lang]}", "", f"_{t['status_note']}_", "",
         f"## {t['facts']}", f"| {t['item']} | {t['value']} |", "|---|---|",
         f"| {t['endpoint']} | `GET {cat['url_template']}` |",
         f"| {t['auth']} | {prof['auth'][lang]} |",
         f"| {t['operator']} | {prof['operator'][lang]} |",
         f"| {t['website']} | {prof['website']} |",
         f"| {t['docs']} | {prof.get('docs_url') or t['none']} |",
         f"| {t['code']} | {prof.get('repo_url') or t['none']} |",
         f"| {t['limit_doc']} | {prof['limit_documented'][lang]} |",
         f"| {t['limit_obs']} | {prof['limit_observed'][lang]} |",
         f"| {t['upstream']} | {prof['upstream'][lang]} |",
         f"| {t['cadence']} | {prof['cadence'][lang]} |",
         f"| {t['terms']} | {prof['terms'][lang]} |",
         f"| {t['alnum']} | {alnum_verdict((fr or {}).get('alphanumeric_probe'), t)} |", "",
         f"## {t['connect']}", "```bash", f"curl -s '{url}'", "```", "```python",
         "import requests",
         f"r = requests.get('{cat['url_template'].replace('{cnpj}', '{cnpj}')}'.format(cnpj='{EXAMPLE}'), timeout=20)",
         prof["python_check"], "```", "```javascript",
         f"const r = await fetch(`{cat['url_template'].replace('{cnpj}', '${cnpj}')}`);",
         prof["js_check"], "```"]
    if prof.get("connect_notes"):
        L += ["", prof["connect_notes"][lang]]
    probe = (fr or {}).get("alphanumeric_probe") or {}
    rows = [(t["found"], probe.get("33000167000101")), (t["badcd"], probe.get("33000167000102")),
            (t["alex"], probe.get("12ABC34501DE35"))]
    L += ["", f"### {t['responses']}", f"| {t['case']} | {t['http']} | {t['body']} |", "|---|---|---|"]
    for case, p in rows:
        if p:
            body = (p.get("message") or "").replace("|", "\\|").replace("\n", " ")[:90]
            L.append(f"| {case} | {p['http_status']} | `{body}` |" if body else f"| {case} | {p['http_status']} | {t['none']} |")
    if prof.get("rate_limit_response"):
        L.append(f"| HTTP 429 | 429 | {prof['rate_limit_response'][lang]} |")

    L += ["", f"## {t['fields']}", f"| {t['field']} | {t['path']} | {t['fill']} | {t['agree']} |", "|---|---|---|---|"]
    fmap = FIELDS.get(sid) or {}
    for f in SCORED_FIELDS:
        m = (w1 or {}).get("fields", {}).get(f, {})
        path = fmap.get(f)
        if not m.get("fill"):
            L.append(f"| `{f}` | {('`' + str(path) + '`') if path else t['none']} | {t['notret']} | {t['none']} |")
        else:
            L.append(f"| `{f}` | `{path}` | {pct(m['fill'])} | {pct(m.get('agreement'))} |")

    L += ["", f"## {t['perf']}", f"| {t['item']} | {t['value']} |", "|---|---|"]
    if w1:
        oc = w1.get("outcomes") or {}
        answered = oc.get("found", 0) + oc.get("not_found", 0) + oc.get("restricted", 0)
        ci = wilson(oc.get("found", 0), answered) or [None, None]
        tp = w1["throughput"]
        L += [f"| {t['coverage']} | {pct(w1['coverage'], 1)}% ({pct(ci[0], 1)}–{pct(ci[1], 1)}), n = {answered} |",
              f"| {t['latency']} | {num(tp['T5_latency_ms']['p50'], 0)} / {num(tp['T5_latency_ms']['p95'], 0)} ms |",
              f"| {t['rpm']} | {num(tp['T4_effective_rpm'])} {t['cpm']} ({num(tp['configured_rpm'], 0)} req/min) |",
              f"| {t['r429']} | {pct(tp['T6_rate_limited_share'], 1)}% |"]
    if w1 and not (w2 and w2.get("steps")):
        L.append(f"| {t['ramp']} | {'not run: provider degraded (HTTP 500/504)' if lang == 'en' else 'não executada: provedor degradado (HTTP 500/504)'} |")
    if w2 and w2.get("steps"):
        st_ = w2["steps"]
        ramp = " / ".join(f"{pct(st_[k]['S4_rate_limited_share'], 1)}% @ {num(st_[k]['S1_attempted_rpm'], 0)}"
                          for k in ("w2a-x1", "w2a-x2", "w2a-x4") if k in st_)
        L.append(f"| {t['ramp']} | {ramp} |")
        burst = []
        for k in ("w2b-r1", "w2b-r2"):
            if k in st_:
                v = st_[k]
                burst.append(t["stopped"] if v["status"] == "stopped_breaker"
                             else f"{pct(v['S4_rate_limited_share'], 1)}% @ {num(v['S1_attempted_rpm'], 0)}")
        if len(set(burst)) == 1 and len(burst) == 2:
            burst = [f"{burst[0]} ({'both' if lang == 'en' else 'ambas'})"]
        L.append(f"| {t['burst']} | {' / '.join(burst)} |")
    L += ["", f"## {t['fresh']}", f"| {t['item']} | {t['value']} |", "|---|---|"]
    if fr:
        rr, k, n = recent_recall(fr, SUMMARY.get("freshness_meta", {}).get("computed_on"))
        age = fr.get("declared_record_age_days")
        L += [f"| {t['newest']} | {day(fr.get('newest_opening_date'))} |",
              f"| {t['recent']} | {pct(rr)}% ({k}/{n}) |" if n else f"| {t['recent']} | {t['none']} |",
              f"| {t['age']} | {num(age['p50_days'], 0)} / {num(age['p90_days'], 0)} {t['days']} |" if age and age.get("n")
              else f"| {t['age']} | {t['none']} |"]
    L += ["", f"## {t['issues']}"] + [f"- {x}" for x in prof["issues"][lang]]
    up = "../../" if lang == "en" else "../../../"
    rep = "REPORT.md" if lang == "en" else "REPORT.pt-BR.md"
    mod = f"{sid.lower()}_{cat['slug']}.py"
    L += ["", f"## {t['evidence']}",
          ("- Reports: " if lang == "en" else "- Relatórios: ")
          + f"[{'wave 1, quality' if lang == 'en' else 'onda 1, qualidade'}]({up}results/wave1/{rep}) · "
          + f"[{'wave 2, rate limits' if lang == 'en' else 'onda 2, limites'}]({up}results/wave2/{rep}) · "
          + f"[{'freshness' if lang == 'en' else 'frescor'}]({up}results/freshness/{rep})",
          f"- {'Connector code' if lang == 'en' else 'Código do conector'}: [{mod}]({up}src/cnpjbench/connectors/{mod})"]
    return fname, "\n".join(L) + "\n"


if __name__ == "__main__":
    for sid in PROFILES:
        if sid not in SUMMARY["sources"] or "catalog" not in SUMMARY["sources"][sid]:
            continue
        for lang, folder in (("en", PROJECT_ROOT / "docs" / "sources"), ("pt", PROJECT_ROOT / "docs" / "pt-BR" / "sources")):
            folder.mkdir(parents=True, exist_ok=True)
            name, text = page(sid, lang)
            (folder / name).write_text(text, encoding="utf-8")
            print(folder / name)
