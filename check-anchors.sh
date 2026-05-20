#!/usr/bin/env bash
# check-anchors.sh — falha se algum anchor crítico sumir
set -euo pipefail

SITE="https://free-llm-hub.freedomdigitalhub.com.br/"
HTML=$(curl -fsSL "${SITE}?t=$(date +%s)")

CRITICAL=(provider-apis inference-engines-oss gateways-routers
          vector-databases open-weights-families desktop-uis
          auto-discovered-models)

missing=0
for slug in "${CRITICAL[@]}"; do
  if ! echo "$HTML" | grep -qE "id=\"?${slug}\"?"; then
    echo "❌ FALTANDO: #${slug}"
    missing=$((missing + 1))
  fi
done

if [ "$missing" -gt 0 ]; then
  echo "💥 $missing anchor(s) crítico(s) ausente(s)"
  exit 1
fi

echo "✅ Todos os $((${#CRITICAL[@]})) anchors críticos OK"
