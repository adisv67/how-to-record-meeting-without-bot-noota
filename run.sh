#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
PYTHONPATH=. python -m polymeetai.main
