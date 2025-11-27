#!/bin/bash

###############################################################################
# Script de Backup de Base de Datos - Lavadero AL
###############################################################################

# Configuración
BACKUP_DIR="/home/lavadero/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/lavadero_al_$TIMESTAMP.sql"
DB_NAME="lavadero_al"
DB_USER="lavadero_user"

# Crear directorio de backups si no existe
mkdir -p "$BACKUP_DIR"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "📦 Backup de Base de Datos - Lavadero AL"
echo "=========================================="
echo ""

# Leer password de forma segura (si no está en .my.cnf)
if [ -f ~/.my.cnf ]; then
    echo -e "${GREEN}Usando credenciales de ~/.my.cnf${NC}"
    mysqldump "$DB_NAME" > "$BACKUP_FILE" 2>&1
else
    echo "Ingresa la contraseña de MySQL para el usuario $DB_USER:"
    read -s DB_PASSWORD
    mysqldump -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" > "$BACKUP_FILE" 2>&1
fi

# Verificar si el backup fue exitoso
if [ $? -eq 0 ]; then
    # Comprimir el backup
    gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"

    # Obtener tamaño del archivo
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

    echo -e "${GREEN}✅ Backup completado exitosamente!${NC}"
    echo "Archivo: $BACKUP_FILE"
    echo "Tamaño: $SIZE"

    # Mantener solo los últimos 7 días de backups
    find "$BACKUP_DIR" -name "lavadero_al_*.sql.gz" -mtime +7 -delete

    # Listar backups disponibles
    echo ""
    echo "Backups disponibles:"
    ls -lh "$BACKUP_DIR"/lavadero_al_*.sql.gz
else
    echo -e "${RED}❌ Error al crear el backup${NC}"
    exit 1
fi

echo ""
echo "Para restaurar un backup:"
echo "  gunzip < $BACKUP_FILE | mysql -u $DB_USER -p $DB_NAME"
