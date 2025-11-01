#!/usr/bin/env bash
# Build script para Render

set -o errexit  # Sair se algum comando falhar

echo "🔧 Iniciando build do backend..."

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo "✅ Build concluído com sucesso!"
