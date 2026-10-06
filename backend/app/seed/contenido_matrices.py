"""Tarjetas de la unidad de matrices y determinantes.

Fuentes: los dos PDF de la unidad, «Matrices y determinantes»
(`Matrices-Determinantes.pdf`, 47 láminas) y «Matrices y determinantes II»
(`Matrices-determ.pdf`, 27 láminas: menores, cofactores, Cramer de 3 × 3 e
inversa). Casi todas sus láminas son imágenes sin capa de texto, así que los
ejercicios se transcribieron **mirando las láminas rasterizadas**, no desde el
texto extraído.

Las tarjetas que declaran `matriz` muestran la operación resuelta paso a paso
por `services/matrices.py`, con aritmética exacta; las que declaran `sistema`
usan el método de Cramer de `services/ecuaciones.py`. Como en la unidad de
ecuaciones, el desarrollo escrito a mano y el que calcula el motor son dos
caminos distintos hacia el mismo resultado, y sus resultados esperados están
en `tests/test_contenido.py`, resueltos a mano desde la lámina.

Notación dentro del texto: una matriz se escribe por filas, separadas por
punto y coma. [1 2; 3 4] es la matriz de filas (1, 2) y (3, 4).

Lo que **no** entra, a propósito: los determinantes de orden mayor que 3 y la
inversa por Gauss-Jordan. Ninguno de los dos PDF los enseña.
"""

from __future__ import annotations

# Matrices que aparecen en más de una tarjeta. Son las de la lámina 31, con las
# que el PDF muestra que AB ≠ BA; varias propiedades se comprueban sobre ellas.
A_LAMINA_31 = [[1, 2], [3, 4]]
B_LAMINA_31 = [[-2, 0], [-1, 3]]
AB_LAMINA_31 = [[-4, 6], [-10, 12]]

