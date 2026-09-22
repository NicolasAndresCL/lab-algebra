#!/usr/bin/env bash
# Prueba de humo de punta a punta contra el stack ya levantado.
#
# Comprueba lo que de verdad importa que funcione: que los tres contenedores
# están sanos, que se puede iniciar sesión con el usuario del laboratorio, que
# el temario de las TRES unidades está cargado y que los motores de cálculo
# —lógica, conjuntos y sistemas de ecuaciones— responden.
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

comprobar "el temario está cargado (70 tarjetas o más; hay ${total:-0})" \
    bash -c "[ '${total:-0}' -ge 70 ]"

# Contar tarjetas no basta: un mazo entero podría faltar y el total seguir
# alto. Las tres unidades tienen que estar sembradas, no «alguna».
mazos_ecuaciones=$(echo "$mazos" | grep -o '"unidad": *"Ecuaciones"' | wc -l)
comprobar "la unidad de ecuaciones está sembrada (3 mazos; hay ${mazos_ecuaciones:-0})" \
    bash -c "[ '${mazos_ecuaciones:-0}' -ge 3 ]"

# --- 4. Motores de cálculo ----------------------------------------------
# Se manda con los alias ASCII a propósito: así se comprueba de paso que el
# analizador los acepta desde un cliente que no puede escribir ∧ ni →.
tabla=$(curl -fsS -X POST "$API/api/v1/herramientas/tabla-verdad" \
    "${autorizado[@]}" -H 'Content-Type: application/json' \
    -d '{"formula":"(p ^ q) -> p"}' 2>/dev/null || echo '{}')
comprobar "(p ∧ q) → p se clasifica como tautología" \
    bash -c "echo '$tabla' | grep -q 'tautolog'"

regiones=$(curl -fsS -X POST "$API/api/v1/herramientas/venn/regiones" \
    "${autorizado[@]}" -H 'Content-Type: application/json' \
    -d '{"etiquetas":["Java","Python"],"cardinalidades":{"a":70,"b":50,"ab":30},"universo":120}' \
    2>/dev/null || echo '{}')
comprobar "el problema de los 120 estudiantes da 40 solo Java" \
    bash -c "echo '$regiones' | grep -q '\"solo_a\": *40'"

# Sistemas de ecuaciones: se manda con una fracción como TEXTO, que es como
# viaja desde la interfaz. Si en algún punto del camino se convirtiera en
# flotante, «1/2» volvería como «0.5» y esta comprobación lo cantaría.
#
# El método va escapado como \u00f3 y no con la «ó» literal: en Git Bash sobre
# Windows el cuerpo sale del shell en cp1252 y la API responde «error parsing
# the body», así que la prueba fallaba en la máquina de desarrollo y pasaba en
# el runner. El JSON con escape Unicode es ASCII puro y llega igual en los dos.
sistema=$(curl -fsS -X POST "$API/api/v1/herramientas/ecuaciones" \
    "${autorizado[@]}" -H 'Content-Type: application/json' \
    -d '{"matriz":[[3,-4,4],["1/2",-3,"-1/2"]],"metodo":"sustituci\u00f3n"}' \
    2>/dev/null || echo '{}')
comprobar "el sistema con fracciones da y = 1/2 exacto, sin redondear" \
    bash -c "echo '$sistema' | grep -q '\"y\": *\"1/2\"'"
comprobar "y se clasifica como compatible determinado" \
    bash -c "echo '$sistema' | grep -q 'compatible determinado'"
comprobar "y el desarrollo se hizo por el método pedido" \
    bash -c "echo '$sistema' | grep -q 'sustituc'"

# Un sistema sin solución NO es un error de la API: es una de las tres
# clasificaciones de la unidad y tiene que salir con 200.
codigo_incompatible=$(curl -s -o /dev/null -w '%{http_code}' -X POST \
    "$API/api/v1/herramientas/ecuaciones" "${autorizado[@]}" \
    -H 'Content-Type: application/json' \
    -d '{"matriz":[[7,4,1],[-7,-4,-3]]}')
comprobar "un sistema incompatible responde 200, no un error" \
    bash -c "[ '$codigo_incompatible' = '200' ]"

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
