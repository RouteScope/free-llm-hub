#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Cabeçalho
cat > data/hub.yaml <<'HEADER'
# ============================================================
# Free LLM Hub - Master Database
# Auto-merged from data/0X-*.yaml files
# ============================================================
HEADER

# Mescla todos os arquivos parciais
for f in data/0*.yaml; do
  echo "" >> data/hub.yaml
  cat "$f" >> data/hub.yaml
done

echo "✅ Mesclado: $(grep -c '^- slug:' data/hub.yaml) entradas em data/hub.yaml"
