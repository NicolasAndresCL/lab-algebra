"""Tarjetas de la unidad de lógica proposicional.

Fuente: «Clases 1 y 2 — Lógica ST 2026», «Clase 3 — Lógica», la Tarea-Taller 1 y
el Test Acumulativo N.º 1 de la asignatura.

Cada tarjeta lleva un **ejercicio resuelto**: enunciado, desarrollo paso a paso
y respuesta. Las que declaran `formula` muestran además su tabla de verdad
calculada en vivo por el motor, de modo que el desarrollo escrito y el cálculo
del programa se contrastan solos.
"""

from __future__ import annotations

MAZOS_LOGICA: list[dict] = [
    {
        "slug": "logica-fundamentos",
        "nombre": "Lógica proposicional — fundamentos",
        "unidad": "Lógica",
        "orden": 10,
        "descripcion": (
            "Qué es una proposición, qué no lo es y cómo se clasifican. "
            "La base sobre la que se apoya todo lo demás de la unidad."
        ),
        "tarjetas": [
            {
                "concepto": "Lógica proposicional",
                "pregunta": "¿Qué estudia la lógica proposicional y para qué sirve?",
                "definicion": (
                    "Es la parte de la lógica clásica que estudia las proposiciones: frases "
                    "que son verdaderas o falsas, pero no ambas a la vez. Analiza cómo se "
                    "combinan y cómo se determina el valor de verdad de una expresión "
                    "compleja a partir del de sus partes."
                ),
                "clave_memoria": (
                    "Enseña a construir argumentos sólidos y a detectar los incorrectos. "
                    "En matemáticas es la columna vertebral de las demostraciones."
                ),
                "ejercicio_enunciado": (
                    "Clasifica cada frase como proposición o como expresión no "
                    "proposicional: (1) «El sol es una estrella», (2) «¿Cuántos años "
                    "tienes?», (3) «x + 5 = 10», (4) «La raíz cuadrada de 169 es 12»."
                ),
                "ejercicio_desarrollo": (
                    "1. «El sol es una estrella» → se puede decidir: es verdadera. "
                    "Es proposición.\n"
                    "2. «¿Cuántos años tienes?» → es una pregunta; no afirma nada que "
                    "pueda ser V o F. No es proposición.\n"
                    "3. «x + 5 = 10» → su valor depende de x: es una ecuación abierta. "
                    "No es proposición.\n"
                    "4. «La raíz cuadrada de 169 es 12» → se puede decidir: √169 = 13, "
                    "luego es falsa. Es proposición (falsa, pero proposición)."
                ),
                "ejercicio_respuesta": (
                    "Proposiciones: (1) verdadera y (4) falsa. No proposicionales: "
                    "(2) pregunta y (3) ecuación abierta."
                ),
                "fuente": "Clases 1 y 2 — Lógica ST 2026, láminas 5 a 10",
            },
            {
                "concepto": "Proposición",
                "pregunta": "¿Qué es una proposición y cómo se denota?",
                "definicion": (
                    "Una frase sobre la cual se puede decidir unívocamente si es verdadera "
                    "(V) o falsa (F), sin que existan ambas posibilidades a la vez. Se "
                    "denotan con letras minúsculas: p, q, r, s, t."
                ),
                "notacion": "p, q, r… con valor de verdad V o F",
                "clave_memoria": (
                    "La prueba es siempre la misma: ¿puedo responder «esto es verdad» o "
                    "«esto es mentira»? Si no puedo, no es proposición."
                ),
                "ejercicio_enunciado": (
                    "El test de la asignatura define: p = «el código supera las pruebas», "
                    "q = «la base de datos es compatible». En una evaluación se observó "
                    "p = V y q = F. ¿Cuál es el valor de la conjunción «el código supera "
                    "las pruebas y la base de datos es compatible»?"
                ),
                "ejercicio_desarrollo": (
                    "La frase une dos proposiciones con «y», luego es p ∧ q.\n"
                    "La conjunción solo es verdadera si ambas lo son.\n"
                    "Con p = V y q = F: V ∧ F ≡ F."
                ),
                "ejercicio_respuesta": "V ∧ F ≡ F (la alternativa correcta es «c»).",
                "formula": "p ∧ q",
                "fuente": "Test Acumulativo N.º 1, ítem I pregunta 2",
            },
            {
                "concepto": "Expresión no proposicional",
                "pregunta": "¿Qué tipos de frases NO son proposiciones?",
                "definicion": (
                    "Las que no tienen un valor de verdad definido: preguntas, órdenes, "
                    "exclamaciones, deseos, saludos, frases incompletas, opiniones "
                    "subjetivas y ecuaciones abiertas (su verdad depende de una variable)."
                ),
                "clave_memoria": (
                    "Regla práctica: si la frase termina en «?» o «!», o si contiene una "
                    "incógnita libre, casi seguro que no es proposición."
                ),
                "ejercicio_enunciado": (
                    "De la lista, indica cuáles NO son proposiciones y por qué: "
                    "«¡Qué bonito día!», «Chile está en América del Sur», «¡Cierra la "
                    "puerta!», «La belleza es subjetiva», «2 + 2 = 4»."
                ),
                "ejercicio_desarrollo": (
                    "«¡Qué bonito día!» → exclamación, no afirma nada decidible.\n"
                    "«Chile está en América del Sur» → proposición verdadera.\n"
                    "«¡Cierra la puerta!» → orden.\n"
                    "«La belleza es subjetiva» → opinión, no afirmación objetiva.\n"
                    "«2 + 2 = 4» → proposición verdadera."
                ),
                "ejercicio_respuesta": (
                    "No son proposiciones: «¡Qué bonito día!» (exclamación), «¡Cierra la "
                    "puerta!» (orden) y «La belleza es subjetiva» (opinión)."
                ),
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 10",
            },
            {
                "concepto": "Principio del tercero excluido",
                "pregunta": "¿Qué afirma el principio del tercero excluido?",
                "definicion": (
                    "Toda proposición es verdadera o es falsa; no hay una tercera "
                    "posibilidad, y no puede ser ambas a la vez. Formalmente: p ∨ ¬p es "
                    "siempre verdadera."
                ),
                "notacion": "p ∨ ¬p ≡ V (tautología)",
                "clave_memoria": "«Llueva o no llueva» — una de las dos ocurre, seguro.",
                "ejercicio_enunciado": "Construye la tabla de verdad de p ∨ ¬p y clasifícala.",
                "ejercicio_desarrollo": (
                    "Hay 1 variable, luego 2¹ = 2 filas.\n"
                    "Fila 1: p = V → ¬p = F → V ∨ F = V.\n"
                    "Fila 2: p = F → ¬p = V → F ∨ V = V.\n"
                    "La columna final tiene solo V."
                ),
                "ejercicio_respuesta": (
                    "p ∨ ¬p es una **tautología**. Ojo: son 2 filas, no 4, porque solo "
                    "hay una variable."
                ),
                "formula": "p ∨ ¬p",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 25",
            },
            {
                "concepto": "Principio de no contradicción",
                "pregunta": "¿Qué afirma el principio de no contradicción?",
                "definicion": (
                    "Una proposición no puede ser verdadera y falsa al mismo tiempo. "
                    "Formalmente: p ∧ ¬p es siempre falsa."
                ),
                "notacion": "p ∧ ¬p ≡ F (contradicción)",
                "clave_memoria": "«El pasto es verde y el pasto no es verde»: imposible.",
                "ejercicio_enunciado": "Construye la tabla de verdad de p ∧ ¬p y clasifícala.",
                "ejercicio_desarrollo": (
                    "1 variable → 2 filas.\n"
                    "p = V → ¬p = F → V ∧ F = F.\n"
                    "p = F → ¬p = V → F ∧ V = F.\n"
                    "Todos los resultados son F."
                ),
                "ejercicio_respuesta": "p ∧ ¬p es una **contradicción**.",
                "formula": "p ∧ ¬p",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 29",
            },
            {
                "concepto": "Proposición simple o atómica",
                "pregunta": "¿Qué es una proposición simple?",
                "definicion": (
                    "La que no se puede dividir en otras proposiciones. Es la unidad "
                    "básica de la lógica: una sola afirmación, sin conectivos."
                ),
                "clave_memoria": "Una afirmación, cero conectivos.",
                "ejercicio_enunciado": (
                    "¿Cuáles de estas son simples? (a) «El número 5 es primo», "
                    "(b) «El sol es una estrella y la luna es un satélite», "
                    "(c) «La Luna es el satélite de la Tierra»."
                ),
                "ejercicio_desarrollo": (
                    "(a) Una sola afirmación sobre el 5 → simple.\n"
                    "(b) Une dos afirmaciones con «y» → compuesta (p ∧ q).\n"
                    "(c) Una sola afirmación sobre la Luna → simple."
                ),
                "ejercicio_respuesta": "Simples: (a) y (c). Compuesta: (b).",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 11",
            },
            {
                "concepto": "Proposición compuesta o molecular",
                "pregunta": "¿Qué es una proposición compuesta?",
                "definicion": (
                    "La que se forma uniendo dos o más proposiciones simples mediante "
                    "conectivos lógicos (no, y, o, si… entonces, si y solo si)."
                ),
                "clave_memoria": (
                    "Busca las palabras clave: «y», «o», «si… entonces», «si y solo si», "
                    "«no». Donde hay una, hay una proposición compuesta."
                ),
                "ejercicio_enunciado": (
                    "Traduce a símbolos, con p = «los equipos poseen antivirus "
                    "actualizado», r = «el ambiente tiene fuente de energía compatible» y "
                    "t = «el ambiente cumple las normas de calidad»: «si los equipos "
                    "poseen antivirus actualizado o el ambiente tiene fuente de energía "
                    "compatible, entonces el ambiente cumple las normas»."
                ),
                "ejercicio_desarrollo": (
                    "«o» une p con r → (p ∨ r).\n"
                    "«si…, entonces…» convierte esa disyunción en antecedente y a t en "
                    "consecuente → (p ∨ r) → t.\n"
                    "El paréntesis es obligatorio: sin él, p ∨ r → t se leería como "
                    "p ∨ (r → t), que no dice lo mismo."
                ),
                "ejercicio_respuesta": "(p ∨ r) ⇒ t (alternativa «a» del taller).",
                "formula": "(p ∨ r) → t",
                "fuente": "Tarea-Taller 1, ítem I pregunta 1",
            },
        ],
    },
    {
        "slug": "conectivos-logicos",
        "nombre": "Conectivos lógicos",
        "unidad": "Lógica",
        "orden": 20,
        "descripcion": (
            "Los cinco conectivos de la asignatura, con su tabla de verdad, cómo se "
            "leen en lenguaje natural y el caso en que cada uno falla."
        ),
        "tarjetas": [
            {
                "concepto": "Negación (¬)",
                "pregunta": "¿Cómo funciona la negación y cuántas proposiciones afecta?",
                "definicion": (
                    "Único conectivo unario: actúa sobre una sola proposición e invierte "
                    "su valor de verdad. Si p es V, ¬p es F, y al revés. Se lee «no», "
                    "«no es cierto que», «es falso que»."
                ),
                "notacion": "¬p  (también ~p)",
                "clave_memoria": "Interruptor: da vuelta el valor, siempre.",
                "ejercicio_enunciado": (
                    "Sea p: «5 > 10». Determina el valor de p y de ¬p, y escribe ¬p en "
                    "lenguaje natural."
                ),
                "ejercicio_desarrollo": (
                    "5 no es mayor que 10, luego p = F.\n"
                    "La negación invierte: ¬p = V.\n"
                    "En palabras: «no es cierto que 5 > 10»."
                ),
                "ejercicio_respuesta": "p = F y ¬p = V: «no es cierto que 5 > 10».",
                "formula": "¬p",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 14",
            },
            {
                "concepto": "Conjunción (∧)",
                "pregunta": "¿Cuándo es verdadera una conjunción?",
                "definicion": (
                    "Une dos proposiciones y es verdadera **solo si ambas** son verdaderas "
                    "al mismo tiempo. En cualquier otro caso es falsa. Se lee «y», "
                    "«pero», «además»."
                ),
                "notacion": "p ∧ q",
                "clave_memoria": "La más exigente: un solo F la hunde.",
                "ejercicio_enunciado": (
                    "p: «la raíz cuadrada de 4 es 2» (V); q: «2 + 2 = 5» (F). "
                    "Determina el valor de p ∧ q."
                ),
                "ejercicio_desarrollo": (
                    "p = V porque √4 = 2.\n"
                    "q = F porque 2 + 2 = 4, no 5.\n"
                    "La conjunción exige que ambas sean V; una es F."
                ),
                "ejercicio_respuesta": "p ∧ q = F.",
                "formula": "p ∧ q",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 15",
            },
            {
                "concepto": "Disyunción inclusiva (∨)",
                "pregunta": "¿Cuándo es falsa una disyunción inclusiva?",
                "definicion": (
                    "Es verdadera si **al menos una** de las proposiciones es verdadera; "
                    "solo es falsa cuando ambas son falsas. Es inclusiva: admite que las "
                    "dos sean verdaderas. Se lee «o»."
                ),
                "notacion": "p ∨ q",
                "clave_memoria": (
                    "La más permisiva: solo el caso F∨F da F. Inclusiva = «o ambas»."
                ),
                "ejercicio_enunciado": (
                    "El test pregunta cuál es la tabla de verdad correcta de r ∨ s. "
                    "Constrúyela y descarta la opción que pone V en la última fila."
                ),
                "ejercicio_desarrollo": (
                    "2 variables → 2² = 4 filas, con V primero.\n"
                    "r = V, s = V → V.\n"
                    "r = V, s = F → V (basta con una).\n"
                    "r = F, s = V → V.\n"
                    "r = F, s = F → F (única fila falsa).\n"
                    "Cualquier alternativa con F en las tres primeras filas o V en la "
                    "última está mal."
                ),
                "ejercicio_respuesta": "La tabla correcta es V, V, V, F (alternativa «a»).",
                "formula": "r ∨ s",
                "fuente": "Test Acumulativo N.º 1, ítem I pregunta 3",
            },
            {
                "concepto": "Disyunción exclusiva (⊻)",
                "pregunta": "¿En qué se diferencia la disyunción exclusiva de la inclusiva?",
                "definicion": (
                    "Es verdadera cuando **exactamente una** de las dos proposiciones es "
                    "verdadera. Si ambas son verdaderas, es falsa. Se lee «o…, o…, "
                    "pero no ambas»."
                ),
                "notacion": "p ⊻ q  (equivale a ¬(p ↔ q))",
                "clave_memoria": (
                    "«O café o té» en un menú: puedes elegir uno, no los dos. Es la "
                    "negación del bicondicional."
                ),
                "ejercicio_enunciado": (
                    "Comprueba con una tabla de verdad que p ⊻ q equivale a ¬(p ↔ q)."
                ),
                "ejercicio_desarrollo": (
                    "p ⊻ q: V⊻V = F, V⊻F = V, F⊻V = V, F⊻F = F.\n"
                    "p ↔ q: V, F, F, V → su negación: F, V, V, F.\n"
                    "Las dos columnas coinciden fila a fila."
                ),
                "ejercicio_respuesta": (
                    "Coinciden: p ⊻ q ≡ ¬(p ↔ q). El bicondicional entre ambas es una "
                    "tautología."
                ),
                "formula": "(p ⊻ q) ↔ ¬(p ↔ q)",
                "fuente": "Cuaderno de clase 10-08-26 (tablas de los conectivos)",
            },
            {
                "concepto": "Condicional (→)",
                "pregunta": "¿En qué único caso es falso un condicional?",
                "definicion": (
                    "Establece una relación de causa y efecto. Es falso **solo** cuando el "
                    "antecedente es verdadero y el consecuente es falso (V → F). En "
                    "cualquier otro caso es verdadero. Se lee «si…, entonces…», "
                    "«implica», «solo si», «cuando»."
                ),
                "notacion": "p → q  (p antecedente, q consecuente)",
                "clave_memoria": (
                    "La promesa: solo se rompe si prometiste (V) y no cumpliste (F). "
                    "Si nunca prometiste, no mentiste."
                ),
                "ejercicio_enunciado": (
                    "El test pide la tabla de q ⇒ t («si la base de datos es compatible, "
                    "entonces el despliegue es aprobado»). Constrúyela e identifica la "
                    "única fila falsa."
                ),
                "ejercicio_desarrollo": (
                    "2 variables → 4 filas.\n"
                    "q = V, t = V → V.\n"
                    "q = V, t = F → **F** (prometió y no cumplió).\n"
                    "q = F, t = V → V.\n"
                    "q = F, t = F → V."
                ),
                "ejercicio_respuesta": (
                    "La tabla es V, F, V, V; la única fila falsa es V ⇒ F."
                ),
                "formula": "q → t",
                "fuente": "Test Acumulativo N.º 1, ítem I pregunta 5",
            },
            {
                "concepto": "Bicondicional (↔)",
                "pregunta": "¿Cuándo es verdadero un bicondicional?",
                "definicion": (
                    "Establece equivalencia: es verdadero cuando **ambas proposiciones "
                    "tienen el mismo valor de verdad** (las dos V o las dos F), y falso "
                    "cuando difieren. Se lee «si y solo si», «cuando y solo cuando», "
                    "«es condición necesaria y suficiente»."
                ),
                "notacion": "p ↔ q",
                "clave_memoria": "«Iguales → V, distintos → F». Es un detector de igualdad.",
                "ejercicio_enunciado": (
                    "Criterio de evaluación: (q ∧ s) ⇔ t. Se observó q = V (base "
                    "compatible), s = F (sin backup) y t = V (despliegue aprobado). "
                    "¿Cuál es el valor final?"
                ),
                "ejercicio_desarrollo": (
                    "Primero el paréntesis: q ∧ s = V ∧ F = F.\n"
                    "Ahora el bicondicional: F ⇔ V.\n"
                    "Los valores son distintos, luego el resultado es F."
                ),
                "ejercicio_respuesta": "(V ∧ F) ⇔ V ≡ F (alternativa «d»).",
                "formula": "(q ∧ s) ↔ t",
                "fuente": "Test Acumulativo N.º 1, ítem I pregunta 4",
            },
            {
                "concepto": "Traducción del lenguaje natural",
                "pregunta": "¿Cómo se pasa de una frase en español a una fórmula lógica?",
                "definicion": (
                    "Se identifican las proposiciones simples y se les asigna una letra; "
                    "se localizan las palabras clave («no», «y», «o», «si… entonces», "
                    "«si y solo si») y se traducen a conectivos; se añaden paréntesis "
                    "para respetar el orden que exige la frase."
                ),
                "clave_memoria": (
                    "El error típico está en el alcance de la negación: «no p y q» "
                    "(¬p ∧ q) no es lo mismo que «no (p y q)» (¬(p ∧ q))."
                ),
                "ejercicio_enunciado": (
                    "Traduce «el código no supera las pruebas y la base de datos es "
                    "compatible», con p = «el código supera las pruebas» y q = «la base "
                    "de datos es compatible». Descarta las alternativas ¬p ∨ q, "
                    "¬(p ∧ q) y p ∧ ¬q."
                ),
                "ejercicio_desarrollo": (
                    "«El código NO supera las pruebas» niega solo a p → ¬p.\n"
                    "«y» une esa negación con q → ¬p ∧ q.\n"
                    "¬p ∨ q usa «o», no «y».\n"
                    "¬(p ∧ q) niega la frase entera, no solo la primera parte.\n"
                    "p ∧ ¬q niega la proposición equivocada."
                ),
                "ejercicio_respuesta": "¬p ∧ q (alternativa «b»).",
                "formula": "¬p ∧ q",
                "fuente": "Test Acumulativo N.º 1, ítem I pregunta 6",
            },
            {
                "concepto": "Lectura del condicional negado",
                "pregunta": "¿Cómo se lee en lenguaje natural ¬s → ¬r?",
                "definicion": (
                    "El antecedente es la negación de s y el consecuente la negación de r: "
                    "«si no s, entonces no r». El orden importa: ¬s → ¬r no es lo mismo "
                    "que ¬r → ¬s (esa es su recíproca)."
                ),
                "notacion": "¬s → ¬r",
                "clave_memoria": (
                    "Lee de izquierda a derecha: primero el «si» (antecedente), después "
                    "el «entonces» (consecuente). No los intercambies."
                ),
                "ejercicio_enunciado": (
                    "Con r = «el servidor tiene recursos» y s = «se generó el backup», "
                    "¿qué enunciado corresponde a ¬s ⇒ ¬r?"
                ),
                "ejercicio_desarrollo": (
                    "¬s = «no se generó el backup» → va tras el «si».\n"
                    "¬r = «el servidor no tiene recursos» → va tras el «entonces».\n"
                    "«Si el servidor no tiene recursos, entonces no se generó el backup» "
                    "sería ¬r ⇒ ¬s: invierte los papeles."
                ),
                "ejercicio_respuesta": (
                    "«Si no se generó el backup, entonces el servidor no tiene recursos» "
                    "(alternativa «c»)."
                ),
                "formula": "¬s → ¬r",
                "fuente": "Test Acumulativo N.º 1, ítem I pregunta 7",
            },
        ],
    },
    {
        "slug": "tablas-verdad",
        "nombre": "Tablas de verdad y clasificación",
        "unidad": "Lógica",
        "orden": 30,
        "descripcion": (
            "Cómo se arma una tabla (filas y columnas), cómo se clasifica el resultado "
            "y las equivalencias que más se preguntan."
        ),
        "tarjetas": [
            {
                "concepto": "Número de filas de una tabla de verdad",
                "pregunta": "¿Cuántas filas tiene la tabla de verdad de una fórmula?",
                "definicion": (
                    "2ⁿ filas, donde n es el número de proposiciones simples **distintas** "
                    "que aparecen en la fórmula. Cada proposición admite dos valores, así "
                    "que las combinaciones se duplican con cada letra nueva."
                ),
                "notacion": "filas = 2ⁿ",
                "clave_memoria": (
                    "1 letra → 2 filas, 2 → 4, 3 → 8, 4 → 16. Se cuentan letras "
                    "**distintas**, no apariciones: en p ∧ (p ∨ q) hay 2 letras, no 3."
                ),
                "ejercicio_enunciado": (
                    "¿Cuántas filas tienen las tablas de (a) p ↔ ¬p, (b) (p ∨ r) ⇒ "
                    "(p ∧ ¬s) y (c) (p ∧ q) ⇒ (r ∨ ¬s)?"
                ),
                "ejercicio_desarrollo": (
                    "(a) Letras distintas: solo p → n = 1 → 2¹ = 2 filas.\n"
                    "(b) Letras distintas: p, r, s → n = 3 → 2³ = 8 filas.\n"
                    "(c) Letras distintas: p, q, r, s → n = 4 → 2⁴ = 16 filas."
                ),
                "ejercicio_respuesta": (
                    "(a) 2 filas, (b) 8 filas, (c) 16 filas. Error frecuente: dar 4 filas "
                    "en (a) por costumbre; con una sola variable, la mitad de esas filas "
                    "estarían repetidas."
                ),
                "formula": "p ↔ ¬p",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 19",
            },
            {
                "concepto": "Número de columnas de una tabla de verdad",
                "pregunta": "¿Cómo se decide cuántas columnas lleva la tabla?",
                "definicion": (
                    "Una columna por cada letra distinta, más una por cada resultado "
                    "intermedio que haga falta calcular: los paréntesis internos primero, "
                    "después los externos, y al final la fórmula completa."
                ),
                "notacion": "columnas = n (variables) + m (subfórmulas)",
                "clave_memoria": (
                    "No se cuentan conectores al azar: se cuenta cada paso que necesitas "
                    "escribir para no equivocarte."
                ),
                "ejercicio_enunciado": "¿Qué columnas lleva la tabla de ¬(p ∨ q)?",
                "ejercicio_desarrollo": (
                    "Letras distintas: p y q → 2 columnas.\n"
                    "Paréntesis interno: p ∨ q → 1 columna intermedia.\n"
                    "Negación de todo: ¬(p ∨ q) → 1 columna final."
                ),
                "ejercicio_respuesta": (
                    "4 columnas: p, q, p ∨ q, ¬(p ∨ q). Resultado final: F, F, F, V."
                ),
                "formula": "¬(p ∨ q)",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, láminas 20 y 22",
            },
            {
                "concepto": "Tautología",
                "pregunta": "¿Qué es una tautología?",
                "definicion": (
                    "Una proposición compuesta **siempre verdadera**, sin importar los "
                    "valores de sus proposiciones simples: la columna final es toda V. "
                    "Es una verdad lógica que se sostiene por su propia estructura."
                ),
                "notacion": "columna final: todo V",
                "clave_memoria": "«A prueba de fallas»: da igual lo que valgan las piezas.",
                "ejercicio_enunciado": "Clasifica (p ∧ q) → p construyendo su tabla.",
                "ejercicio_desarrollo": (
                    "2 variables → 4 filas.\n"
                    "V,V: p∧q = V → V → V = V.\n"
                    "V,F: p∧q = F → F → V = V.\n"
                    "F,V: p∧q = F → F → F = V.\n"
                    "F,F: p∧q = F → F → F = V.\n"
                    "La columna final es V, V, V, V."
                ),
                "ejercicio_respuesta": (
                    "Es una **tautología**: si «p y q» es verdad, p tiene que serlo."
                ),
                "formula": "(p ∧ q) → p",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 26",
            },
            {
                "concepto": "Contradicción",
                "pregunta": "¿Qué es una contradicción?",
                "definicion": (
                    "Una proposición compuesta **siempre falsa**, sin importar los valores "
                    "de sus proposiciones simples: la columna final es toda F. Se anula a "
                    "sí misma."
                ),
                "notacion": "columna final: todo F",
                "clave_memoria": "Afirma algo y su negación al mismo tiempo.",
                "ejercicio_enunciado": "Clasifica (p ∧ q) ∧ (¬p ∨ ¬q).",
                "ejercicio_desarrollo": (
                    "Por De Morgan, ¬p ∨ ¬q es exactamente ¬(p ∧ q).\n"
                    "La fórmula queda como «X y no X», con X = p ∧ q.\n"
                    "V,V: (V) ∧ (F) = F.\n"
                    "V,F: (F) ∧ (V) = F.\n"
                    "F,V: (F) ∧ (V) = F.\n"
                    "F,F: (F) ∧ (V) = F."
                ),
                "ejercicio_respuesta": (
                    "Es una **contradicción**: afirma p ∧ q y su negación a la vez."
                ),
                "formula": "(p ∧ q) ∧ (¬p ∨ ¬q)",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 31",
            },
            {
                "concepto": "Contingencia",
                "pregunta": "¿Qué es una contingencia?",
                "definicion": (
                    "Una proposición compuesta cuyo valor **depende** de los valores de "
                    "sus proposiciones simples: la columna final tiene al menos un V y al "
                    "menos un F. Es el caso más común."
                ),
                "notacion": "columna final: mezcla de V y F",
                "clave_memoria": (
                    "Ni verdad universal ni falsedad absoluta: «el examen es difícil o no "
                    "estudié»."
                ),
                "ejercicio_enunciado": "Clasifica (p ∨ q) ∧ ¬p.",
                "ejercicio_desarrollo": (
                    "V,V: (V) ∧ F = F.\n"
                    "V,F: (V) ∧ F = F.\n"
                    "F,V: (V) ∧ V = V.\n"
                    "F,F: (F) ∧ V = F.\n"
                    "La columna final es F, F, V, F: hay V y hay F."
                ),
                "ejercicio_respuesta": (
                    "Es una **contingencia**. Solo es verdadera cuando p es falsa y q "
                    "verdadera (silogismo disyuntivo)."
                ),
                "formula": "(p ∨ q) ∧ ¬p",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 34",
            },
            {
                "concepto": "Ley de De Morgan (lógica)",
                "pregunta": "¿Cómo se niega una conjunción y cómo una disyunción?",
                "definicion": (
                    "Negar una conjunción equivale a la disyunción de las negaciones, y "
                    "negar una disyunción equivale a la conjunción de las negaciones: "
                    "¬(p ∧ q) ≡ ¬p ∨ ¬q  y  ¬(p ∨ q) ≡ ¬p ∧ ¬q."
                ),
                "notacion": "¬(p ∧ q) ↔ (¬p ∨ ¬q)",
                "clave_memoria": (
                    "«Entra la negación y el conectivo se da vuelta»: ∧ pasa a ∨ y ∨ pasa "
                    "a ∧."
                ),
                "ejercicio_enunciado": (
                    "Verifica con tabla de verdad que ¬(p ∧ q) ↔ (¬p ∨ ¬q) es una "
                    "tautología."
                ),
                "ejercicio_desarrollo": (
                    "V,V: p∧q = V → ¬(p∧q) = F; ¬p∨¬q = F∨F = F; F ↔ F = V.\n"
                    "V,F: p∧q = F → ¬(p∧q) = V; ¬p∨¬q = F∨V = V; V ↔ V = V.\n"
                    "F,V: p∧q = F → ¬(p∧q) = V; ¬p∨¬q = V∨F = V; V ↔ V = V.\n"
                    "F,F: p∧q = F → ¬(p∧q) = V; ¬p∨¬q = V∨V = V; V ↔ V = V."
                ),
                "ejercicio_respuesta": (
                    "La columna final es toda V: es una **tautología**, luego las dos "
                    "expresiones son lógicamente equivalentes."
                ),
                "formula": "¬(p ∧ q) ↔ (¬p ∨ ¬q)",
                "fuente": "Clase 3 — Lógica, lámina 3; Taller de 10 proposiciones, n.º 4",
            },
            {
                "concepto": "Modus ponens",
                "pregunta": "¿Qué dice la regla de inferencia modus ponens?",
                "definicion": (
                    "Si «p implica q» es verdadero y p es verdadero, entonces q debe ser "
                    "verdadero. Formalmente, [(p → q) ∧ p] → q es una tautología."
                ),
                "notacion": "[(p → q) ∧ p] → q",
                "clave_memoria": (
                    "«Si llueve, la calle se moja. Y hoy llueve. Luego la calle se moja.»"
                ),
                "ejercicio_enunciado": (
                    "Construye la tabla de [(p → q) ∧ p] → q y clasifícala."
                ),
                "ejercicio_desarrollo": (
                    "V,V: p→q = V; (p→q)∧p = V; V → V = V.\n"
                    "V,F: p→q = F; (p→q)∧p = F; F → F = V.\n"
                    "F,V: p→q = V; (p→q)∧p = F; F → V = V.\n"
                    "F,F: p→q = V; (p→q)∧p = F; F → F = V."
                ),
                "ejercicio_respuesta": (
                    "Es una **tautología**: una de las reglas de inferencia más usadas."
                ),
                "formula": "((p → q) ∧ p) → q",
                "fuente": "Clases 1 y 2 — Lógica ST 2026, lámina 27",
            },
            {
                "concepto": "Negación de un condicional",
                "pregunta": "¿A qué equivale ¬(p → q)?",
                "definicion": (
                    "A p ∧ ¬q: un condicional solo falla cuando el antecedente es "
                    "verdadero y el consecuente falso, así que negarlo es afirmar "
                    "exactamente ese caso."
                ),
                "notacion": "¬(p → q) ↔ (p ∧ ¬q)",
                "clave_memoria": (
                    "Negar una promesa = «prometí y no cumplí». No aparece ningún «o»."
                ),
                "ejercicio_enunciado": (
                    "Comprueba que ¬(p → q) ↔ (p ∧ ¬q) es una tautología (proposición "
                    "n.º 9 del taller de clasificación)."
                ),
                "ejercicio_desarrollo": (
                    "V,V: p→q = V → ¬(p→q) = F; p∧¬q = V∧F = F; F ↔ F = V.\n"
                    "V,F: p→q = F → ¬(p→q) = V; p∧¬q = V∧V = V; V ↔ V = V.\n"
                    "F,V: p→q = V → ¬(p→q) = F; p∧¬q = F∧F = F; F ↔ F = V.\n"
                    "F,F: p→q = V → ¬(p→q) = F; p∧¬q = F∧V = F; F ↔ F = V."
                ),
                "ejercicio_respuesta": "Tautología: las dos expresiones son equivalentes.",
                "formula": "¬(p → q) ↔ (p ∧ ¬q)",
                "fuente": "Clase 3 — Lógica, taller de 10 proposiciones, n.º 9",
            },
            {
                "concepto": "Silogismo disyuntivo",
                "pregunta": "¿Qué permite concluir [(p ∨ q) ∧ ¬p]?",
                "definicion": (
                    "Si se sabe que «p o q» es verdadero y que p es falso, entonces q "
                    "tiene que ser verdadero. Formalmente, [(p ∨ q) ∧ ¬p] → q es una "
                    "tautología."
                ),
                "notacion": "[(p ∨ q) ∧ ¬p] → q",
                "clave_memoria": (
                    "«Está en la mochila o en la mesa. No está en la mochila. Luego está "
                    "en la mesa.»"
                ),
                "ejercicio_enunciado": "Clasifica [(p ∨ q) ∧ ¬p] → q.",
                "ejercicio_desarrollo": (
                    "V,V: (V)∧F = F → F → V = V.\n"
                    "V,F: (V)∧F = F → F → F = V.\n"
                    "F,V: (V)∧V = V → V → V = V.\n"
                    "F,F: (F)∧V = F → F → F = V."
                ),
                "ejercicio_respuesta": "**Tautología**: es una regla de inferencia válida.",
                "formula": "((p ∨ q) ∧ ¬p) → q",
                "fuente": "Clase 3 — Lógica, taller de 10 proposiciones, n.º 7",
            },
            {
                "concepto": "Evaluación con valores asignados",
                "pregunta": "¿Cómo se evalúa una fórmula si ya conoces todos los valores?",
                "definicion": (
                    "No hace falta la tabla completa: se sustituye cada letra por su valor "
                    "y se resuelve de dentro hacia fuera, respetando los paréntesis y la "
                    "precedencia (¬ antes que ∧, ∧ antes que ∨, y estos antes que → y ↔)."
                ),
                "clave_memoria": (
                    "Una sola fila de la tabla. Escribe los pasos intermedios: el error "
                    "casi siempre aparece al resolver el paréntesis, no al final."
                ),
                "ejercicio_enunciado": (
                    "Con p = V, q = F, r = V, s = F, evalúa (¬p ∨ q) ⇔ (r ∧ ¬s)."
                ),
                "ejercicio_desarrollo": (
                    "¬p = ¬V = F.\n"
                    "¬p ∨ q = F ∨ F = F.\n"
                    "¬s = ¬F = V.\n"
                    "r ∧ ¬s = V ∧ V = V.\n"
                    "Queda F ⇔ V: valores distintos."
                ),
                "ejercicio_respuesta": "F ⇔ V ≡ F (alternativa «b»).",
                "formula": "(¬p ∨ q) ↔ (r ∧ ¬s)",
                "fuente": "Test Acumulativo N.º 1, ítem I pregunta 8",
            },
            {
                "concepto": "Tabla con tres variables",
                "pregunta": "¿Cómo se ordenan las filas de una tabla de tres variables?",
                "definicion": (
                    "Con 3 variables hay 2³ = 8 filas. Se ordenan empezando por todo V y "
                    "alternando: la primera columna cambia cada 4 filas, la segunda cada "
                    "2 y la tercera en cada fila. Así no se olvida ninguna combinación."
                ),
                "notacion": "VVV, VVF, VFV, VFF, FVV, FVF, FFV, FFF",
                "clave_memoria": (
                    "Mitades: 4 V y 4 F en la primera columna; dentro de cada mitad, 2 y "
                    "2; dentro de cada par, 1 y 1."
                ),
                "ejercicio_enunciado": (
                    "Construye la tabla de (p ∨ r) ⇒ (p ∧ ¬s) —el ítem de desarrollo del "
                    "taller— y clasifícala."
                ),
                "ejercicio_desarrollo": (
                    "Variables p, r, s → 8 filas.\n"
                    "El antecedente p ∨ r es falso solo cuando p = F y r = F: en esas dos "
                    "filas el condicional es verdadero automáticamente.\n"
                    "En las otras seis, el valor depende de p ∧ ¬s, que solo es verdadero "
                    "con p = V y s = F.\n"
                    "Resultado por filas (VVV, VVF, VFV, VFF, FVV, FVF, FFV, FFF): "
                    "F, V, F, V, F, F, V, V."
                ),
                "ejercicio_respuesta": (
                    "Es una **contingencia**: hay cuatro V y cuatro F en la columna final."
                ),
                "formula": "(p ∨ r) → (p ∧ ¬s)",
                "fuente": "Tarea-Taller 1, ítem II de desarrollo",
            },
        ],
    },
]
