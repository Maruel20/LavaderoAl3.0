# Guía de Deployment en Hostinger VPS Ubuntu

Esta guía te llevará paso a paso para deployar la aplicación Lavadero AL en un VPS de Hostinger con Ubuntu.

## Arquitectura de la Aplicación

- **Backend**: FastAPI (Python) - Puerto 8000
- **Frontend**: Vue.js 3 con Vite - Archivos estáticos
- **Base de Datos**: MySQL
- **Servidor Web**: Nginx (reverse proxy + archivos estáticos)
- **Servidor de Aplicación**: Uvicorn con Systemd

---

## PASO 1: Acceder al VPS y Actualizar el Sistema

Conecta a tu VPS por SSH:

```bash
ssh root@tu_ip_del_vps
```

Actualiza el sistema:

```bash
apt update && apt upgrade -y
```

---

## PASO 2: Instalar Dependencias del Sistema

### 2.1 Instalar Python 3.11+ y herramientas

```bash
apt install -y python3 python3-pip python3-venv python3-dev
```

### 2.2 Instalar Node.js 20.x (para compilar el frontend)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
```

### 2.3 Instalar MySQL Server

```bash
apt install -y mysql-server
```

### 2.4 Instalar Nginx

```bash
apt install -y nginx
```

### 2.5 Instalar Git

```bash
apt install -y git
```

---

## PASO 3: Configurar MySQL

### 3.1 Iniciar y asegurar MySQL

```bash
systemctl start mysql
systemctl enable mysql
mysql_secure_installation
```

Responde las preguntas:
- Set root password: **YES** (elige una contraseña segura)
- Remove anonymous users: **YES**
- Disallow root login remotely: **YES**
- Remove test database: **YES**
- Reload privilege tables: **YES**

### 3.2 Crear base de datos y usuario

```bash
mysql -u root -p
```

Ejecuta estos comandos SQL:

```sql
CREATE DATABASE lavadero_al CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lavadero_user'@'localhost' IDENTIFIED BY 'TU_PASSWORD_SEGURA_AQUI';
GRANT ALL PRIVILEGES ON lavadero_al.* TO 'lavadero_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3.3 Importar el esquema de la base de datos

Si tienes un archivo SQL con el esquema:

```bash
mysql -u root -p lavadero_al < /ruta/a/tu/schema.sql
```

---

## PASO 4: Clonar el Repositorio

### 4.1 Crear usuario de aplicación (recomendado)

```bash
adduser --disabled-password --gecos "" lavadero
```

### 4.2 Clonar el repositorio

```bash
cd /home/lavadero
sudo -u lavadero git clone https://github.com/Maruel20/LavaderoAl3.0.git
cd LavaderoAl3.0
```

O si ya tienes el código, súbelo por SFTP a `/home/lavadero/LavaderoAl3.0`

---

## PASO 5: Configurar el Backend

### 5.1 Crear entorno virtual de Python

```bash
cd /home/lavadero/LavaderoAl3.0
sudo -u lavadero python3 -m venv venv
```

### 5.2 Instalar dependencias de Python

```bash
sudo -u lavadero bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r backend/requirements.txt"
```

### 5.3 Configurar variables de entorno

Crea el archivo `.env` en la raíz del proyecto:

```bash
sudo -u lavadero nano /home/lavadero/LavaderoAl3.0/.env
```

Contenido del archivo `.env`:

