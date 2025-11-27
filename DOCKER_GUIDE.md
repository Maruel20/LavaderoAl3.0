# 🐳 Guía Paso a Paso: Deployment con Docker

Esta guía te llevará desde cero hasta tener tu aplicación Lavadero AL funcionando con Docker.

---

## 📋 Requisitos Previos

### 1. Instalar Docker y Docker Compose

#### En Ubuntu/Debian:

```bash
# Actualizar paquetes
sudo apt update
sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Agregar repositorio de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalación
docker --version
docker compose version
```

#### En macOS:

```bash
# Instalar Docker Desktop desde:
# https://www.docker.com/products/docker-desktop

# O con Homebrew:
brew install --cask docker
```

#### En Windows:

1. Descargar Docker Desktop desde: https://www.docker.com/products/docker-desktop
2. Instalar y reiniciar
3. Verificar en PowerShell: `docker --version`

### 2. Configurar Docker (Linux)

```bash
# Agregar tu usuario al grupo docker (evita usar sudo)
sudo usermod -aG docker $USER

# Aplicar cambios (o reiniciar sesión)
newgrp docker

# Verificar que funciona sin sudo
docker ps
```

---

## 🚀 Paso 1: Preparar el Proyecto

### 1.1 Clonar o Actualizar el Repositorio

```bash
# Si es primera vez
git clone https://github.com/Maruel20/LavaderoAl3.0.git
cd LavaderoAl3.0

# Si ya lo tienes, actualizar
cd LavaderoAl3.0
git pull origin main
```

### 1.2 Verificar Archivos Docker

```bash
# Verificar que existan estos archivos
ls -la | grep -E "Dockerfile|docker-compose|.dockerignore"

# Deberías ver:
# - Dockerfile (frontend)
# - docker-compose.yml
# - .dockerignore
# - backend/Dockerfile (backend)
```

---

## ⚙️ Paso 2: Configurar Variables de Entorno

### 2.1 Crear Archivo .env

```bash
# Copiar el template
cp .env.docker.example .env

# Editar el archivo
nano .env
# O usa tu editor favorito: vim, code, etc.
```

### 2.2 Configurar Valores

Edita el archivo `.env` con estos valores:

```bash
# Variables de entorno para Docker Compose

# MySQL Root Password (para el usuario root de MySQL)
MYSQL_ROOT_PASSWORD=MiPasswordRoot2024!Seguro

# Base de datos (credenciales de la aplicación)
DB_USER=lavadero_user
DB_PASSWORD=LavaderoSecure2024!Password
DB_NAME=lavadero_al

# JWT Secret Key - MUY IMPORTANTE: Genera una clave única
SECRET_KEY=tu_clave_super_secreta_de_minimo_32_caracteres_aleatoria_2024

# Entorno
ENVIRONMENT=production
```

### 2.3 Generar SECRET_KEY Seguro (Recomendado)

```bash
# Generar una clave aleatoria segura
openssl rand -hex 32

# O en Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Copia el resultado y pégalo en SECRET_KEY en el archivo .env
```

### 2.4 Verificar Configuración

```bash
# Ver el contenido (sin mostrar contraseñas)
cat .env
```

---

## 🏗️ Paso 3: Construir las Imágenes Docker

### 3.1 Construir Todas las Imágenes

```bash
# Este comando construye las imágenes de frontend y backend
docker compose build

# Esto puede tardar 5-10 minutos la primera vez
# Verás el progreso de:
# - Descarga de imágenes base
# - Instalación de dependencias
# - Construcción del frontend
```

### 3.2 Verificar Imágenes Creadas

```bash
# Ver imágenes creadas
docker images

# Deberías ver algo como:
# REPOSITORY              TAG       SIZE
# lavaderoal30-frontend   latest    ~100MB
# lavaderoal30-backend    latest    ~500MB
# mysql                   8.0       ~500MB
```

---

## 🚢 Paso 4: Levantar los Servicios

### 4.1 Iniciar Todos los Contenedores

```bash
# Modo detached (en background)
docker compose up -d

# Verás algo como:
# [+] Running 4/4
#  ✔ Network lavaderoal30_lavadero_network  Created
#  ✔ Container lavadero_mysql               Started
#  ✔ Container lavadero_backend             Started
#  ✔ Container lavadero_frontend            Started
```

### 4.2 Verificar Estado de Contenedores

```bash
# Ver contenedores corriendo
docker compose ps

# Deberías ver:
# NAME                  STATUS    PORTS
# lavadero_mysql        Up        0.0.0.0:3306->3306/tcp
# lavadero_backend      Up        0.0.0.0:8000->8000/tcp
# lavadero_frontend     Up        0.0.0.0:80->80/tcp
```

