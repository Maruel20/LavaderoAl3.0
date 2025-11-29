#!/bin/bash

###############################################################################
# Script de Backup para Lavadero AL
# Uso: ./backup.sh
###############################################################################

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Configuración
APP_DIR="/home/lavadero/LavaderoAl3.0"
BACKUP_DIR="/home/lavadero/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

print_info "Iniciando backup de Lavadero AL..."

# Cargar variables de entorno
if [ -f "$APP_DIR/.env" ]; then
    source $APP_DIR/.env
else
    echo "Error: No se encontró el archivo .env"
    exit 1
fi

# Backup de la base de datos
print_info "Creando backup de la base de datos..."
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz
print_success "Backup de base de datos creado: db_backup_$DATE.sql.gz"

# Backup del código (opcional, si quieres incluir el código)
print_info "Creando backup del código..."
tar -czf $BACKUP_DIR/code_backup_$DATE.tar.gz \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='dist' \
    --exclude='.git' \
    -C /home/lavadero LavaderoAl3.0
print_success "Backup del código creado: code_backup_$DATE.tar.gz"

# Backup del archivo .env
print_info "Creando backup de .env..."
cp $APP_DIR/.env $BACKUP_DIR/env_backup_$DATE
print_success "Backup de .env creado: env_backup_$DATE"

# Eliminar backups antiguos (mantener solo los últimos 7 días)
print_info "Eliminando backups antiguos (más de 7 días)..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "env_backup_*" -mtime +7 -delete

print_success "Backup completado exitosamente"
print_info "Archivos guardados en: $BACKUP_DIR"

# Listar backups
echo ""
print_info "Backups disponibles:"
ls -lh $BACKUP_DIR | grep backup_$DATE
