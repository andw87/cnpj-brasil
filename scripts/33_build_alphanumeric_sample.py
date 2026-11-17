"""Step 33 — build the alphanumeric-format sample (docs/methodology.md, section 4; metric F4).

Contains the Receita Federal published example 12.ABC.345/01DE-35, synthetic valid alphanumeric
head-office CNPJs (random base of digits and letters, check digits computed) and, optionally,
real alphanumeric CNPJs passed with --cnpjs. Synthetic CNPJs most likely do not exist, so the test
separates sources that accept the format (not_found) from sources that reject it (invalid_input).
Two numeric controls are included: an existing CNPJ and the same CNPJ with a wrong check digit.
A source that answers invalid_input for the bad check digit but not_found for a valid alphanumeric
CNPJ demonstrably parses the new format.

Usage: python scripts/33_build_alphanumeric_sample.py --synthetic 9 [--cnpjs A1B2... ...]
Sample ID: SMP-<YYYYMMDD>-n<size>-r<seed>-alnum
"""
import _bootstrap  # noqa: F401

import argparse
import random
import string
from datetime import datetime, timezone

from cnpjbench import storage as st
from cnpjbench.cnpj import head_office_cnpj, is_valid, normalize

OFFICIAL_EXAMPLE = "12ABC34501DE35"
CONTROL_FOUND = "33000167000101"       # valid numeric, exists: the source answers at all
CONTROL_BAD_DV = "33000167000102"      # numeric with wrong check digit: does the source validate input?

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", type=int, default=9)
    ap.add_argument("--cnpjs", nargs="*", default=[])
    ap.add_argument("--seed", type=int, default=20261116)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    real = [normalize(c) for c in a.cnpjs]
    bad = [c for c in real if not is_valid(c)]
    if bad:
        raise SystemExit(f"invalid: {bad}")
    synth = []
    while len(synth) < a.synthetic:
        base = "".join(rng.choice(string.digits + string.ascii_uppercase) for _ in range(8))
        if any(ch.isalpha() for ch in base):
            synth.append(head_office_cnpj(base))
    cnpjs = [CONTROL_FOUND, CONTROL_BAD_DV, OFFICIAL_EXAMPLE] + real + synth
    now = datetime.now(timezone.utc)
    sample_id = f"SMP-{now:%Y%m%d}-n{len(cnpjs)}-r{a.seed}-alnum"
    st.get_db()[st.SAMPLES].replace_one({"_id": sample_id}, {
        "_id": sample_id, "created_at": now, "method": "alphanumeric_format_probe", "rng": "python.random.Random",
        "rng_seed": a.seed, "size": len(cnpjs), "label": "alnum",
        "composition": {"controls": 2, "official_example": 1, "real": len(real), "synthetic": len(synth)}, "cnpjs": cnpjs,
    }, upsert=True)
    print(sample_id)
