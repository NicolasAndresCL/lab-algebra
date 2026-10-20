# Changelog

Todos los cambios notables de este proyecto se documentan aquí. El formato sigue
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa
[versionado semántico](https://semver.org/lang/es/).

## [Sin publicar]

## [1.4.0] — 2026-10-20

### Añadido

- `compose.traefik.yml`: override que se aplica sobre `docker-compose.yml` para
  desplegar detrás de un Traefik ya existente (el VPS con n8n). No publica
  ningún puerto en el host, solo `web` se une a la red de Traefik, pone basic
  auth de Traefik delante del login propio, fija `mem_limit` (db 128m, api 320m,
  web 256m) y `ENTORNO=prod`.
- Variables nuevas: `LAB_ALGEBRA_HOST`, `TRAEFIK_NETWORK`,
  `LAB_ALGEBRA_BASIC_AUTH`, `TRAEFIK_CERTRESOLVER` (por defecto `le`) y
  `TRAEFIK_ENTRYPOINT` (por defecto `websecure`).
- CI y `scripts/verificar.sh`: el override se valida con
  `docker compose config --quiet` y se exige que publique 0 puertos.
- README: sección «Desplegar detrás de Traefik».

### Cambiado

- Las imágenes se etiquetan `lab-algebra-api:1.4.0` y `lab-algebra-web:1.4.0`
  (decían `1.1.0` siendo la v1.3.0).
- Versión 1.4.0 en `backend` y `frontend` (`__init__.py` y `pyproject.toml`).
- README con el formato fijo: tagline, badges de versión y Python, tabla de
  metadatos y bloque de autor.

## [1.3.0] — 2026-10-06

### Añadido

- Segunda parte de la unidad de matrices: menores, cofactores, adjunta e
  inversa de 2 × 2 y de 3 × 3, y determinante de 3 × 3 por cualquier fila o
  columna.
- Regla de Cramer de 3 × 3 en el motor de ecuaciones.
- Mazo de 15 tarjetas (129 en total, en 14 mazos).
- Parámetros declarativos de las operaciones con matrices y métodos de
  resolución por orden, publicados por el catálogo de la API.

### Cambiado

- La interfaz construye los campos de cada operación desde el catálogo en vez de
  tener dos campos fijos.
- El determinante de 3 × 3 se narra por cofactores (antes, regla de Sarrus).

## [1.2.0] — 2026-10-05

### Añadido

- Cuarta unidad: matrices y determinantes, con un motor sobre numpy y
  aritmética exacta.
- Pestaña de matrices en la interfaz, construida desde el catálogo de la API.
- Regla de Cramer de 2 × 2 y números exactos compartidos entre motores.

## [1.1.0] — 2026-09-22

### Añadido

- Tercera unidad: sistemas de ecuaciones lineales, con un motor en aritmética
  exacta (`fractions.Fraction`).
- Pestaña de sistemas de ecuaciones y sistema resuelto en la tarjeta.
- Columna `sistema` en las tarjetas, con el esquema puesto al día sobre un
  volumen existente.

## [1.0.0] — 2026-08-29

### Añadido

- Laboratorio de tarjetas de Álgebra: API FastAPI, interfaz NiceGUI y
  PostgreSQL en tres contenedores sobre la red `lab-algebra-net`.
- 52 tarjetas de lógica proposicional y teoría de conjuntos, con tablas de
  verdad y diagramas de Venn generados en vivo.
- Cuatro temas de la interfaz con cambio en caliente.
- CI que construye y arranca el stack, no solo lintea.

[Sin publicar]: https://github.com/NicolasAndresCL/lab-algebra/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/NicolasAndresCL/lab-algebra/releases/tag/v1.4.0
