"""Tarjetas de la unidad de sistemas de ecuaciones lineales.

Fuentes: «Sistemas de ecuaciones 2 × 2», «Sistemas de ecuaciones» (3 × 3) y
«Sistemas de ecuaciones y aplicaciones» de la asignatura, más el documento de
ejercicios resueltos de la carpeta de apuntes.

Las tarjetas que declaran `sistema` muestran el sistema resuelto **paso a
paso** por `services/ecuaciones.py`, con aritmética exacta: donde la respuesta
es 1/2 aparece 1/2, no 0,5. El desarrollo escrito a mano en
`ejercicio_desarrollo` y el que calcula el motor son dos caminos distintos
hacia el mismo resultado; si alguna vez dejaran de coincidir, se vería en la
propia tarjeta.

Lo que **no** entra, a propósito: regla de Cramer de orden 3, matriz inversa y
rangos. No se enseñaron en clase y meterlos desalinearía el laboratorio del
curso. El único determinante que aparece es el Δ de 2 × 2, porque el libro lo
pide en cada ejercicio.

Los coeficientes de `sistema` van como **entero o texto**, nunca como número
con coma: esta estructura viaja a una columna JSON y de ahí al motor, y un
0.333 guardado en la base ya no se puede convertir en el 1/3 que decía el
enunciado.
"""

from __future__ import annotations

