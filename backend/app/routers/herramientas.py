"""Herramientas de cálculo: lógica, conjuntos, Venn y sistemas de ecuaciones.

Son las que convierten la aplicación en un laboratorio y no en un montón de
texto: el estudiante escribe su propia fórmula o su propio enunciado y ve el
resultado, con los pasos intermedios.
"""

from __future__ import annotations

from fastapi import APIRouter, Response

from app.dependencias import UsuarioDep
from app.esquemas import (
    EquivalenciaEntrada,
    EquivalenciaSalida,
    FormulaEntrada,
    OperacionConjuntosEntrada,
    OperacionConjuntosSalida,
    RegionesSalida,
    SistemaEntrada,
    SistemaSalida,
    TablaVerdadSalida,
    VennEntrada,
)
from app.services import conjuntos as svc_conjuntos
from app.services import ecuaciones, logica, venn

router = APIRouter(prefix="/herramientas", tags=["herramientas"])


def _a_salida(tabla: logica.TablaVerdad) -> TablaVerdadSalida:
    return TablaVerdadSalida(
        formula=tabla.formula,
        formula_normalizada=tabla.formula_normalizada,
        variables=tabla.variables,
        columnas=tabla.columnas,
        filas=tabla.como_texto(),
        clasificacion=tabla.clasificacion,
        numero_filas=tabla.numero_filas,
    )


@router.post(
    "/tabla-verdad", response_model=TablaVerdadSalida, summary="Tabla de verdad de una fórmula"
)
def tabla_verdad(datos: FormulaEntrada, _: UsuarioDep) -> TablaVerdadSalida:
    return _a_salida(logica.construir_tabla(datos.formula))


@router.post(
    "/equivalencia",
    response_model=EquivalenciaSalida,
    summary="¿Son equivalentes dos fórmulas?",
)
def equivalencia(datos: EquivalenciaEntrada, _: UsuarioDep) -> EquivalenciaSalida:
    """Dos fórmulas son equivalentes si su bicondicional es una tautología."""
    combinada = f"({datos.formula_a}) {logica.BICONDICIONAL} ({datos.formula_b})"
    tabla = logica.construir_tabla(combinada)
    return EquivalenciaSalida(
        formula_a=datos.formula_a,
        formula_b=datos.formula_b,
        equivalentes=tabla.clasificacion == "tautología",
        tabla=_a_salida(tabla),
    )


@router.post(
    "/conjuntos", response_model=OperacionConjuntosSalida, summary="Operar con dos conjuntos"
)
def operar_conjuntos(
    datos: OperacionConjuntosEntrada, _: UsuarioDep
) -> OperacionConjuntosSalida:
    a = set(datos.a)
    b = set(datos.b)
    universo = set(datos.universo) | a | b

    def ordenar(valores: set) -> list[str]:
        return [str(v) for v in sorted(valores, key=str)]

    return OperacionConjuntosSalida(
        union=ordenar(svc_conjuntos.union(a, b)),
        interseccion=ordenar(svc_conjuntos.interseccion(a, b)),
        diferencia_ab=ordenar(svc_conjuntos.diferencia(a, b)),
        diferencia_ba=ordenar(svc_conjuntos.diferencia(b, a)),
        diferencia_simetrica=ordenar(svc_conjuntos.diferencia_simetrica(a, b)),
        complemento_a=ordenar(svc_conjuntos.complemento(universo, a)),
        complemento_b=ordenar(svc_conjuntos.complemento(universo, b)),
        cardinalidades={
            "a": len(a),
            "b": len(b),
            "union": len(a | b),
            "interseccion": len(a & b),
            "universo": len(universo),
            "partes_de_a": 2 ** len(a),
        },
    )


@router.post("/venn/regiones", response_model=RegionesSalida, summary="Regiones de un Venn")
def regiones_venn(datos: VennEntrada, _: UsuarioDep) -> RegionesSalida:
    spec = svc_conjuntos.EspecificacionVenn.desde_dict(datos.model_dump())
    regiones = spec.resolver_regiones()
    return RegionesSalida(etiquetas=datos.etiquetas, regiones=regiones.como_dict())


@router.post(
    "/venn/imagen",
    summary="Diagrama de Venn en PNG",
    response_class=Response,
    responses={200: {"content": {"image/png": {}}, "description": "Diagrama generado"}},
)
def imagen_venn(datos: VennEntrada, _: UsuarioDep) -> Response:
    png = venn.generar_png_cacheado(datos.model_dump())
    return Response(content=png, media_type="image/png")


@router.post(
    "/ecuaciones",
    response_model=SistemaSalida,
    summary="Resolver y clasificar un sistema lineal de 2×2 o 3×3",
)
def resolver_sistema(datos: SistemaEntrada, _: UsuarioDep) -> SistemaSalida:
    """Resuelve con aritmética exacta y devuelve el desarrollo paso a paso.

    Un sistema sin solución **no** es un error: «incompatible» es una de las
    tres clasificaciones de la unidad y sale con un 200 como las otras dos. El
    422 queda para lo que de verdad está mal escrito (una matriz que no es
    cuadrada, un coeficiente ilegible).
    """
    solucion = ecuaciones.resolver_datos(datos.matriz, datos.incognitas, datos.metodo)
    return SistemaSalida(**solucion.como_dict())