```env
# Base de Datos
DB_HOST=localhost
DB_USER=lavadero_user
DB_PASSWORD=TU_PASSWORD_SEGURA_AQUI
DB_NAME=lavadero_al
DB_PORT=3306

# JWT
SECRET_KEY=GENERA_UNA_CLAVE_SUPER_SEGURA_AQUI_min_32_caracteres
ALGORITHM=HS256

# CORS - Agrega tu dominio
ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

Para generar una SECRET_KEY segura:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## PASO 6: Compilar el Frontend

### 6.1 Instalar dependencias de Node.js

```bash
cd /home/lavadero/LavaderoAl3.0
sudo -u lavadero npm install
```

### 6.2 Configurar la URL del backend

Edita el archivo de configuración de Axios (normalmente en `src/` o archivo de configuración):

Busca donde se define la URL base del API y cámbiala a:

```javascript
const API_URL = 'https://tudominio.com/api'
```

### 6.3 Compilar el frontend para producción

```bash
sudo -u lavadero npm run build
```

Esto creará una carpeta `dist/` con los archivos estáticos compilados.

---

## PASO 7: Configurar Systemd para el Backend

Crea el archivo de servicio:

```bash
nano /etc/systemd/system/lavadero-backend.service
```

Pega el contenido del archivo `deployment/lavadero-backend.service` (ver archivos creados).

Habilita e inicia el servicio:

```bash
systemctl daemon-reload
systemctl enable lavadero-backend
systemctl start lavadero-backend
systemctl status lavadero-backend
```

---

## PASO 8: Configurar Nginx

### 8.1 Crear configuración del sitio

```bash
nano /etc/nginx/sites-available/lavadero
```

Pega el contenido del archivo `deployment/nginx-lavadero.conf` (ver archivos creados).

### 8.2 Habilitar el sitio

```bash
ln -s /etc/nginx/sites-available/lavadero /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # Opcional: remover sitio por defecto
```

### 8.3 Verificar configuración

```bash
nginx -t
```

### 8.4 Reiniciar Nginx

```bash
systemctl restart nginx
systemctl enable nginx
```

---

## PASO 9: Configurar Firewall

```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

---

## PASO 10: Configurar SSL con Let's Encrypt (HTTPS)

### 10.1 Instalar Certbot

```bash
apt install -y certbot python3-certbot-nginx
```

### 10.2 Obtener certificado SSL

```bash
certbot --nginx -d tudominio.com -d www.tudominio.com
```

Sigue las instrucciones:
- Ingresa tu email
- Acepta los términos
- Elige si quieres redireccionar HTTP a HTTPS (recomendado: YES)

### 10.3 Verificar renovación automática

```bash
certbot renew --dry-run
```

---

## PASO 11: Verificar Deployment

### 11.1 Verificar backend

```bash
curl http://localhost:8000/health
```

### 11.2 Verificar Nginx

```bash
systemctl status nginx
```

### 11.3 Acceder desde el navegador

- Frontend: `https://tudominio.com`
- API: `https://tudominio.com/api`
- Health check: `https://tudominio.com/api/health`

---

## Comandos Útiles

### Ver logs del backend
```bash
journalctl -u lavadero-backend -f
```

### Ver logs de Nginx
```bash
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Reiniciar servicios
```bash
systemctl restart lavadero-backend
systemctl restart nginx
```

### Actualizar la aplicación
```bash
cd /home/lavadero/LavaderoAl3.0
sudo -u lavadero git pull
sudo -u lavadero npm install
sudo -u lavadero npm run build
sudo -u lavadero bash -c "source venv/bin/activate && pip install -r backend/requirements.txt"
systemctl restart lavadero-backend
```

---

## Solución de Problemas

### El backend no inicia
```bash
journalctl -u lavadero-backend -n 50
```

### Error de conexión a MySQL
```bash
mysql -u lavadero_user -p lavadero_al
# Verifica que puedes conectarte
```

### Error 502 Bad Gateway
- Verifica que el backend esté corriendo: `systemctl status lavadero-backend`
- Verifica los logs: `journalctl -u lavadero-backend -f`

### Permiso denegado
```bash
chown -R lavadero:lavadero /home/lavadero/LavaderoAl3.0
```

---

## Script de Deployment Automatizado

Hemos creado un script para facilitar el deployment. Revisa el archivo:

`deployment/deploy.sh`

Para usarlo:

```bash
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

---

## Seguridad Adicional

1. **Cambiar puerto SSH** (opcional pero recomendado)
2. **Configurar fail2ban** para protección contra ataques de fuerza bruta
3. **Hacer backups regulares de la base de datos**
4. **Mantener el sistema actualizado**: `apt update && apt upgrade`

---

## Mantenimiento

### Backup de base de datos
```bash
mysqldump -u root -p lavadero_al > backup_$(date +%Y%m%d).sql
```

### Monitoreo de recursos
```bash
htop
df -h
free -m
```

---

¿Necesitas ayuda? Revisa los logs y verifica cada paso cuidadosamente.
