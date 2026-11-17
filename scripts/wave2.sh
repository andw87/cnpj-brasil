#!/usr/bin/env sh
# Wave 2 (docs/methodology.md, section 4) for one source: ramp 1x/2x/4x on sample A, burst twice on sample B.
# Usage: sh scripts/wave2.sh S01 SMP-...-w2      (A = [0:96] in thirds, B = [96:196])
set -e
S=$1; W2=$2; R=".venv/Scripts/python scripts/40_run_collection.py"
G="--max-retries 0 --breaker-429 10"
$R --source $S --sample $W2 --offset 0  --limit 32 --mode ramp --rpm-multiplier 1 $G --label w2a-x1
$R --source $S --sample $W2 --offset 32 --limit 32 --mode ramp --rpm-multiplier 2 $G --label w2a-x2
$R --source $S --sample $W2 --offset 64 --limit 32 --mode ramp --rpm-multiplier 4 $G --label w2a-x4
$R --source $S --sample $W2 --offset 96 --limit 100 --mode burst --concurrency 4 $G --label w2b-r1
$R --source $S --sample $W2 --offset 96 --limit 100 --mode burst --concurrency 4 $G --label w2b-r2
