#!/bin/bash

###############################################################################
# Script de Monitoreo para Lavadero AL
# Uso: ./monitor.sh
# Uso con cron (cada 5 minutos): */5 * * * * /home/lavadero/LavaderoAl3.0/deployment/monitor.sh
###############################################################################

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

APP_DIR="/home/lavadero/LavaderoAl3.0"
ERRORS=0

echo "=============================================="
echo "Monitor de Estado - Lavadero AL"
echo "Fecha: $(date)"
echo "=============================================="
echo ""

# 1. Verificar servicio backend
echo "[1] Servicio Backend (lavadero-backend)"
if systemctl is-active --quiet lavadero-backend; then
    print_ok "Servicio activo"
else
    print_error "Servicio INACTIVO"
    ((ERRORS++))
fi
echo ""

# 2. Verificar Nginx
echo "[2] Servidor Web (Nginx)"
if systemctl is-active --quiet nginx; then
    print_ok "Nginx activo"
else
    print_error "Nginx INACTIVO"
    ((ERRORS++))
fi
echo ""

# 3. Verificar MySQL
echo "[3] Base de Datos (MySQL)"
if systemctl is-active --quiet mysql; then
    print_ok "MySQL activo"
else
    print_error "MySQL INACTIVO"
    ((ERRORS++))
fi
echo ""

# 4. Verificar endpoint de health
echo "[4] Health Check API"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
if [ "$HEALTH_RESPONSE" = "200" ]; then
    print_ok "API respondiendo correctamente (HTTP 200)"
else
    print_error "API no responde correctamente (HTTP $HEALTH_RESPONSE)"
    ((ERRORS++))
fi
echo ""

# 5. Verificar espacio en disco
echo "[5] Espacio en Disco"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_ok "Espacio disponible: $((100-DISK_USAGE))% libre"
elif [ "$DISK_USAGE" -lt 90 ]; then
    print_warning "Espacio en disco al $DISK_USAGE% - Considerar limpieza"
else
    print_error "Espacio crítico: $DISK_USAGE% usado"
    ((ERRORS++))
fi
echo ""

# 6. Verificar memoria
echo "[6] Memoria RAM"
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ "$MEM_USAGE" -lt 80 ]; then
    print_ok "Memoria RAM: $MEM_USAGE% en uso"
elif [ "$MEM_USAGE" -lt 90 ]; then
    print_warning "Memoria RAM al $MEM_USAGE%"
else
    print_error "Memoria RAM crítica: $MEM_USAGE% en uso"
fi
echo ""

# 7. Verificar conexión a MySQL
if [ -f "$APP_DIR/.env" ]; then
    source $APP_DIR/.env
    echo "[7] Conexión a Base de Datos"
    if mysql -u $DB_USER -p$DB_PASSWORD -e "USE $DB_NAME" 2>/dev/null; then
        print_ok "Conexión a base de datos exitosa"
    else
        print_error "No se puede conectar a la base de datos"
        ((ERRORS++))
    fi
    echo ""
fi

# 8. Verificar últimos errores en logs
echo "[8] Errores Recientes en Logs"
RECENT_ERRORS=$(journalctl -u lavadero-backend --since "5 minutes ago" --no-pager | grep -i "error" | wc -l)
if [ "$RECENT_ERRORS" -eq 0 ]; then
    print_ok "Sin errores en los últimos 5 minutos"
else
    print_warning "$RECENT_ERRORS errores encontrados en los últimos 5 minutos"
fi
echo ""

# Resumen
echo "=============================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}Estado General: SALUDABLE${NC}"
    echo "Todos los servicios están funcionando correctamente"
else
    echo -e "${RED}Estado General: PROBLEMAS DETECTADOS${NC}"
    echo "Se encontraron $ERRORS problemas críticos"
    echo ""
    echo "Acciones recomendadas:"
    echo "1. Revisar logs: journalctl -u lavadero-backend -n 50"
    echo "2. Verificar configuración: nginx -t"
    echo "3. Reiniciar servicios si es necesario"
fi
echo "=============================================="

# Salir con código de error si hay problemas (útil para monitoreo automatizado)
exit $ERRORS
