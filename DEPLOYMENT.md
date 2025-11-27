# 🚀 Guía de Deployment - Lavadero AL

Esta guía te ayudará a desplegar el sistema Lavadero AL en producción usando diferentes opciones.

## 📋 Índice

1. [Preparación Previa](#preparación-previa)
2. [Opción 1: Deployment con Docker](#opción-1-deployment-con-docker)
3. [Opción 2: Deployment en VPS (Ubuntu)](#opción-2-deployment-en-vps-ubuntu)
4. [Opción 3: Deployment en Servicios Cloud](#opción-3-deployment-en-servicios-cloud)
5. [Configuración de Base de Datos](#configuración-de-base-de-datos)
6. [Configuración de Dominio y SSL](#configuración-de-dominio-y-ssl)
7. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

---

## 🔧 Preparación Previa

### 1. Variables de Entorno

Crea un archivo `.env` en la carpeta `backend/` con las siguientes variables:

```bash
# Base de Datos - PRODUCCIÓN
DB_HOST=tu_host_mysql
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_password_seguro
DB_NAME=lavadero_al
DB_PORT=3306

# JWT Secret - CAMBIAR OBLIGATORIAMENTE
SECRET_KEY=una_clave_super_segura_de_al_menos_32_caracteres_aleatoria

# Entorno
ENVIRONMENT=production
```

### 2. Checklist Pre-Deployment

- [ ] Cambiar todas las contraseñas por defecto (admin, empleado1)
- [ ] Configurar SECRET_KEY seguro en .env
- [ ] Configurar credenciales de base de datos
- [ ] Revisar configuración de CORS en `backend/main.py`
- [ ] Hacer backup de datos si migras desde desarrollo
- [ ] Probar la aplicación localmente antes de desplegar

---

## 🐳 Opción 1: Deployment con Docker

### Ventajas
- ✅ Fácil de configurar
- ✅ Consistente en cualquier entorno
- ✅ Fácil actualización y rollback
- ✅ Aislamiento de dependencias

### Paso 1: Construir con Docker

Los archivos `Dockerfile`, `docker-compose.yml` y `.dockerignore` ya están incluidos en el proyecto.

```bash
# Construir y levantar los servicios
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Paso 2: Acceder a la Aplicación

- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

### Paso 3: Deployment en Servidor

```bash
# En tu servidor (DigitalOcean, AWS, etc.)
git clone https://github.com/tuusuario/LavaderoAl3.0.git
cd LavaderoAl3.0

# Configurar variables de entorno
cp backend/.env.example backend/.env
nano backend/.env  # Editar con tus datos

# Levantar con Docker
docker-compose up -d --build

# Configurar Nginx como proxy reverso (recomendado)
# Ver sección "Configuración de Dominio y SSL"
```

### Comandos Útiles

```bash
# Ver estado de contenedores
docker-compose ps

# Reiniciar un servicio específico
docker-compose restart backend

# Ver logs de un servicio
docker-compose logs -f backend

# Ejecutar comandos dentro del contenedor
docker-compose exec backend bash

# Actualizar la aplicación
git pull
docker-compose up -d --build

# Backup de la base de datos
docker-compose exec mysql mysqldump -u root -p lavadero_al > backup.sql
```

---

## 🖥 Opción 2: Deployment en VPS (Ubuntu)

### Requisitos del Servidor
- Ubuntu 20.04 o superior
- 2GB RAM mínimo (4GB recomendado)
- 20GB de espacio en disco
- Acceso root o sudo

### Paso 1: Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv nodejs npm mysql-server nginx git

# Verificar versiones
python3 --version  # 3.8+
node --version     # 20.19+
mysql --version    # 5.7+
```

### Paso 2: Configurar MySQL

```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Crear base de datos
sudo mysql -u root -p
```

```sql
CREATE DATABASE lavadero_al CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lavadero_user'@'localhost' IDENTIFIED BY 'tu_password_seguro';
GRANT ALL PRIVILEGES ON lavadero_al.* TO 'lavadero_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Paso 3: Clonar y Configurar el Proyecto

```bash
# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash lavadero
sudo su - lavadero

# Clonar el repositorio
git clone https://github.com/tuusuario/LavaderoAl3.0.git
cd LavaderoAl3.0

# Importar schema de base de datos
mysql -u lavadero_user -p lavadero_al < backend/schema.sql
```

### Paso 4: Configurar Backend

```bash
# Crear entorno virtual
cd backend
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus datos de producción
```

### Paso 5: Configurar Frontend

```bash
cd ..  # Volver a raíz del proyecto
npm install
npm run build  # Construir para producción
```

### Paso 6: Configurar Systemd para Backend

Crea el archivo `/etc/systemd/system/lavadero-backend.service`:

```bash
sudo nano /etc/systemd/system/lavadero-backend.service
```

```ini
[Unit]
Description=Lavadero AL Backend API
After=network.target mysql.service

[Service]
Type=simple
User=lavadero
WorkingDirectory=/home/lavadero/LavaderoAl3.0/backend
Environment="PATH=/home/lavadero/LavaderoAl3.0/backend/venv/bin"
ExecStart=/home/lavadero/LavaderoAl3.0/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Paso 7: Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/lavadero
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    # Frontend (archivos estáticos)
    location / {
        root /home/lavadero/LavaderoAl3.0/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Docs de la API
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

### Paso 8: Activar y Iniciar Servicios

```bash
# Habilitar sitio en Nginx
sudo ln -s /etc/nginx/sites-available/lavadero /etc/nginx/sites-enabled/
sudo nginx -t  # Verificar configuración
sudo systemctl restart nginx

# Iniciar backend
sudo systemctl enable lavadero-backend
sudo systemctl start lavadero-backend

# Verificar estado
sudo systemctl status lavadero-backend
```

### Comandos de Mantenimiento

```bash
# Ver logs del backend
sudo journalctl -u lavadero-backend -f

# Reiniciar backend
sudo systemctl restart lavadero-backend

# Actualizar la aplicación
cd /home/lavadero/LavaderoAl3.0
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..
npm install
npm run build
sudo systemctl restart lavadero-backend
```

---

## ☁️ Opción 3: Deployment en Servicios Cloud

### 3.1 Render.com (Recomendado para Principiantes)

**Backend:**
1. Crear nuevo "Web Service"
2. Conectar repositorio GitHub
3. Configurar:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
4. Agregar variables de entorno (.env)

**Frontend:**
1. Crear nuevo "Static Site"
2. Configurar:
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
3. Configurar variable: `VITE_API_URL=https://tu-backend.onrender.com`

**Base de Datos:**
1. Crear "MySQL Database" en Render
2. Copiar credenciales a variables de entorno del backend

### 3.2 Railway.app

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Agregar MySQL
railway add

# Deploy
railway up
```

### 3.3 Vercel (Solo Frontend)

```bash
npm i -g vercel
vercel login
vercel --prod
```

> **Nota**: Para el backend necesitarás un servicio separado (Render, Railway, etc.)

### 3.4 DigitalOcean App Platform

1. Crear nueva App desde GitHub
2. Detecta automáticamente componentes
3. Agregar base de datos MySQL
4. Configurar variables de entorno
5. Deploy automático

---

## 🗄️ Configuración de Base de Datos

### Backup Automático

Crear script de backup:

```bash
#!/bin/bash
# /home/lavadero/backup-db.sh

BACKUP_DIR="/home/lavadero/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/lavadero_al_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

mysqldump -u lavadero_user -p'tu_password' lavadero_al > $BACKUP_FILE

# Mantener solo últimos 7 días
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completado: $BACKUP_FILE"
```

Agregar a crontab:

```bash
crontab -e

# Backup diario a las 2 AM
0 2 * * * /home/lavadero/backup-db.sh
```

### Optimización de MySQL

```sql
-- Agregar índices para mejor rendimiento
USE lavadero_al;

CREATE INDEX idx_servicios_fecha ON servicios(fecha);
CREATE INDEX idx_servicios_empleado ON servicios(empleado_id);
CREATE INDEX idx_liquidaciones_empleado ON liquidaciones(empleado_id);
CREATE INDEX idx_movimientos_producto ON movimientos_inventario(producto_id);
```

---

## 🔒 Configuración de Dominio y SSL

### Configurar Dominio

1. En tu proveedor de dominios (GoDaddy, Namecheap, etc.):
   - Crear registro A apuntando a la IP de tu servidor
   - Opcional: Crear registro CNAME para www

### Instalar Certificado SSL (Gratis con Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Renovación automática (ya configurado por Certbot)
sudo certbot renew --dry-run
```

Nginx se configurará automáticamente para usar HTTPS.

---

## 📊 Monitoreo y Mantenimiento

### Ver Logs

```bash
# Backend
sudo journalctl -u lavadero-backend -f

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# MySQL
sudo tail -f /var/log/mysql/error.log
```

### Monitoreo de Recursos

```bash
# Uso de CPU y memoria
htop

# Espacio en disco
df -h

# Estado de servicios
sudo systemctl status lavadero-backend nginx mysql
```

### Actualización del Sistema

```bash
# Script de actualización
cd /home/lavadero/LavaderoAl3.0
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..
npm install
npm run build
sudo systemctl restart lavadero-backend
sudo systemctl restart nginx
```

### Firewall

```bash
# Configurar UFW
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw enable
sudo ufw status
```

---

## 🚨 Solución de Problemas

### Backend no inicia

```bash
# Verificar logs
sudo journalctl -u lavadero-backend -n 50

# Verificar que MySQL esté corriendo
sudo systemctl status mysql

# Probar conexión manual
cd /home/lavadero/LavaderoAl3.0/backend
source venv/bin/activate
python -c "from database import get_db_connection; print(get_db_connection())"
```

### Error 502 Bad Gateway

```bash
# Verificar que el backend esté corriendo
sudo systemctl status lavadero-backend

# Reiniciar servicios
sudo systemctl restart lavadero-backend nginx
```

### Base de datos muy lenta

```sql
-- Analizar queries lentas
SHOW PROCESSLIST;

-- Optimizar tablas
OPTIMIZE TABLE servicios;
OPTIMIZE TABLE liquidaciones;
```

---

## 📝 Checklist Final

- [ ] Aplicación desplegada y funcionando
- [ ] SSL/HTTPS configurado
- [ ] Contraseñas por defecto cambiadas
- [ ] Backup automático configurado
- [ ] Firewall configurado
- [ ] Monitoreo básico en su lugar
- [ ] Documentación de accesos guardada de forma segura
- [ ] Pruebas de funcionalidad realizadas

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs correspondientes
2. Verifica que todos los servicios estén corriendo
3. Consulta la [documentación de instalación](INSTALACION.md)
4. Abre un issue en GitHub

---

## 📚 Recursos Adicionales

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación Vue 3](https://vuejs.org/)
- [Guía Nginx](https://nginx.org/en/docs/)
- [DigitalOcean Tutorials](https://www.digitalocean.com/community/tutorials)
- [Let's Encrypt](https://letsencrypt.org/)