### 4.3 Ver Logs en Tiempo Real

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mysql

# Presiona Ctrl+C para salir
```

---

## ✅ Paso 5: Verificar la Instalación

### 5.1 Esperar a que MySQL Inicie

```bash
# MySQL tarda ~30 segundos en inicializar la primera vez
# Verificar estado
docker compose logs mysql | grep "ready for connections"

# Cuando veas esto, MySQL está listo:
# [Server] /usr/sbin/mysqld: ready for connections
```

### 5.2 Verificar Backend

```bash
# Verificar que el backend responde
curl http://localhost:8000

# Deberías ver:
# {"message":"API del Lavadero funcionando correctamente 🚀"}

# Ver health del backend
docker compose logs backend | tail -20
```

### 5.3 Verificar Frontend

```bash
# Verificar que Nginx sirve el frontend
curl -I http://localhost

# Deberías ver:
# HTTP/1.1 200 OK
# Server: nginx
```

---

## 🌐 Paso 6: Acceder a la Aplicación

### 6.1 Abrir en el Navegador

Abre tu navegador y accede a:

- **Frontend (Aplicación Web)**: http://localhost
- **Backend API**: http://localhost:8000
- **Documentación API Interactiva**: http://localhost:8000/docs

### 6.2 Iniciar Sesión

Usa las credenciales por defecto:

**Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`

**Empleado:**
- Usuario: `empleado1`
- Contraseña: `emp123`

> ⚠️ **IMPORTANTE**: Cambia estas contraseñas inmediatamente desde la aplicación.

### 6.3 Si Accedes desde Otra Computadora

Si el servidor está en otra máquina (VPS, servidor local, etc.):

```bash
# Reemplaza X.X.X.X con la IP de tu servidor
http://X.X.X.X           # Frontend
http://X.X.X.X:8000      # Backend
http://X.X.X.X:8000/docs # Docs
```

---

## 🔧 Paso 7: Comandos Útiles

### 7.1 Gestión de Contenedores

```bash
# Ver estado
docker compose ps

# Ver logs
docker compose logs -f

# Reiniciar todos los servicios
docker compose restart

# Reiniciar un servicio específico
docker compose restart backend

# Detener todos los servicios
docker compose stop

# Detener y eliminar contenedores
docker compose down

# Detener y eliminar TODO (incluyendo volúmenes/datos)
docker compose down -v  # ⚠️ CUIDADO: Elimina la base de datos
```

### 7.2 Acceder a un Contenedor

```bash
# Acceder al contenedor del backend
docker compose exec backend bash

# Dentro puedes hacer:
# - Ver archivos: ls
# - Ver variables de entorno: env
# - Ejecutar Python: python
# - Salir: exit

# Acceder a MySQL
docker compose exec mysql mysql -u root -p
# Ingresa el MYSQL_ROOT_PASSWORD

# Ejecutar comandos SQL
docker compose exec mysql mysql -u root -p lavadero_al -e "SHOW TABLES;"
```

### 7.3 Ver Uso de Recursos

```bash
# Ver CPU, memoria, red de cada contenedor
docker stats

# Ver solo un contenedor
docker stats lavadero_backend
```

---

## 💾 Paso 8: Backup de la Base de Datos

### 8.1 Crear Backup Manual

```bash
# Crear backup
docker compose exec mysql mysqldump -u root -p lavadero_al > backup_$(date +%Y%m%d_%H%M%S).sql

# Ingresa el MYSQL_ROOT_PASSWORD cuando lo pida

# Verificar el backup
ls -lh backup_*.sql
```

### 8.2 Restaurar Backup

```bash
# Restaurar desde un backup
docker compose exec -T mysql mysql -u root -p lavadero_al < backup_20240120_140000.sql

# Ingresa el MYSQL_ROOT_PASSWORD
```

### 8.3 Backup Automático

Puedes configurar un cron job:

```bash
# Editar crontab
crontab -e

# Agregar (backup diario a las 2 AM)
0 2 * * * cd /ruta/a/LavaderoAl3.0 && docker compose exec -T mysql mysqldump -u root -pMiPasswordRoot2024!Seguro lavadero_al | gzip > ~/backups/lavadero_$(date +\%Y\%m\%d).sql.gz
```

---

## 🔄 Paso 9: Actualizar la Aplicación

### 9.1 Actualizar desde Git

```bash
# 1. Detener servicios
docker compose down

# 2. Obtener últimos cambios
git pull origin main

# 3. Reconstruir imágenes
docker compose build

# 4. Levantar con nuevas imágenes
docker compose up -d

# 5. Verificar logs
docker compose logs -f
```

