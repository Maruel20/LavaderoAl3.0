#!/bin/bash

###############################################################################
# Script de Deployment Automatizado para Lavadero AL
# Uso: ./deploy.sh
###############################################################################

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
APP_DIR="/home/lavadero/LavaderoAl3.0"
APP_USER="lavadero"
SERVICE_NAME="lavadero-backend"

# Función para imprimir mensajes
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

# Verificar que el script se ejecute como root
if [ "$EUID" -ne 0 ]; then
    print_error "Por favor ejecuta este script como root (usa sudo)"
    exit 1
fi

print_info "==================================================================="
print_info "Script de Deployment Automatizado - Lavadero AL"
print_info "==================================================================="

# Paso 1: Actualizar sistema
print_info "Paso 1: Actualizando sistema..."
apt update && apt upgrade -y
print_success "Sistema actualizado"

# Paso 2: Instalar dependencias del sistema
print_info "Paso 2: Instalando dependencias del sistema..."
apt install -y python3 python3-pip python3-venv python3-dev \
    mysql-server nginx git curl build-essential

# Instalar Node.js 20.x
if ! command -v node &> /dev/null; then
    print_info "Instalando Node.js 20.x..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

print_success "Dependencias instaladas"

# Paso 3: Configurar MySQL
print_info "Paso 3: Configurando MySQL..."
systemctl start mysql
systemctl enable mysql

# Pedir credenciales de base de datos
read -p "Ingresa el nombre de la base de datos [lavadero_al]: " DB_NAME
DB_NAME=${DB_NAME:-lavadero_al}

read -p "Ingresa el usuario de la base de datos [lavadero_user]: " DB_USER
DB_USER=${DB_USER:-lavadero_user}

read -sp "Ingresa la contraseña para el usuario de la base de datos: " DB_PASSWORD
echo

# Crear base de datos y usuario
mysql -u root <<MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

print_success "MySQL configurado"

# Paso 4: Crear usuario de aplicación
print_info "Paso 4: Creando usuario de aplicación..."
if ! id -u $APP_USER > /dev/null 2>&1; then
    adduser --disabled-password --gecos "" $APP_USER
    print_success "Usuario $APP_USER creado"
else
    print_warning "Usuario $APP_USER ya existe"
fi

# Paso 5: Clonar o actualizar repositorio
print_info "Paso 5: Configurando código de la aplicación..."

if [ -d "$APP_DIR" ]; then
    print_warning "El directorio $APP_DIR ya existe. ¿Quieres actualizarlo desde Git? (s/n)"
    read -p "" UPDATE_REPO
    if [ "$UPDATE_REPO" = "s" ] || [ "$UPDATE_REPO" = "S" ]; then
        cd $APP_DIR
        sudo -u $APP_USER git pull
        print_success "Repositorio actualizado"
    fi
else
    read -p "Ingresa la URL del repositorio Git: " REPO_URL
    sudo -u $APP_USER git clone $REPO_URL $APP_DIR
    print_success "Repositorio clonado"
fi

cd $APP_DIR

# Paso 6: Configurar backend
print_info "Paso 6: Configurando backend Python..."

# Crear entorno virtual
if [ ! -d "venv" ]; then
    sudo -u $APP_USER python3 -m venv venv
    print_success "Entorno virtual creado"
fi

# Instalar dependencias de Python
print_info "Instalando dependencias de Python..."
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r backend/requirements.txt"
print_success "Dependencias de Python instaladas"

# Paso 7: Configurar variables de entorno
print_info "Paso 7: Configurando variables de entorno..."

read -p "Ingresa tu dominio (ej: ejemplo.com): " DOMAIN
read -sp "Ingresa una SECRET_KEY para JWT (mín 32 caracteres): " SECRET_KEY
echo

# Crear archivo .env
cat > $APP_DIR/.env <<ENV_FILE
# Base de Datos
DB_HOST=localhost
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_NAME}
DB_PORT=3306

# JWT
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256

# CORS
ALLOWED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}
ENV_FILE

chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env
print_success "Archivo .env configurado"

# Paso 8: Compilar frontend
print_info "Paso 8: Compilando frontend..."

# Configurar variables de entorno del frontend
print_info "Configurando variables de entorno del frontend..."
cat > $APP_DIR/.env.production <<FRONTEND_ENV
# Variables de entorno para producción - Frontend
# Generado automáticamente el $(date)

# URL del API en producción
VITE_API_URL=https://${DOMAIN}/api
FRONTEND_ENV

chown $APP_USER:$APP_USER $APP_DIR/.env.production
print_success "Variables de entorno del frontend configuradas"

# Instalar dependencias de Node.js
sudo -u $APP_USER npm install

# Compilar para producción
sudo -u $APP_USER npm run build
print_success "Frontend compilado"

# Paso 9: Configurar servicio systemd
print_info "Paso 9: Configurando servicio systemd..."

cp $APP_DIR/deployment/lavadero-backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# Verificar estado del servicio
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Servicio $SERVICE_NAME iniciado correctamente"
else
    print_error "Error al iniciar el servicio. Verifica los logs con: journalctl -u $SERVICE_NAME -n 50"
fi

# Paso 10: Configurar Nginx
print_info "Paso 10: Configurando Nginx..."

# Copiar configuración de Nginx
cp $APP_DIR/deployment/nginx-lavadero.conf /etc/nginx/sites-available/lavadero

# Actualizar dominio en la configuración
sed -i "s/tudominio.com/${DOMAIN}/g" /etc/nginx/sites-available/lavadero

# Habilitar sitio
ln -sf /etc/nginx/sites-available/lavadero /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Verificar configuración
if nginx -t; then
    systemctl restart nginx
    systemctl enable nginx
    print_success "Nginx configurado correctamente"
else
    print_error "Error en la configuración de Nginx"
    exit 1
fi

# Paso 11: Configurar firewall
print_info "Paso 11: Configurando firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable
print_success "Firewall configurado"

# Paso 12: Configurar SSL (opcional)
print_info "Paso 12: ¿Quieres configurar SSL con Let's Encrypt ahora? (s/n)"
read -p "" SETUP_SSL

if [ "$SETUP_SSL" = "s" ] || [ "$SETUP_SSL" = "S" ]; then
    apt install -y certbot python3-certbot-nginx
    certbot --nginx -d $DOMAIN -d www.$DOMAIN
    print_success "SSL configurado"
else
    print_warning "Puedes configurar SSL más tarde con: certbot --nginx -d $DOMAIN -d www.$DOMAIN"
fi

# Resumen final
print_info "==================================================================="
print_success "¡Deployment completado con éxito!"
print_info "==================================================================="
echo ""
print_info "Detalles de la instalación:"
echo "  - Aplicación: $APP_DIR"
echo "  - Usuario: $APP_USER"
echo "  - Base de datos: $DB_NAME"
echo "  - Dominio: $DOMAIN"
echo ""
print_info "URLs de acceso:"
echo "  - Frontend: http://$DOMAIN (o https:// si configuraste SSL)"
echo "  - API: http://$DOMAIN/api"
echo "  - Health check: http://$DOMAIN/health"
echo ""
print_info "Comandos útiles:"
echo "  - Ver logs del backend: journalctl -u $SERVICE_NAME -f"
echo "  - Reiniciar backend: systemctl restart $SERVICE_NAME"
echo "  - Reiniciar Nginx: systemctl restart nginx"
echo "  - Ver logs de Nginx: tail -f /var/log/nginx/lavadero_error.log"
echo ""
print_success "¡Tu aplicación está lista para usarse!"
