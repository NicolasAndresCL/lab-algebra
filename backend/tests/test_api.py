"""Pruebas de los endpoints HTTP."""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestSalud:
    def test_healthz_consulta_la_base_de_datos(self, cliente: TestClient) -> None:
        cuerpo = cliente.get("/healthz").json()
        assert cuerpo["estado"] == "ok"
        assert cuerpo["base_de_datos"] == "ok"


class TestAutenticacion:
    def test_login_correcto_devuelve_token_y_usuario(self, cliente: TestClient) -> None:
        respuesta = cliente.post(
            "/api/v1/auth/login", json={"username": "nico", "password": "1234"}
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["token_type"] == "bearer"
        assert cuerpo["usuario"]["username"] == "nico"
        assert "password" not in respuesta.text

    def test_password_incorrecta_da_401(self, cliente: TestClient) -> None:
        respuesta = cliente.post(
            "/api/v1/auth/login", json={"username": "nico", "password": "incorrecta"}
        )
        assert respuesta.status_code == 401
        assert respuesta.json()["error"]["codigo"] == "credenciales_invalidas"

    def test_usuario_inexistente_da_el_mismo_error(self, cliente: TestClient) -> None:
        """No debe poder distinguirse «no existe» de «contraseña mala»."""
        inexistente = cliente.post(
            "/api/v1/auth/login", json={"username": "fantasma", "password": "1234"}
        ).json()["error"]
        mala = cliente.post(
            "/api/v1/auth/login", json={"username": "nico", "password": "x"}
        ).json()["error"]
        assert inexistente == mala

    def test_sin_token_no_se_accede_a_los_mazos(self, cliente: TestClient) -> None:
        respuesta = cliente.get("/api/v1/mazos")
        assert respuesta.status_code == 401
        assert respuesta.json()["error"]["codigo"] == "no_autenticado"

    def test_token_invalido_da_401(self, cliente: TestClient) -> None:
        respuesta = cliente.get(
            "/api/v1/mazos", headers={"Authorization": "Bearer no-es-un-token"}
        )
        assert respuesta.status_code == 401

    def test_yo_devuelve_el_usuario_de_la_sesion(self, autenticado: TestClient) -> None:
        assert autenticado.get("/api/v1/auth/yo").json()["username"] == "nico"


class TestMazos:
    def test_lista_los_trece_mazos_con_sus_conteos(self, autenticado: TestClient) -> None:
        """Tres mazos por unidad en lógica, conjuntos y ecuaciones, y cuatro en matrices."""
        mazos = autenticado.get("/api/v1/mazos").json()
        assert len(mazos) == 13
        assert all(m["total_tarjetas"] > 0 for m in mazos)
        assert sum(m["total_tarjetas"] for m in mazos) >= 110
        assert sum(m["unidad"] == "Matrices" for m in mazos) == 4

    def test_tarjetas_de_un_mazo_vienen_ordenadas(self, autenticado: TestClient) -> None:
        mazo = autenticado.get("/api/v1/mazos").json()[0]
        tarjetas = autenticado.get(f"/api/v1/mazos/{mazo['id']}/tarjetas").json()
        assert [t["orden"] for t in tarjetas] == sorted(t["orden"] for t in tarjetas)

    def test_buscar_filtra_por_concepto(self, autenticado: TestClient) -> None:
        mazos = {m["slug"]: m["id"] for m in autenticado.get("/api/v1/mazos").json()}
        tarjetas = autenticado.get(
            f"/api/v1/mazos/{mazos['conectivos-logicos']}/tarjetas",
            params={"buscar": "Negación"},
        ).json()
        conceptos = [t["concepto"] for t in tarjetas]
        assert "Negación (¬)" in conceptos
        # Busca también en la definición, así que puede traer más de una; lo
        # que no puede es traerlas todas.
        completo = autenticado.get(
            f"/api/v1/mazos/{mazos['conectivos-logicos']}/tarjetas"
        ).json()
        assert 0 < len(tarjetas) < len(completo)

    def test_mazo_inexistente_da_404(self, autenticado: TestClient) -> None:
        respuesta = autenticado.get("/api/v1/mazos/99999/tarjetas")
        assert respuesta.status_code == 404
        assert respuesta.json()["error"]["codigo"] == "recurso_no_encontrado"


class TestCrearTarjetas:
    def _mazo_id(self, cliente: TestClient) -> int:
        return cliente.get("/api/v1/mazos").json()[0]["id"]

    def _datos(self, mazo_id: int, concepto: str) -> dict:
        return {
            "mazo_id": mazo_id,
            "concepto": concepto,
            "pregunta": "¿Pregunta de prueba?",
            "definicion": "Definición de prueba.",
            "ejercicio_enunciado": "Enunciado de prueba.",
            "ejercicio_desarrollo": "Paso 1. Paso 2.",
            "ejercicio_respuesta": "Respuesta.",
        }

    def test_se_puede_crear_una_tarjeta_propia(self, autenticado: TestClient) -> None:
        mazo_id = self._mazo_id(autenticado)
        respuesta = autenticado.post(
            "/api/v1/tarjetas", json=self._datos(mazo_id, "Concepto propio 1")
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["es_semilla"] is False

    def test_no_se_puede_repetir_un_concepto_en_el_mismo_mazo(
        self, autenticado: TestClient
    ) -> None:
        mazo_id = self._mazo_id(autenticado)
        datos = self._datos(mazo_id, "Concepto repetido")
        assert autenticado.post("/api/v1/tarjetas", json=datos).status_code == 201
        repetida = autenticado.post("/api/v1/tarjetas", json=datos)
        assert repetida.status_code == 409
        assert repetida.json()["error"]["codigo"] == "recurso_duplicado"

    def test_una_formula_invalida_se_rechaza_al_guardar(
        self, autenticado: TestClient
    ) -> None:
        """Mejor fallar al crear que en mitad de un repaso."""
        datos = self._datos(self._mazo_id(autenticado), "Con fórmula rota")
        datos["formula"] = "p ∧ ∧ q"
        respuesta = autenticado.post("/api/v1/tarjetas", json=datos)
        assert respuesta.status_code == 422
        assert respuesta.json()["error"]["codigo"] == "formula_invalida"

    def test_un_venn_imposible_se_rechaza_al_guardar(self, autenticado: TestClient) -> None:
        datos = self._datos(self._mazo_id(autenticado), "Con venn imposible")
        datos["venn"] = {"etiquetas": ["A", "B"], "cardinalidades": {"a": 5, "b": 5, "ab": 9}}
        respuesta = autenticado.post("/api/v1/tarjetas", json=datos)
        assert respuesta.status_code == 422
        assert respuesta.json()["error"]["codigo"] == "datos_venn_invalidos"

    def test_una_matriz_mal_formada_se_rechaza_al_guardar(
        self, autenticado: TestClient
    ) -> None:
        datos = self._datos(self._mazo_id(autenticado), "Con matriz rota")
        datos["matriz"] = {"operacion": "suma", "a": [[1, 2], [3]], "b": [[1, 2], [3, 4]]}
        respuesta = autenticado.post("/api/v1/tarjetas", json=datos)
        assert respuesta.status_code == 422
        assert respuesta.json()["error"]["codigo"] == "matriz_invalida"

    def test_una_tarjeta_con_matriz_se_guarda_y_la_conserva(
        self, autenticado: TestClient
    ) -> None:
        datos = self._datos(self._mazo_id(autenticado), "Con matriz")
        datos["matriz"] = {"operacion": "traza", "a": [[2, 5], [1, 3]]}
        respuesta = autenticado.post("/api/v1/tarjetas", json=datos)
        assert respuesta.status_code == 201
        assert respuesta.json()["matriz"] == datos["matriz"]

    def test_editar_valida_tambien_los_campos_calculados(
        self, autenticado: TestClient
    ) -> None:
        """El PATCH pasa por el mismo registro de validadores que el alta."""
        creada = autenticado.post(
            "/api/v1/tarjetas", json=self._datos(self._mazo_id(autenticado), "Editable 2")
        ).json()
        respuesta = autenticado.patch(
            f"/api/v1/tarjetas/{creada['id']}",
            json={"matriz": {"operacion": "potencia", "a": [[1]]}},
        )
        assert respuesta.status_code == 422
        assert respuesta.json()["error"]["codigo"] == "matriz_invalida"

    def test_las_tarjetas_del_temario_no_se_borran(self, autenticado: TestClient) -> None:
        mazo_id = self._mazo_id(autenticado)
        tarjetas = autenticado.get(f"/api/v1/mazos/{mazo_id}/tarjetas").json()
        semilla = next(t for t in tarjetas if t["es_semilla"])
        respuesta = autenticado.delete(f"/api/v1/tarjetas/{semilla['id']}")
        assert respuesta.status_code == 409

    def test_una_tarjeta_propia_si_se_borra(self, autenticado: TestClient) -> None:
        mazo_id = self._mazo_id(autenticado)
        creada = autenticado.post(
            "/api/v1/tarjetas", json=self._datos(mazo_id, "Concepto desechable")
        ).json()
        assert autenticado.delete(f"/api/v1/tarjetas/{creada['id']}").status_code == 204
        assert autenticado.get(f"/api/v1/tarjetas/{creada['id']}").status_code == 404

    def test_se_puede_editar_una_tarjeta(self, autenticado: TestClient) -> None:
        mazo_id = self._mazo_id(autenticado)
        creada = autenticado.post(
            "/api/v1/tarjetas", json=self._datos(mazo_id, "Concepto editable")
        ).json()
        editada = autenticado.patch(
            f"/api/v1/tarjetas/{creada['id']}", json={"definicion": "Nueva definición."}
        )
        assert editada.status_code == 200
        assert editada.json()["definicion"] == "Nueva definición."


class TestHerramientas:
    def test_tabla_de_verdad(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/tabla-verdad", json={"formula": "p → q"}
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["numero_filas"] == 4
        assert cuerpo["clasificacion"] == "contingencia"
        assert cuerpo["filas"][1] == ["V", "F", "F"]

    def test_formula_invalida_devuelve_la_posicion(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/tabla-verdad", json={"formula": "p ∧ #"}
        )
        assert respuesta.status_code == 422
        assert respuesta.json()["error"]["detalle"]["posicion"] == 4

    def test_equivalencia_de_de_morgan(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/equivalencia",
            json={"formula_a": "¬(p ∧ q)", "formula_b": "¬p ∨ ¬q"},
        )
        assert respuesta.json()["equivalentes"] is True

    def test_operaciones_de_conjuntos(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/conjuntos",
            json={"a": [1, 2, 3, 4], "b": [3, 4, 5, 6]},
        )
        cuerpo = respuesta.json()
        assert cuerpo["interseccion"] == ["3", "4"]
        assert cuerpo["diferencia_ab"] == ["1", "2"]
        assert cuerpo["diferencia_ba"] == ["5", "6"]
        assert cuerpo["cardinalidades"]["partes_de_a"] == 16

    def test_regiones_de_un_venn(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/venn/regiones",
            json={
                "etiquetas": ["Java", "Python"],
                "cardinalidades": {"a": 70, "b": 50, "ab": 30},
                "universo": 120,
            },
        )
        regiones = respuesta.json()["regiones"]
        assert regiones == {
            "solo_a": 40,
            "solo_b": 20,
            "ambos": 30,
            "ninguno": 30,
            "union": 90,
            "exactamente_uno": 60,
        }

    def test_imagen_de_venn_devuelve_un_png(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/venn/imagen",
            json={
                "etiquetas": ["A", "B"],
                "cardinalidades": {"a": 10, "b": 8, "ab": 4},
                "universo": 20,
            },
        )
        assert respuesta.status_code == 200
        assert respuesta.headers["content-type"] == "image/png"
        assert respuesta.content.startswith(b"\x89PNG")

    def test_sistema_2x2_con_delta_y_desarrollo(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/ecuaciones",
            json={"matriz": [[1, 1, 3], [1, 2, -8]], "metodo": "reducción"},
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["clasificacion"] == "compatible determinado"
        assert cuerpo["valores"] == {"x": "14", "y": "−11"}
        assert cuerpo["delta"] == "1"
        assert len(cuerpo["pasos"]) >= 4

    def test_un_coeficiente_fraccionario_no_se_redondea(
        self, autenticado: TestClient
    ) -> None:
        """La fracción viaja como texto y vuelve como fracción, sin pasar por float."""
        respuesta = autenticado.post(
            "/api/v1/herramientas/ecuaciones",
            json={"matriz": [[3, -4, 4], ["1/2", -3, "-1/2"]]},
        )
        assert respuesta.json()["valores"] == {"x": "2", "y": "1/2"}

    def test_un_sistema_incompatible_no_es_un_error(
        self, autenticado: TestClient
    ) -> None:
        """«No tiene solución» es una clasificación de la unidad, no un fallo: 200."""
        respuesta = autenticado.post(
            "/api/v1/herramientas/ecuaciones",
            json={"matriz": [[7, 4, 1], [-7, -4, -3]]},
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["clasificacion"] == "incompatible"

    def test_sistema_3x3_indeterminado(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/ecuaciones",
            json={
                "matriz": [[1, -1, -1, 1], [-1, 2, -3, -4], [3, -2, -7, 0]],
                "incognitas": ["x", "y", "z"],
            },
        )
        cuerpo = respuesta.json()
        assert cuerpo["clasificacion"] == "compatible indeterminado"
        assert cuerpo["parametros"] == ["z"]
        assert cuerpo["delta"] is None

    def test_una_matriz_mal_formada_da_422_con_codigo_estable(
        self, autenticado: TestClient
    ) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/ecuaciones", json={"matriz": [[1, 1, 3], [1, 2]]}
        )
        assert respuesta.status_code == 422
        assert respuesta.json()["error"]["codigo"] == "sistema_invalido"

    def test_sistema_por_cramer(self, autenticado: TestClient) -> None:
        """Lámina 46: 3x − 2y = 4 ; 6x + y = 13."""
        respuesta = autenticado.post(
            "/api/v1/herramientas/ecuaciones",
            json={"matriz": [[3, -2, 4], [6, 1, 13]], "metodo": "Cramer"},
        )
        cuerpo = respuesta.json()
        assert cuerpo["metodo"] == "Cramer"
        assert cuerpo["valores"] == {"x": "2", "y": "1"}
        assert any(paso.startswith("Dₓ = ") for paso in cuerpo["pasos"])

    def test_catalogo_de_operaciones_con_matrices(self, autenticado: TestClient) -> None:
        """La interfaz se construye desde aquí: cada operación trae su ejemplo."""
        catalogo = autenticado.get("/api/v1/herramientas/matrices/operaciones").json()
        claves = [op["clave"] for op in catalogo]
        assert {"suma", "producto", "traspuesta", "traza", "determinante"} <= set(claves)
        assert all(op["ejemplo"].get("a") for op in catalogo)
        assert all("lámina" in op["fuente"] for op in catalogo)

    def test_producto_de_matrices_con_desarrollo(self, autenticado: TestClient) -> None:
        """Lámina 30, con la respuesta impresa en la propia lámina."""
        respuesta = autenticado.post(
            "/api/v1/herramientas/matrices",
            json={
                "operacion": "producto",
                "a": [[2, 1, 5], [3, 0, 4]],
                "b": [[-1, 7, 8], [4, 6, 0], [5, 7, 3]],
            },
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["definida"] is True
        assert cuerpo["resultado"] == [["27", "55", "31"], ["17", "49", "36"]]
        assert cuerpo["ordenes"] == {"A": "2 × 3", "B": "3 × 3"}
        assert "c₁₁ = 2·(−1) + 1·4 + 5·5 = 27" in cuerpo["pasos"]

    def test_un_producto_no_definido_no_es_un_error(self, autenticado: TestClient) -> None:
        """Saber cuándo NO se puede multiplicar es temario: 200, no 422."""
        respuesta = autenticado.post(
            "/api/v1/herramientas/matrices",
            json={"operacion": "producto", "a": [[1, 2, 3]], "b": [[1, 2, 3]]},
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["definida"] is False
        assert cuerpo["resultado"] is None
        assert "columnas de A (3)" in cuerpo["pasos"][0]

    def test_determinante_con_fracciones_e_invertibilidad(
        self, autenticado: TestClient
    ) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/matrices",
            json={"operacion": "determinante", "a": [["1/2", 1], [3, "-1/3"]]},
        )
        cuerpo = respuesta.json()
        assert cuerpo["valor"] == "−19/6"
        assert cuerpo["invertible"] is True

    def test_filas_desiguales_dan_422(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/matrices",
            json={"operacion": "traspuesta", "a": [[1, 2], [3]]},
        )
        assert respuesta.status_code == 422
        assert respuesta.json()["error"]["codigo"] == "matriz_invalida"


class TestContratoDeError:
    def test_todos_los_errores_tienen_la_misma_forma(self, cliente: TestClient) -> None:
        cuerpo = cliente.get("/api/v1/mazos").json()
        assert set(cuerpo) == {"error"}
        assert set(cuerpo["error"]) == {"codigo", "mensaje", "detalle"}

    def test_los_datos_invalidos_dan_422_con_codigo_estable(
        self, autenticado: TestClient
    ) -> None:
        respuesta = autenticado.post("/api/v1/auth/login", json={"username": "nico"})
        assert respuesta.status_code == 422
        assert respuesta.json()["error"]["codigo"] == "datos_invalidos"
