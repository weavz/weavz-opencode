#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
python3 -m unittest discover -s tests -v
opencode mcp auth weavz
