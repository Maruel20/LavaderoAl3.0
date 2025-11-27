#!/bin/bash

###############################################################################
# Script de Health Check - Lavadero AL
# Verifica el estado de todos los servicios
###############################################################################

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🏥 Health Check - Lavadero AL"
echo "=========================================="
echo ""

# Función para verificar servicio
check_service() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✅ $service: Corriendo${NC}"
        return 0
    else
        echo -e "${RED}❌ $service: No está corriendo${NC}"
        return 1
    fi
}

# Función para verificar endpoint HTTP
check_endpoint() {
    local url=$1
    local name=$2
    local status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)

    if [ "$status" = "200" ]; then
        echo -e "${GREEN}✅ $name: Responde correctamente (HTTP $status)${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: Error (HTTP $status)${NC}"
        return 1
    fi
}

# Función para verificar MySQL
check_mysql() {
    if mysql -u root -e "SELECT 1;" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ MySQL: Conectado${NC}"

        # Verificar base de datos
        if mysql -u root -e "USE lavadero_al; SELECT 1;" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Base de datos lavadero_al: Existe${NC}"
        else
            echo -e "${RED}❌ Base de datos lavadero_al: No existe${NC}"
        fi
        return 0
    else
        echo -e "${RED}❌ MySQL: No conectado${NC}"
        return 1
    fi
}

# Variables para contar errores
ERRORS=0

# Verificar servicios
echo "📋 Servicios del Sistema:"
check_service "lavadero-backend" || ((ERRORS++))
check_service "nginx" || ((ERRORS++))
check_service "mysql" || ((ERRORS++))

echo ""
echo "🔌 Endpoints HTTP:"
check_endpoint "http://localhost:8000" "Backend API" || ((ERRORS++))
check_endpoint "http://localhost:80" "Frontend" || ((ERRORS++))

echo ""
echo "💾 Base de Datos:"
check_mysql || ((ERRORS++))

echo ""
echo "💻 Uso de Recursos:"
echo "CPU y Memoria:"
top -bn1 | head -20 | grep -E "Cpu|Mem"

echo ""
echo "Disco:"
df -h | grep -E "Filesystem|/$"

echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Todos los servicios funcionan correctamente${NC}"
else
    echo -e "${RED}❌ Se encontraron $ERRORS error(es)${NC}"
    echo ""
    echo "Para ver logs:"
    echo "  Backend: sudo journalctl -u lavadero-backend -n 50"
    echo "  Nginx: sudo tail -n 50 /var/log/nginx/error.log"
    echo "  MySQL: sudo tail -n 50 /var/log/mysql/error.log"
fi
echo "=========================================="