MAZOS_ECUACIONES: list[dict] = [
    {
        "slug": "ecuaciones-fundamentos",
        "nombre": "Sistemas lineales — fundamentos",
        "unidad": "Ecuaciones",
        "orden": 70,
        "descripcion": (
            "Qué es una ecuación lineal, qué es un sistema, qué significa resolverlo "
            "y qué se está dibujando cuando se resuelve."
        ),
        "tarjetas": [
            {
                "concepto": "Ecuación lineal",
                "pregunta": "¿Qué hace que una ecuación sea lineal (o de primer grado)?",
                "definicion": (
                    "Una igualdad en la que cada incógnita aparece **elevada a la "
                    "potencia 1**, multiplicada solo por un número y sin multiplicarse "
                    "entre sí. Su forma general con dos incógnitas es a·x + b·y = c, "
                    "donde a y b son los coeficientes y c el término independiente."
                ),
                "notacion": "a₁₁x + a₁₂y = b₁",
                "clave_memoria": (
                    "Si ves x², xy, √x o 1/x, ya no es lineal. «Lineal» viene de que su "
                    "gráfica es una línea recta."
                ),
                "ejercicio_enunciado": (
                    "¿Cuáles de estas ecuaciones son lineales? "
                    "(a) 3x − 4y = 4, (b) x² + y = 7, (c) 2xy = 5, "
                    "(d) (1/2)x − 3y = −1/2."
                ),
                "ejercicio_desarrollo": (
                    "(a) x e y están elevadas a 1 y multiplicadas por números → lineal.\n"
                    "(b) x² es de segundo grado → no lineal.\n"
                    "(c) las incógnitas se multiplican entre sí → no lineal.\n"
                    "(d) los coeficientes pueden ser fracciones; sigue siendo de primer "
                    "grado → lineal."
                ),
                "ejercicio_respuesta": "Son lineales (a) y (d).",
                "fuente": "Sistemas de ecuaciones 2 × 2, láminas 2 y 3",
            },
            {
                "concepto": "Sistema de ecuaciones lineales",
                "pregunta": "¿Qué es un sistema de ecuaciones lineales de m × n?",
                "definicion": (
                    "Un conjunto de **m ecuaciones lineales** que deben cumplirse "
                    "**a la vez** con las **n mismas incógnitas**. En la asignatura se "
                    "trabajan los cuadrados: 2 × 2 (dos ecuaciones, dos incógnitas) y "
                    "3 × 3."
                ),
                "notacion": "a₁₁x + a₁₂y = b₁ ; a₂₁x + a₂₂y = b₂",
                "clave_memoria": (
                    "La llave «{» del sistema se lee como una conjunción: se pide que "
                    "**todas** las ecuaciones se cumplan simultáneamente, no una u otra."
                ),
                "ejercicio_enunciado": (
                    "Identifica el orden del sistema y escribe su matriz de coeficientes:\n"
                    "x + y − z = −1 ; 4x − 3y + 2z = 16 ; 2x − 2y − 3z = 5."
                ),
                "ejercicio_desarrollo": (
                    "Hay tres ecuaciones y tres incógnitas (x, y, z) → es un sistema "
                    "3 × 3.\n"
                    "La matriz de coeficientes recoge los números que acompañan a cada "
                    "incógnita, en el mismo orden en todas las filas:\n"
                    "   [ 1   1  −1 ]\n"
                    "   [ 4  −3   2 ]\n"
                    "   [ 2  −2  −3 ]\n"
                    "Ojo con los signos: el −z de la primera es un coeficiente −1, no un 1."
                ),
                "ejercicio_respuesta": (
                    "Sistema 3 × 3; la matriz de coeficientes es "
                    "[[1, 1, −1], [4, −3, 2], [2, −2, −3]]."
                ),
                "fuente": "Sistemas de ecuaciones (3 × 3), lámina 4 (sistema 1)",
            },
            {
                "concepto": "Solución de un sistema",
                "pregunta": "¿Qué es una solución de un sistema y cómo se comprueba?",
                "definicion": (
                    "El **par ordenado** (x, y) —o la **terna** (x, y, z)— que al "
                    "sustituirse convierte **todas** las ecuaciones en igualdades "
                    "verdaderas. Resolver el sistema es encontrar ese conjunto de valores."
                ),
                "notacion": "(x, y) = (14, −11)",
                "clave_memoria": (
                    "Un valor que cumple una ecuación pero no la otra **no** es solución. "
                    "Comprobar significa sustituir en todas, no en la que salió más fácil."
                ),
                "ejercicio_enunciado": (
                    "Resuelve y comprueba: x + y = 3 ; x + 2y = −8."
                ),
                "ejercicio_desarrollo": (
                    "Restando la primera de la segunda desaparece la x:\n"
                    "   (x + 2y) − (x + y) = −8 − 3 → y = −11.\n"
                    "Sustituyo en la primera: x + (−11) = 3 → x = 14.\n"
                    "Comprobación en las DOS ecuaciones:\n"
                    "   14 + (−11) = 3 ✓\n"
                    "   14 + 2(−11) = 14 − 22 = −8 ✓"
                ),
                "ejercicio_respuesta": "(x, y) = (14, −11).",
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 14 (problema 1)",
                "sistema": {
                    "matriz": [[1, 1, 3], [1, 2, -8]],
                    "incognitas": ["x", "y"],
                    "metodo": "reducción",
                },
            },
            {
                "concepto": "Matriz aumentada",
                "pregunta": "¿Qué es la matriz aumentada de un sistema?",
                "definicion": (
                    "La matriz de coeficientes con **una columna más**: la de los "
                    "términos independientes, separada por una raya vertical. Resume el "
                    "sistema entero sin escribir las incógnitas, que solo se repiten."
                ),
                "notacion": "[ 1  1 | 3 ; 1  2 | −8 ]",
                "clave_memoria": (
                    "Una incógnita que no aparece en una ecuación va como **coeficiente "
                    "0**, no se salta la columna. Saltarla descoloca todas las demás."
                ),
                "ejercicio_enunciado": (
                    "Escribe la matriz aumentada de: −2x = 1 ; 4x − 3y = 0."
                ),
                "ejercicio_desarrollo": (
                    "La primera ecuación no lleva y, así que se escribe completa como "
                    "−2x + 0y = 1.\n"
                    "   [ −2   0 |  1 ]\n"
                    "   [  4  −3 |  0 ]\n"
                    "Ese 0 es el que hay que recordar: es un coeficiente que vale cero, "
                    "no una incógnita que falta."
                ),
                "ejercicio_respuesta": "[[−2, 0 | 1], [4, −3 | 0]].",
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 14 (problema 4)",
                "sistema": {
                    "matriz": [[-2, 0, 1], [4, -3, 0]],
                    "incognitas": ["x", "y"],
                    "metodo": "sustitución",
                },
            },
            {
                "concepto": "Sistemas equivalentes",
                "pregunta": "¿Qué operaciones se pueden hacer sin cambiar la solución?",
                "definicion": (
                    "Dos sistemas son **equivalentes** si tienen exactamente las mismas "
                    "soluciones. Se pasa de uno a otro con tres operaciones: "
                    "**(1)** intercambiar dos ecuaciones, **(2)** multiplicar una "
                    "ecuación por un número distinto de cero y **(3)** sumar a una "
                    "ecuación un múltiplo de otra."
                ),
                "notacion": "(2) → (2) − 4·(1)",
                "clave_memoria": (
                    "Multiplicar por **cero** no vale: destruye la ecuación y convierte el "
                    "sistema en otro con más soluciones. Todos los métodos de la unidad "
                    "son cadenas de estas tres operaciones."
                ),
                "ejercicio_enunciado": (
                    "Partiendo de x + y − z = −1 ; 4x − 3y + 2z = 16, elimina la x de la "
                    "segunda ecuación."
                ),
                "ejercicio_desarrollo": (
                    "La x de la segunda tiene coeficiente 4 y la de la primera, 1.\n"
                    "Aplico la operación (3): a la segunda le resto 4 veces la primera.\n"
                    "   (4x − 3y + 2z) − 4(x + y − z) = 16 − 4(−1)\n"
                    "   4x − 3y + 2z − 4x − 4y + 4z = 16 + 4\n"
                    "   −7y + 6z = 20\n"
                    "El sistema {x + y − z = −1 ; −7y + 6z = 20} es equivalente al de "
                    "partida: tiene las mismas soluciones y una incógnita menos en la "
                    "segunda fila."
                ),
                "ejercicio_respuesta": "(2) − 4·(1) da −7y + 6z = 20.",
                "fuente": "Sistemas de ecuaciones (3 × 3), lámina 4",
            },
            {
                "concepto": "Interpretación geométrica en el plano",
                "pregunta": "¿Qué representa cada ecuación de un 2 × 2 y qué es la solución?",
                "definicion": (
                    "Cada ecuación a·x + b·y = c es una **recta** del plano. La solución "
                    "del sistema es el **punto de corte** de las dos rectas. De ahí las "
                    "tres únicas posibilidades: se cortan en un punto, son paralelas (no "
                    "se cortan) o son coincidentes (se cortan en infinitos puntos)."
                ),
                "notacion": "y = −(a/b)x + c/b",
                "clave_memoria": (
                    "Dos rectas del plano no pueden cortarse en exactamente dos puntos. "
                    "Por eso un sistema lineal tiene una solución, ninguna o infinitas — "
                    "nunca «dos»."
                ),
                "ejercicio_enunciado": (
                    "Resuelve 2x − y = 5 ; 5x + 2y = 8 y di qué significa el resultado "
                    "en el plano."
                ),
                "ejercicio_desarrollo": (
                    "Despejo y en la primera: y = 2x − 5.\n"
                    "Sustituyo en la segunda: 5x + 2(2x − 5) = 8 → 9x − 10 = 8 → 9x = 18 "
                    "→ x = 2.\n"
                    "y = 2(2) − 5 = −1.\n"
                    "Geométricamente: las rectas y = 2x − 5 e y = (8 − 5x)/2 tienen "
                    "pendientes distintas (2 y −5/2), así que se cortan, y lo hacen en "
                    "(2, −1)."
                ),
                "ejercicio_respuesta": (
                    "(x, y) = (2, −1): las dos rectas se cortan en ese único punto."
                ),
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 13 (práctica 1)",
                "sistema": {
                    "matriz": [[2, -1, 5], [5, 2, 8]],
                    "incognitas": ["x", "y"],
                    "metodo": "sustitución",
                },
            },
            {
                "concepto": "Interpretación geométrica en el espacio",
                "pregunta": "¿Qué representa cada ecuación de un 3 × 3?",
                "definicion": (
                    "Cada ecuación a·x + b·y + c·z = d es un **plano** del espacio. La "
                    "solución del sistema es la **intersección de los tres planos**: un "
                    "punto (solución única), una recta o un plano entero (infinitas "
                    "soluciones), o nada en común (sin solución)."
                ),
                "notacion": "ax + by + cz = d",
                "clave_memoria": (
                    "Un punto, una recta, un plano o el vacío. Si la intersección es una "
                    "recta, la solución se escribe en función de un parámetro: hay "
                    "infinitos puntos, pero no cualquiera."
                ),
                "ejercicio_enunciado": (
                    "Resuelve x + y − z = −1 ; 4x − 3y + 2z = 16 ; 2x − 2y − 3z = 5 e "
                    "interpreta el resultado."
                ),
                "ejercicio_desarrollo": (
                    "Con la primera elimino x de las otras dos:\n"
                    "   (2) − 4·(1):  −7y + 6z = 20\n"
                    "   (3) − 2·(1):  −4y − z = 7\n"
                    "De la última despejo z = −4y − 7 y la llevo a la otra:\n"
                    "   −7y + 6(−4y − 7) = 20 → −7y − 24y − 42 = 20 → −31y = 62 → y = −2.\n"
                    "   z = −4(−2) − 7 = 1 ;  x = −1 − y + z = −1 + 2 + 1 = 2.\n"
                    "Los tres planos tienen un único punto en común."
                ),
                "ejercicio_respuesta": (
                    "(x, y, z) = (2, −2, 1): los tres planos se cortan en un solo punto."
                ),
                "fuente": "Sistemas de ecuaciones (3 × 3), lámina 4 (sistema 1)",
                "sistema": {
                    "matriz": [[1, 1, -1, -1], [4, -3, 2, 16], [2, -2, -3, 5]],
                    "incognitas": ["x", "y", "z"],
                },
            },
        ],
    },
    {
        "slug": "ecuaciones-metodos",
        "nombre": "Métodos de resolución 2 × 2",
        "unidad": "Ecuaciones",
        "orden": 80,
        "descripcion": (
            "Sustitución, igualación y reducción: cuándo conviene cada uno, y cómo se "
            "plantea un problema con enunciado."
        ),
        "tarjetas": [
            {
                "concepto": "Método de sustitución",
                "pregunta": "¿En qué consiste el método de sustitución y cuándo conviene?",
                "definicion": (
                    "Se **despeja una incógnita** en una de las ecuaciones y se "
                    "**reemplaza su expresión** en la otra, que queda con una sola "
                    "incógnita. Resuelta esa, se vuelve a la expresión despejada para "
                    "obtener la otra."
                ),
                "notacion": "de (2): x = 7y − 30",
                "clave_memoria": (
                    "Conviene cuando alguna incógnita ya tiene coeficiente 1 o −1: "
                    "despejarla no introduce fracciones."
                ),
                "ejercicio_enunciado": "Resuelve por sustitución: 3x + 2y = 2 ; x − 7y = −30.",
                "ejercicio_desarrollo": (
                    "La x de la segunda tiene coeficiente 1, así que la despejo ahí:\n"
                    "   x = 7y − 30.\n"
                    "La sustituyo en la primera:\n"
                    "   3(7y − 30) + 2y = 2 → 21y − 90 + 2y = 2 → 23y = 92 → y = 4.\n"
                    "Vuelvo a la expresión despejada: x = 7(4) − 30 = 28 − 30 = −2.\n"
                    "Comprobación: 3(−2) + 2(4) = −6 + 8 = 2 ✓ ; −2 − 7(4) = −30 ✓"
                ),
                "ejercicio_respuesta": "(x, y) = (−2, 4).",
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 13 (práctica 2)",
                "sistema": {
                    "matriz": [[3, 2, 2], [1, -7, -30]],
                    "incognitas": ["x", "y"],
                    "metodo": "sustitución",
                },
            },
            {
                "concepto": "Método de igualación",
                "pregunta": "¿En qué consiste el método de igualación?",
                "definicion": (
                    "Se despeja la **misma incógnita en las dos ecuaciones** y se "
                    "**igualan las dos expresiones** obtenidas. Queda una sola ecuación "
                    "con una sola incógnita."
                ),
                "notacion": "y = 3 + x  ;  y = 1 + 3x  →  3 + x = 1 + 3x",
                "clave_memoria": (
                    "Es sustitución disfrazada: si a = c y b = c, entonces a = b. Exige "
                    "que la incógnita elegida **aparezca en las dos** ecuaciones."
                ),
                "ejercicio_enunciado": "Resuelve por igualación: x − y = 3 ; −3x + y = 1.",
                "ejercicio_desarrollo": (
                    "Despejo y en las dos ecuaciones:\n"
                    "   de (1):  y = x − 3\n"
                    "   de (2):  y = 1 + 3x\n"
                    "Igualo: x − 3 = 1 + 3x → −3 − 1 = 3x − x → −4 = 2x → x = −2.\n"
                    "En cualquiera de las dos expresiones: y = (−2) − 3 = −5.\n"
                    "Comprobación: −2 − (−5) = 3 ✓ ; −3(−2) + (−5) = 6 − 5 = 1 ✓"
                ),
                "ejercicio_respuesta": "(x, y) = (−2, −5).",
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 13 (práctica 5)",
                "sistema": {
                    "matriz": [[1, -1, 3], [-3, 1, 1]],
                    "incognitas": ["x", "y"],
                    "metodo": "igualación",
                },
            },
            {
                "concepto": "Método de reducción",
                "pregunta": "¿En qué consiste el método de reducción o eliminación?",
                "definicion": (
                    "Se multiplican las ecuaciones por los números que hagan falta para "
                    "que una incógnita tenga **coeficientes opuestos** (o iguales) y "
                    "luego se **suman o restan**, con lo que esa incógnita desaparece. "
                    "Es el método que usa el docente en los sistemas de 3 × 3."
                ),
                "notacion": "(1)·a₂₁ − (2)·a₁₁",
                "clave_memoria": (
                    "El único método que no obliga a despejar nada, así que no introduce "
                    "fracciones antes de tiempo. Es el que mejor escala a 3 × 3."
                ),
                "ejercicio_enunciado": (
                    "Resuelve por reducción: x − y = 3 ; (1/2)x + y = 3."
                ),
                "ejercicio_desarrollo": (
                    "Los coeficientes de y ya son opuestos (−1 y 1), así que basta sumar "
                    "las dos ecuaciones:\n"
                    "   (x − y) + ((1/2)x + y) = 3 + 3 → (3/2)x = 6 → x = 4.\n"
                    "En la primera: 4 − y = 3 → y = 1.\n"
                    "Comprobación: 4 − 1 = 3 ✓ ; (1/2)(4) + 1 = 2 + 1 = 3 ✓"
                ),
                "ejercicio_respuesta": "(x, y) = (4, 1).",
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 13 (práctica 4)",
                "sistema": {
                    "matriz": [[1, -1, 3], ["1/2", 1, 3]],
                    "incognitas": ["x", "y"],
                    "metodo": "reducción",
                },
            },
            {
                "concepto": "Sistemas con coeficientes fraccionarios",
                "pregunta": "¿Qué se hace cuando el sistema trae fracciones?",
                "definicion": (
                    "Se **multiplica cada ecuación entera** por el mínimo común múltiplo "
                    "de sus denominadores. El sistema que queda es equivalente —misma "
                    "solución— pero con coeficientes enteros, mucho más cómodos."
                ),
                "notacion": "(1/2)x − 3y = −1/2  ⟶ (×2)  x − 6y = −1",
                "clave_memoria": (
                    "Multiplicar por el m.c.m. es la operación (2) de los sistemas "
                    "equivalentes. Hay que multiplicar **todos** los términos, también el "
                    "independiente: olvidarlo es el error clásico."
                ),
                "ejercicio_enunciado": "Resuelve: 3x − 4y = 4 ; (1/2)x − 3y = −1/2.",
                "ejercicio_desarrollo": (
                    "Multiplico la segunda por 2 para quitar los denominadores:\n"
                    "   x − 6y = −1  →  x = 6y − 1.\n"
                    "Sustituyo en la primera:\n"
                    "   3(6y − 1) − 4y = 4 → 18y − 3 − 4y = 4 → 14y = 7 → y = 1/2.\n"
                    "   x = 6(1/2) − 1 = 3 − 1 = 2.\n"
                    "Comprobación: 3(2) − 4(1/2) = 6 − 2 = 4 ✓ ; "
                    "(1/2)(2) − 3(1/2) = 1 − 3/2 = −1/2 ✓"
                ),
                "ejercicio_respuesta": "(x, y) = (2, 1/2).",
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 13 (práctica 3)",
                "sistema": {
                    "matriz": [[3, -4, 4], ["1/2", -3, "-1/2"]],
                    "incognitas": ["x", "y"],
                    "metodo": "sustitución",
                },
            },
            {
                "concepto": "Planteamiento de un problema",
                "pregunta": "¿Cuáles son los pasos para llevar un enunciado a un sistema?",
                "definicion": (
                    "**(1)** Nombrar las incógnitas diciendo qué mide cada una y en qué "
                    "unidad. **(2)** Traducir cada condición del enunciado a una "
                    "ecuación. **(3)** Resolver el sistema. **(4)** Volver al enunciado y "
                    "comprobar que la respuesta tiene sentido."
                ),
                "notacion": "x = nº de autos, y = nº de motos",
                "clave_memoria": (
                    "Tantas ecuaciones como incógnitas: si el enunciado solo da un dato, "
                    "falta leer algo. Y el paso (4) no es decorativo — «−3 motos» "
                    "resuelve el sistema pero no el problema."
                ),
                "ejercicio_enunciado": (
                    "En un estacionamiento hay 55 vehículos entre autos y motos. Si el "
                    "total de ruedas es 170, ¿cuántos autos y cuántas motos hay?"
                ),
                "ejercicio_desarrollo": (
                    "x = cantidad de autos ; y = cantidad de motos.\n"
                    "Vehículos:  x + y = 55.\n"
                    "Ruedas: cada auto aporta 4 y cada moto 2 → 4x + 2y = 170.\n"
                    "Multiplico la primera por 2: 2x + 2y = 110.\n"
                    "Se la resto a la segunda: 2x = 60 → x = 30 ; y = 55 − 30 = 25.\n"
                    "Comprobación con el enunciado: 30 + 25 = 55 vehículos y "
                    "4(30) + 2(25) = 120 + 50 = 170 ruedas ✓"
                ),
                "ejercicio_respuesta": "30 autos y 25 motos.",
                "fuente": "Sistemas de ecuaciones y aplicaciones, lámina 16 (problema 1)",
                "sistema": {
                    "matriz": [[1, 1, 55], [4, 2, 170]],
                    "incognitas": ["x", "y"],
                    "metodo": "reducción",
                },
            },
            {
                "concepto": "Problema de precios",
                "pregunta": "¿Cómo se plantea un problema de dos productos y dos compras?",
                "definicion": (
                    "Las incógnitas son los **precios unitarios**, no las cantidades: "
                    "las cantidades ya las da el enunciado y son los coeficientes. Cada "
                    "compra aporta una ecuación «cantidad × precio + cantidad × precio = "
                    "total»."
                ),
                "notacion": "2x + 3y = 7,80",
                "clave_memoria": (
                    "Lo que se repite en las dos compras es el **precio**: esa es la "
                    "incógnita. Confundirla con la cantidad deja un sistema que no "
                    "responde a la pregunta."
                ),
                "ejercicio_enunciado": (
                    "Dos kilos de naranjas y tres de manzanas cuestan 7,80 €. Cinco "
                    "kilos de naranjas y cuatro de manzanas cuestan 13,20 €. ¿A cuánto "
                    "está el kilo de cada fruta?"
                ),
                "ejercicio_desarrollo": (
                    "x = precio del kilo de naranjas ; y = precio del kilo de manzanas.\n"
                    "   2x + 3y = 7,80\n"
                    "   5x + 4y = 13,20\n"
                    "Multiplico la primera por 4 y la segunda por 3 para igualar la y:\n"
                    "   8x + 12y = 31,20  y  15x + 12y = 39,60.\n"
                    "Restando: 7x = 8,40 → x = 1,20.\n"
                    "En la primera: 2(1,20) + 3y = 7,80 → 3y = 5,40 → y = 1,80."
                ),
                "ejercicio_respuesta": (
                    "El kilo de naranjas cuesta 1,20 € y el de manzanas, 1,80 €."
                ),
                "fuente": "Sistemas de ecuaciones y aplicaciones, lámina 16 (problema 2)",
                "sistema": {
                    "matriz": [[2, 3, "39/5"], [5, 4, "66/5"]],
                    "incognitas": ["x", "y"],
                    "metodo": "reducción",
                },
            },
            {
                "concepto": "Sistema homogéneo",
                "pregunta": "¿Qué es un sistema homogéneo y por qué nunca es incompatible?",
                "definicion": (
                    "Aquel en el que **todos los términos independientes son cero**. "
                    "Siempre admite la **solución trivial** (todas las incógnitas a "
                    "cero), así que nunca puede ser incompatible: o esa es la única "
                    "solución (Δ ≠ 0) o hay infinitas (Δ = 0)."
                ),
                "notacion": "7x + 3y = 0 ; −5x + 10y = 0",
                "clave_memoria": (
                    "En un homogéneo la pregunta nunca es «¿hay solución?» sino «¿hay "
                    "alguna además de la trivial?»."
                ),
                "ejercicio_enunciado": "Resuelve 7x + 3y = 0 ; −5x + 10y = 0.",
                "ejercicio_desarrollo": (
                    "Δ = (7)(10) − (3)(−5) = 70 + 15 = 85 ≠ 0, así que hay solución "
                    "única.\n"
                    "Como el sistema es homogéneo, (0, 0) siempre lo cumple, y al ser "
                    "única, es esa.\n"
                    "Comprobación: 7(0) + 3(0) = 0 ✓ ; −5(0) + 10(0) = 0 ✓\n"
                    "Si Δ hubiera dado 0, las dos ecuaciones serían la misma recta por el "
                    "origen y habría infinitas soluciones."
                ),
                "ejercicio_respuesta": "(x, y) = (0, 0), la solución trivial.",
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 14 (problema 5)",
                "sistema": {
                    "matriz": [[7, 3, 0], [-5, 10, 0]],
                    "incognitas": ["x", "y"],
                    "metodo": "reducción",
                },
            },
        ],
    },
    {
        "slug": "ecuaciones-clasificacion",
        "nombre": "Clasificación y sistemas 3 × 3",
        "unidad": "Ecuaciones",
        "orden": 90,
        "descripcion": (
            "El determinante Δ, los tres tipos de sistema con su lectura geométrica, y "
            "la resolución de sistemas de tres ecuaciones."
        ),
        "tarjetas": [
            {
                "concepto": "Determinante Δ de un 2 × 2",
                "pregunta": "¿Cómo se calcula Δ y qué decide?",
                "definicion": (
                    "Δ = a₁₁·a₂₂ − a₁₂·a₂₁, el producto de la diagonal principal menos "
                    "el de la secundaria. **Si Δ ≠ 0 el sistema tiene solución única**; "
                    "si Δ = 0 no la tiene única: o no hay ninguna o hay infinitas, y hay "
                    "que seguir operando para saber cuál de las dos."
                ),
                "notacion": "Δ = a₁₁a₂₂ − a₁₂a₂₁",
                "clave_memoria": (
                    "Δ ≠ 0 cierra el caso; **Δ = 0 no lo cierra**. Responder «no tiene "
                    "solución» solo porque Δ = 0 es el error más caro de la unidad."
                ),
                "ejercicio_enunciado": (
                    "Calcula Δ y resuelve: 4x + 5y = 0 ; −2x − y = 3."
                ),
                "ejercicio_desarrollo": (
                    "Δ = (4)(−1) − (5)(−2) = −4 + 10 = 6 ≠ 0 → compatible determinado.\n"
                    "Despejo y en la segunda: −y = 3 + 2x → y = −2x − 3.\n"
                    "En la primera: 4x + 5(−2x − 3) = 0 → 4x − 10x − 15 = 0 → −6x = 15 "
                    "→ x = −5/2.\n"
                    "   y = −2(−5/2) − 3 = 5 − 3 = 2.\n"
                    "Comprobación: 4(−5/2) + 5(2) = −10 + 10 = 0 ✓ ; "
                    "−2(−5/2) − 2 = 5 − 2 = 3 ✓"
                ),
                "ejercicio_respuesta": "Δ = 6; (x, y) = (−5/2, 2).",
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 14 (problema 3)",
                "sistema": {
                    "matriz": [[4, 5, 0], [-2, -1, 3]],
                    "incognitas": ["x", "y"],
                    "metodo": "sustitución",
                },
            },
            {
                "concepto": "Compatible determinado",
                "pregunta": "¿Cuándo es un sistema compatible determinado?",
                "definicion": (
                    "Cuando tiene **una única solución**. En 2 × 2 ocurre exactamente si "
                    "Δ ≠ 0, y las dos rectas se cortan en un punto; en 3 × 3, cuando los "
                    "tres planos se cortan en un solo punto del espacio."
                ),
                "notacion": "Δ ≠ 0",
                "clave_memoria": (
                    "«Compatible» = tiene solución. «Determinado» = está determinada, es "
                    "una sola. Las dos palabras responden preguntas distintas."
                ),
                "ejercicio_enunciado": (
                    "Clasifica y resuelve: −13x + 3y = 7 ; 5x + 22y = 9."
                ),
                "ejercicio_desarrollo": (
                    "Δ = (−13)(22) − (3)(5) = −286 − 15 = −301 ≠ 0 → compatible "
                    "determinado.\n"
                    "Para eliminar y: (1)·22 y (2)·3 → −286x + 66y = 154 y 15x + 66y = 27."
                    "\nRestando: −301x = 127 → x = −127/301.\n"
                    "Para eliminar x: (1)·5 y (2)·13 → −65x + 15y = 35 y "
                    "65x + 286y = 117.\nSumando: 301y = 152 → y = 152/301.\n"
                    "La solución es fraccionaria y así se deja: 152/301 no se simplifica "
                    "y escribirla como 0,505 perdería exactitud."
                ),
                "ejercicio_respuesta": (
                    "Compatible determinado: (x, y) = (−127/301, 152/301)."
                ),
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 14 (problema 9)",
                "sistema": {
                    "matriz": [[-13, 3, 7], [5, 22, 9]],
                    "incognitas": ["x", "y"],
                    "metodo": "reducción",
                },
            },
            {
                "concepto": "Compatible indeterminado",
                "pregunta": "¿Cuándo tiene un sistema infinitas soluciones?",
                "definicion": (
                    "Cuando Δ = 0 **y** las ecuaciones son **dependientes**: una es "
                    "múltiplo de la otra, así que no aporta información nueva. Al operar "
                    "se llega a 0 = 0. Las rectas son **coincidentes** y la solución se "
                    "escribe en función de un parámetro."
                ),
                "notacion": "Δ = 0  y  0 = 0",
                "clave_memoria": (
                    "0 = 0 significa «siempre cierto» → infinitas soluciones. La respuesta "
                    "no es «cualquier valor»: es una **familia**, y hay que dar su fórmula."
                ),
                "ejercicio_enunciado": "Clasifica y resuelve: 7x + 4y = 0 ; −7x − 4y = 0.",
                "ejercicio_desarrollo": (
                    "Δ = (7)(−4) − (4)(−7) = −28 + 28 = 0 → no hay solución única.\n"
                    "Sumando las dos ecuaciones: 0 = 0, cierto siempre.\n"
                    "La segunda es la primera multiplicada por −1: es la misma recta.\n"
                    "Despejo de la primera: 4y = −7x → y = −7x/4.\n"
                    "Comprobación con dos puntos de la familia: (0, 0) y (4, −7) cumplen "
                    "las dos ecuaciones ✓\n"
                    "La parametrización no es única: despejando la otra incógnita queda "
                    "x = −(4/7)y, que describe exactamente la misma recta. El laboratorio "
                    "muestra esta segunda forma."
                ),
                "ejercicio_respuesta": (
                    "Compatible indeterminado: infinitas soluciones y = −7x/4, con x "
                    "cualquier número real."
                ),
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 14 (problema 8)",
                "sistema": {
                    "matriz": [[7, 4, 0], [-7, -4, 0]],
                    "incognitas": ["x", "y"],
                    "metodo": "reducción",
                },
            },
            {
                "concepto": "Incompatible",
                "pregunta": "¿Cuándo no tiene solución un sistema?",
                "definicion": (
                    "Cuando Δ = 0 y al operar se llega a una **igualdad falsa** del tipo "
                    "0 = k con k ≠ 0. Los coeficientes son proporcionales pero los "
                    "términos independientes no: las rectas tienen la misma pendiente y "
                    "distinta ordenada, es decir, son **paralelas**."
                ),
                "notacion": "Δ = 0  y  0 = k (k ≠ 0)",
                "clave_memoria": (
                    "Lo que distingue incompatible de indeterminado no es Δ —vale 0 en "
                    "los dos— sino en qué acaba la última línea: 0 = k es paralelas; "
                    "0 = 0 es la misma recta."
                ),
                "ejercicio_enunciado": "Clasifica: 7x + 4y = 1 ; −7x − 4y = −3.",
                "ejercicio_desarrollo": (
                    "Δ = (7)(−4) − (4)(−7) = −28 + 28 = 0 → no hay solución única.\n"
                    "Sumando las dos ecuaciones: 0x + 0y = 1 + (−3) → 0 = −2, que es "
                    "falso.\n"
                    "Los coeficientes de la segunda son los de la primera por −1, pero el "
                    "término independiente no lo es: −3 ≠ −1.\n"
                    "Las rectas 7x + 4y = 1 y 7x + 4y = 3 son paralelas."
                ),
                "ejercicio_respuesta": (
                    "Incompatible: no tiene solución (rectas paralelas)."
                ),
                "fuente": "Sistemas de ecuaciones 2 × 2, lámina 14 (problema 7)",
                "sistema": {
                    "matriz": [[7, 4, 1], [-7, -4, -3]],
                    "incognitas": ["x", "y"],
                    "metodo": "reducción",
                },
            },
            {
                "concepto": "Resolver un 3 × 3 por sustitución",
                "pregunta": "¿Cómo se ataca un sistema de tres ecuaciones por sustitución?",
                "definicion": (
                    "Se despeja una incógnita en la ecuación donde sea más cómodo y se "
                    "**reemplaza en las otras dos**. Queda un sistema 2 × 2, que ya se "
                    "sabe resolver; al final se deshace el camino hacia atrás."
                ),
                "notacion": "3 × 3 → 2 × 2 → 1 ecuación",
                "clave_memoria": (
                    "La estrategia siempre es **bajar de orden**: cada sustitución quita "
                    "una incógnita y una ecuación. Elegir la ecuación con un coeficiente "
                    "1 ahorra todas las fracciones."
                ),
                "ejercicio_enunciado": (
                    "Resuelve: 3x + 3y + 2z = 4 ; x − 3y + z = 10 ; 5x − 2y − 3z = 8."
                ),
                "ejercicio_desarrollo": (
                    "La x de la segunda tiene coeficiente 1: x = 3y − z + 10.\n"
                    "En la primera: 3(3y − z + 10) + 3y + 2z = 4 → 9y − 3z + 30 + 3y + 2z "
                    "= 4 → 12y − z = −26.\n"
                    "En la tercera: 5(3y − z + 10) − 2y − 3z = 8 → 15y − 5z + 50 − 2y − 3z "
                    "= 8 → 13y − 8z = −42.\n"
                    "De 12y − z = −26 saco z = 12y + 26 y lo llevo a la otra:\n"
                    "   13y − 8(12y + 26) = −42 → 13y − 96y − 208 = −42 → −83y = 166 "
                    "→ y = −2.\n"
                    "   z = 12(−2) + 26 = 2 ;  x = 3(−2) − 2 + 10 = 2."
                ),
                "ejercicio_respuesta": "(x, y, z) = (2, −2, 2).",
                "fuente": "Sistemas de ecuaciones (3 × 3), lámina 4 (sistema 2)",
                "sistema": {
                    "matriz": [[3, 3, 2, 4], [1, -3, 1, 10], [5, -2, -3, 8]],
                    "incognitas": ["x", "y", "z"],
                },
            },
            {
                "concepto": "Un 3 × 3 sin solución",
                "pregunta": "¿Cómo se detecta que un sistema de 3 × 3 es incompatible?",
                "definicion": (
                    "Igual que en 2 × 2: eliminando incógnitas se llega a una **igualdad "
                    "imposible**. Aquí la señal típica es que **la misma expresión tenga "
                    "que valer dos cosas distintas**, o que una fila quede como "
                    "0x + 0y + 0z = k con k ≠ 0."
                ),
                "notacion": "4x − y = −7  y  4x − y = 12",
                "clave_memoria": (
                    "No hace falta llegar hasta el final: en cuanto aparece la "
                    "contradicción, el sistema ya está clasificado y no hay nada más que "
                    "calcular."
                ),
                "ejercicio_enunciado": (
                    "Clasifica: 3x − 2y + 2z = 6 ; 7x − 3y + 2z = −1 ; 2x − 3y + 4z = 0."
                ),
                "ejercicio_desarrollo": (
                    "Resto (1) de (2) para eliminar z:\n"
                    "   (7x − 3y + 2z) − (3x − 2y + 2z) = −1 − 6 → 4x − y = −7.\n"
                    "Ahora (1)·2 − (3), que también elimina z:\n"
                    "   (6x − 4y + 4z) − (2x − 3y + 4z) = 12 − 0 → 4x − y = 12.\n"
                    "La misma expresión 4x − y no puede valer −7 y 12 a la vez.\n"
                    "Restando ambas: 0 = 19, que es falso."
                ),
                "ejercicio_respuesta": "Incompatible: el sistema no tiene solución.",
                "fuente": "Sistemas de ecuaciones (3 × 3), lámina 5 (sistema 7)",
                "sistema": {
                    "matriz": [[3, -2, 2, 6], [7, -3, 2, -1], [2, -3, 4, 0]],
                    "incognitas": ["x", "y", "z"],
                },
            },
            {
                "concepto": "Un 3 × 3 con infinitas soluciones",
                "pregunta": "¿Cómo se escribe la solución de un 3 × 3 indeterminado?",
                "definicion": (
                    "Cuando una de las tres ecuaciones no aporta información nueva, queda "
                    "una incógnita **libre**. La solución se expresa dando a esa incógnita "
                    "el papel de **parámetro** y escribiendo las otras dos en función de "
                    "ella: es una recta de puntos, no un punto."
                ),
                "notacion": "(x, y, z) = (5t − 2, 4t − 3, t)",
                "clave_memoria": (
                    "«Infinitas soluciones» no es «cualquier terna». Hay que entregar la "
                    "**fórmula de la familia**; si no, la respuesta no dice cuáles son."
                ),
                "ejercicio_enunciado": (
                    "Resuelve: x − y − z = 1 ; −x + 2y − 3z = −4 ; 3x − 2y − 7z = 0."
                ),
                "ejercicio_desarrollo": (
                    "Sumo (1) y (2) para eliminar x:  y − 4z = −3.\n"
                    "Ahora (1)·3 − (3):  (3x − 3y − 3z) − (3x − 2y − 7z) = 3 − 0 → "
                    "−y + 4z = 3.\n"
                    "Es la misma ecuación anterior cambiada de signo: no hay una tercera "
                    "condición independiente.\n"
                    "Tomo z = t como parámetro: y = 4t − 3 y, de (1), "
                    "x = 1 + y + z = 1 + (4t − 3) + t = 5t − 2.\n"
                    "Comprobación con t = 1 → (3, 1, 1): 3 − 1 − 1 = 1 ✓, "
                    "−3 + 2 − 3 = −4 ✓, 9 − 2 − 7 = 0 ✓"
                ),
                "ejercicio_respuesta": (
                    "Compatible indeterminado: (x, y, z) = (5t − 2, 4t − 3, t), con t "
                    "cualquier número real."
                ),
                "fuente": "Sistemas de ecuaciones (3 × 3), lámina 5 (sistema 6)",
                "sistema": {
                    "matriz": [[1, -1, -1, 1], [-1, 2, -3, -4], [3, -2, -7, 0]],
                    "incognitas": ["x", "y", "z"],
                },
            },
        ],
    },
]
