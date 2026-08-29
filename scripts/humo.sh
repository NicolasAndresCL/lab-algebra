#!/usr/bin/env bash
# Prueba de humo de punta a punta contra el stack ya levantado.
#
# Comprueba lo que de verdad importa que funcione: que los tres contenedores
# están sanos, que se puede iniciar sesión con el usuario del laboratorio, que
# el temario está cargado y que los motores de cálculo responden.
#
# Uso:  bash scripts/humo.sh [URL_API] [URL_WEB]

set -uo pipefail

API="${1:-http://localhost:8000}"
WEB="${2:-http://localhost:8080}"
USUARIO="${USUARIO_INICIAL:-nico}"
CLAVE="${PASSWORD_INICIAL:-1234}"

fallos=0

comprobar() {  # <descripción> <condición-como-comando>
    local descripcion="$1"; shift
    if "$@" > /tmp/humo.log 2>&1; then
        echo "  OK   $descripcion"
    else
        echo "  FALLA  $descripcion"
        sed 's/^/         /' /tmp/humo.log | head -10
        fallos=$((fallos + 1))
    fi
}

echo "Prueba de humo de lab-algebra"
echo "  API: $API"
echo "  WEB: $WEB"
echo

# --- 1. Salud ------------------------------------------------------------
estado_api=$(curl -fsS "$API/healthz" 2>/dev/null || echo '{}')
comprobar "la API responde y su base de datos contesta" \
    bash -c "echo '$estado_api' | grep -q '\"base_de_datos\": *\"ok\"'"

comprobar "la interfaz responde" curl -fsS -o /dev/null "$WEB/healthz"

# --- 2. Autenticación ----------------------------------------------------
token=$(curl -fsS -X POST "$API/api/v1/auth/login" \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"$USUARIO\",\"password\":\"$CLAVE\"}" 2>/dev/null \
    | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

comprobar "se inicia sesión con el usuario del laboratorio" \
    bash -c "[ -n '$token' ]"

# Una contraseña incorrecta TIENE que fallar. Sin esta comprobación, un bug que
# aceptara cualquier clave dejaría el resto de la prueba en verde.
codigo=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$API/api/v1/auth/login" \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"$USUARIO\",\"password\":\"clave-incorrecta\"}")
comprobar "una contraseña incorrecta se rechaza con 401" \
    bash -c "[ '$codigo' = '401' ]"

if [ -z "$token" ]; then
    echo
    echo "Sin token no se puede seguir. Revisa los logs de lab-algebra-api."
    exit 1
fi

autorizado=(-H "Authorization: Bearer $token")

# --- 3. Contenido --------------------------------------------------------
mazos=$(curl -fsS "${autorizado[@]}" "$API/api/v1/mazos" 2>/dev/null || echo '[]')
total=$(echo "$mazos" | grep -o '"total_tarjetas":[0-9]*' | cut -d: -f2 \
        | awk '{suma += $1} END {print suma + 0}')

comprobar "el temario está cargado (50 tarjetas o más; hay ${total:-0})" \
    bash -c "[ '${total:-0}' -ge 50 ]"

# --- 4. Motores de cálculo ----------------------------------------------
# Se manda con los alias ASCII a propósito: así se comprueba de paso que el
# analizador los acepta desde un cliente que no puede escribir ∧ ni →.
tabla=$(curl -fsS -X POST "$API/api/v1/herramientas/tabla-verdad"     "${autorizado[@]}" -H 'Content-Type: application/json'     -d '{"formula":"(p ^ q) -> p"}' 2>/dev/null || echo '{}')
comprobar "(p ∧ q) → p se clasifica como tautología" \
    bash -c "echo '$tabla' | grep -q 'tautolog'"

regiones=$(curl -fsS -X POST "$API/api/v1/herramientas/venn/regiones" \
    "${autorizado[@]}" -H 'Content-Type: application/json' \
    -d '{"etiquetas":["Java","Python"],"cardinalidades":{"a":70,"b":50,"ab":30},"universo":120}' \
    2>/dev/null || echo '{}')
comprobar "el problema de los 120 estudiantes da 40 solo Java" \
    bash -c "echo '$regiones' | grep -q '\"solo_a\": *40'"

png=$(mktemp)
curl -fsS -X POST "$API/api/v1/herramientas/venn/imagen" \
    "${autorizado[@]}" -H 'Content-Type: application/json' \
    -d '{"etiquetas":["A","B"],"cardinalidades":{"a":10,"b":8,"ab":4},"universo":20}' \
    -o "$png" 2>/dev/null || true
comprobar "el diagrama de Venn se genera como PNG" \
    bash -c "head -c 4 '$png' | grep -q 'PNG'"
rm -f "$png"

# --- 5. Estudio ----------------------------------------------------------
cola=$(curl -fsS "${autorizado[@]}" "$API/api/v1/estudio/cola?limite=3" 2>/dev/null || echo '[]')
comprobar "hay tarjetas en la cola de estudio" \
    bash -c "echo '$cola' | grep -q '\"concepto\"'"

echo
if [ "$fallos" -eq 0 ]; then
    echo "Todo en verde: el laboratorio funciona de punta a punta."
else
    echo "$fallos comprobación(es) en rojo."
    exit 1
fi
