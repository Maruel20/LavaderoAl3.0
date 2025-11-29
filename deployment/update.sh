#!/bin/bash

###############################################################################
# Script de Actualización para Lavadero AL
# Uso: ./update.sh
###############################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
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

# Configuración
APP_DIR="/home/lavadero/LavaderoAl3.0"
APP_USER="lavadero"
SERVICE_NAME="lavadero-backend"

# Verificar que el script se ejecute como root
if [ "$EUID" -ne 0 ]; then
    print_error "Por favor ejecuta este script como root (usa sudo)"
    exit 1
fi

print_info "==================================================================="
print_info "Actualizando Lavadero AL"
print_info "==================================================================="

# Ir al directorio de la aplicación
cd $APP_DIR

# Paso 1: Crear backup
print_info "Paso 1: Creando backup de la base de datos..."
BACKUP_FILE="/home/$APP_USER/backup_$(date +%Y%m%d_%H%M%S).sql"
if [ -f "$APP_DIR/.env" ]; then
    source $APP_DIR/.env
    mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_FILE
    chown $APP_USER:$APP_USER $BACKUP_FILE
    print_success "Backup creado: $BACKUP_FILE"
fi

# Paso 2: Actualizar código desde Git
print_info "Paso 2: Actualizando código desde Git..."
sudo -u $APP_USER git pull
print_success "Código actualizado"

# Paso 3: Actualizar dependencias del backend
print_info "Paso 3: Actualizando dependencias de Python..."
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r backend/requirements.txt"
print_success "Dependencias de Python actualizadas"

# Paso 4: Actualizar dependencias del frontend
print_info "Paso 4: Actualizando dependencias de Node.js..."
sudo -u $APP_USER npm install
print_success "Dependencias de Node.js actualizadas"

# Paso 5: Compilar frontend
print_info "Paso 5: Compilando frontend..."

# Verificar que exista .env.production
if [ ! -f "$APP_DIR/.env.production" ]; then
    print_info "No se encontró .env.production. Creando con configuración por defecto..."
    echo "VITE_API_URL=/api" > $APP_DIR/.env.production
    chown $APP_USER:$APP_USER $APP_DIR/.env.production
fi

sudo -u $APP_USER npm run build
print_success "Frontend compilado"

# Paso 6: Reiniciar servicio del backend
print_info "Paso 6: Reiniciando servicio del backend..."
systemctl restart $SERVICE_NAME

# Verificar estado del servicio
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Servicio reiniciado correctamente"
else
    print_error "Error al reiniciar el servicio. Verifica los logs con: journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

# Paso 7: Reiniciar Nginx
print_info "Paso 7: Reiniciando Nginx..."
nginx -t && systemctl reload nginx
print_success "Nginx reiniciado"

print_info "==================================================================="
print_success "¡Actualización completada con éxito!"
print_info "==================================================================="
echo ""
print_info "Backup de la base de datos guardado en: $BACKUP_FILE"
print_info "Verifica que todo funcione correctamente en tu dominio"
