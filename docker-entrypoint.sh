#!/usr/bin/env bash

set -euo pipefail

# Ensure required runtime directories exist with correct permissions
mkdir -p hippocampus/longterm hippocampus/shortterm logs

# Run comprehensive initialization if system.db doesn't exist or FORCE_INIT is set
if [ ! -f "hippocampus/system.db" ] || [ "${FORCE_INIT:-false}" = "true" ]; then
    echo "[entrypoint] Running Tatlock initialization..."
    python docker-init.py
fi

exec "$@"
