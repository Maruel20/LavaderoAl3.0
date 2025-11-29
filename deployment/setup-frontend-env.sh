#!/bin/bash

###############################################################################
# Script para configurar variables de entorno del frontend
# Uso: ./setup-frontend-env.sh <dominio>
# Ejemplo: ./setup-frontend-env.sh milavadero.com
###############################################################################

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar argumentos
if [ $# -eq 0 ]; then
    print_error "Uso: $0 <dominio>"
    echo "Ejemplo: $0 milavadero.com"
    exit 1
fi

DOMAIN=$1
APP_DIR="/home/lavadero/LavaderoAl3.0"

print_info "Configurando variables de entorno del frontend para $DOMAIN..."

# Crear archivo .env.production
cat > $APP_DIR/.env.production <<EOF
# Variables de entorno para producción - Frontend
# Generado automáticamente el $(date)

# URL del API en producción
VITE_API_URL=https://${DOMAIN}/api
EOF

print_success "Archivo .env.production creado"

# Mostrar el contenido
print_info "Contenido del archivo:"
cat $APP_DIR/.env.production

echo ""
print_success "Configuración completada"
print_info "Ahora ejecuta 'npm run build' para compilar el frontend con esta configuración"
