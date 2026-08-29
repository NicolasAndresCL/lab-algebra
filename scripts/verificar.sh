#!/usr/bin/env bash
# Reproduce en local, y en el mismo orden, lo que hace el CI.
#
# Se ejecuta ANTES de armar un commit. El job que siempre se olvida es el que
# no se reproduce a mano: aquí están los cinco, incluido el que levanta el
# stack entero.
#
# Uso:
#   bash scripts/verificar.sh            # lint + tests (rápido, ~15 s)
#   bash scripts/verificar.sh --completo # además build y arranque en Docker

set -uo pipefail
cd "$(dirname "$0")/.."

# La ruta del intérprete se resuelve a ABSOLUTA: los pasos que entran en
# `backend/` romperían una ruta relativa («No such file or directory»), y el
# job de tests quedaría en rojo por un motivo que no tiene nada que ver con el
# código.
raiz="$(pwd)"
for candidato in "$raiz/.venv/Scripts/python.exe" "$raiz/.venv/bin/python"; do
    [ -x "$candidato" ] && PY="$candidato" && break
done
PY="${PY:-python3}"

fallos=0
completo=false
[ "${1:-}" = "--completo" ] && completo=true

# El resultado va DELANTE de la descripción: alinear con `printf %-46s`
# desajusta las columnas en cuanto el texto lleva tildes, porque printf cuenta
# bytes y no caracteres.
ejecutar() {  # <descripción> <comando...>
    local desc="$1"; shift
    if "$@" > /tmp/verificar.log 2>&1; then
        echo "  OK     $desc"
    else
        echo "  FALLA  $desc"
        tail -25 /tmp/verificar.log | sed 's/^/         /'
        fallos=$((fallos + 1))
    fi
}

echo "Verificación de lab-algebra (intérprete: $PY)"
echo
echo "1. Lint"
ejecutar "ruff — backend" "$PY" -m ruff check backend
ejecutar "ruff — frontend" "$PY" -m ruff check frontend

echo
echo "2. Tests"
# El umbral de cobertura es condición de fallo, igual que en el CI: que los
# tests pasen no basta si dejaron de cubrir la mitad del código.
ejecutar "pytest con cobertura (mínimo 90 %)" \
    bash -c "cd backend && '$PY' -m pytest -rs -q --cov --cov-report=term-missing --cov-fail-under=90"

if [ "$completo" = false ]; then
    echo
    if [ "$fallos" -eq 0 ]; then
        echo "Lint y tests en verde."
        echo "Para incluir build y arranque en Docker: bash scripts/verificar.sh --completo"
    else
        echo "$fallos comprobación(es) en rojo. NO commitees todavía."
        exit 1
    fi
    exit 0
fi

echo
echo "3. Docker"
ejecutar "las imágenes construyen" docker compose build
ejecutar "el stack levanta y queda sano" \
    docker compose up -d --wait --wait-timeout 240
ejecutar "prueba de humo de punta a punta" bash scripts/humo.sh
docker compose down > /dev/null 2>&1

echo
if [ "$fallos" -eq 0 ]; then
    echo "Todo en verde."
else
    echo "$fallos comprobación(es) en rojo. NO commitees todavía."
    exit 1
fi
