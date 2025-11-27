#!/bin/bash

###############################################################################
# Script de Setup Inicial para VPS - Lavadero AL
# Para Ubuntu 20.04+
# Ejecutar como root o con sudo
###############################################################################

set -e

echo "=========================================="
echo "🛠️  Setup Inicial VPS - Lavadero AL"
echo "=========================================="
echo ""

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "Por favor ejecuta este script como root o con sudo"
    exit 1
fi

# Variables
APP_USER="lavadero"
APP_DIR="/home/$APP_USER/LavaderoAl3.0"
REPO_URL="https://github.com/Maruel20/LavaderoAl3.0.git"  # Cambiar por tu repo

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}==>${NC} $1"
}

# 1. Actualizar sistema
print_step "Actualizando sistema..."
apt update && apt upgrade -y

# 2. Instalar dependencias
print_step "Instalando dependencias..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    mysql-server \
    nginx \
    git \
    curl \
    build-essential \
    libmysqlclient-dev

# 3. Instalar versión específica de Node si es necesaria
print_step "Verificando versión de Node..."
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    print_step "Instalando Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

# 4. Configurar MySQL
print_step "Configurando MySQL..."
mysql_secure_installation

# 5. Crear usuario de aplicación
print_step "Creando usuario de aplicación..."
if id "$APP_USER" &>/dev/null; then
    echo "Usuario $APP_USER ya existe"
else
    useradd -m -s /bin/bash "$APP_USER"
    echo "Usuario $APP_USER creado"
fi

# 6. Clonar repositorio
print_step "Clonando repositorio..."
if [ -d "$APP_DIR" ]; then
    echo "Directorio ya existe, saltando clonación"
else
    su - "$APP_USER" -c "git clone $REPO_URL $APP_DIR"
fi

# 7. Configurar base de datos
print_step "Configurando base de datos..."
echo "Por favor ingresa la información de la base de datos:"
read -p "Contraseña para el usuario lavadero_user: " -s DB_PASSWORD
echo ""

mysql -u root -p <<EOF
CREATE DATABASE IF NOT EXISTS lavadero_al CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'lavadero_user'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON lavadero_al.* TO 'lavadero_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Importar schema
mysql -u root -p lavadero_al < "$APP_DIR/backend/schema.sql"

# 8. Configurar entorno del backend
print_step "Configurando backend..."
su - "$APP_USER" <<USEREOF
cd "$APP_DIR/backend"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Crear .env
cat > .env <<ENVEOF
DB_HOST=localhost
DB_USER=lavadero_user
DB_PASSWORD=$DB_PASSWORD
DB_NAME=lavadero_al
DB_PORT=3306
SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
ENVEOF
USEREOF

# 9. Configurar frontend
print_step "Configurando frontend..."
su - "$APP_USER" <<USEREOF
cd "$APP_DIR"
npm install
npm run build
USEREOF

# 10. Crear servicio systemd para backend
print_step "Creando servicio systemd..."
cat > /etc/systemd/system/lavadero-backend.service <<SERVICEEOF
[Unit]
Description=Lavadero AL Backend API
After=network.target mysql.service

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR/backend
Environment="PATH=$APP_DIR/backend/venv/bin"
ExecStart=$APP_DIR/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# 11. Configurar Nginx
print_step "Configurando Nginx..."
read -p "Ingresa tu dominio (o presiona Enter para usar la IP): " DOMAIN

if [ -z "$DOMAIN" ]; then
    DOMAIN="_"
fi

cat > /etc/nginx/sites-available/lavadero <<NGINXEOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        root $APP_DIR/dist;
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /docs {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
    }
}
NGINXEOF

# Activar sitio
ln -sf /etc/nginx/sites-available/lavadero /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Verificar configuración
nginx -t

# 12. Configurar Firewall
print_step "Configurando firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

# 13. Iniciar servicios
print_step "Iniciando servicios..."
systemctl daemon-reload
systemctl enable lavadero-backend
systemctl start lavadero-backend
systemctl restart nginx

# 14. Configurar backup automático
print_step "Configurando backup automático..."
chmod +x "$APP_DIR/scripts/backup-db.sh"
chmod +x "$APP_DIR/scripts/deploy.sh"

# Agregar a crontab del usuario lavadero
su - "$APP_USER" -c "(crontab -l 2>/dev/null; echo '0 2 * * * $APP_DIR/scripts/backup-db.sh') | crontab -"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Setup completado!${NC}"
echo "=========================================="
echo ""
echo "Servicios:"
systemctl status lavadero-backend --no-pager
echo ""
systemctl status nginx --no-pager
echo ""
echo "Accede a tu aplicación en:"
if [ "$DOMAIN" = "_" ]; then
    IP=$(hostname -I | awk '{print $1}')
    echo "  http://$IP"
else
    echo "  http://$DOMAIN"
fi
echo ""
echo "Documentación API:"
echo "  http://$DOMAIN/docs"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Configura SSL con: sudo certbot --nginx -d $DOMAIN"
echo "2. Cambia las contraseñas por defecto en la aplicación"
echo "3. Revisa los logs: sudo journalctl -u lavadero-backend -f"
