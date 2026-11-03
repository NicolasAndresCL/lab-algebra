# =========================================================================
# lab-algebra — interfaz NiceGUI
#
# Misma base Ubuntu 24.04 que la API, para que ambas imágenes compartan capas
# y el conjunto pese menos de lo que suman por separado.
# =========================================================================

# ------------------------------------------------------------------ build
FROM ubuntu:25.10 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        python3-pip \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN python3.12 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# ---------------------------------------------------------------- runtime
FROM ubuntu:25.10 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.12 \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash algebra

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=algebra:algebra app ./app

USER algebra
EXPOSE 8080

# El healthcheck NO consulta a la API a propósito: si la API está caída, quien
# debe marcarse enfermo es su contenedor. Un healthcheck que se contagia del
# vecino provoca reinicios en cascada de un servicio que está perfectamente.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8080/healthz || exit 1

CMD ["python", "-m", "app.main"]
