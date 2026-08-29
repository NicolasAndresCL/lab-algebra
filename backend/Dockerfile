# =========================================================================
# lab-algebra-api — API FastAPI
#
# Base Ubuntu 24.04 LTS en vez de python:3.12-slim: el laboratorio se apoya en
# matplotlib y matplotlib-venn, y con la imagen de Ubuntu las fuentes y las
# bibliotecas gráficas del sistema son las mismas que en una máquina de
# escritorio — los diagramas salen idénticos dentro y fuera del contenedor.
# Ubuntu 24.04 trae Python 3.12 en sus repositorios, así que no hace falta un
# PPA ni compilar el intérprete.
# =========================================================================

# ------------------------------------------------------------------ build
FROM ubuntu:24.04 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# build-essential y los headers solo viven en esta etapa: si algún paquete no
# trae rueda para la plataforma, aquí se compila y la imagen final no arrastra
# el compilador.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        python3-pip \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Las dependencias se copian antes que el código: mientras requirements.txt no
# cambie, Docker reutiliza esta capa aunque se toque cada archivo de app/.
COPY requirements.txt ./
RUN python3.12 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# ---------------------------------------------------------------- runtime
FROM ubuntu:24.04 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH" \
    MPLCONFIGDIR=/tmp/matplotlib

# Solo lo necesario para *ejecutar*: el intérprete, curl para el healthcheck y
# las fuentes que matplotlib usa al rotular los diagramas. Sin fonts-dejavu los
# números de las regiones salen como rectángulos vacíos.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.12 \
        curl \
        fonts-dejavu-core \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash algebra

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=algebra:algebra app ./app

USER algebra
EXPOSE 8000

# «Sano» aquí significa que la API responde Y que la base de datos contesta:
# /healthz devuelve 503 si la consulta falla, y `curl -f` lo convierte en un
# contenedor unhealthy. Un 200 que no tocara la base no probaría nada.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips", "*"]