### 9.2 Actualizar Solo un Servicio

```bash
# Actualizar solo el backend
docker compose up -d --build backend

# Actualizar solo el frontend
docker compose up -d --build frontend
```

---

## 🌍 Paso 10: Configurar Dominio y SSL (Opcional)

### 10.1 Configurar Dominio

En tu proveedor de dominios (GoDaddy, Namecheap, etc.):

1. Crear registro tipo **A**
2. Apuntar a la IP de tu servidor
3. Esperar propagación DNS (5-30 minutos)

### 10.2 Instalar Nginx como Proxy Reverso

```bash
# Instalar Nginx en el host (no en Docker)
sudo apt install nginx

# Crear configuración
sudo nano /etc/nginx/sites-available/lavadero
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/lavadero /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10.3 Instalar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Seguir las instrucciones
# Certbot configurará automáticamente HTTPS
```

---

## 🔍 Paso 11: Monitoreo y Troubleshooting

### 11.1 Verificar Salud del Sistema

```bash
# Ver todos los logs
docker compose logs

# Ver logs de errores del backend
docker compose logs backend | grep -i error

# Ver logs recientes
docker compose logs --tail=50

# Seguir logs en tiempo real
docker compose logs -f --tail=100
```

### 11.2 Problemas Comunes

#### Backend no inicia

```bash
# Ver logs detallados
docker compose logs backend

# Verificar variables de entorno
docker compose exec backend env | grep DB_

# Reiniciar
docker compose restart backend
```

#### MySQL no conecta

```bash
# Verificar que MySQL esté listo
docker compose logs mysql | grep "ready for connections"

# Probar conexión manualmente
docker compose exec mysql mysql -u root -p

# Verificar puerto
docker compose ps | grep mysql
```

#### Frontend muestra página en blanco

```bash
# Verificar logs de Nginx
docker compose logs frontend

# Verificar que el build se hizo correctamente
docker compose exec frontend ls -la /usr/share/nginx/html/

# Reconstruir
docker compose up -d --build frontend
```

#### Error 502 Bad Gateway

```bash
# Verificar que backend esté corriendo
docker compose ps backend

# Verificar que backend responde
curl http://localhost:8000

# Ver configuración de Nginx
docker compose exec frontend cat /etc/nginx/conf.d/default.conf
```

---

## 📊 Paso 12: Optimizaciones (Producción)

### 12.1 Limitar Recursos

Editar `docker-compose.yml`:

```yaml
services:
  backend:
    # ... otras configuraciones
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 12.2 Configurar Reinicio Automático

```bash
# Asegurar que Docker inicie al arrancar el sistema
sudo systemctl enable docker

# Los contenedores ya tienen restart: unless-stopped
# en docker-compose.yml, así que se reiniciarán automáticamente
```

### 12.3 Limpiar Imágenes Viejas

```bash
# Eliminar imágenes no usadas
docker image prune -a

# Eliminar contenedores detenidos
docker container prune

# Limpiar todo lo no usado
docker system prune -a
```

---

## ✅ Checklist Final

- [ ] Docker y Docker Compose instalados
- [ ] Proyecto clonado/actualizado
- [ ] Archivo `.env` configurado con valores seguros
- [ ] Imágenes construidas (`docker compose build`)
- [ ] Servicios iniciados (`docker compose up -d`)
- [ ] MySQL inicializado y listo
- [ ] Backend responde en http://localhost:8000
- [ ] Frontend accesible en http://localhost
- [ ] Login exitoso con credenciales por defecto
- [ ] Contraseñas por defecto cambiadas
- [ ] Backup configurado
- [ ] (Opcional) Dominio configurado
- [ ] (Opcional) SSL instalado

---

## 🆘 Ayuda Adicional

### Logs Completos

```bash
# Guardar todos los logs para análisis
docker compose logs > logs_completos.txt
```

### Reinicio Completo

```bash
# Si algo sale mal, reinicio desde cero
docker compose down -v  # ⚠️ ELIMINA DATOS
docker compose up -d --build
```

### Contacto

Si tienes problemas:
1. Revisa los logs: `docker compose logs -f`
2. Verifica el archivo `.env`
3. Asegúrate de que los puertos 80, 8000, 3306 estén disponibles
4. Consulta DEPLOYMENT.md para más detalles

---

## 🎉 ¡Felicidades!

Si llegaste hasta aquí, tu aplicación Lavadero AL debería estar funcionando con Docker. 🚀

Para acceder:
- **Aplicación**: http://localhost o http://tu-dominio.com
- **API Docs**: http://localhost:8000/docs
