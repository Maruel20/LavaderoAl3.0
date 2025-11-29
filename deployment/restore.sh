#!/bin/bash

###############################################################################
# Script de Restauración para Lavadero AL
# Uso: ./restore.sh <archivo_backup.sql.gz>
###############################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar argumentos
if [ $# -eq 0 ]; then
    print_error "Uso: $0 <archivo_backup.sql.gz>"
    echo "Ejemplo: $0 /home/lavadero/backups/db_backup_20250129_120000.sql.gz"
    exit 1
fi

BACKUP_FILE=$1
APP_DIR="/home/lavadero/LavaderoAl3.0"

# Verificar que el archivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    print_error "El archivo $BACKUP_FILE no existe"
    exit 1
fi

# Cargar variables de entorno
if [ -f "$APP_DIR/.env" ]; then
    source $APP_DIR/.env
else
    print_error "No se encontró el archivo .env"
    exit 1
fi

print_warning "==================================================================="
print_warning "¡ADVERTENCIA!"
print_warning "Estás a punto de restaurar la base de datos desde un backup."
print_warning "Esto ELIMINARÁ todos los datos actuales de la base de datos."
print_warning "==================================================================="
print_warning ""
print_warning "Archivo de backup: $BACKUP_FILE"
print_warning "Base de datos: $DB_NAME"
print_warning ""
read -p "¿Estás seguro de continuar? (escribe 'SI' para confirmar): " CONFIRM

if [ "$CONFIRM" != "SI" ]; then
    print_info "Restauración cancelada"
    exit 0
fi

# Crear backup de seguridad antes de restaurar
print_info "Creando backup de seguridad antes de restaurar..."
SAFETY_BACKUP="/tmp/safety_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME | gzip > $SAFETY_BACKUP
print_success "Backup de seguridad creado: $SAFETY_BACKUP"

# Restaurar base de datos
print_info "Restaurando base de datos desde $BACKUP_FILE..."
gunzip < $BACKUP_FILE | mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME

if [ $? -eq 0 ]; then
    print_success "Base de datos restaurada exitosamente"
    print_info "Backup de seguridad guardado en: $SAFETY_BACKUP"
else
    print_error "Error al restaurar la base de datos"
    print_info "Puedes restaurar el backup de seguridad con:"
    print_info "gunzip < $SAFETY_BACKUP | mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME"
    exit 1
fi

# Reiniciar servicio backend
print_info "Reiniciando servicio backend..."
systemctl restart lavadero-backend

if systemctl is-active --quiet lavadero-backend; then
    print_success "Servicio reiniciado correctamente"
else
    print_error "Error al reiniciar el servicio"
fi

print_success "Restauración completada"
