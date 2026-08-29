"""Tarjetas de la unidad de teoría de conjuntos.

Fuente: «Clase 1 — Conjuntos» y «Clase 2 — Conjuntos 2026» de la asignatura.

Las tarjetas que declaran `venn` muestran el diagrama generado con
matplotlib-venn a partir de los datos del enunciado: las regiones que aparecen
en la imagen son las que calcula el motor de inclusión-exclusión, no números
escritos a mano.
"""

from __future__ import annotations

MAZOS_CONJUNTOS: list[dict] = [
    {
        "slug": "conjuntos-fundamentos",
        "nombre": "Conjuntos — fundamentos",
        "unidad": "Conjuntos",
        "orden": 40,
        "descripcion": (
            "Qué es un conjunto, cómo se describe, cómo se relaciona con sus elementos "
            "y con otros conjuntos."
        ),
        "tarjetas": [
            {
                "concepto": "Conjunto",
                "pregunta": "¿Qué es un conjunto y qué significa que esté «bien definido»?",
                "definicion": (
                    "Una colección bien definida de objetos (números, personas, letras…). "
                    "«Bien definida» significa que se puede determinar sin ambigüedad si "
                    "un objeto pertenece o no al conjunto."
                ),
                "notacion": "A = {1, 2, 3}",
                "clave_memoria": (
                    "El criterio de pertenencia no puede admitir discusión: «los números "
                    "pares» sí es un conjunto; «las películas buenas» no."
                ),
                "ejercicio_enunciado": (
                    "¿Cuáles de estas colecciones son conjuntos bien definidos? "
                    "(a) las vocales del alfabeto, (b) los alumnos altos del curso, "
                    "(c) los números enteros entre −2 y 8."
                ),
                "ejercicio_desarrollo": (
                    "(a) «Vocal» tiene una definición precisa → sí.\n"
                    "(b) «Alto» depende de dónde se ponga el corte → no está bien "
                    "definido.\n"
                    "(c) La condición −2 ≤ x ≤ 8 con x ∈ ℤ es verificable → sí."
                ),
                "ejercicio_respuesta": (
                    "Son conjuntos (a) = {a, e, i, o, u} y (c) = {−2, −1, 0, 1, 2, 3, 4, "
                    "5, 6, 7, 8}. (b) no lo es."
                ),
                "fuente": "Clase 1 — Conjuntos, lámina 2",
            },
            {
                "concepto": "Pertenencia (∈)",
                "pregunta": "¿Qué expresan los símbolos ∈ y ∉?",
                "definicion": (
                    "∈ indica que un elemento es parte de un conjunto («pertenece a»); ∉ "
                    "indica lo contrario. Relacionan un **elemento** con un **conjunto**, "
                    "no dos conjuntos entre sí."
                ),
                "notacion": "2 ∈ A,  4 ∉ A",
                "clave_memoria": (
                    "∈ es elemento-conjunto; ⊂ es conjunto-conjunto. Confundirlos es el "
                    "error más frecuente de la unidad."
                ),
                "ejercicio_enunciado": (
                    "Sea A = {1, 2, 3}. Decide si es verdadero o falso: (a) 2 ∈ A, "
                    "(b) 4 ∈ A, (c) {2} ∈ A, (d) {2} ⊂ A."
                ),
                "ejercicio_desarrollo": (
                    "(a) El 2 aparece listado en A → V.\n"
                    "(b) El 4 no aparece → F (se escribe 4 ∉ A).\n"
                    "(c) A contiene el número 2, no el conjunto {2} → F.\n"
                    "(d) Todo elemento de {2} (solo el 2) está en A → V."
                ),
                "ejercicio_respuesta": "(a) V, (b) F, (c) F, (d) V.",
                "fuente": "Clase 1 — Conjuntos, lámina 14",
            },
            {
                "concepto": "Por extensión y por comprensión",
                "pregunta": "¿Cuáles son las dos formas de describir un conjunto?",
                "definicion": (
                    "**Por extensión**: se enumeran todos los elementos separados por "
                    "comas entre llaves. **Por comprensión**: se elige un elemento "
                    "arbitrario x y se señala la propiedad P(x) que cumple, "
                    "A = {x | x cumple P(x)}, donde «|» se lee «tal que»."
                ),
                "notacion": "A = {1,2,3,4,5}  ≡  A = {x | x es uno de los 5 primeros enteros positivos}",
                "clave_memoria": (
                    "Extensión para pocos elementos; comprensión para muchos o infinitos."
                ),
                "ejercicio_enunciado": (
                    "Escribe por extensión A = {x ∈ ℤ | −2 ≤ x ≤ 8} y "
                    "B = {y ∈ ℕ | 0 < y ≤ 10}, y determina A ∪ B."
                ),
                "ejercicio_desarrollo": (
                    "ℤ son los enteros: A = {−2, −1, 0, 1, 2, 3, 4, 5, 6, 7, 8}.\n"
                    "ℕ son los naturales, y 0 < y: B = {1, 2, …, 10}.\n"
                    "La unión reúne todo, sin repetir: de −2 a 10."
                ),
                "ejercicio_respuesta": (
                    "A ∪ B = {−2, −1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}."
                ),
                "fuente": "Clase 1 — Conjuntos, láminas 4 y 5; Clase 2, lámina 10",
            },
            {
                "concepto": "Conjunto finito e infinito",
                "pregunta": "¿Cuándo es finito un conjunto y cuándo infinito?",
                "definicion": (
                    "Es finito si tiene un número finito de elementos; infinito si no lo "
                    "tiene. A = {1,2,3,4,5,6} es finito (seis elementos); "
                    "A = {x | x es entero positivo} es infinito."
                ),
                "clave_memoria": (
                    "Si puedes terminar de contarlos, es finito. Solo los finitos tienen "
                    "cardinalidad numérica."
                ),
                "ejercicio_enunciado": (
                    "Clasifica: (a) {x ∈ ℕ | x < 100}, (b) {x ∈ ℝ | 0 ≤ x ≤ 6}, "
                    "(c) el conjunto de soluciones de x + y = 5 con x − y = 1."
                ),
                "ejercicio_desarrollo": (
                    "(a) Los naturales menores que 100 se pueden contar → finito.\n"
                    "(b) Entre 0 y 6 hay infinitos reales → infinito.\n"
                    "(c) El sistema tiene solución única (3, 2) → finito, con un solo "
                    "elemento."
                ),
                "ejercicio_respuesta": (
                    "(a) finito, (b) infinito, (c) finito y unitario: B = {(3, 2)}, "
                    "|B| = 1."
                ),
                "fuente": "Clase 1 — Conjuntos, láminas 8 y 9",
            },
            {
                "concepto": "Cardinalidad",
                "pregunta": "¿Qué es la cardinalidad de un conjunto y cómo se denota?",
                "definicion": (
                    "El número de elementos **distintos** de un conjunto finito. Se "
                    "denota Card(A), |A| o n(A)."
                ),
                "notacion": "|A| = n(A) = Card(A)",
                "clave_memoria": (
                    "Elementos distintos: en {1, 2, 2, 3} la cardinalidad es 3, no 4. Un "
                    "conjunto no repite elementos."
                ),
                "ejercicio_enunciado": (
                    "Calcula |A| para A = {2, 4, 6, 8} y para el conjunto de soluciones "
                    "del sistema 2x + y = 5, x − y = 1."
                ),
                "ejercicio_desarrollo": (
                    "A tiene cuatro elementos distintos → |A| = 4.\n"
                    "Del sistema: sumando ambas ecuaciones, 3x = 6 → x = 2; entonces "
                    "y = x − 1 = 1.\n"
                    "El conjunto solución es C = {(2, 1)}."
                ),
                "ejercicio_respuesta": "|A| = 4 y |C| = 1.",
                "fuente": "Clase 1 — Conjuntos, lámina 10; Clase 2, lámina 18",
            },
            {
                "concepto": "Conjuntos equipotentes",
                "pregunta": "¿Cuándo dos conjuntos son equipotentes?",
                "definicion": (
                    "Dos conjuntos finitos X e Y son equipotentes si tienen exactamente "
                    "el mismo número de elementos, es decir |X| = |Y|. No hace falta que "
                    "los elementos sean los mismos."
                ),
                "notacion": "|X| = |Y|",
                "clave_memoria": "Misma cantidad, no mismo contenido.",
                "ejercicio_enunciado": (
                    "C es la solución de {2x + y = 5, x − y = 1} y D la de "
                    "{x + 2y = 7, 3x − 2y = 5}. ¿Son equipotentes?"
                ),
                "ejercicio_desarrollo": (
                    "C: sumando, 3x = 6 → x = 2, y = 1 → C = {(2, 1)}, |C| = 1.\n"
                    "D: sumando, 4x = 12 → x = 3, y = (7 − 3)/2 = 2 → D = {(3, 2)}, "
                    "|D| = 1.\n"
                    "Los elementos son distintos, pero las cardinalidades coinciden."
                ),
                "ejercicio_respuesta": "Sí: |C| = |D| = 1, luego C y D son equipotentes.",
                "fuente": "Clase 1 — Conjuntos, lámina 11",
            },
            {
                "concepto": "Igualdad de conjuntos",
                "pregunta": "¿Cuándo dos conjuntos son iguales?",
                "definicion": (
                    "Cuando tienen exactamente los mismos elementos, sin importar el "
                    "orden ni las repeticiones. Equivale a que A ⊂ B y B ⊂ A a la vez; "
                    "formalmente, ∀x, x ∈ A ↔ x ∈ B."
                ),
                "notacion": "A = B  ⟺  A ⊂ B ∧ B ⊂ A",
                "clave_memoria": "El orden no cuenta: {1,2,3} = {3,1,2}.",
                "ejercicio_enunciado": (
                    "Decide si son iguales: (a) A = {1,2,3} y B = {3,1,2}; "
                    "(b) C = {a,b} y D = {a,b,c}."
                ),
                "ejercicio_desarrollo": (
                    "(a) Todo elemento de A está en B y viceversa → A = B.\n"
                    "(b) c ∈ D pero c ∉ C, luego D ⊄ C. Sí se cumple C ⊂ D, pero falta la "
                    "otra mitad."
                ),
                "ejercicio_respuesta": (
                    "(a) A = B. (b) C ≠ D, aunque C ⊂ D (subconjunto propio)."
                ),
                "fuente": "Clase 1 — Conjuntos, lámina 7",
            },
            {
                "concepto": "Conjunto vacío, unitario y universal",
                "pregunta": "¿Qué son los conjuntos vacío, unitario y universal?",
                "definicion": (
                    "**Vacío**: el que carece de elementos, se denota { } o ∅. "
                    "**Unitario**: el que tiene un solo elemento. **Universal (U)**: el "
                    "conjunto fijo que contiene a todos los elementos considerados en el "
                    "problema; en un diagrama de Venn es el rectángulo exterior."
                ),
                "notacion": "∅ ⊂ A ⊂ U",
                "clave_memoria": (
                    "∅ es subconjunto de todo conjunto. Ojo: ∅ y {∅} no son lo mismo — el "
                    "segundo tiene un elemento."
                ),
                "ejercicio_enunciado": (
                    "Si C = {a, b, c} y D = {d, e, f}, ¿cuánto vale C ∩ D? ¿Y cuál es su "
                    "cardinalidad?"
                ),
                "ejercicio_desarrollo": (
                    "La intersección reúne los elementos comunes.\n"
                    "C y D no comparten ninguna letra.\n"
                    "Por tanto la intersección no tiene elementos."
                ),
                "ejercicio_respuesta": (
                    "C ∩ D = ∅, con |C ∩ D| = 0. C y D son conjuntos **disjuntos**."
                ),
                "fuente": "Clase 1 — Conjuntos, láminas 11 y 18",
            },
            {
                "concepto": "Subconjunto (⊂)",
                "pregunta": "¿Qué significa A ⊂ B y qué propiedades cumple?",
                "definicion": (
                    "Cada elemento de A es también elemento de B: A está contenido en B. "
                    "Formalmente ∀x, x ∈ A → x ∈ B. Si además A ≠ B, se dice que A es "
                    "**subconjunto propio** de B. Si algún elemento de A no está en B, "
                    "se escribe A ⊄ B.\n"
                    "Propiedades: ∅ ⊂ A ⊂ U; A ⊂ A; si A ⊂ B y B ⊂ C entonces A ⊂ C."
                ),
                "notacion": "A ⊂ B  ≡  B ⊃ A",
                "clave_memoria": (
                    "Todo conjunto es subconjunto de sí mismo, y el vacío lo es de todos."
                ),
                "ejercicio_enunciado": (
                    "Con A = {1, 2}, B = {1, 2, 3} y C = {1, 2, 3, 4}, verifica la "
                    "transitividad y di si A es subconjunto propio de C."
                ),
                "ejercicio_desarrollo": (
                    "1 ∈ B y 2 ∈ B, luego A ⊂ B.\n"
                    "Todos los elementos de B están en C, luego B ⊂ C.\n"
                    "Por transitividad, A ⊂ C.\n"
                    "Además 3 ∈ C pero 3 ∉ A, luego A ≠ C."
                ),
                "ejercicio_respuesta": (
                    "A ⊂ C por transitividad, y es subconjunto **propio** porque A ≠ C."
                ),
                "fuente": "Clase 1 — Conjuntos, láminas 12 y 13",
            },
            {
                "concepto": "Conjunto potencia ℘(A)",
                "pregunta": "¿Qué es el conjunto potencia y cuántos elementos tiene?",
                "definicion": (
                    "La familia de **todos** los subconjuntos de A, incluidos ∅ y el "
                    "propio A. Se denota ℘(A). Si |A| = n, entonces |℘(A)| = 2ⁿ."
                ),
                "notacion": "|℘(A)| = 2^|A|",
                "clave_memoria": (
                    "Cada elemento se incluye o no: dos opciones por elemento → 2ⁿ "
                    "combinaciones. Es la misma cuenta que las filas de una tabla de "
                    "verdad."
                ),
                "ejercicio_enunciado": "Determina ℘(A) para A = {a, b, c}.",
                "ejercicio_desarrollo": (
                    "|A| = 3, luego |℘(A)| = 2³ = 8 subconjuntos.\n"
                    "De 0 elementos: ∅.\n"
                    "De 1 elemento: {a}, {b}, {c}.\n"
                    "De 2 elementos: {a,b}, {a,c}, {b,c}.\n"
                    "De 3 elementos: {a,b,c}."
                ),
                "ejercicio_respuesta": (
                    "℘(A) = {∅, {a}, {b}, {c}, {a,b}, {a,c}, {b,c}, {a,b,c}} — 8 elementos."
                ),
                "fuente": "Clase 1 — Conjuntos, láminas 16 y 17",
            },
            {
                "concepto": "Diagrama de Venn",
                "pregunta": "¿Qué es un diagrama de Venn y cómo se dibuja el universo?",
                "definicion": (
                    "Una representación gráfica de los conjuntos y sus relaciones "
                    "mediante figuras planas cerradas: el conjunto universal se dibuja "
                    "como el interior de un rectángulo y los demás conjuntos como discos "
                    "incluidos en él."
                ),
                "clave_memoria": (
                    "Lo que queda dentro del rectángulo pero fuera de todos los discos es "
                    "«ninguno de ellos» — la región que más se olvida al contar."
                ),
                "ejercicio_enunciado": (
                    "Dados A = {1,3,5,7,9,11,13,15} y B = {2,3,5,7,11,13,17,19}, ubica "
                    "los elementos en un diagrama de Venn y determina A Δ B."
                ),
                "ejercicio_desarrollo": (
                    "Zona común (A ∩ B): 3, 5, 7, 11, 13.\n"
                    "Solo en A: 1, 9, 15.\n"
                    "Solo en B: 2, 17, 19.\n"
                    "La diferencia simétrica reúne las dos zonas exteriores."
                ),
                "ejercicio_respuesta": "A Δ B = {1, 2, 9, 15, 17, 19}.",
                "venn": {
                    "etiquetas": ["A", "B"],
                    "conjuntos": {
                        "A": [1, 3, 5, 7, 9, 11, 13, 15],
                        "B": [2, 3, 5, 7, 11, 13, 17, 19],
                    },
                    "titulo": "A Δ B: las dos zonas exteriores",
                },
                "fuente": "Clase 1 — Conjuntos, láminas 15 y 29",
            },
        ],
    },
    {
        "slug": "operaciones-conjuntos",
        "nombre": "Operaciones y álgebra de conjuntos",
        "unidad": "Conjuntos",
        "orden": 50,
        "descripcion": (
            "Unión, intersección, diferencia, complemento y diferencia simétrica, más "
            "las leyes que permiten simplificar expresiones."
        ),
        "tarjetas": [
            {
                "concepto": "Unión (∪)",
                "pregunta": "¿Qué elementos tiene A ∪ B?",
                "definicion": (
                    "Todos los que están en A, en B, o en ambos. Es la operación más "
                    "permisiva: nada se descarta."
                ),
                "notacion": "A ∪ B = {x | x ∈ A ∨ x ∈ B}",
                "clave_memoria": (
                    "La unión se corresponde con la disyunción lógica «o»: basta con "
                    "pertenecer a uno."
                ),
                "ejercicio_enunciado": (
                    "Calcula A ∪ B para A = {1, 2} y B = {2, 3}, y para C = {a, b} y "
                    "D = {c, d}."
                ),
                "ejercicio_desarrollo": (
                    "A ∪ B: se reúnen 1, 2 y 3; el 2 está en ambos pero se escribe una "
                    "sola vez.\n"
                    "C ∪ D: no hay elementos repetidos, se juntan los cuatro."
                ),
                "ejercicio_respuesta": "A ∪ B = {1, 2, 3} y C ∪ D = {a, b, c, d}.",
                "venn": {
                    "etiquetas": ["A", "B"],
                    "conjuntos": {"A": [1, 2], "B": [2, 3]},
                    "titulo": "A ∪ B = todo lo sombreado",
                },
                "fuente": "Clase 1 — Conjuntos, lámina 21",
            },
            {
                "concepto": "Intersección (∩)",
                "pregunta": "¿Qué elementos tiene A ∩ B?",
                "definicion": (
                    "Solo los que están en **ambos** conjuntos a la vez. Si no hay "
                    "ninguno, la intersección es el conjunto vacío y los conjuntos son "
                    "disjuntos."
                ),
                "notacion": "A ∩ B = {x | x ∈ A ∧ x ∈ B}",
                "clave_memoria": (
                    "La intersección se corresponde con la conjunción lógica «y»: hay que "
                    "pertenecer a los dos."
                ),
                "ejercicio_enunciado": (
                    "Calcula A ∩ B con A = {1,2,3} y B = {3,4,5}; y C ∩ D con "
                    "C = {a,b,c} y D = {d,e,f}."
                ),
                "ejercicio_desarrollo": (
                    "El único elemento común entre A y B es el 3.\n"
                    "C y D no comparten ninguna letra."
                ),
                "ejercicio_respuesta": "A ∩ B = {3} y C ∩ D = ∅ (conjuntos disjuntos).",
                "venn": {
                    "etiquetas": ["A", "B"],
                    "conjuntos": {"A": [1, 2, 3], "B": [3, 4, 5]},
                    "titulo": "A ∩ B = la zona central",
                },
                "fuente": "Clase 1 — Conjuntos, lámina 18",
            },
            {
                "concepto": "Diferencia (−)",
                "pregunta": "¿Qué elementos tiene A − B?",
                "definicion": (
                    "Los que están en A pero **no** en B. No es simétrica: A − B y B − A "
                    "suelen ser distintos."
                ),
                "notacion": "A − B = {x | x ∈ A ∧ x ∉ B}",
                "clave_memoria": "«A quitándole lo que comparte con B».",
                "ejercicio_enunciado": (
                    "Con A = {1,2,3,4} y B = {3,4,5,6}, calcula A − B y B − A."
                ),
                "ejercicio_desarrollo": (
                    "A − B: de {1,2,3,4} se quitan 3 y 4 (que están en B) → {1, 2}.\n"
                    "B − A: de {3,4,5,6} se quitan 3 y 4 → {5, 6}.\n"
                    "Los resultados son distintos: la diferencia no es conmutativa."
                ),
                "ejercicio_respuesta": "A − B = {1, 2} y B − A = {5, 6}.",
                "venn": {
                    "etiquetas": ["A", "B"],
                    "conjuntos": {"A": [1, 2, 3, 4], "B": [3, 4, 5, 6]},
                    "titulo": "A − B = la media luna izquierda",
                },
                "fuente": "Clase 1 — Conjuntos, lámina 26",
            },
            {
                "concepto": "Complemento (Aᶜ)",
                "pregunta": "¿Qué es el complemento de un conjunto?",
                "definicion": (
                    "El conjunto de todos los elementos que están en el universo U pero "
                    "no en A. Se denota Aᶜ o A′. Cumple A ∪ Aᶜ = U y A ∩ Aᶜ = ∅, y la "
                    "ley involutiva (Aᶜ)ᶜ = A."
                ),
                "notacion": "Aᶜ = U − A;  n(Aᶜ) = n(U) − n(A)",
                "clave_memoria": (
                    "Sin universo declarado no hay complemento posible: siempre es "
                    "«complemento respecto de U»."
                ),
                "ejercicio_enunciado": (
                    "Con U = {a,b,c,d,e,f,g,h,i,j,k,l,m}, A = {a,b,c,d}, B = {a,e,f,g} y "
                    "C = {a,b,h,k}, calcula (A − B)ᶜ ∩ C."
                ),
                "ejercicio_desarrollo": (
                    "A − B = {b, c, d} (se quita la a, que está en B).\n"
                    "(A − B)ᶜ = U − {b,c,d} = {a, e, f, g, h, i, j, k, l, m}.\n"
                    "Ahora se interseca con C = {a, b, h, k}: se conservan los elementos "
                    "presentes en ambos → a, h, k (la b no está en el complemento)."
                ),
                "ejercicio_respuesta": "(A − B)ᶜ ∩ C = {a, h, k}.",
                "fuente": "Clase 1 — Conjuntos, láminas 27 y 33",
            },
            {
                "concepto": "Diferencia simétrica (Δ)",
                "pregunta": "¿Qué elementos tiene A Δ B?",
                "definicion": (
                    "Los que están en exactamente uno de los dos conjuntos: "
                    "A Δ B = (A − B) ∪ (B − A). Su cardinalidad es "
                    "|A| + |B| − 2·|A ∩ B|."
                ),
                "notacion": "A Δ B = (A − B) ∪ (B − A)",
                "clave_memoria": (
                    "Es el «o exclusivo» de los conjuntos: la zona común queda fuera."
                ),
                "ejercicio_enunciado": (
                    "Con A = {a,b,c,d}, C = {a,b,h,k} y U = {a,…,m}, calcula "
                    "(A Δ C) ∪ Aᶜ."
                ),
                "ejercicio_desarrollo": (
                    "A − C = {c, d}; C − A = {h, k}.\n"
                    "A Δ C = {c, d, h, k}.\n"
                    "Aᶜ = U − A = {e, f, g, h, i, j, k, l, m}.\n"
                    "La unión reúne ambas listas sin repetir."
                ),
                "ejercicio_respuesta": (
                    "(A Δ C) ∪ Aᶜ = {c, d, e, f, g, h, i, j, k, l, m}."
                ),
                "fuente": "Clase 1 — Conjuntos, láminas 29 y 34",
            },
            {
                "concepto": "Conjuntos disjuntos",
                "pregunta": "¿Cuándo dos conjuntos son disjuntos?",
                "definicion": (
                    "Cuando no tienen ningún elemento en común: A ∩ B = ∅. También se "
                    "llaman mutuamente excluyentes. Formalmente, ∀x, ¬(x ∈ A ∧ x ∈ B)."
                ),
                "notacion": "A ∩ B = ∅  ⟹  n(A ∪ B) = n(A) + n(B)",
                "clave_memoria": (
                    "Solo con conjuntos disjuntos se pueden sumar las cardinalidades sin "
                    "corregir nada."
                ),
                "ejercicio_enunciado": (
                    "Si A = {1,2,3} y B = {4,5}, ¿son disjuntos? ¿Cuánto vale n(A ∪ B)?"
                ),
                "ejercicio_desarrollo": (
                    "A ∩ B = ∅: no comparten elementos → son disjuntos.\n"
                    "Al no haber solapamiento, no hay nada contado dos veces.\n"
                    "n(A ∪ B) = n(A) + n(B) = 3 + 2."
                ),
                "ejercicio_respuesta": "Sí son disjuntos, y n(A ∪ B) = 5.",
                "venn": {
                    "etiquetas": ["A", "B"],
                    "conjuntos": {"A": [1, 2, 3], "B": [4, 5]},
                    "titulo": "Conjuntos disjuntos: A ∩ B = ∅",
                },
                "fuente": "Clase 2 — Conjuntos 2026, lámina 18",
            },
            {
                "concepto": "Leyes del álgebra de conjuntos",
                "pregunta": "¿Qué leyes permiten simplificar expresiones de conjuntos?",
                "definicion": (
                    "Idempotentes: A ∪ A = A, A ∩ A = A.\n"
                    "Conmutativas: A ∪ B = B ∪ A, A ∩ B = B ∩ A.\n"
                    "Asociativas: (A ∪ B) ∪ C = A ∪ (B ∪ C) e igual con ∩.\n"
                    "Distributivas: A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C); "
                    "A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C).\n"
                    "Identidad y absorción: A ∪ ∅ = A, A ∩ U = A, A ∪ U = U, A ∩ ∅ = ∅.\n"
                    "Involutiva: (Aᶜ)ᶜ = A.  Complementario: A ∪ Aᶜ = U, A ∩ Aᶜ = ∅, "
                    "Uᶜ = ∅."
                ),
                "clave_memoria": (
                    "Son las mismas leyes de la lógica proposicional: ∪ se comporta como "
                    "∨, ∩ como ∧ y el complemento como ¬."
                ),
                "ejercicio_enunciado": (
                    "Simplifica (A ∩ B) ∪ (A ∩ Bᶜ) justificando cada paso con una ley."
                ),
                "ejercicio_desarrollo": (
                    "Por la distributiva (al revés): (A ∩ B) ∪ (A ∩ Bᶜ) = A ∩ (B ∪ Bᶜ).\n"
                    "Por la ley del complementario: B ∪ Bᶜ = U.\n"
                    "Por la ley de identidad: A ∩ U = A."
                ),
                "ejercicio_respuesta": (
                    "(A ∩ B) ∪ (A ∩ Bᶜ) = A. Tiene sentido: todo elemento de A o está en "
                    "B o no lo está."
                ),
                "fuente": "Clase 1 — Conjuntos, lámina 32 («Leyes del álgebra de conjuntos»)",
            },
            {
                "concepto": "Leyes de De Morgan (conjuntos)",
                "pregunta": "¿Cómo se complementa una unión y cómo una intersección?",
                "definicion": (
                    "(A ∪ B)ᶜ = Aᶜ ∩ Bᶜ  y  (A ∩ B)ᶜ = Aᶜ ∪ Bᶜ. Al complementar, la "
                    "operación se invierte."
                ),
                "notacion": "(A ∪ B)ᶜ = Aᶜ ∩ Bᶜ",
                "clave_memoria": (
                    "«No estar en A ni en B» = «no estar en A y no estar en B». Es la "
                    "misma ley que en lógica, con ∪↔∨ y ∩↔∧."
                ),
                "ejercicio_enunciado": (
                    "Con U = {1,…,10}, A = {1,2,3,4} y B = {3,4,5,6}, comprueba que "
                    "(A ∪ B)ᶜ = Aᶜ ∩ Bᶜ."
                ),
                "ejercicio_desarrollo": (
                    "A ∪ B = {1,2,3,4,5,6} → (A ∪ B)ᶜ = {7, 8, 9, 10}.\n"
                    "Aᶜ = {5,6,7,8,9,10}; Bᶜ = {1,2,7,8,9,10}.\n"
                    "Aᶜ ∩ Bᶜ = {7, 8, 9, 10}."
                ),
                "ejercicio_respuesta": "Ambos lados dan {7, 8, 9, 10}: la ley se cumple.",
                "fuente": "Clase 1 — Conjuntos, lámina 28",
            },
        ],
    },
    {
        "slug": "cardinalidad-venn",
        "nombre": "Cardinalidad e inclusión-exclusión",
        "unidad": "Conjuntos",
        "orden": 60,
        "descripcion": (
            "Contar sin contar dos veces: las fórmulas de inclusión-exclusión y los "
            "problemas de encuesta con diagrama de Venn."
        ),
        "tarjetas": [
            {
                "concepto": "Cardinalidad de la unión de conjuntos disjuntos",
                "pregunta": "¿Cómo se cuenta la unión cuando los conjuntos no se solapan?",
                "definicion": (
                    "Si A ∩ B = ∅, la cardinalidad de la unión es la simple suma: "
                    "n(A ∪ B) = n(A) + n(B). No hay nada contado dos veces que corregir."
                ),
                "notacion": "A ∩ B = ∅ ⟹ n(A ∪ B) = n(A) + n(B)",
                "clave_memoria": (
                    "Es el único caso en que sumar directo es correcto. Comprueba siempre "
                    "que la intersección sea vacía antes de usarla."
                ),
                "ejercicio_enunciado": (
                    "En un curso, 12 alumnos rinden solo el examen de la mañana y 9 solo "
                    "el de la tarde; nadie rinde ambos. ¿Cuántos rinden examen?"
                ),
                "ejercicio_desarrollo": (
                    "Los conjuntos «mañana» y «tarde» son disjuntos por enunciado.\n"
                    "n(M ∩ T) = 0, luego no hay solapamiento que descontar.\n"
                    "n(M ∪ T) = 12 + 9."
                ),
                "ejercicio_respuesta": "21 alumnos rinden examen.",
                "fuente": "Clase 2 — Conjuntos 2026, lámina 18",
            },
            {
                "concepto": "Inclusión-exclusión para dos conjuntos",
                "pregunta": "¿Cuál es la fórmula de n(A ∪ B) cuando hay solapamiento?",
                "definicion": (
                    "n(A ∪ B) = n(A) + n(B) − n(A ∩ B). Al sumar n(A) + n(B), los "
                    "elementos de A ∩ B se cuentan dos veces; se resta una para corregir "
                    "la sobreestimación."
                ),
                "notacion": "n(A ∪ B) = n(A) + n(B) − n(A ∩ B)",
                "clave_memoria": (
                    "Solo A = n(A) − n(A ∩ B). Ninguno de los dos = n(U) − n(A ∪ B)."
                ),
                "ejercicio_enunciado": (
                    "En Santo Tomás Rancagua se encuestó a 120 estudiantes de "
                    "informática: 70 saben Java, 50 saben Python y 30 saben ambos. "
                    "(a) ¿Cuántos saben solo Java? (b) ¿Solo Python? (c) ¿Ninguno de los "
                    "dos?"
                ),
                "ejercicio_desarrollo": (
                    "(a) Solo Java = n(J) − n(J ∩ P) = 70 − 30 = 40.\n"
                    "(b) Solo Python = n(P) − n(J ∩ P) = 50 − 30 = 20.\n"
                    "n(J ∪ P) = 70 + 50 − 30 = 90.\n"
                    "(c) Ninguno = n(U) − n(J ∪ P) = 120 − 90 = 30."
                ),
                "ejercicio_respuesta": (
                    "(a) 40 solo Java, (b) 20 solo Python, (c) 30 no saben ninguno. "
                    "Comprobación: 40 + 30 + 20 + 30 = 120."
                ),
                "venn": {
                    "etiquetas": ["Java", "Python"],
                    "cardinalidades": {"a": 70, "b": 50, "ab": 30},
                    "universo": 120,
                    "titulo": "Encuesta a 120 estudiantes de informática",
                },
                "fuente": "Clase 2 — Conjuntos 2026, problema 1 (láminas 25 y 26)",
            },
            {
                "concepto": "Cardinalidad del complemento",
                "pregunta": "¿Cómo se cuenta el complemento de un conjunto?",
                "definicion": (
                    "n(A′) = n(U) − n(A). Es la cuenta que responde a «cuántos NO "
                    "cumplen» una condición."
                ),
                "notacion": "n(A′) = n(U) − n(A)",
                "clave_memoria": (
                    "En los problemas de encuesta, «no usa ninguno» es el complemento de "
                    "la unión: n((A ∪ B)′) = n(U) − n(A ∪ B)."
                ),
                "ejercicio_enunciado": (
                    "En un curso de bases de datos, de 90 estudiantes: 40 saben SQL, 30 "
                    "MongoDB y 20 ambos. (a) ¿Cuántos saben al menos uno? (b) ¿Cuántos "
                    "solo SQL? (c) Si se escoge uno al azar, ¿cuál es la probabilidad de "
                    "que no sepa ninguno?"
                ),
                "ejercicio_desarrollo": (
                    "(a) n(S ∪ M) = 40 + 30 − 20 = 50.\n"
                    "(b) Solo SQL = 40 − 20 = 20.\n"
                    "Ninguno = 90 − 50 = 40.\n"
                    "(c) Probabilidad = 40/90 = 4/9 ≈ 0,444."
                ),
                "ejercicio_respuesta": (
                    "(a) 50 saben al menos uno, (b) 20 solo SQL, (c) 4/9 ≈ 44,4 %."
                ),
                "venn": {
                    "etiquetas": ["SQL", "MongoDB"],
                    "cardinalidades": {"a": 40, "b": 30, "ab": 20},
                    "universo": 90,
                    "titulo": "Curso de bases de datos (90 estudiantes)",
                },
                "fuente": "Clase 2 — Conjuntos 2026, problema 2 (láminas 28 y 29)",
            },
            {
                "concepto": "Exactamente uno de dos conjuntos",
                "pregunta": "¿Cómo se cuentan los que cumplen exactamente una condición?",
                "definicion": (
                    "Es la cardinalidad de la diferencia simétrica: "
                    "|A Δ B| = |A| + |B| − 2·|A ∩ B|. Se resta **dos veces** la "
                    "intersección: una por cada conjunto en que se contó."
                ),
                "notacion": "|A Δ B| = |A| + |B| − 2|A ∩ B|",
                "clave_memoria": (
                    "«Exactamente uno» resta dos veces la intersección; «al menos uno» "
                    "solo una."
                ),
                "ejercicio_enunciado": (
                    "En un taller de seguridad informática participaron 100 personas: 60 "
                    "manejan antivirus, 45 firewall y 25 ambos. (a) ¿Cuántas manejan "
                    "exactamente una herramienta? (b) ¿Cuántas ninguna? (c) ¿Cuántas al "
                    "menos una?"
                ),
                "ejercicio_desarrollo": (
                    "Solo antivirus = 60 − 25 = 35; solo firewall = 45 − 25 = 20.\n"
                    "(a) Exactamente una = 35 + 20 = 55. Con la fórmula: "
                    "60 + 45 − 2·25 = 55.\n"
                    "(c) Al menos una = n(A ∪ F) = 60 + 45 − 25 = 80.\n"
                    "(b) Ninguna = 100 − 80 = 20."
                ),
                "ejercicio_respuesta": (
                    "(a) 55 exactamente una, (b) 20 ninguna, (c) 80 al menos una."
                ),
                "venn": {
                    "etiquetas": ["Antivirus", "Firewall"],
                    "cardinalidades": {"a": 60, "b": 45, "ab": 25},
                    "universo": 100,
                    "titulo": "Taller de seguridad informática (100 personas)",
                },
                "fuente": "Clase 2 — Conjuntos 2026, problema 3 (láminas 31 y 32)",
            },
            {
                "concepto": "Inclusión-exclusión para tres conjuntos",
                "pregunta": "¿Cuál es la fórmula de n(A ∪ B ∪ C)?",
                "definicion": (
                    "n(A∪B∪C) = n(A) + n(B) + n(C) − n(A∩B) − n(A∩C) − n(B∩C) + n(A∩B∩C).\n"
                    "Al sumar los tres totales, las intersecciones dos a dos se cuentan "
                    "dos veces, así que se restan; pero los elementos de A∩B∩C se habían "
                    "contado tres veces y restado tres veces, de modo que hay que "
                    "volver a sumarlos."
                ),
                "notacion": "+ simples − dobles + triple",
                "clave_memoria": (
                    "Alterna los signos: +, −, +. Para rellenar el diagrama se empieza "
                    "**siempre por el centro** (A∩B∩C) y se va hacia afuera restando."
                ),
                "ejercicio_enunciado": (
                    "Encuesta a 200 personas sobre revistas: 120 leen A, 90 leen B, 70 "
                    "leen C, 50 leen A y B, 40 leen A y C, 30 leen B y C, 20 leen las "
                    "tres. (a) ¿Cuántas leen al menos una? (b) ¿Exactamente una? "
                    "(c) ¿Ninguna?"
                ),
                "ejercicio_desarrollo": (
                    "(a) n(A∪B∪C) = 120 + 90 + 70 − 50 − 40 − 30 + 20 = 180.\n"
                    "Centro: 20. Solo A y B = 50 − 20 = 30; solo A y C = 40 − 20 = 20; "
                    "solo B y C = 30 − 20 = 10.\n"
                    "Solo A = 120 − 30 − 20 − 20 = 50; solo B = 90 − 30 − 10 − 20 = 30; "
                    "solo C = 70 − 20 − 10 − 20 = 20.\n"
                    "(b) Exactamente una = 50 + 30 + 20 = 100.\n"
                    "(c) Ninguna = 200 − 180 = 20."
                ),
                "ejercicio_respuesta": (
                    "(a) 180 leen al menos una, (b) 100 leen exactamente una, (c) 20 no "
                    "leen ninguna. Comprobación: 50+30+20+30+20+10+20+20 = 200."
                ),
                "venn": {
                    "etiquetas": ["A", "B", "C"],
                    "cardinalidades": {
                        "a": 120, "b": 90, "c": 70,
                        "ab": 50, "ac": 40, "bc": 30, "abc": 20,
                    },
                    "universo": 200,
                    "titulo": "Preferencias de revistas (200 personas)",
                },
                "fuente": "Clase 2 — Conjuntos 2026, problema 8 (láminas 46 y 47)",
            },
            {
                "concepto": "«Solo uno» con tres conjuntos",
                "pregunta": "¿Cómo se calcula cuántos están en un solo conjunto de tres?",
                "definicion": (
                    "Solo A = n(A) − n(A∩B) − n(A∩C) + n(A∩B∩C). Se descuentan las dos "
                    "intersecciones y se devuelve el centro, que se había restado dos "
                    "veces."
                ),
                "notacion": "solo A = A − (A∩B) − (A∩C) + (A∩B∩C)",
                "clave_memoria": (
                    "El «+ centro» al final es lo que más se olvida; sin él, el resultado "
                    "sale corto."
                ),
                "ejercicio_enunciado": (
                    "Estudio con 150 ingenieros: 90 usan Git, 80 Docker, 70 Kubernetes; "
                    "50 Git y Docker, 40 Git y Kubernetes, 30 Docker y Kubernetes, 20 las "
                    "tres. (a) ¿Cuántos usan al menos una? (b) ¿Cuántos solo una? "
                    "(c) ¿Cuántos ninguna?"
                ),
                "ejercicio_desarrollo": (
                    "(a) n(G∪D∪K) = 90 + 80 + 70 − 50 − 40 − 30 + 20 = 140.\n"
                    "Solo Git = 90 − 50 − 40 + 20 = 20.\n"
                    "Solo Docker = 80 − 50 − 30 + 20 = 20.\n"
                    "Solo Kubernetes = 70 − 40 − 30 + 20 = 20.\n"
                    "(b) Total solo una = 20 + 20 + 20 = 60.\n"
                    "(c) Ninguna = 150 − 140 = 10."
                ),
                "ejercicio_respuesta": (
                    "(a) 140 usan al menos una, (b) 60 usan solo una, (c) 10 no usan "
                    "ninguna."
                ),
                "venn": {
                    "etiquetas": ["Git", "Docker", "Kubernetes"],
                    "cardinalidades": {
                        "a": 90, "b": 80, "c": 70,
                        "ab": 50, "ac": 40, "bc": 30, "abc": 20,
                    },
                    "universo": 150,
                    "titulo": "Herramientas usadas por 150 ingenieros",
                },
                "fuente": "Clase 2 — Conjuntos 2026, problema 11 (láminas 57 a 59)",
            },
            {
                "concepto": "Universo desconocido en un problema de Venn",
                "pregunta": "¿Cómo se halla el total cuando el enunciado no lo da?",
                "definicion": (
                    "Se calcula n(A∪B∪C) con inclusión-exclusión y se le suma la cantidad "
                    "que no pertenece a ningún conjunto: n(U) = n(A∪B∪C) + n((A∪B∪C)′)."
                ),
                "notacion": "n(U) = n(A∪B∪C) + «ninguno»",
                "clave_memoria": (
                    "Cuando el enunciado da «ninguna de las tres», el total es un "
                    "resultado, no un dato."
                ),
                "ejercicio_enunciado": (
                    "Panadería de Rancagua, consumo de marraqueta (M), hallulla (H) y "
                    "dobladas (D): M = 109, H = 203, D = 162, M∩H = 25, H∩D = 41, "
                    "D∩M = 28, M∩H∩D = 5, y 115 no consumen ninguna. (a) ¿Cuántas "
                    "personas se consultaron? (b) ¿Cuántas consumen solo marraqueta? "
                    "(c) ¿Cuántas consumen al menos dos tipos de pan?"
                ),
                "ejercicio_desarrollo": (
                    "(a) n(M∪H∪D) = 109 + 203 + 162 − 25 − 41 − 28 + 5 = 385.\n"
                    "Total = 385 + 115 = 500.\n"
                    "(b) Solo M = 109 − 25 − 28 + 5 = 61.\n"
                    "(c) Solo M y H = 25 − 5 = 20; solo H y D = 41 − 5 = 36; solo D y M = "
                    "28 − 5 = 23.\n"
                    "Al menos dos = 20 + 36 + 23 + 5 = 84."
                ),
                "ejercicio_respuesta": (
                    "(a) 500 personas consultadas, (b) 61 consumen solo marraqueta, "
                    "(c) 84 consumen al menos dos tipos."
                ),
                "venn": {
                    "etiquetas": ["Marraqueta", "Hallulla", "Dobladas"],
                    "cardinalidades": {
                        "a": 109, "b": 203, "c": 162,
                        "ab": 25, "ac": 28, "bc": 41, "abc": 5,
                    },
                    "universo": 500,
                    "titulo": "Consumo de pan en Rancagua (500 personas)",
                },
                "fuente": "Clase 2 — Conjuntos 2026, práctica 1 (láminas 60 a 62)",
            },
        ],
    },
]
