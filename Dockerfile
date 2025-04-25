# 1) BUILDER: genera el ejecutable
FROM python:3.12-slim AS builder

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential libssl-dev libffi-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia y instala deps de Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Instala PyInstaller y copia tu código
RUN pip install pyinstaller
COPY . .

# Genera el ejecutable Linux
RUN pyinstaller \
    --clean \
    --onefile \
    --version-file version_info.txt \
    --hidden-import=eventlet.hubs.epolls \
    --hidden-import=eventlet.hubs.kqueue \
    --hidden-import=eventlet.hubs.selects \
    --hidden-import=dns \
    --hidden-import=dns.dnssec \
    --hidden-import=dns.e164 \
    --hidden-import=dns.hash \
    --hidden-import=dns.namedict \
    --hidden-import=dns.tsigkeyring \
    --hidden-import=dns.update \
    --hidden-import=dns.version \
    --hidden-import=dns.zone \
    --hidden-import=dns.versioned \
    -n reloj_asistencias \
    -i resources/fingerprint.ico \
    --add-data "json/errors.json:json" \
    --add-data "resources/window:resources/window" \
    --add-data "resources/system_tray:resources/system_tray" \
    --add-data "resources/fingerprint.ico:resources" \
    --noupx \
    --log-level=INFO \
    --debug all \
    main.py

# 2) RUNTIME: imagen mínima con glibc ≥ 2.35
FROM debian:bookworm-slim AS runtime

COPY --from=builder /app/dist/reloj_asistencias /usr/local/bin/reloj_asistencias

ENTRYPOINT ["reloj_asistencias"]