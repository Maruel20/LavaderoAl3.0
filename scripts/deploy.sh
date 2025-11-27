#!/bin/bash

###############################################################################
# Script de Deployment Automático - Lavadero AL
# Para VPS Ubuntu 20.04+
###############################################################################

set -e  # Detener en caso de error

echo "=========================================="
echo "🚀 Deployment de Lavadero AL"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio de la aplicación
APP_DIR="/home/lavadero/LavaderoAl3.0"
BACKEND_DIR="$APP_DIR/backend"

# Función para imprimir mensajes
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -d "$APP_DIR" ]; then
    print_error "Directorio de aplicación no encontrado: $APP_DIR"
    exit 1
fi

cd "$APP_DIR"

# 1. Hacer backup de la base de datos
print_message "Creando backup de base de datos..."
./scripts/backup-db.sh || print_warning "Backup falló, continuando..."

# 2. Obtener últimos cambios
print_message "Obteniendo últimos cambios desde Git..."
git pull origin main || {
    print_error "Git pull falló"
    exit 1
}

# 3. Actualizar Backend
print_message "Actualizando Backend..."
cd "$BACKEND_DIR"
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 4. Actualizar Frontend
print_message "Actualizando Frontend..."
cd "$APP_DIR"
npm install
npm run build

# 5. Reiniciar servicios
print_message "Reiniciando servicios..."
sudo systemctl restart lavadero-backend
sudo systemctl restart nginx

# 6. Verificar estado de servicios
sleep 3
if systemctl is-active --quiet lavadero-backend; then
    print_message "Backend: ✅ Corriendo"
else
    print_error "Backend: ❌ No está corriendo"
    sudo systemctl status lavadero-backend
    exit 1
fi

if systemctl is-active --quiet nginx; then
    print_message "Nginx: ✅ Corriendo"
else
    print_error "Nginx: ❌ No está corriendo"
    sudo systemctl status nginx
    exit 1
fi

echo ""
print_message "=========================================="
print_message "✅ Deployment completado exitosamente!"
print_message "=========================================="
echo ""
print_message "Ver logs:"
echo "  Backend: sudo journalctl -u lavadero-backend -f"
echo "  Nginx: sudo tail -f /var/log/nginx/error.log"