MAZOS_MATRICES: list[dict] = [
    {
        "slug": "matrices-fundamentos",
        "nombre": "Matrices — fundamentos",
        "unidad": "Matrices",
        "orden": 100,
        "descripcion": (
            "Qué es una matriz, cómo se nombran sus elementos, cuándo dos matrices "
            "son iguales, y las dos operaciones de una sola matriz: la traspuesta y "
            "la traza."
        ),
        "tarjetas": [
            {
                "concepto": "Matriz",
                "pregunta": "¿Qué es una matriz y qué es su orden?",
                "definicion": (
                    "Un **arreglo rectangular** de números organizados en **filas** "
                    "(horizontales) y **columnas** (verticales), encerrado entre "
                    "paréntesis o corchetes. Su **orden** o dimensión es m × n: m filas "
                    "por n columnas, siempre en ese orden."
                ),
                "notacion": "A = (aᵢⱼ)ₘₓₙ",
                "clave_memoria": (
                    "Primero filas, después columnas. Un 2 × 3 es ancho (2 filas, 3 "
                    "columnas); un 3 × 2 es alto."
                ),
                "ejercicio_enunciado": (
                    "Indica el orden de A = [2 5 −1; 0 3 4] y escribe cada uno de sus "
                    "elementos aᵢⱼ. (Las filas se separan con punto y coma.)"
                ),
                "ejercicio_desarrollo": (
                    "Filas (horizontales): 2. Columnas (verticales): 3.\n"
                    "Orden: 2 × 3, filas por columnas.\n"
                    "Cada elemento se nombra por su fila y su columna:\n"
                    "   a₁₁ = 2   a₁₂ = 5   a₁₃ = −1\n"
                    "   a₂₁ = 0   a₂₂ = 3   a₂₃ = 4"
                ),
                "ejercicio_respuesta": (
                    "A es de orden 2 × 3; a₁₁ = 2, a₁₂ = 5, a₁₃ = −1, a₂₁ = 0, "
                    "a₂₂ = 3 y a₂₃ = 4."
                ),
                "fuente": "Matrices y determinantes, láminas 2 a 4",
                "matriz": {"operacion": "clasificar", "a": [[2, 5, -1], [0, 3, 4]]},
            },
            {
                "concepto": "Elemento aᵢⱼ",
                "pregunta": "¿Qué indica el elemento aᵢⱼ de una matriz?",
                "definicion": (
                    "La entrada que está en la **fila i** y la **columna j**. El primer "
                    "subíndice es siempre la fila y el segundo la columna: a₂₃ es el "
                    "elemento de la fila 2, columna 3."
                ),
                "notacion": "aᵢⱼ: i = fila, j = columna",
                "clave_memoria": (
                    "Igual que el orden: primero la fila. a₃₁ y a₁₃ son posiciones "
                    "distintas, y solo valen lo mismo si la matriz es simétrica."
                ),
                "ejercicio_enunciado": (
                    "En B = [1 −2 0; 3 4 10; −5 −1 9], ¿cuánto valen b₂₃, b₃₁ y b₁₂? "
                    "¿Qué elementos forman su diagonal principal y cuánto suman?"
                ),
                "ejercicio_desarrollo": (
                    "b₂₃: fila 2 (3, 4, 10), columna 3 → 10.\n"
                    "b₃₁: fila 3 (−5, −1, 9), columna 1 → −5.\n"
                    "b₁₂: fila 1 (1, −2, 0), columna 2 → −2.\n"
                    "La diagonal principal son los bᵢᵢ (fila = columna):\n"
                    "   b₁₁ = 1, b₂₂ = 4, b₃₃ = 9, que suman 1 + 4 + 9 = 14."
                ),
                "ejercicio_respuesta": (
                    "b₂₃ = 10, b₃₁ = −5, b₁₂ = −2; la diagonal principal es 1, 4, 9 y "
                    "suma 14."
                ),
                "fuente": "Matrices y determinantes, láminas 3 y 6",
                "matriz": {"operacion": "traza", "a": [[1, -2, 0], [3, 4, 10], [-5, -1, 9]]},
            },
            {
                "concepto": "Igualdad de matrices",
                "pregunta": "¿Cuándo son iguales dos matrices?",
                "definicion": (
                    "Cuando tienen el **mismo orden** y sus **entradas correspondientes** "
                    "son iguales: A = B si y solo si aᵢⱼ = bᵢⱼ para toda i y toda j. Una "
                    "igualdad de matrices m × n equivale a m·n igualdades de números."
                ),
                "notacion": "A = B ⟺ aᵢⱼ = bᵢⱼ para toda i, j",
                "clave_memoria": (
                    "Si el orden no coincide, ni se comparan las entradas: las matrices "
                    "ya son distintas."
                ),
                "ejercicio_enunciado": "Halla x e y si [−1 2; x³ 0] = [2y + 1 2; 8 0].",
                "ejercicio_desarrollo": (
                    "Mismo orden (2 × 2): se igualan las entradas en la misma posición.\n"
                    "   a₁₁: −1 = 2y + 1 → 2y = −2 → y = −1\n"
                    "   a₂₁: x³ = 8 → x = 2\n"
                    "   a₁₂ y a₂₂ ya coinciden (2 = 2 y 0 = 0).\n"
                    "Comprobación: 2(−1) + 1 = −1 ✓ y 2³ = 8 ✓"
                ),
                "ejercicio_respuesta": "x = 2, y = −1.",
                "fuente": "Matrices y determinantes, lámina 7",
            },
            {
                "concepto": "Igualdad con varias incógnitas",
                "pregunta": (
                    "¿Cómo se resuelve una igualdad de matrices con incógnitas en varias "
                    "entradas?"
                ),
                "definicion": (
                    "Se escribe **una ecuación por posición** y se resuelven en el orden "
                    "que convenga: a veces el valor despejado en una entrada se usa en "
                    "otra. Las entradas sin incógnitas sirven de comprobación."
                ),
                "clave_memoria": (
                    "Resuelve primero las ecuaciones de una sola incógnita y sustituye "
                    "ese valor en las demás."
                ),
                "ejercicio_enunciado": (
                    "Halla w, x, y, z si [w + 1  10 + x; 3y − 2  x − 4] = "
                    "[2  2x + 1; y − 5  4z]."
                ),
                "ejercicio_desarrollo": (
                    "a₁₁: w + 1 = 2 → w = 1\n"
                    "a₁₂: 10 + x = 2x + 1 → 10 − 1 = 2x − x → x = 9\n"
                    "a₂₁: 3y − 2 = y − 5 → 2y = −3 → y = −3/2\n"
                    "a₂₂: x − 4 = 4z → 9 − 4 = 4z → z = 5/4\n"
                    "Comprobación de a₂₁: 3(−3/2) − 2 = −13/2 y −3/2 − 5 = −13/2 ✓"
                ),
                "ejercicio_respuesta": "w = 1, x = 9, y = −3/2, z = 5/4.",
                "fuente": "Matrices y determinantes, lámina 8 (ejercicio 3)",
            },
            {
                "concepto": "Igualdad con más de una solución",
                "pregunta": "¿Puede una igualdad de matrices tener más de una solución?",
                "definicion": (
                    "Sí: si una entrada lleva la incógnita al cuadrado, la ecuación de esa "
                    "posición es de segundo grado y puede tener **dos** valores. Hay que "
                    "dar todos los que cumplen **todas** las posiciones a la vez."
                ),
                "clave_memoria": (
                    "y² = 1 no es y = 1: es y = 1 o y = −1. Olvidar la raíz negativa es "
                    "el error típico."
                ),
                "ejercicio_enunciado": (
                    "Halla x e y si [x² − 9x  x; 1  0] = [10  x; 1  y² − 1]."
                ),
                "ejercicio_desarrollo": (
                    "a₁₁: x² − 9x = 10 → x² − 9x − 10 = 0 → (x − 10)(x + 1) = 0\n"
                    "     → x = 10 o x = −1\n"
                    "a₁₂: x = x, se cumple para cualquier x.\n"
                    "a₂₁: 1 = 1 ✓\n"
                    "a₂₂: 0 = y² − 1 → y² = 1 → y = 1 o y = −1\n"
                    "x e y aparecen en posiciones distintas, así que valen las cuatro "
                    "combinaciones."
                ),
                "ejercicio_respuesta": (
                    "x = 10 o x = −1; y = 1 o y = −1 (cuatro pares posibles)."
                ),
                "fuente": "Matrices y determinantes, lámina 8 (ejercicio 6)",
            },
            {
                "concepto": "Matriz traspuesta",
                "pregunta": "¿Qué es la traspuesta Aᵀ de una matriz?",
                "definicion": (
                    "La matriz que se obtiene **intercambiando filas por columnas**: la "
                    "fila i de A pasa a ser la columna i de Aᵀ. Si A es m × n, Aᵀ es "
                    "n × m."
                ),
                "notacion": "Aᵀ (también A' o Aᵗ)",
                "clave_memoria": (
                    "Se «voltea» sobre la diagonal principal: la diagonal no se mueve y "
                    "lo de arriba pasa abajo."
                ),
                "ejercicio_enunciado": "Obtén la traspuesta de A = [1 2 10; 5 6 9].",
                "ejercicio_desarrollo": (
                    "A es 2 × 3, así que Aᵀ es 3 × 2.\n"
                    "Fila 1 de A (1, 2, 10) → columna 1 de Aᵀ.\n"
                    "Fila 2 de A (5, 6, 9) → columna 2 de Aᵀ.\n"
                    "   Aᵀ = [  1  5 ]\n"
                    "        [  2  6 ]\n"
                    "        [ 10  9 ]"
                ),
                "ejercicio_respuesta": "Aᵀ = [1 5; 2 6; 10 9], de orden 3 × 2.",
                "fuente": "Matrices y determinantes, láminas 13 y 14",
                "matriz": {"operacion": "traspuesta", "a": [[1, 2, 10], [5, 6, 9]]},
            },
            {
                "concepto": "Propiedades de la traspuesta",
                "pregunta": "¿Qué propiedades cumple la traspuesta?",
                "definicion": (
                    "(Aᵀ)ᵀ = A; (A + B)ᵀ = Aᵀ + Bᵀ; (k·A)ᵀ = k·Aᵀ; y la más importante: "
                    "**(A·B)ᵀ = Bᵀ·Aᵀ**, la traspuesta de un producto es el producto de "
                    "las traspuestas **en orden inverso**."
                ),
                "notacion": "(AB)ᵀ = BᵀAᵀ",
                "clave_memoria": (
                    "Como los calcetines y los zapatos: lo último que te pones es lo "
                    "primero que te quitas."
                ),
                "ejercicio_enunciado": (
                    "Con A = [1 2; 3 4] y B = [−2 0; −1 3], comprueba que (AB)ᵀ = BᵀAᵀ y "
                    "que no es igual a AᵀBᵀ."
                ),
                "ejercicio_desarrollo": (
                    "AB = [−4 6; −10 12] (lámina 31) → (AB)ᵀ = [−4 −10; 6 12].\n"
                    "Bᵀ = [−2 −1; 0 3] y Aᵀ = [1 3; 2 4].\n"
                    "BᵀAᵀ: c₁₁ = (−2)·1 + (−1)·2 = −4;  c₁₂ = (−2)·3 + (−1)·4 = −10\n"
                    "      c₂₁ = 0·1 + 3·2 = 6;          c₂₂ = 0·3 + 3·4 = 12\n"
                    "BᵀAᵀ = [−4 −10; 6 12] = (AB)ᵀ ✓\n"
                    "En cambio AᵀBᵀ = [−2 8; −4 10], que es otra matriz."
                ),
                "ejercicio_respuesta": (
                    "(AB)ᵀ = BᵀAᵀ = [−4 −10; 6 12]; AᵀBᵀ = [−2 8; −4 10] no coincide."
                ),
                "fuente": "Matrices y determinantes, láminas 13 y 31",
                "matriz": {"operacion": "traspuesta", "a": AB_LAMINA_31},
            },
            {
                "concepto": "Traza de una matriz",
                "pregunta": "¿Qué es la traza de una matriz cuadrada?",
                "definicion": (
                    "La **suma de los elementos de la diagonal principal**. Solo está "
                    "definida para matrices cuadradas."
                ),
                "notacion": "tr(A) = a₁₁ + a₂₂ + … + aₙₙ",
                "clave_memoria": (
                    "Se recorre la diagonal de la esquina superior izquierda a la "
                    "inferior derecha y se suma. Lo que está fuera de ella no cuenta."
                ),
                "ejercicio_enunciado": (
                    "Calcula la traza de A = [2 5 7; 1 3 4; 0 −2 6] y de B = [−1 4; 7 5]."
                ),
                "ejercicio_desarrollo": (
                    "Diagonal principal de A: a₁₁ = 2, a₂₂ = 3, a₃₃ = 6.\n"
                    "tr(A) = 2 + 3 + 6 = 11.\n"
                    "Diagonal principal de B: −1 y 5.\n"
                    "tr(B) = −1 + 5 = 4."
                ),
                "ejercicio_respuesta": "tr(A) = 11 y tr(B) = 4.",
                "fuente": "Matrices y determinantes, láminas 16 y 17",
                "matriz": {"operacion": "traza", "a": [[2, 5, 7], [1, 3, 4], [0, -2, 6]]},
            },
            {
                "concepto": "Propiedades de la traza",
                "pregunta": "¿Qué propiedades tiene la traza?",
                "definicion": (
                    "Es **lineal**: tr(A + B) = tr(A) + tr(B) y tr(c·A) = c·tr(A). Es "
                    "**invariante cíclica**: tr(AB) = tr(BA), aunque AB y BA sean "
                    "matrices distintas. Y **solo se define para matrices cuadradas**."
                ),
                "notacion": "tr(AB) = tr(BA)",
                "clave_memoria": (
                    "tr(AB) = tr(BA) es de las pocas cosas que el producto respeta al "
                    "cambiar el orden de los factores."
                ),
                "ejercicio_enunciado": (
                    "Con A = [1 2; 3 4] y B = [−2 0; −1 3], comprueba que tr(AB) = tr(BA) "
                    "aunque AB ≠ BA."
                ),
                "ejercicio_desarrollo": (
                    "AB = [−4 6; −10 12] → tr(AB) = −4 + 12 = 8.\n"
                    "BA = [−2 −4; 8 10] → tr(BA) = −2 + 10 = 8.\n"
                    "Las matrices AB y BA son distintas, pero sus trazas coinciden ✓"
                ),
                "ejercicio_respuesta": "tr(AB) = tr(BA) = 8.",
                "fuente": "Matrices y determinantes, láminas 18 y 31",
                "matriz": {"operacion": "traza", "a": AB_LAMINA_31},
            },
        ],
    },
    {
        "slug": "matrices-tipos",
        "nombre": "Tipos de matrices",
        "unidad": "Matrices",
        "orden": 110,
        "descripcion": (
            "Cuadrada, identidad, diagonal, escalar, triangular, simétrica y "
            "antisimétrica: qué define a cada una y cómo se relacionan entre sí."
        ),
        "tarjetas": [
            {
                "concepto": "Matriz cuadrada",
                "pregunta": "¿Qué es una matriz cuadrada y qué es su diagonal principal?",
                "definicion": (
                    "La que tiene el **mismo número de filas que de columnas** (m = n); "
                    "su orden se escribe n × n. Su **diagonal principal** son los "
                    "elementos a₁₁, a₂₂, …, aₙₙ, de la esquina superior izquierda a la "
                    "inferior derecha. Solo las cuadradas tienen determinante, inversa "
                    "y traza."
                ),
                "notacion": "Aₙₓₙ; diagonal principal: a₁₁, a₂₂, …, aₙₙ",
                "clave_memoria": "Diagonal principal: los elementos con fila = columna (aᵢᵢ).",
                "ejercicio_enunciado": (
                    "¿Son cuadradas B = [1 −2 0; 3 4 10; −5 −1 9] y C = [−3 −1; 5 0]? "
                    "Indica la diagonal principal de cada una."
                ),
                "ejercicio_desarrollo": (
                    "B tiene 3 filas y 3 columnas → cuadrada de orden 3.\n"
                    "Diagonal principal de B: b₁₁ = 1, b₂₂ = 4, b₃₃ = 9.\n"
                    "C tiene 2 filas y 2 columnas → cuadrada de orden 2.\n"
                    "Diagonal principal de C: c₁₁ = −3, c₂₂ = 0. Un cero en la diagonal "
                    "no cambia nada: sigue siendo su diagonal."
                ),
                "ejercicio_respuesta": (
                    "Las dos son cuadradas; diagonales: 1, 4, 9 en B y −3, 0 en C."
                ),
                "fuente": "Matrices y determinantes, láminas 5 y 6",
                "matriz": {"operacion": "clasificar", "a": [[-3, -1], [5, 0]]},
            },
            {
                "concepto": "Matriz identidad",
                "pregunta": "¿Qué es la matriz identidad y para qué sirve?",
                "definicion": (
                    "La matriz cuadrada con **1 en toda la diagonal principal y 0 en el "
                    "resto**. Es el **elemento neutro del producto**: Iₘ·A = A = A·Iₙ si "
                    "A es m × n, igual que el 1 en los números."
                ),
                "notacion": "Iₙ;  I₂ = [1 0; 0 1]",
                "clave_memoria": (
                    "Multiplicar por I es multiplicar por 1: no cambia nada. Ojo con el "
                    "tamaño: a la derecha de un 2 × 3 va I₃, no I₂."
                ),
                "ejercicio_enunciado": "Calcula A·I₃ con A = [1 2 0; 7 3 −4].",
                "ejercicio_desarrollo": (
                    "A es 2 × 3 e I₃ es 3 × 3: columnas de A = filas de I₃ = 3, así que "
                    "el producto existe y es 2 × 3.\n"
                    "c₁₁ = 1·1 + 2·0 + 0·0 = 1;  c₁₂ = 1·0 + 2·1 + 0·0 = 2;  c₁₃ = 0\n"
                    "c₂₁ = 7·1 + 3·0 + (−4)·0 = 7;  c₂₂ = 3;  c₂₃ = −4\n"
                    "Cada columna de I₃ «elige» una columna de A, así que A·I₃ = A."
                ),
                "ejercicio_respuesta": "A·I₃ = [1 2 0; 7 3 −4] = A.",
                "fuente": "Matrices y determinantes, láminas 9, 10 y 32",
                "matriz": {
                    "operacion": "producto",
                    "a": [[1, 2, 0], [7, 3, -4]],
                    "b": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                },
            },
            {
                "concepto": "Matriz diagonal",
                "pregunta": "¿Qué es una matriz diagonal?",
                "definicion": (
                    "Una matriz cuadrada en la que **todo lo que está fuera de la "
                    "diagonal principal es 0**: aᵢⱼ = 0 para todo i ≠ j. Los elementos "
                    "de la diagonal pueden ser cualquier número, incluido el 0."
                ),
                "notacion": "aᵢⱼ = 0 si i ≠ j",
                "clave_memoria": (
                    "«Diagonal» no le exige nada a la diagonal: exige ceros fuera de ella."
                ),
                "ejercicio_enunciado": (
                    "¿Es diagonal D = [3 0 0; 0 −2 0; 0 0 8]? ¿Es también escalar?"
                ),
                "ejercicio_desarrollo": (
                    "Fuera de la diagonal: d₁₂ = d₁₃ = d₂₁ = d₂₃ = d₃₁ = d₃₂ = 0 → es "
                    "diagonal.\n"
                    "En la diagonal hay 3, −2 y 8: no son iguales, así que no es escalar.\n"
                    "Al tener ceros a los dos lados de la diagonal es, a la vez, "
                    "triangular superior, triangular inferior y simétrica."
                ),
                "ejercicio_respuesta": "D es diagonal, pero no escalar.",
                "fuente": "Matrices y determinantes, lámina 11",
                "matriz": {"operacion": "clasificar", "a": [[3, 0, 0], [0, -2, 0], [0, 0, 8]]},
            },
            {
                "concepto": "Matriz escalar",
                "pregunta": "¿Qué es una matriz escalar?",
                "definicion": (
                    "Una matriz **diagonal con todos los elementos de la diagonal "
                    "iguales**. Equivale a la identidad multiplicada por un número: "
                    "E = k·Iₙ. Toda escalar es diagonal, y si k = 1 es la identidad."
                ),
                "notacion": "E = k·Iₙ, con k real",
                "clave_memoria": (
                    "Identidad ⊂ escalar ⊂ diagonal: cada tipo es un caso particular del "
                    "siguiente."
                ),
                "ejercicio_enunciado": (
                    "Escribe E = [5 0 0; 0 5 0; 0 0 5] como un número por la identidad."
                ),
                "ejercicio_desarrollo": (
                    "E es diagonal y su diagonal es 5, 5, 5: es escalar, con k = 5.\n"
                    "5·I₃ multiplica cada entrada de I₃ por 5:\n"
                    "   5·1 = 5 en la diagonal y 5·0 = 0 fuera de ella.\n"
                    "5·I₃ = [5 0 0; 0 5 0; 0 0 5] = E ✓"
                ),
                "ejercicio_respuesta": "E = 5·I₃.",
                "fuente": "Matrices y determinantes, lámina 12",
                "matriz": {
                    "operacion": "escalar",
                    "a": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                    "k": 5,
                },
            },
            {
                "concepto": "Matriz triangular",
                "pregunta": "¿Qué es una matriz triangular superior y una triangular inferior?",
                "definicion": (
                    "Una matriz cuadrada con **ceros a un lado de la diagonal "
                    "principal**. **Superior**: ceros debajo de la diagonal (aᵢⱼ = 0 si "
                    "i > j). **Inferior**: ceros encima (aᵢⱼ = 0 si i < j). Su "
                    "determinante es el producto de la diagonal."
                ),
                "notacion": "superior: aᵢⱼ = 0 si i > j;  inferior: aᵢⱼ = 0 si i < j",
                "clave_memoria": (
                    "El nombre dice dónde están los números, no dónde están los ceros: "
                    "la «superior» tiene los números arriba."
                ),
                "ejercicio_enunciado": (
                    "Clasifica A = [1 2 7; 0 −3 −9; 0 0 5] y calcula su determinante."
                ),
                "ejercicio_desarrollo": (
                    "Debajo de la diagonal: a₂₁ = a₃₁ = a₃₂ = 0 → triangular superior.\n"
                    "Encima hay 2, 7 y −9 → no es triangular inferior.\n"
                    "Por ser triangular, det A es el producto de la diagonal:\n"
                    "   det A = 1·(−3)·5 = −15"
                ),
                "ejercicio_respuesta": "A es triangular superior y det A = −15.",
                "fuente": "Matrices y determinantes, láminas 19, 20 y 43",
                "matriz": {"operacion": "determinante", "a": [[1, 2, 7], [0, -3, -9], [0, 0, 5]]},
            },
            {
                "concepto": "Matriz simétrica",
                "pregunta": "¿Cuándo es simétrica una matriz?",
                "definicion": (
                    "Una matriz cuadrada es **simétrica** si coincide con su traspuesta: "
                    "**Aᵀ = A**, es decir, aᵢⱼ = aⱼᵢ. Lo que hay a un lado de la "
                    "diagonal se repite, como en un espejo, al otro lado."
                ),
                "notacion": "Aᵀ = A ⟺ aᵢⱼ = aⱼᵢ",
                "clave_memoria": (
                    "Dobla la matriz por la diagonal: si cada número cae sobre otro "
                    "igual, es simétrica. La diagonal puede ser cualquier cosa."
                ),
                "ejercicio_enunciado": (
                    "Comprueba que A = [1 0 3; 0 2 −1; 3 −1 0] es simétrica."
                ),
                "ejercicio_desarrollo": (
                    "Se comparan las parejas reflejadas sobre la diagonal:\n"
                    "   a₁₂ = 0 y a₂₁ = 0 ✓\n"
                    "   a₁₃ = 3 y a₃₁ = 3 ✓\n"
                    "   a₂₃ = −1 y a₃₂ = −1 ✓\n"
                    "Todas coinciden, así que Aᵀ = A."
                ),
                "ejercicio_respuesta": "A es simétrica.",
                "fuente": "Matrices y determinantes, lámina 15",
                "matriz": {"operacion": "clasificar", "a": [[1, 0, 3], [0, 2, -1], [3, -1, 0]]},
            },
            {
                "concepto": "Matriz antisimétrica",
                "pregunta": "¿Cuándo es antisimétrica una matriz?",
                "definicion": (
                    "Una matriz cuadrada es **antisimétrica** si su traspuesta es su "
                    "opuesta: **Aᵀ = −A**, es decir, aᵢⱼ = −aⱼᵢ. En consecuencia su "
                    "diagonal es toda de ceros, porque aᵢᵢ = −aᵢᵢ solo lo cumple el 0."
                ),
                "notacion": "Aᵀ = −A ⟺ aᵢⱼ = −aⱼᵢ",
                "clave_memoria": (
                    "Al doblar por la diagonal, cada número cae sobre su opuesto. Si la "
                    "diagonal no es de ceros, ya no puede ser antisimétrica."
                ),
                "ejercicio_enunciado": (
                    "Comprueba que B = [0 3 −1; −3 0 2; 1 −2 0] es antisimétrica."
                ),
                "ejercicio_desarrollo": (
                    "La diagonal es 0, 0, 0 ✓\n"
                    "Cada pareja reflejada es un número y su opuesto:\n"
                    "   b₁₂ = 3 y b₂₁ = −3 ✓\n"
                    "   b₁₃ = −1 y b₃₁ = 1 ✓\n"
                    "   b₂₃ = 2 y b₃₂ = −2 ✓\n"
                    "Por tanto Bᵀ = −B."
                ),
                "ejercicio_respuesta": "B es antisimétrica.",
                "fuente": "Matrices y determinantes, lámina 15",
                "matriz": {"operacion": "clasificar", "a": [[0, 3, -1], [-3, 0, 2], [1, -2, 0]]},
            },
        ],
    },
    {
        "slug": "matrices-operaciones",
        "nombre": "Operaciones con matrices",
        "unidad": "Matrices",
        "orden": 120,
        "descripcion": (
            "Suma, resta, producto por un escalar y producto de matrices, con las "
            "condiciones de orden que hacen que cada operación esté definida, y cómo "
            "despejar una ecuación matricial."
        ),
        "tarjetas": [
            {
                "concepto": "Suma de matrices",
                "pregunta": "¿Cómo se suman dos matrices y cuándo se puede?",
                "definicion": (
                    "Solo se suman matrices del **mismo orden**. Si A y B son m × n, "
                    "A + B es la matriz m × n que se obtiene **sumando las entradas que "
                    "ocupan la misma posición**: A + B = (aᵢⱼ + bᵢⱼ)ₘₓₙ."
                ),
                "notacion": "A + B = (aᵢⱼ + bᵢⱼ)ₘₓₙ",
                "clave_memoria": (
                    "Posición con posición. Si los órdenes no coinciden la suma no está "
                    "definida: sobran entradas sin pareja."
                ),
                "ejercicio_enunciado": (
                    "Calcula A + B con A = [1 2 0; 7 3 −4] y B = [3 1 3; −5 0 6]."
                ),
                "ejercicio_desarrollo": (
                    "Las dos son 2 × 3: la suma existe y es 2 × 3.\n"
                    "Fila 1: 1 + 3 = 4 · 2 + 1 = 3 · 0 + 3 = 3\n"
                    "Fila 2: 7 + (−5) = 2 · 3 + 0 = 3 · −4 + 6 = 2"
                ),
                "ejercicio_respuesta": "A + B = [4 3 3; 2 3 2].",
                "fuente": "Matrices y determinantes, láminas 21 a 23",
                "matriz": {
                    "operacion": "suma",
                    "a": [[1, 2, 0], [7, 3, -4]],
                    "b": [[3, 1, 3], [-5, 0, 6]],
                },
            },
            {
                "concepto": "Propiedades de la suma",
                "pregunta": "¿Qué propiedades cumple la suma de matrices?",
                "definicion": (
                    "Las mismas que la suma de números, porque se suma entrada a entrada: "
                    "**conmutativa**, A + B = B + A, y **asociativa**, A + (B + C) = "
                    "(A + B) + C. La matriz nula O es el neutro (A + O = A) y −A es la "
                    "opuesta (A + (−A) = O)."
                ),
                "notacion": "A + B = B + A",
                "clave_memoria": "La suma no tiene sorpresas; las sorpresas están en el producto.",
                "ejercicio_enunciado": (
                    "Con A = [1 2 0; 7 3 −4] y B = [3 1 3; −5 0 6], comprueba que "
                    "B + A = A + B."
                ),
                "ejercicio_desarrollo": (
                    "B + A suma las mismas parejas en el otro orden:\n"
                    "Fila 1: 3 + 1 = 4 · 1 + 2 = 3 · 3 + 0 = 3\n"
                    "Fila 2: −5 + 7 = 2 · 0 + 3 = 3 · 6 + (−4) = 2\n"
                    "B + A = [4 3 3; 2 3 2] = A + B ✓, porque cada entrada es una suma "
                    "de números, que ya es conmutativa."
                ),
                "ejercicio_respuesta": "B + A = A + B = [4 3 3; 2 3 2].",
                "fuente": "Matrices y determinantes, lámina 23",
                "matriz": {
                    "operacion": "suma",
                    "a": [[3, 1, 3], [-5, 0, 6]],
                    "b": [[1, 2, 0], [7, 3, -4]],
                },
            },
            {
                "concepto": "Resta de matrices",
                "pregunta": "¿Cómo se restan dos matrices?",
                "definicion": (
                    "Como la suma: solo con matrices del **mismo orden** y **entrada a "
                    "entrada**, A − B = (aᵢⱼ − bᵢⱼ). Equivale a sumar la opuesta, "
                    "A − B = A + (−1)B. La resta **no** es conmutativa: B − A = −(A − B)."
                ),
                "notacion": "A − B = A + (−1)·B",
                "clave_memoria": (
                    "Cuidado al restar un negativo: 10 − (−1) = 11. Los paréntesis "
                    "evitan el error de signo."
                ),
                "ejercicio_enunciado": (
                    "Si A = [4 5 −2; 10 6 8; 9 −7 −1] y B = [5 1 3; −1 2 6; 4 9 −8], "
                    "encuentra A − B y B − A."
                ),
                "ejercicio_desarrollo": (
                    "Fila 1: 4 − 5 = −1 · 5 − 1 = 4 · −2 − 3 = −5\n"
                    "Fila 2: 10 − (−1) = 11 · 6 − 2 = 4 · 8 − 6 = 2\n"
                    "Fila 3: 9 − 4 = 5 · −7 − 9 = −16 · −1 − (−8) = 7\n"
                    "B − A tiene cada entrada cambiada de signo: B − A = −(A − B)."
                ),
                "ejercicio_respuesta": (
                    "A − B = [−1 4 −5; 11 4 2; 5 −16 7] y "
                    "B − A = [1 −4 5; −11 −4 −2; −5 16 −7]."
                ),
                "fuente": "Matrices y determinantes, lámina 27",
                "matriz": {
                    "operacion": "resta",
                    "a": [[4, 5, -2], [10, 6, 8], [9, -7, -1]],
                    "b": [[5, 1, 3], [-1, 2, 6], [4, 9, -8]],
                },
            },
            {
                "concepto": "Producto por un escalar",
                "pregunta": "¿Cómo se multiplica una matriz por un número?",
                "definicion": (
                    "Si k es un número real —un **escalar**—, k·A es la matriz del mismo "
                    "orden que se obtiene **multiplicando cada entrada de A por k**: "
                    "kA = (k·aᵢⱼ)ₘₓₙ."
                ),
                "notacion": "kA = (k·aᵢⱼ)ₘₓₙ",
                "clave_memoria": (
                    "El escalar entra en todas las casillas, no solo en una fila (eso es "
                    "otra cosa: la propiedad 7 de los determinantes)."
                ),
                "ejercicio_enunciado": "Calcula 3A para A = [1 2; 3 4].",
                "ejercicio_desarrollo": (
                    "Cada entrada se multiplica por 3:\n"
                    "   3·1 = 3   3·2 = 6\n"
                    "   3·3 = 9   3·4 = 12"
                ),
                "ejercicio_respuesta": "3A = [3 6; 9 12].",
                "fuente": "Matrices y determinantes, láminas 24 y 25",
                "matriz": {"operacion": "escalar", "a": [[1, 2], [3, 4]], "k": 3},
            },
            {
                "concepto": "Propiedades del producto por un escalar",
                "pregunta": "¿Qué propiedades tiene el producto por un escalar?",
                "definicion": (
                    "Con k₁ y k₂ números reales: k₁(A + B) = k₁A + k₁B; "
                    "(k₁ + k₂)A = k₁A + k₂A; y k₁(k₂A) = (k₁k₂)A. Además "
                    "(−1)A + A = O: (−1)A es la opuesta de A."
                ),
                "notacion": "k₁(A + B) = k₁A + k₁B",
                "clave_memoria": (
                    "Se comporta como el álgebra de números: se puede distribuir y "
                    "agrupar."
                ),
                "ejercicio_enunciado": (
                    "Con A = [1 0 2; −3 4 5] y B = [7 2 −1; 4 0 3], calcula "
                    "(a) (−1)A + 2B y (b) (−1)A + A."
                ),
                "ejercicio_desarrollo": (
                    "(a) Entrada a entrada, (−1)·aᵢⱼ + 2·bᵢⱼ:\n"
                    "Fila 1: −1 + 14 = 13 · 0 + 4 = 4 · −2 − 2 = −4\n"
                    "Fila 2: 3 + 8 = 11 · −4 + 0 = −4 · −5 + 6 = 1\n"
                    "(b) (−1)A + A = (−1 + 1)A = 0·A: todas las entradas se anulan."
                ),
                "ejercicio_respuesta": "(a) [13 4 −4; 11 −4 1]; (b) la matriz nula de 2 × 3.",
                "fuente": "Matrices y determinantes, láminas 25 y 26",
                "matriz": {
                    "operacion": "combinacion",
                    "a": [[1, 0, 2], [-3, 4, 5]],
                    "b": [[7, 2, -1], [4, 0, 3]],
                    "k": -1,
                    "m": 2,
                },
            },
            {
                "concepto": "Producto de matrices",
                "pregunta": (
                    "¿Cuándo se pueden multiplicar dos matrices y de qué orden es el "
                    "resultado?"
                ),
                "definicion": (
                    "A·B existe solo si el **número de columnas de A es igual al número "
                    "de filas de B**. Si A es m × n y B es n × p, el producto C = AB es "
                    "**m × p**. Cada entrada cᵢⱼ es la **fila i de A por la columna j de "
                    "B**: se multiplican término a término y se suman los productos."
                ),
                "notacion": "Aₘₓₙ · Bₙₓₚ = Cₘₓₚ",
                "clave_memoria": (
                    "Escribe los órdenes uno junto al otro, (m × n)(n × p): si los del "
                    "medio coinciden se puede, y los de los extremos dan el orden del "
                    "resultado."
                ),
                "ejercicio_enunciado": "Si A = [6 −5] y B = [1 −2; 3 6], calcula AB.",
                "ejercicio_desarrollo": (
                    "A es 1 × 2 y B es 2 × 2: los del medio coinciden (2) y AB es 1 × 2.\n"
                    "c₁₁ = fila 1 de A · columna 1 de B = 6·1 + (−5)·3 = 6 − 15 = −9\n"
                    "c₁₂ = fila 1 de A · columna 2 de B = 6·(−2) + (−5)·6 = −12 − 30 = −42"
                ),
                "ejercicio_respuesta": "AB = [−9 −42].",
                "fuente": "Matrices y determinantes, láminas 28 y 29",
                "matriz": {"operacion": "producto", "a": [[6, -5]], "b": [[1, -2], [3, 6]]},
            },
            {
                "concepto": "Producto fila por columna",
                "pregunta": (
                    "¿Cómo se calcula, entrada por entrada, el producto de dos matrices "
                    "más grandes?"
                ),
                "definicion": (
                    "Se recorre el resultado posición por posición. Para cᵢⱼ se toma la "
                    "**fila i** de la primera y la **columna j** de la segunda, se "
                    "multiplican los elementos que ocupan el mismo lugar y se suman. Un "
                    "2 × 3 por un 3 × 3 da 6 entradas, cada una con 3 productos."
                ),
                "notacion": "cᵢⱼ = aᵢ₁b₁ⱼ + aᵢ₂b₂ⱼ + … + aᵢₙbₙⱼ",
                "clave_memoria": (
                    "Un dedo recorre la fila de la izquierda y el otro baja por la "
                    "columna de la derecha."
                ),
                "ejercicio_enunciado": (
                    "Si A = [2 1 5; 3 0 4] y B = [−1 7 8; 4 6 0; 5 7 3], encuentra AB."
                ),
                "ejercicio_desarrollo": (
                    "A es 2 × 3 y B es 3 × 3 → AB es 2 × 3.\n"
                    "c₁₁ = 2·(−1) + 1·4 + 5·5 = 27\n"
                    "c₁₂ = 2·7 + 1·6 + 5·7 = 55\n"
                    "c₁₃ = 2·8 + 1·0 + 5·3 = 31\n"
                    "c₂₁ = 3·(−1) + 0·4 + 4·5 = 17\n"
                    "c₂₂ = 3·7 + 0·6 + 4·7 = 49\n"
                    "c₂₃ = 3·8 + 0·0 + 4·3 = 36"
                ),
                "ejercicio_respuesta": "AB = [27 55 31; 17 49 36].",
                "fuente": "Matrices y determinantes, lámina 30",
                "matriz": {
                    "operacion": "producto",
                    "a": [[2, 1, 5], [3, 0, 4]],
                    "b": [[-1, 7, 8], [4, 6, 0], [5, 7, 3]],
                },
            },
            {
                "concepto": "El producto no es conmutativo",
                "pregunta": "¿Es lo mismo AB que BA?",
                "definicion": (
                    "En general **no**. Puede que solo uno de los dos esté definido, y "
                    "aunque lo estén los dos, suelen dar matrices distintas. Por eso en "
                    "una ecuación matricial importa **por qué lado** se multiplica."
                ),
                "notacion": "AB ≠ BA (en general)",
                "clave_memoria": (
                    "Con números 2·3 = 3·2; con matrices el orden es parte de la "
                    "operación."
                ),
                "ejercicio_enunciado": (
                    "Si A = [1 2; 3 4] y B = [−2 0; −1 3], encuentra AB y BA."
                ),
                "ejercicio_desarrollo": (
                    "AB: c₁₁ = 1·(−2) + 2·(−1) = −4;  c₁₂ = 1·0 + 2·3 = 6\n"
                    "    c₂₁ = 3·(−2) + 4·(−1) = −10; c₂₂ = 3·0 + 4·3 = 12\n"
                    "BA: c₁₁ = (−2)·1 + 0·3 = −2;    c₁₂ = (−2)·2 + 0·4 = −4\n"
                    "    c₂₁ = (−1)·1 + 3·3 = 8;     c₂₂ = (−1)·2 + 3·4 = 10\n"
                    "Las dos son 2 × 2, pero no coinciden en ninguna entrada."
                ),
                "ejercicio_respuesta": "AB = [−4 6; −10 12] y BA = [−2 −4; 8 10]: AB ≠ BA.",
                "fuente": "Matrices y determinantes, lámina 31",
                "matriz": {"operacion": "producto", "a": A_LAMINA_31, "b": B_LAMINA_31},
            },
            {
                "concepto": "Cuándo no está definido el producto",
                "pregunta": (
                    "¿Qué pasa si el número de columnas de la primera matriz no coincide "
                    "con el de filas de la segunda?"
                ),
                "definicion": (
                    "El producto **no está definido**: no existe, no es «cero» ni un "
                    "error de cálculo. Es una respuesta válida de un ejercicio, y se da "
                    "con el motivo: qué orden tiene cada matriz y qué número no coincide."
                ),
                "clave_memoria": (
                    "Antes de multiplicar, escribe los órdenes. Si los del medio no "
                    "coinciden, has terminado."
                ),
                "ejercicio_enunciado": (
                    "Con A = [2 1 5; 3 0 4] y B = [−1 7 8; 4 6 0; 5 7 3] (lámina 30), "
                    "¿se puede calcular BA?"
                ),
                "ejercicio_desarrollo": (
                    "B es 3 × 3 y A es 2 × 3.\n"
                    "Para BA se escribe (3 × 3)(2 × 3): los del medio son 3 y 2, no "
                    "coinciden.\n"
                    "Cada fila de B tiene 3 números y cada columna de A solo 2: no hay "
                    "con qué emparejar el tercero.\n"
                    "En cambio AB sí existe: (2 × 3)(3 × 3) da un 2 × 3, el de la "
                    "lámina 30."
                ),
                "ejercicio_respuesta": "BA no está definida; AB sí (y es 2 × 3).",
                "fuente": "Matrices y determinantes, láminas 28 y 30",
                "matriz": {
                    "operacion": "producto_ba",
                    "a": [[2, 1, 5], [3, 0, 4]],
                    "b": [[-1, 7, 8], [4, 6, 0], [5, 7, 3]],
                },
            },
            {
                "concepto": "Propiedades del producto de matrices",
                "pregunta": "¿Qué propiedades cumple el producto de matrices?",
                "definicion": (
                    "Con órdenes que permitan las operaciones y k un escalar: "
                    "**asociativa**, A(BC) = (AB)C; **distributiva**, A(B + C) = AB + AC "
                    "y (A + B)C = AC + BC; k(AB) = (kA)B = A(kB); y la identidad es "
                    "neutra, IₘA = A = AIₙ. **No** es conmutativa."
                ),
                "notacion": "k(AB) = (kA)B = A(kB)",
                "clave_memoria": (
                    "Se puede agrupar y distribuir, pero nunca cambiar el orden de los "
                    "factores."
                ),
                "ejercicio_enunciado": (
                    "Con A = [1 2; 3 4] y B = [−2 0; −1 3], comprueba que 2(AB) = (2A)B."
                ),
                "ejercicio_desarrollo": (
                    "AB = [−4 6; −10 12] (lámina 31) → 2(AB) = [−8 12; −20 24].\n"
                    "2A = [2 4; 6 8], y (2A)B:\n"
                    "   c₁₁ = 2·(−2) + 4·(−1) = −8;   c₁₂ = 2·0 + 4·3 = 12\n"
                    "   c₂₁ = 6·(−2) + 8·(−1) = −20;  c₂₂ = 6·0 + 8·3 = 24\n"
                    "(2A)B = [−8 12; −20 24] = 2(AB) ✓"
                ),
                "ejercicio_respuesta": "2(AB) = (2A)B = [−8 12; −20 24].",
                "fuente": "Matrices y determinantes, lámina 32",
                "matriz": {"operacion": "producto", "a": [[2, 4], [6, 8]], "b": B_LAMINA_31},
            },
            {
                "concepto": "Ecuaciones matriciales",
                "pregunta": "¿Cómo se despeja X en una ecuación matricial como AX + B = C?",
                "definicion": (
                    "No se «divide» entre una matriz: se multiplica por su **inversa** "
                    "A⁻¹, y **por el mismo lado** en que está A. Como A⁻¹A = I e IX = X, "
                    "de AX = B sale X = A⁻¹B, y de XA = B sale X = BA⁻¹. Solo es posible "
                    "si A tiene inversa, es decir, si det A ≠ 0."
                ),
                "notacion": "AX = B ⟹ X = A⁻¹B;  XA = B ⟹ X = BA⁻¹",
                "clave_memoria": (
                    "Si A está a la izquierda de X, se quita multiplicando por la "
                    "izquierda; si está a la derecha, por la derecha. A⁻¹B y BA⁻¹ no "
                    "son lo mismo."
                ),
                "ejercicio_enunciado": "Despeja X en AX + B = C.",
                "ejercicio_desarrollo": (
                    "1) Se resta B en los dos lados: AX = C − B.\n"
                    "2) Se multiplica por A⁻¹ por la izquierda, que es donde está A:\n"
                    "   A⁻¹·A·X = A⁻¹·(C − B)\n"
                    "3) A⁻¹A = I e I·X = X:\n"
                    "   X = A⁻¹·(C − B)\n"
                    "Condición: det A ≠ 0; si no, A⁻¹ no existe."
                ),
                "ejercicio_respuesta": "X = A⁻¹·(C − B), siempre que det A ≠ 0.",
                "fuente": "Matrices y determinantes, lámina 33",
            },
            {
                "concepto": "Ecuaciones matriciales con factor común",
                "pregunta": "¿Cómo se despeja X cuando aparece en dos términos, como en XA + C = XB?",
                "definicion": (
                    "Se agrupan los términos con X en un mismo lado y se **saca X como "
                    "factor común por el lado en que está**: XA − XB = X(A − B). Después "
                    "se multiplica por la inversa de (A − B) por ese mismo lado."
                ),
                "notacion": "XA − XB = X(A − B)",
                "clave_memoria": (
                    "X(A − B) y (A − B)X son distintos: el factor común sale por el lado "
                    "en que estaba X."
                ),
                "ejercicio_enunciado": "Despeja X en XA + C = XB.",
                "ejercicio_desarrollo": (
                    "1) Los términos con X a la izquierda: XA − XB = −C.\n"
                    "2) X está a la izquierda en los dos, así que sale por la izquierda:\n"
                    "   X(A − B) = −C\n"
                    "3) Se multiplica por (A − B)⁻¹ por la derecha:\n"
                    "   X(A − B)(A − B)⁻¹ = (−C)(A − B)⁻¹\n"
                    "4) (A − B)(A − B)⁻¹ = I:\n"
                    "   X = (−C)(A − B)⁻¹\n"
                    "Condición: det(A − B) ≠ 0."
                ),
                "ejercicio_respuesta": "X = (−C)·(A − B)⁻¹, siempre que A − B tenga inversa.",
                "fuente": "Matrices y determinantes, lámina 34 (ejercicio 5)",
            },
        ],
    },
    {
        "slug": "determinantes",
        "nombre": "Determinantes y regla de Cramer",
        "unidad": "Matrices",
        "orden": 130,
        "descripcion": (
            "Qué es el determinante, cómo se calcula en 2 × 2 y 3 × 3, sus diez "
            "propiedades, cuándo una matriz tiene inversa y la regla de Cramer para "
            "sistemas de 2 × 2."
        ),
        "tarjetas": [
            {
                "concepto": "Determinante",
                "pregunta": "¿Qué es el determinante de una matriz y para qué sirve?",
                "definicion": (
                    "Un **número** —no otra matriz— asociado a cada matriz **cuadrada**. "
                    "Indica propiedades clave: si det A ≠ 0 la matriz **tiene inversa**, "
                    "y si det A = 0 es **singular**; con la regla de Cramer resuelve "
                    "sistemas; y en geometría, |det A| es el área (2 × 2) o el volumen "
                    "(3 × 3) que encierran sus vectores."
                ),
                "notacion": "det A = |A|",
                "clave_memoria": (
                    "Las barras |A| no son un valor absoluto: el determinante puede ser "
                    "negativo, y eso indica un cambio de orientación (un reflejo)."
                ),
                "ejercicio_enunciado": "¿Admite inversa A = [−3 1; 2 3]?",
                "ejercicio_desarrollo": (
                    "det A = (−3)(3) − (1)(2) = −9 − 2 = −11.\n"
                    "−11 ≠ 0, así que A tiene inversa.\n"
                    "El signo no importa para la inversa: solo importa que no sea 0."
                ),
                "ejercicio_respuesta": "Sí: det A = −11 ≠ 0.",
                "fuente": "Matrices y determinantes, láminas 35, 36 y 42",
                "matriz": {"operacion": "determinante", "a": [[-3, 1], [2, 3]]},
            },
            {
                "concepto": "Determinante de 2 × 2",
                "pregunta": "¿Cómo se calcula el determinante de una matriz de 2 × 2?",
                "definicion": (
                    "**Producto de la diagonal principal menos producto de la diagonal "
                    "secundaria**: si A = [a₁₁ a₁₂; a₂₁ a₂₂], det A = a₁₁a₂₂ − a₁₂a₂₁. "
                    "Con letras: |a b; c d| = ad − bc."
                ),
                "notacion": "|a b; c d| = ad − bc",
                "clave_memoria": (
                    "La flecha que baja (↘) suma y la que sube (↗) resta: «ad menos bc»."
                ),
                "ejercicio_enunciado": "Calcula D = |3 −2; 6 1|.",
                "ejercicio_desarrollo": (
                    "Diagonal principal: 3·1 = 3.\n"
                    "Diagonal secundaria: (−2)·6 = −12.\n"
                    "D = 3 − (−12) = 3 + 12 = 15."
                ),
                "ejercicio_respuesta": "D = 15.",
                "fuente": "Matrices y determinantes, láminas 37, 38 y 46",
                "matriz": {"operacion": "determinante", "a": [[3, -2], [6, 1]]},
            },
            {
                "concepto": "Determinante de 3 × 3 (regla de Sarrus)",
                "pregunta": "¿Cómo se calcula el determinante de una matriz de 3 × 3?",
                "definicion": (
                    "Con la **regla de Sarrus**: se suman los productos de las tres "
                    "diagonales que «bajan» (a₁₁a₂₂a₃₃, a₁₂a₂₃a₃₁, a₁₃a₂₁a₃₂) y se "
                    "restan los de las tres que «suben» (a₁₃a₂₂a₃₁, a₁₁a₂₃a₃₂, "
                    "a₁₂a₂₁a₃₃). Es un atajo que solo vale en 3 × 3: el método que "
                    "enseña el curso es el desarrollo por cofactores (tarjeta "
                    "«Determinante de 3 × 3 por cofactores»). Sirve para comprobar."
                ),
                "notacion": "det A = (bajan) − (suben)",
                "clave_memoria": (
                    "Copia las dos primeras columnas a la derecha de la matriz: las seis "
                    "diagonales quedan a la vista, tres hacia abajo y tres hacia arriba."
                ),
                "ejercicio_enunciado": "Calcula |1 0 −2; 3 1 1; 3 2 0|.",
                "ejercicio_desarrollo": (
                    "Bajan: (1)(1)(0) + (0)(1)(3) + (−2)(3)(2) = 0 + 0 − 12 = −12\n"
                    "Suben: (−2)(1)(3) + (1)(1)(2) + (0)(3)(0) = −6 + 2 + 0 = −4\n"
                    "det = −12 − (−4) = −8"
                ),
                "ejercicio_respuesta": "El determinante vale −8.",
                "fuente": (
                    "Matrices y determinantes, lámina 39 (el método es la regla de "
                    "Sarrus, que la lámina no desarrolla)"
                ),
                "matriz": {
                    "operacion": "determinante", "a": [[1, 0, -2], [3, 1, 1], [3, 2, 0]],
                    "desarrollo": "Sarrus",
                },
            },
            {
                "concepto": "Traspuesta y permutación de líneas",
                "pregunta": (
                    "¿Qué le pasa al determinante al trasponer la matriz y al "
                    "intercambiar dos filas?"
                ),
                "definicion": (
                    "**Propiedad 1**: el determinante de una matriz coincide con el de su "
                    "traspuesta, |A| = |Aᵀ|. **Propiedad 2**: si se **permutan dos filas "
                    "o dos columnas**, el determinante **cambia de signo**. Por la "
                    "propiedad 1, todo lo que vale para filas vale también para columnas."
                ),
                "notacion": "|Aᵀ| = |A|",
                "clave_memoria": (
                    "Un intercambio, un cambio de signo. Dos intercambios devuelven el "
                    "signo original."
                ),
                "ejercicio_enunciado": (
                    "Comprueba que |1 0 −2; 3 1 1; 3 2 0| = −|3 2 0; 3 1 1; 1 0 −2| "
                    "(se intercambiaron la fila 1 y la fila 3)."
                ),
                "ejercicio_desarrollo": (
                    "El primero vale −8 (tarjeta de la regla de Sarrus).\n"
                    "El segundo, por Sarrus:\n"
                    "   Bajan: (3)(1)(−2) + (2)(1)(1) + (0)(3)(0) = −6 + 2 + 0 = −4\n"
                    "   Suben: (0)(1)(1) + (3)(1)(0) + (2)(3)(−2) = 0 + 0 − 12 = −12\n"
                    "   det = −4 − (−12) = 8\n"
                    "−8 = −(8) ✓: intercambiar dos filas cambió el signo."
                ),
                "ejercicio_respuesta": "−8 = −(8): el intercambio de filas cambió el signo.",
                "fuente": "Matrices y determinantes, lámina 39 (propiedades 1 y 2)",
                "matriz": {"operacion": "determinante", "a": [[3, 2, 0], [3, 1, 1], [1, 0, -2]]},
            },
            {
                "concepto": "Determinantes que se anulan",
                "pregunta": "¿Qué tres situaciones hacen que un determinante valga 0 sin calcularlo?",
                "definicion": (
                    "**Propiedad 3**: dos líneas paralelas (dos filas o dos columnas) "
                    "**iguales**. **Propiedad 4**: una línea con **todos sus términos "
                    "iguales a cero**. **Propiedad 5**: dos líneas paralelas "
                    "**proporcionales**, una múltiplo de la otra. En los tres casos el "
                    "determinante es 0."
                ),
                "clave_memoria": (
                    "Iguales es proporcional con factor 1, y una línea de ceros es "
                    "proporcional a cualquiera con factor 0: las tres son la misma idea."
                ),
                "ejercicio_enunciado": "Sin aplicar Sarrus, ¿cuánto vale |1 0 −2; 3 1 1; 2 0 −4|?",
                "ejercicio_desarrollo": (
                    "Fila 3 = (2, 0, −4) = 2·(1, 0, −2) = 2·fila 1.\n"
                    "Las filas 1 y 3 son proporcionales → propiedad 5 → el determinante "
                    "es 0.\n"
                    "Comprobación con Sarrus:\n"
                    "   Bajan: (1)(1)(−4) + (0)(1)(2) + (−2)(3)(0) = −4\n"
                    "   Suben: (−2)(1)(2) + (1)(1)(0) + (0)(3)(−4) = −4\n"
                    "   det = −4 − (−4) = 0 ✓"
                ),
                "ejercicio_respuesta": "Vale 0: la fila 3 es el doble de la fila 1.",
                "fuente": "Matrices y determinantes, láminas 40 y 41 (propiedades 3, 4 y 5)",
                "matriz": {"operacion": "determinante", "a": [[1, 0, -2], [3, 1, 1], [2, 0, -4]]},
            },
            {
                "concepto": "Determinante de un producto",
                "pregunta": "¿Cuánto vale el determinante de un producto de matrices?",
                "definicion": (
                    "**Propiedad 6**: el determinante del producto es el **producto de "
                    "los determinantes**, |A·B| = |A|·|B|. Vale aunque AB ≠ BA: por eso "
                    "|AB| = |BA| siempre."
                ),
                "notacion": "|AB| = |A|·|B|",
                "clave_memoria": (
                    "El determinante sí reparte sobre el producto. Sobre la suma, no: "
                    "|A + B| no es |A| + |B|."
                ),
                "ejercicio_enunciado": (
                    "Con A = [1 2; 3 4] y B = [−2 0; −1 3], comprueba que |AB| = |A|·|B|."
                ),
                "ejercicio_desarrollo": (
                    "|A| = (1)(4) − (2)(3) = −2\n"
                    "|B| = (−2)(3) − (0)(−1) = −6\n"
                    "|A|·|B| = (−2)(−6) = 12\n"
                    "AB = [−4 6; −10 12] (lámina 31) → "
                    "|AB| = (−4)(12) − (6)(−10) = −48 + 60 = 12 ✓"
                ),
                "ejercicio_respuesta": "|AB| = |A|·|B| = 12.",
                "fuente": "Matrices y determinantes, láminas 31 y 41 (propiedad 6)",
                "matriz": {"operacion": "determinante", "a": AB_LAMINA_31},
            },
            {
                "concepto": "Multiplicar una línea por un número",
                "pregunta": (
                    "¿Qué le pasa al determinante si se multiplica una sola fila por un "
                    "número?"
                ),
                "definicion": (
                    "**Propiedad 7**: si se multiplica **una línea** (fila o columna) por "
                    "un número k, el determinante **queda multiplicado por k**. "
                    "**Propiedad 8**: el determinante de la identidad vale 1, |I| = 1."
                ),
                "notacion": "una fila por k ⟹ el determinante por k",
                "clave_memoria": (
                    "Una línea por k multiplica el determinante por k. La matriz entera "
                    "por k son n líneas: el determinante queda multiplicado por kⁿ."
                ),
                "ejercicio_enunciado": (
                    "Si A = [−3 1; 2 3] y B se obtiene multiplicando la primera fila de A "
                    "por 2, compara |A| y |B|."
                ),
                "ejercicio_desarrollo": (
                    "|A| = (−3)(3) − (1)(2) = −9 − 2 = −11\n"
                    "B = [2·(−3) 2·1; 2 3] = [−6 2; 2 3]\n"
                    "|B| = (−6)(3) − (2)(2) = −18 − 4 = −22\n"
                    "−22 = 2·(−11) = 2·|A| ✓"
                ),
                "ejercicio_respuesta": "|B| = −22 = 2·|A|.",
                "fuente": "Matrices y determinantes, lámina 42 (propiedades 7 y 8)",
                "matriz": {"operacion": "determinante", "a": [[-6, 2], [2, 3]]},
            },
            {
                "concepto": "Determinante de una matriz triangular",
                "pregunta": "¿Cómo se calcula rápido el determinante de una matriz triangular?",
                "definicion": (
                    "**Propiedad 9**: el determinante de una matriz triangular —superior "
                    "o inferior, y por tanto también de una diagonal— es el **producto "
                    "de los términos de la diagonal principal**."
                ),
                "notacion": "det A = a₁₁·a₂₂·…·aₙₙ",
                "clave_memoria": (
                    "Si ves ceros a un lado de la diagonal, no hagas Sarrus: multiplica "
                    "la diagonal."
                ),
                "ejercicio_enunciado": "Calcula |−2 4 −5; 0 1 3; 0 0 6|.",
                "ejercicio_desarrollo": (
                    "Debajo de la diagonal todo es 0 → triangular superior.\n"
                    "det = (−2)·1·6 = −12\n"
                    "Con Sarrus saldría lo mismo: las otras cinco diagonales tienen algún "
                    "0 y no suman nada."
                ),
                "ejercicio_respuesta": "El determinante vale −12.",
                "fuente": "Matrices y determinantes, lámina 43 (propiedad 9)",
                "matriz": {"operacion": "determinante", "a": [[-2, 4, -5], [0, 1, 3], [0, 0, 6]]},
            },
            {
                "concepto": "Matriz inversa: cuándo existe",
                "pregunta": "¿Cuándo admite inversa una matriz cuadrada?",
                "definicion": (
                    "**Propiedad 10**: A admite inversa **si y solo si |A| ≠ 0**. Si "
                    "|A| = 0 la matriz es **singular** y no tiene inversa. La inversa "
                    "A⁻¹ cumple A·A⁻¹ = A⁻¹·A = I, y es la que permite despejar "
                    "ecuaciones matriciales. Cómo se calcula está en el mazo «Cofactores, "
                    "inversa y Cramer 3 × 3»."
                ),
                "notacion": "existe A⁻¹ ⟺ |A| ≠ 0",
                "clave_memoria": (
                    "Determinante cero = no hay inversa = no hay solución única. Es la "
                    "misma idea que el Δ = 0 de los sistemas de ecuaciones."
                ),
                "ejercicio_enunciado": (
                    "¿Admiten inversa A = [2 1 1; 2 0 3; 0 0 1] y B = [2 1 1; 2 1 1; 0 −3 1]?"
                ),
                "ejercicio_desarrollo": (
                    "A, por Sarrus:\n"
                    "   Bajan: (2)(0)(1) + (1)(3)(0) + (1)(2)(0) = 0\n"
                    "   Suben: (1)(0)(0) + (2)(3)(0) + (1)(2)(1) = 2\n"
                    "   |A| = 0 − 2 = −2 ≠ 0 → A admite inversa.\n"
                    "B: las filas 1 y 2 son iguales → propiedad 3 → |B| = 0 → B no "
                    "admite inversa."
                ),
                "ejercicio_respuesta": "A sí (|A| = −2); B no (|B| = 0).",
                "fuente": "Matrices y determinantes, lámina 43 (propiedad 10)",
                "matriz": {"operacion": "determinante", "a": [[2, 1, 1], [2, 1, 1], [0, -3, 1]]},
            },
            {
                "concepto": "Regla de Cramer",
                "pregunta": "¿Cómo resuelve la regla de Cramer un sistema de 2 × 2?",
                "definicion": (
                    "Para ax + by = s ; cx + dy = t, con **D = |a b; c d| = ad − bc ≠ 0**: "
                    "x = Dₓ / D e y = D_y / D. **Dₓ** es D con la columna de x cambiada "
                    "por los términos independientes, |s b; t d|; **D_y**, con la columna "
                    "de y cambiada, |a s; c t|."
                ),
                "notacion": "x = Dₓ / D,  y = D_y / D",
                "clave_memoria": (
                    "El denominador es siempre D. En el numerador, la columna de la "
                    "incógnita que buscas se cambia por la de los resultados."
                ),
                "ejercicio_enunciado": (
                    "Usa la regla de Cramer, si es aplicable, para resolver "
                    "3x − 2y = 4 ; 6x + y = 13."
                ),
                "ejercicio_desarrollo": (
                    "D = |3 −2; 6 1| = (3)(1) − (−2)(6) = 3 + 12 = 15 ≠ 0 → es aplicable.\n"
                    "Dₓ = |4 −2; 13 1| = (4)(1) − (−2)(13) = 4 + 26 = 30\n"
                    "D_y = |3 4; 6 13| = (3)(13) − (4)(6) = 39 − 24 = 15\n"
                    "x = 30 / 15 = 2;  y = 15 / 15 = 1\n"
                    "Comprobación: 3(2) − 2(1) = 4 ✓ y 6(2) + 1 = 13 ✓"
                ),
                "ejercicio_respuesta": "(x, y) = (2, 1).",
                "fuente": "Matrices y determinantes, láminas 44 a 46",
                "sistema": {
                    "matriz": [[3, -2, 4], [6, 1, 13]],
                    "incognitas": ["x", "y"],
                    "metodo": "Cramer",
                },
            },
            {
                "concepto": "Cramer cuando D = 0",
                "pregunta": "¿Qué pasa con la regla de Cramer si D = 0?",
                "definicion": (
                    "**No es aplicable**: habría que dividir entre cero. D = 0 significa "
                    "que el sistema **no tiene solución única**: o no tiene ninguna "
                    "(incompatible) o tiene infinitas (compatible indeterminado). Se "
                    "distinguen con Dₓ y D_y: si alguno no es 0, es incompatible; si los "
                    "dos son 0, indeterminado."
                ),
                "notacion": "D = 0 ⟹ no hay solución única",
                "clave_memoria": (
                    "«Si es aplicable» no es relleno en el enunciado: lo primero es "
                    "calcular D."
                ),
                "ejercicio_enunciado": (
                    "Resuelve por Cramer, si es aplicable: 7x + 4y = 1 ; −7x − 4y = −3."
                ),
                "ejercicio_desarrollo": (
                    "D = |7 4; −7 −4| = (7)(−4) − (4)(−7) = −28 + 28 = 0 → no es "
                    "aplicable.\n"
                    "Dₓ = |1 4; −3 −4| = (1)(−4) − (4)(−3) = −4 + 12 = 8 ≠ 0 → "
                    "incompatible.\n"
                    "Se confirma sumando las dos ecuaciones: 0x + 0y = −2, que es falso.\n"
                    "Son dos rectas paralelas: el sistema no tiene solución."
                ),
                "ejercicio_respuesta": (
                    "D = 0: Cramer no es aplicable, y el sistema es incompatible."
                ),
                "fuente": "Matrices y determinantes, lámina 47 (ejercicio 7)",
                "sistema": {
                    "matriz": [[7, 4, 1], [-7, -4, -3]],
                    "incognitas": ["x", "y"],
                    "metodo": "Cramer",
                },
            },
            {
                "concepto": "Cramer con soluciones fraccionarias",
                "pregunta": "¿Qué se hace si Dₓ / D o D_y / D no da un número entero?",
                "definicion": (
                    "Nada especial: la solución es la **fracción exacta**, simplificada. "
                    "Cramer da directamente las dos fracciones con el mismo denominador "
                    "D, y la comprobación se hace con esas fracciones, no con decimales "
                    "redondeados."
                ),
                "clave_memoria": "Si D no divide a Dₓ, la respuesta es Dₓ/D tal cual: 1/19, no «0,05».",
                "ejercicio_enunciado": "Resuelve por Cramer: 3x − 7y = −5 ; 4x − 3y = −2.",
                "ejercicio_desarrollo": (
                    "D = |3 −7; 4 −3| = (3)(−3) − (−7)(4) = −9 + 28 = 19\n"
                    "Dₓ = |−5 −7; −2 −3| = (−5)(−3) − (−7)(−2) = 15 − 14 = 1\n"
                    "D_y = |3 −5; 4 −2| = (3)(−2) − (−5)(4) = −6 + 20 = 14\n"
                    "x = 1/19;  y = 14/19\n"
                    "Comprobación: 3(1/19) − 7(14/19) = −95/19 = −5 ✓\n"
                    "              4(1/19) − 3(14/19) = −38/19 = −2 ✓"
                ),
                "ejercicio_respuesta": "(x, y) = (1/19, 14/19).",
                "fuente": "Matrices y determinantes, lámina 47 (ejercicio 6)",
                "sistema": {
                    "matriz": [[3, -7, -5], [4, -3, -2]],
                    "incognitas": ["x", "y"],
                    "metodo": "Cramer",
                },
            },
            {
                "concepto": "Cramer con una incógnita ausente",
                "pregunta": "¿Cómo se aplica Cramer si una ecuación no tiene una de las incógnitas?",
                "definicion": (
                    "La incógnita que falta tiene **coeficiente 0**, y ese 0 se escribe "
                    "en su lugar en D, Dₓ y D_y. Olvidarlo y «correr» los números hacia "
                    "la izquierda es el error más común."
                ),
                "clave_memoria": (
                    "−2x = 1 es −2x + 0y = 1: primero se completa la ecuación y después "
                    "se arman los determinantes."
                ),
                "ejercicio_enunciado": "Resuelve por Cramer: −2x = 1 ; 4x − 3y = 0.",
                "ejercicio_desarrollo": (
                    "Se completa la primera: −2x + 0y = 1.\n"
                    "D = |−2 0; 4 −3| = (−2)(−3) − (0)(4) = 6\n"
                    "Dₓ = |1 0; 0 −3| = (1)(−3) − (0)(0) = −3\n"
                    "D_y = |−2 1; 4 0| = (−2)(0) − (1)(4) = −4\n"
                    "x = −3/6 = −1/2;  y = −4/6 = −2/3\n"
                    "Comprobación: −2(−1/2) = 1 ✓ y 4(−1/2) − 3(−2/3) = −2 + 2 = 0 ✓"
                ),
                "ejercicio_respuesta": "(x, y) = (−1/2, −2/3).",
                "fuente": "Matrices y determinantes, lámina 47 (ejercicio 4)",
                "sistema": {
                    "matriz": [[-2, 0, 1], [4, -3, 0]],
                    "incognitas": ["x", "y"],
                    "metodo": "Cramer",
                },
            },
        ],
    },
    {
        "slug": "cofactores-inversa",
        "nombre": "Cofactores, inversa y Cramer 3 × 3",
        "unidad": "Matrices",
        "orden": 140,
        "descripcion": (
            "Menores y cofactores, el determinante de 3 × 3 desarrollado por "
            "cualquier fila o columna, la regla de Cramer para tres ecuaciones y la "
            "matriz inversa por la adjunta."
        ),
        "tarjetas": [
            {
                "concepto": "Menor de un elemento",
                "pregunta": "¿Qué es el menor Mᵢⱼ de un elemento aᵢⱼ?",
                "definicion": (
                    "El **determinante que queda al eliminar la fila i y la columna j** "
                    "de la matriz, es decir, la fila y la columna que contienen a aᵢⱼ. "
                    "En un 3 × 3, cada menor es un determinante de 2 × 2."
                ),
                "notacion": "Mᵢⱼ",
                "clave_memoria": (
                    "Tacha con una cruz la fila y la columna del elemento: lo que no "
                    "quedó tachado es su menor."
                ),
                "ejercicio_enunciado": (
                    "Para A = |2 −1 3; −2 5 1; 0 6 −9|, encuentra (a) M₁₂ y (b) M₂₃."
                ),
                "ejercicio_desarrollo": (
                    "(a) Se eliminan la fila 1 y la columna 2:\n"
                    "    queda |−2 1; 0 −9|\n"
                    "    M₁₂ = (−2)(−9) − (1)(0) = 18\n"
                    "(b) Se eliminan la fila 2 y la columna 3:\n"
                    "    queda |2 −1; 0 6|\n"
                    "    M₂₃ = (2)(6) − (−1)(0) = 12"
                ),
                "ejercicio_respuesta": "M₁₂ = 18 y M₂₃ = 12.",
                "fuente": "Matrices y determinantes II, láminas 3 y 4",
                "matriz": {
                    "operacion": "menor", "a": [[2, -1, 3], [-2, 5, 1], [0, 6, -9]],
                    "i": 1, "j": 2,
                },
            },
            {
                "concepto": "Cofactor de un elemento",
                "pregunta": "¿Qué es el cofactor Aᵢⱼ y en qué se diferencia del menor?",
                "definicion": (
                    "Es el menor con un **signo** que depende de la posición: "
                    "Aᵢⱼ = (−1)^(i+j)·Mᵢⱼ. Si i + j es **par**, el cofactor es igual al "
                    "menor; si es **impar**, es su opuesto. Es lo que decide si un término "
                    "del desarrollo se suma o se resta."
                ),
                "notacion": "Aᵢⱼ = (−1)^(i+j)·Mᵢⱼ",
                "clave_memoria": (
                    "Los signos forman un tablero de ajedrez que empieza en +: "
                    "[+ − +; − + −; + − +]."
                ),
                "ejercicio_enunciado": (
                    "Para A = |2 −1 3; −2 5 1; 0 6 −9|, con M₁₂ = 18 y M₂₃ = 12, "
                    "calcula los cofactores A₁₂ y A₂₃."
                ),
                "ejercicio_desarrollo": (
                    "A₁₂: 1 + 2 = 3 es impar → (−1)³ = −1 → A₁₂ = −1·18 = −18\n"
                    "A₂₃: 2 + 3 = 5 es impar → (−1)⁵ = −1 → A₂₃ = −1·12 = −12\n"
                    "Las dos posiciones son «−» en el tablero [+ − +; − + −; + − +]."
                ),
                "ejercicio_respuesta": "A₁₂ = −18 y A₂₃ = −12.",
                "fuente": "Matrices y determinantes II, láminas 7 y 8",
                "matriz": {
                    "operacion": "cofactor", "a": [[2, -1, 3], [-2, 5, 1], [0, 6, -9]],
                    "i": 2, "j": 3,
                },
            },
            {
                "concepto": "Determinante de 3 × 3 por cofactores",
                "pregunta": "¿Cómo se calcula un determinante de 3 × 3 desarrollando por la primera fila?",
                "definicion": (
                    "Cada elemento de la fila se multiplica por su **cofactor** y se suman "
                    "los resultados: |A| = a₁₁·A₁₁ + a₁₂·A₁₂ + a₁₃·A₁₃. Con los signos "
                    "escritos: |A| = a₁₁M₁₁ − a₁₂M₁₂ + a₁₃M₁₃. Es el método que enseña "
                    "el curso para el 3 × 3."
                ),
                "notacion": "|A| = a₁₁M₁₁ − a₁₂M₁₂ + a₁₃M₁₃",
                "clave_memoria": (
                    "Más, menos, más. El «menos» del medio no es opcional: es el signo "
                    "del cofactor A₁₂."
                ),
                "ejercicio_enunciado": "Sea A = [4 7 −2; 3 −5 1; −8 6 9]. Calcula |A|.",
                "ejercicio_desarrollo": (
                    "|A| = 4·|−5 1; 6 9| − 7·|3 1; −8 9| + (−2)·|3 −5; −8 6|\n"
                    "M₁₁ = (−5)(9) − (1)(6) = −51\n"
                    "M₁₂ = (3)(9) − (1)(−8) = 35\n"
                    "M₁₃ = (3)(6) − (−5)(−8) = −22\n"
                    "|A| = 4(−51) − 7(35) + (−2)(−22) = −204 − 245 + 44 = −405"
                ),
                "ejercicio_respuesta": "|A| = −405.",
                "fuente": "Matrices y determinantes II, láminas 1, 2 y 5",
                "matriz": {
                    "operacion": "determinante",
                    "a": [[4, 7, -2], [3, -5, 1], [-8, 6, 9]],
                    "desarrollo": "fila 1",
                },
            },
            {
                "concepto": "Desarrollo por cualquier fila o columna",
                "pregunta": "¿Hay que desarrollar siempre por la primera fila?",
                "definicion": (
                    "No: el determinante se obtiene multiplicando los elementos de "
                    "**cualquier fila o columna** por sus cofactores y sumando. Todas las "
                    "líneas dan el mismo valor; lo que cambia es cuánto cuesta llegar."
                ),
                "notacion": "|A| = Σ aᵢⱼ·Aᵢⱼ sobre una fila o una columna",
                "clave_memoria": (
                    "Elegir línea es elegir trabajo, no resultado. Si dos líneas dan "
                    "valores distintos, hay un error de signo."
                ),
                "ejercicio_enunciado": (
                    "Calcula |3 4 −1; 4 6 2; 8 −2 3| desarrollando por la columna 3 y "
                    "compara con el desarrollo por la fila 1."
                ),
                "ejercicio_desarrollo": (
                    "Columna 3: (−1)^(1+3)(−1)·|4 6; 8 −2| + (−1)^(2+3)(2)·|3 4; 8 −2| "
                    "+ (−1)^(3+3)(3)·|3 4; 4 6|\n"
                    "   = −1(−8 − 48) − 2(−6 − 32) + 3(18 − 16)\n"
                    "   = 56 + 76 + 6 = 138\n"
                    "Fila 1 (lámina 10): 3(22) − 4(−4) + (−1)(−56) = 66 + 16 + 56 = 138 ✓"
                ),
                "ejercicio_respuesta": "Por las dos líneas, el determinante vale 138.",
                "fuente": "Matrices y determinantes II, láminas 9 a 11",
                "matriz": {
                    "operacion": "determinante",
                    "a": [[3, 4, -1], [4, 6, 2], [8, -2, 3]],
                    "desarrollo": "columna 3",
                },
            },
            {
                "concepto": "Elegir la línea con más ceros",
                "pregunta": "¿Por qué fila o columna conviene desarrollar un determinante?",
                "definicion": (
                    "Por la que tenga **más ceros**: el término de un elemento que vale 0 "
                    "es 0, así que su menor ni se calcula. Con un cero se ahorra un "
                    "determinante de 2 × 2; con dos, dos."
                ),
                "clave_memoria": "Busca los ceros antes de empezar: cada cero es un menor menos.",
                "ejercicio_enunciado": (
                    "Calcula |2 −3 5; 1 0 4; 3 −3 9| desarrollando por la fila 2."
                ),
                "ejercicio_desarrollo": (
                    "La fila 2 es (1, 0, 4): a₂₂ = 0 y su término desaparece.\n"
                    "Signos de la fila 2: −, +, −.\n"
                    "|A| = −1·|−3 5; −3 9| + 0 − 4·|2 −3; 3 −3|\n"
                    "    = −1(−27 + 15) − 4(−6 + 9)\n"
                    "    = 12 − 12 = 0\n"
                    "La lámina 6 lo desarrolla por la fila 1 y llega al mismo 0, con un "
                    "menor más: 2·12 + 3(−3) + 5(−3) = 0."
                ),
                "ejercicio_respuesta": "El determinante vale 0.",
                "fuente": "Matrices y determinantes II, láminas 6 y 8",
                "matriz": {
                    "operacion": "determinante",
                    "a": [[2, -3, 5], [1, 0, 4], [3, -3, 9]],
                    "desarrollo": "fila 2",
                },
            },
            {
                "concepto": "Regla de Cramer de 3 × 3",
                "pregunta": "¿Cómo se resuelve un sistema de tres ecuaciones por la regla de Cramer?",
                "definicion": (
                    "Si D, el determinante de los coeficientes, es **distinto de 0**: "
                    "x = Dₓ/D, y = D_y/D, z = D_z/D. Cada numerador es D con la columna "
                    "de esa incógnita **cambiada por los términos independientes**. Los "
                    "cuatro determinantes se calculan desarrollando por cofactores."
                ),
                "notacion": "x = Dₓ/D,  y = D_y/D,  z = D_z/D,  D ≠ 0",
                "clave_memoria": (
                    "Igual que en 2 × 2, pero con cuatro determinantes de 3 × 3. El "
                    "denominador es siempre el mismo D."
                ),
                "ejercicio_enunciado": (
                    "Usa la regla de Cramer, si es aplicable: "
                    "2x + y − z = 3 ; −x + 2y + 4z = −3 ; x − 2y − 3z = 4."
                ),
                "ejercicio_desarrollo": (
                    "D = 2·|2 4; −2 −3| − 1·|−1 4; 1 −3| + (−1)·|−1 2; 1 −2|\n"
                    "  = 2(2) − 1(−1) + (−1)(0) = 5 ≠ 0 → es aplicable\n"
                    "Dₓ = 3(2) − 1(−7) + (−1)(−2) = 15\n"
                    "D_y = 2(−7) − 3(−1) + (−1)(−1) = −10\n"
                    "D_z = 2(2) − 1(−1) + 3(0) = 5\n"
                    "x = 15/5 = 3;  y = −10/5 = −2;  z = 5/5 = 1\n"
                    "Comprobación en (1): 2(3) + (−2) − 1 = 3 ✓"
                ),
                "ejercicio_respuesta": "(x, y, z) = (3, −2, 1).",
                "fuente": "Matrices y determinantes II, láminas 12 a 16",
                "sistema": {
                    "matriz": [[2, 1, -1, 3], [-1, 2, 4, -3], [1, -2, -3, 4]],
                    "incognitas": ["x", "y", "z"],
                    "metodo": "Cramer",
                },
            },
            {
                "concepto": "Cramer de 3 × 3 cuando D = 0",
                "pregunta": "¿Qué pasa con la regla de Cramer de 3 × 3 si D = 0?",
                "definicion": (
                    "**No es aplicable**: el sistema es incompatible (incongruente) o "
                    "tiene infinitas soluciones, y Cramer no dice cuál de las dos. Ojo: a "
                    "diferencia del 2 × 2, en 3 × 3 que Dₓ, D_y y D_z valgan también 0 "
                    "**no** garantiza infinitas soluciones; para decidir hay que eliminar."
                ),
                "notacion": "D = 0 ⟹ Cramer no es aplicable",
                "clave_memoria": (
                    "D = 0 cierra la puerta de Cramer y abre la de la eliminación de "
                    "Gauss: ahí se ve si sale 0 = 0 o 0 = k."
                ),
                "ejercicio_enunciado": (
                    "¿Se puede resolver por Cramer 3x − 2y + 2z = 6 ; 7x − 3y + 2z = −1 ; "
                    "2x − 3y + 4z = 0?"
                ),
                "ejercicio_desarrollo": (
                    "D = 3·|−3 2; −3 4| − (−2)·|7 2; 2 4| + 2·|7 −3; 2 −3|\n"
                    "  = 3(−6) + 2(24) + 2(−15) = −18 + 48 − 30 = 0\n"
                    "D = 0 → Cramer no es aplicable.\n"
                    "Por eliminación (tarjeta «Un 3 × 3 sin solución» de la unidad de "
                    "ecuaciones) aparece una igualdad falsa: el sistema es incompatible."
                ),
                "ejercicio_respuesta": "No: D = 0, y el sistema resulta incompatible.",
                "fuente": (
                    "Matrices y determinantes II, lámina 16; sistema de «Sistemas de "
                    "ecuaciones (3 × 3)», lámina 5"
                ),
                "sistema": {
                    "matriz": [[3, -2, 2, 6], [7, -3, 2, -1], [2, -3, 4, 0]],
                    "incognitas": ["x", "y", "z"],
                    "metodo": "Cramer",
                },
            },
            {
                "concepto": "Matriz adjunta de 2 × 2",
                "pregunta": "¿Cómo se obtiene la adjunta de una matriz de 2 × 2?",
                "definicion": (
                    "Con dos pasos: se **intercambian** los elementos de la diagonal "
                    "principal (a y d) y se **cambia el signo** de los de la diagonal "
                    "secundaria (b y c)."
                ),
                "notacion": "adj [a b; c d] = [d −b; −c a]",
                "clave_memoria": "La principal cambia de lugar; la secundaria cambia de signo.",
                "ejercicio_enunciado": "Calcula la adjunta de A = [2 −4; 1 3].",
                "ejercicio_desarrollo": (
                    "Diagonal principal: 2 y 3 se intercambian → 3 arriba, 2 abajo.\n"
                    "Diagonal secundaria: −4 → 4 y 1 → −1.\n"
                    "adj(A) = [3 4; −1 2]"
                ),
                "ejercicio_respuesta": "adj(A) = [3 4; −1 2].",
                "fuente": "Matrices y determinantes II, láminas 17 y 20",
                "matriz": {"operacion": "adjunta", "a": [[2, -4], [1, 3]]},
            },
            {
                "concepto": "Matriz inversa",
                "pregunta": "¿Qué es la matriz inversa A⁻¹?",
                "definicion": (
                    "La matriz A⁻¹ de n × n que cumple **A·A⁻¹ = A⁻¹·A = Iₙ**. No todas "
                    "las cuadradas la tienen: si existe, A es **no singular**; si no, "
                    "**singular**. Existe exactamente cuando det A ≠ 0."
                ),
                "notacion": "A·A⁻¹ = A⁻¹·A = Iₙ",
                "clave_memoria": (
                    "Una inversa se comprueba sin volver a calcularla: multiplícala por A "
                    "y tiene que salir la identidad."
                ),
                "ejercicio_enunciado": (
                    "Comprueba que [3/10 2/5; −1/10 1/5] es la inversa de A = [2 −4; 1 3]."
                ),
                "ejercicio_desarrollo": (
                    "A·A⁻¹, fila por columna:\n"
                    "c₁₁ = 2(3/10) + (−4)(−1/10) = 6/10 + 4/10 = 1\n"
                    "c₁₂ = 2(2/5) + (−4)(1/5) = 4/5 − 4/5 = 0\n"
                    "c₂₁ = 1(3/10) + 3(−1/10) = 3/10 − 3/10 = 0\n"
                    "c₂₂ = 1(2/5) + 3(1/5) = 2/5 + 3/5 = 1\n"
                    "Sale I₂, así que sí es la inversa."
                ),
                "ejercicio_respuesta": "A·A⁻¹ = [1 0; 0 1] = I₂: es la inversa.",
                "fuente": "Matrices y determinantes II, lámina 18",
                "matriz": {
                    "operacion": "producto",
                    "a": [[2, -4], [1, 3]],
                    "b": [["3/10", "2/5"], ["-1/10", "1/5"]],
                },
            },
            {
                "concepto": "Inversa de 2 × 2",
                "pregunta": "¿Cómo se calcula la inversa de una matriz de 2 × 2?",
                "definicion": (
                    "A es invertible si y solo si det A ≠ 0, y entonces "
                    "**A⁻¹ = (1/det A)·[a₂₂ −a₁₂; −a₂₁ a₁₁]**: el inverso del "
                    "determinante por la adjunta."
                ),
                "notacion": "A⁻¹ = (1/det A)·adj(A)",
                "clave_memoria": (
                    "Primero el determinante: si da 0, se termina ahí, porque no hay "
                    "inversa que calcular."
                ),
                "ejercicio_enunciado": "Sea A = [2 −4; 1 3]. Calcula A⁻¹ si existe.",
                "ejercicio_desarrollo": (
                    "det A = (2)(3) − (−4)(1) = 6 + 4 = 10 ≠ 0 → existe.\n"
                    "adj(A) = [3 4; −1 2]\n"
                    "A⁻¹ = (1/10)·[3 4; −1 2] = [3/10 4/10; −1/10 2/10]\n"
                    "Simplificando: [3/10 2/5; −1/10 1/5]. (La lámina 20 deja el "
                    "ejercicio sin la respuesta impresa.)"
                ),
                "ejercicio_respuesta": "A⁻¹ = [3/10 2/5; −1/10 1/5].",
                "fuente": "Matrices y determinantes II, láminas 19 y 20",
                "matriz": {"operacion": "inversa", "a": [[2, -4], [1, 3]]},
            },
            {
                "concepto": "Matriz de cofactores",
                "pregunta": "¿Qué es la matriz de cofactores C de una matriz cuadrada?",
                "definicion": (
                    "La matriz que tiene en cada posición el **cofactor** del elemento "
                    "que ocupa esa posición en A: Cᵢⱼ = (−1)^(i+j)·Mᵢⱼ. En un 3 × 3 son "
                    "nueve determinantes de 2 × 2."
                ),
                "notacion": "C = (Cᵢⱼ), con Cᵢⱼ = (−1)^(i+j)·Mᵢⱼ",
                "clave_memoria": (
                    "Primero los nueve menores, después el tablero de signos encima. "
                    "Separar los dos pasos evita la mayoría de los errores."
                ),
                "ejercicio_enunciado": "Calcula la matriz de cofactores de A = [1 2 0; 0 1 1; 1 0 3].",
                "ejercicio_desarrollo": (
                    "C₁₁ = +|1 1; 0 3| = 3     C₁₂ = −|0 1; 1 3| = 1     C₁₃ = +|0 1; 1 0| = −1\n"
                    "C₂₁ = −|2 0; 0 3| = −6    C₂₂ = +|1 0; 1 3| = 3     C₂₃ = −|1 2; 1 0| = 2\n"
                    "C₃₁ = +|2 0; 1 1| = 2     C₃₂ = −|1 0; 0 1| = −1    C₃₃ = +|1 2; 0 1| = 1"
                ),
                "ejercicio_respuesta": "C = [3 1 −1; −6 3 2; 2 −1 1].",
                "fuente": "Matrices y determinantes II, láminas 23 y 24",
                "matriz": {"operacion": "cofactores", "a": [[1, 2, 0], [0, 1, 1], [1, 0, 3]]},
            },
            {
                "concepto": "Matriz adjunta de 3 × 3",
                "pregunta": "¿Cómo se obtiene la adjunta de una matriz de 3 × 3?",
                "definicion": (
                    "Es la **traspuesta de la matriz de cofactores**: adj(A) = Cᵀ. La "
                    "fila i de C pasa a ser la columna i de la adjunta."
                ),
                "notacion": "adj(A) = Cᵀ",
                "clave_memoria": (
                    "Olvidar trasponer es el error más común: sin ese paso, lo que "
                    "sale es C y no la adjunta."
                ),
                "ejercicio_enunciado": (
                    "Con A = [1 2 0; 0 1 1; 1 0 3] y su matriz de cofactores "
                    "C = [3 1 −1; −6 3 2; 2 −1 1], obtén adj(A)."
                ),
                "ejercicio_desarrollo": (
                    "Se traspone C:\n"
                    "Fila 1 de C (3, 1, −1) → columna 1 de adj(A)\n"
                    "Fila 2 de C (−6, 3, 2) → columna 2\n"
                    "Fila 3 de C (2, −1, 1) → columna 3"
                ),
                "ejercicio_respuesta": "adj(A) = [3 −6 2; 1 3 −1; −1 2 1].",
                "fuente": "Matrices y determinantes II, láminas 21 y 25",
                "matriz": {"operacion": "adjunta", "a": [[1, 2, 0], [0, 1, 1], [1, 0, 3]]},
            },
            {
                "concepto": "Inversa de 3 × 3 por la adjunta",
                "pregunta": "¿Cuáles son los pasos para invertir una matriz de 3 × 3?",
                "definicion": (
                    "1) Calcular det A; si es 0, parar. 2) Calcular los nueve cofactores "
                    "y formar C. 3) Trasponer: adj(A) = Cᵀ. 4) Multiplicar adj(A) por "
                    "1/det A para obtener A⁻¹."
                ),
                "notacion": "A⁻¹ = (1/det A)·Cᵀ",
                "clave_memoria": (
                    "Determinante, cofactores, trasponer, dividir. El determinante va "
                    "primero porque, si es 0, todo lo demás sobra."
                ),
                "ejercicio_enunciado": "Calcula la inversa de A = [1 2 0; 0 1 1; 1 0 3].",
                "ejercicio_desarrollo": (
                    "1) Por la columna 1: det A = 1(3 − 0) − 0 + 1(2 − 0) = 5 ≠ 0\n"
                    "2) C = [3 1 −1; −6 3 2; 2 −1 1]\n"
                    "3) adj(A) = Cᵀ = [3 −6 2; 1 3 −1; −1 2 1]\n"
                    "4) A⁻¹ = (1/5)·adj(A)"
                ),
                "ejercicio_respuesta": "A⁻¹ = [3/5 −6/5 2/5; 1/5 3/5 −1/5; −1/5 2/5 1/5].",
                "fuente": "Matrices y determinantes II, láminas 21 a 25",
                "matriz": {"operacion": "inversa", "a": [[1, 2, 0], [0, 1, 1], [1, 0, 3]]},
            },
            {
                "concepto": "Inversa con determinante 1",
                "pregunta": "¿Qué tiene de particular la inversa de una matriz con det A = 1?",
                "definicion": (
                    "Como A⁻¹ = (1/det A)·adj(A), con det A = 1 la inversa **es la "
                    "adjunta**: si A tiene entradas enteras, A⁻¹ también, sin una sola "
                    "fracción."
                ),
                "clave_memoria": "det A = 1: invertir es solo calcular la adjunta.",
                "ejercicio_enunciado": "Calcula la inversa de A = [1 2 3; 0 1 4; 5 6 0].",
                "ejercicio_desarrollo": (
                    "det A = 1(0 − 24) − 2(0 − 20) + 3(0 − 5) = −24 + 40 − 15 = 1\n"
                    "C = [−24 20 −5; 18 −15 4; 5 −4 1]\n"
                    "adj(A) = Cᵀ = [−24 18 5; 20 −15 −4; −5 4 1]\n"
                    "A⁻¹ = (1/1)·adj(A) = adj(A)"
                ),
                "ejercicio_respuesta": "A⁻¹ = [−24 18 5; 20 −15 −4; −5 4 1].",
                "fuente": "Matrices y determinantes II, láminas 26 y 27",
                "matriz": {"operacion": "inversa", "a": [[1, 2, 3], [0, 1, 4], [5, 6, 0]]},
            },
            {
                "concepto": "Una matriz singular no tiene inversa",
                "pregunta": "¿Qué se responde si piden la inversa de una matriz con det A = 0?",
                "definicion": (
                    "Que **no existe**: A es singular. No es un error de cálculo ni una "
                    "matriz de ceros; la división entre det A no se puede hacer. Por eso "
                    "el primer paso de toda inversa es el determinante."
                ),
                "clave_memoria": (
                    "Antes de los nueve cofactores, el determinante. Si da 0, la "
                    "respuesta ya está."
                ),
                "ejercicio_enunciado": "Calcula, si existe, la inversa de B = [2 1 1; 2 1 1; 0 −3 1].",
                "ejercicio_desarrollo": (
                    "Las filas 1 y 2 son iguales → propiedad 3 → |B| = 0.\n"
                    "Con det B = 0 no se puede multiplicar por 1/det B.\n"
                    "B es singular: no tiene inversa, y no hace falta calcular ningún "
                    "cofactor."
                ),
                "ejercicio_respuesta": "B⁻¹ no existe: B es singular (|B| = 0).",
                "fuente": (
                    "Matrices y determinantes, lámina 43; Matrices y determinantes II, "
                    "láminas 18 y 21"
                ),
                "matriz": {"operacion": "inversa", "a": [[2, 1, 1], [2, 1, 1], [0, -3, 1]]},
            },
        ],
    },
]
