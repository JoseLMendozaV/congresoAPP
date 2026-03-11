#!/usr/bin/env bash
# Salir si ocurre un error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Construir Tailwind
python manage.py tailwind build

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar migraciones de base de datos (opcional, pero recomendado)
python manage.py migrate