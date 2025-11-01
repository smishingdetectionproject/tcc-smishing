#!/usr/bin/env bash
# Start script para Render

echo "🚀 Iniciando servidor..."

# Usar a porta fornecida pelo Render ou 8000 como padrão
PORT=${PORT:-8000}

echo "📡 Servidor rodando na porta $PORT"

# Iniciar Gunicorn com Uvicorn workers
exec gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:$PORT \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
