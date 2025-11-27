# 🌐 Guía Paso a Paso: Deployment en Render.com

Render.com es una plataforma moderna que facilita el deployment de aplicaciones full-stack. Esta guía te llevará desde cero hasta tener tu aplicación Lavadero AL funcionando en producción.

---

## 🎯 ¿Por Qué Render?

- ✅ **Gratis para empezar** (con limitaciones)
- ✅ **SSL automático** (HTTPS)
- ✅ **Deploy automático** desde Git
- ✅ **Fácil configuración**
- ✅ **Base de datos MySQL incluida**
- ✅ **Dominio personalizado gratis**

---

## 📋 Requisitos Previos

1. **Cuenta en Render.com** (gratis)
   - Crear cuenta en: https://render.com
   - Conectar con GitHub

2. **Repositorio en GitHub**
   - Tu proyecto debe estar en GitHub (público o privado)
   - Render se conectará automáticamente

3. **Tu proyecto actualizado**
   ```bash
   git push origin main  # Asegúrate de tener los últimos cambios
   ```

---

## 🗂️ Paso 1: Preparar Archivos para Render

### 1.1 Crear Archivo de Configuración del Backend

Crea `backend/render.yaml`:

```yaml
services:
  - type: web
    name: lavadero-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DB_HOST
        fromDatabase:
          name: lavadero-db
          property: host
      - key: DB_PORT
        fromDatabase:
          name: lavadero-db
          property: port
      - key: DB_USER
        fromDatabase:
          name: lavadero-db
          property: user
      - key: DB_PASSWORD
        fromDatabase:
          name: lavadero-db
          property: password
      - key: DB_NAME
        fromDatabase:
          name: lavadero-db
          property: database

databases:
  - name: lavadero-db
    databaseName: lavadero_al
    user: lavadero_user
```

### 1.2 Crear Script de Inicio para el Backend

Crea `backend/start.sh`:

```bash
#!/bin/bash

# Script de inicio para Render
echo "Iniciando backend en Render..."

# Esperar a que MySQL esté listo
echo "Esperando MySQL..."
sleep 10

# Iniciar uvicorn
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

```bash
# Hacer el script ejecutable
chmod +x backend/start.sh
```

### 1.3 Actualizar main.py para Render

Lee el archivo actual:

```bash
cat backend/main.py
```

Asegúrate de que tenga configuración de CORS correcta. Si necesitas editarlo:

```python
# En backend/main.py, la sección de CORS debe permitir tu dominio de Render
origins = [
    "http://localhost:5173",
    "http://localhost:80",
    "https://*.onrender.com",  # Agregar esto
    "*"  # En producción, especifica tu dominio
]
```

### 1.4 Crear Configuración del Frontend

Crea `render-frontend.yaml` en la raíz:

```yaml
services:
  - type: web
    name: lavadero-frontend
    env: node
    buildCommand: npm install && npm run build
    staticPublishPath: ./dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

---

## 🚀 Paso 2: Crear Base de Datos MySQL en Render

### 2.1 Crear Servicio de Base de Datos

1. Ve a tu **Dashboard de Render**: https://dashboard.render.com
2. Click en **"New +"** → **"MySQL"**

3. **Configurar la base de datos:**
   - **Name**: `lavadero-db`
   - **Database**: `lavadero_al`
   - **User**: `lavadero_user`
   - **Region**: Selecciona el más cercano (ej: Ohio, Oregon)
   - **Plan**:
     - **Free** (limitado, para pruebas)
     - **Starter $7/mes** (recomendado para producción)

4. Click en **"Create Database"**

5. **Esperar a que se cree** (2-3 minutos)
   - Verás: "Database is being created..."
   - Cuando esté listo: "Your database is live"

### 2.2 Guardar Credenciales

Una vez creada, verás:

```
Internal Database URL: mysql://usuario:password@host:3306/lavadero_al
External Database URL: mysql://usuario:password@host:3306/lavadero_al
Host: dpg-xxxxx.oregon-postgres.render.com
Port: 3306
Database: lavadero_al
Username: lavadero_user
Password: xxxxxxxxxxxxx
```

**Guarda estas credenciales** - las necesitarás después.

### 2.3 Importar Schema de Base de Datos

Render no tiene interfaz gráfica para MySQL, así que usaremos conexión desde tu computadora:

```bash
# Instalar cliente MySQL si no lo tienes
sudo apt install mysql-client  # Ubuntu/Debian
brew install mysql-client      # macOS

# Conectar a la base de datos de Render
mysql -h [HOST_DE_RENDER] -u lavadero_user -p lavadero_al

# Cuando te pida password, ingresa el password de Render
```

Una vez conectado:

```sql
-- Copiar y pegar el contenido de backend/schema.sql
-- O importarlo directamente:
```

Desde terminal (más fácil):

```bash
mysql -h [HOST_DE_RENDER] -u lavadero_user -p lavadero_al < backend/schema.sql
```

---

## 🔧 Paso 3: Desplegar Backend en Render

### 3.1 Crear Web Service para Backend

1. En Dashboard de Render: **"New +"** → **"Web Service"**

2. **Conectar Repositorio:**
   - Click en **"Connect a repository"**
   - Si es la primera vez, autoriza Render a acceder a GitHub
   - Selecciona tu repositorio: `LavaderoAl3.0`

3. **Configurar el Servicio:**

   **Basic Info:**
   - **Name**: `lavadero-backend`
   - **Region**: Mismo que la base de datos
   - **Branch**: `main` (o la rama que quieras desplegar)
   - **Root Directory**: `backend`

   **Build & Deploy:**
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

   **Plan:**
   - **Free** (apps dormirán después de 15 min de inactividad)
   - **Starter $7/mes** (recomendado, siempre activo)

4. **Variables de Entorno** (Importante):

   Click en **"Advanced"** → **"Add Environment Variable"**

   Agregar una por una:

   | Key | Value |
   |-----|-------|
   | `DB_HOST` | [HOST de tu MySQL en Render] |
   | `DB_PORT` | `3306` |
   | `DB_USER` | `lavadero_user` |
   | `DB_PASSWORD` | [PASSWORD de tu MySQL] |
   | `DB_NAME` | `lavadero_al` |
   | `SECRET_KEY` | [Genera uno con `openssl rand -hex 32`] |
   | `ENVIRONMENT` | `production` |
   | `PYTHON_VERSION` | `3.11.0` |

   > 💡 **Tip**: Puedes copiar estos valores desde la página de tu base de datos MySQL

5. **Crear el Servicio:**
   - Click en **"Create Web Service"**
   - Render empezará a construir y desplegar
   - Verás los logs en tiempo real

6. **Esperar el Deploy** (3-5 minutos):
   ```
   ==> Building...
   ==> Installing dependencies...
   ==> Starting server...
   ==> Your service is live 🎉
   ```

7. **Obtener la URL del Backend:**
   - Render te dará una URL como: `https://lavadero-backend.onrender.com`
   - **Guarda esta URL** - la necesitarás para el frontend

8. **Verificar que Funciona:**
   ```bash
   curl https://lavadero-backend.onrender.com
   # Deberías ver: {"message":"API del Lavadero funcionando correctamente 🚀"}
   ```

---

## 🎨 Paso 4: Desplegar Frontend en Render

### 4.1 Configurar URL del Backend en el Proyecto

Primero, actualiza tu frontend para usar la URL del backend de Render:

```bash
# Editar el archivo de configuración
nano src/services/api.js
```

Busca esta línea:
```javascript
const API_URL = 'http://localhost:8000/api';
```

Cámbiala a:
```javascript
// Usar variable de entorno o URL de producción
const API_URL = import.meta.env.VITE_API_URL || 'https://lavadero-backend.onrender.com/api';
```

### 4.2 Commit y Push de Cambios

```bash
git add src/services/api.js
git commit -m "Update API URL for Render deployment"
git push origin main
```

### 4.3 Crear Static Site para Frontend

1. En Dashboard: **"New +"** → **"Static Site"**

2. **Conectar Repositorio:**
   - Selecciona: `LavaderoAl3.0`

3. **Configurar el Sitio:**

   **Basic Info:**
   - **Name**: `lavadero-frontend`
   - **Branch**: `main`
   - **Root Directory**: `.` (dejar vacío o poner punto)

   **Build Settings:**
   - **Build Command**:
     ```bash
     npm install && npm run build
     ```
   - **Publish Directory**:
     ```
     dist
     ```

4. **Variables de Entorno:**

   Click en **"Advanced"** → **"Add Environment Variable"**

   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://lavadero-backend.onrender.com/api` |
   | `NODE_VERSION` | `20.19.0` |

5. **Crear el Sitio:**
   - Click en **"Create Static Site"**
   - Render construirá tu frontend

6. **Esperar el Build** (2-3 minutos)

7. **Obtener URL del Frontend:**
   - Render te dará una URL como: `https://lavadero-frontend.onrender.com`

---

## ✅ Paso 5: Verificar el Deployment

### 5.1 Probar Backend

```bash
# Health check
curl https://lavadero-backend.onrender.com

# Probar endpoint
curl https://lavadero-backend.onrender.com/api/empleados
```

### 5.2 Probar Frontend

1. Abre en el navegador: `https://lavadero-frontend.onrender.com`
2. Deberías ver la página de login
3. Intenta iniciar sesión:
   - Usuario: `admin`
   - Contraseña: `admin123`

### 5.3 Verificar Conexión Frontend-Backend

1. Abre **DevTools** del navegador (F12)
2. Ve a **Console**
3. No deberías ver errores de CORS
4. Ve a **Network**
5. Deberías ver requests exitosos a tu backend

---

## 🔧 Paso 6: Configuración Adicional

### 6.1 Configurar Dominio Personalizado (Opcional)

**Para el Frontend:**
1. Ve a tu Static Site en Render
2. Click en **"Settings"** → **"Custom Domain"**
3. Ingresa tu dominio: `milavadero.com`
4. Sigue las instrucciones para configurar DNS
5. Render configurará SSL automáticamente

**Para el Backend:**
1. Ve a tu Web Service en Render
2. Click en **"Settings"** → **"Custom Domain"**
3. Ingresa tu subdominio: `api.milavadero.com`
4. Configura DNS según las instrucciones

### 6.2 Configurar Auto-Deploy

**Ya está configurado por defecto:**
- Cada push a la rama `main` desplegará automáticamente
- Puedes cambiar esto en **Settings** → **"Build & Deploy"**

### 6.3 Configurar Health Checks

1. Ve a **Settings** → **"Health & Alerts"**
2. Configura:
   - **Health Check Path**: `/`
   - **Alert Email**: Tu email

### 6.4 Ver Logs

**Backend:**
- Ve a tu Web Service
- Click en **"Logs"**
- Verás logs en tiempo real

**Frontend:**
- Ve a tu Static Site
- Click en **"Logs"**
- Verás logs de build

---

## 🔄 Paso 7: Actualizar la Aplicación

### 7.1 Deploy Automático

```bash
# Simplemente haz push a GitHub
git add .
git commit -m "Nueva funcionalidad"
git push origin main

# Render detectará los cambios y desplegará automáticamente
```

### 7.2 Deploy Manual

1. Ve a tu servicio en Render
2. Click en **"Manual Deploy"** → **"Deploy latest commit"**
3. O selecciona un commit específico

### 7.3 Rollback

1. Ve a **"Events"**
2. Encuentra el deploy anterior
3. Click en **"Rollback"**

---

## 💾 Paso 8: Backups y Mantenimiento

### 8.1 Backup de Base de Datos

**Desde tu computadora:**

```bash
# Crear backup
mysqldump -h [HOST_DE_RENDER] -u lavadero_user -p lavadero_al > backup_$(date +%Y%m%d).sql

# Comprimir
gzip backup_$(date +%Y%m%d).sql
```

**Configurar Backups Automáticos:**

Render (en planes pagos) incluye backups automáticos. Para el plan Free, configura un cron local:

```bash
# Editar crontab en tu computadora
crontab -e

# Agregar (backup diario a las 2 AM)
0 2 * * * /path/to/backup-script.sh
```

Crear `backup-script.sh`:

```bash
#!/bin/bash
BACKUP_DIR="$HOME/backups/lavadero"
mkdir -p "$BACKUP_DIR"

mysqldump -h [HOST] -u [USER] -p[PASSWORD] lavadero_al | gzip > "$BACKUP_DIR/backup_$(date +\%Y\%m\%d).sql.gz"

# Mantener solo últimos 30 días
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
```

### 8.2 Monitoreo

**UptimeRobot (Gratis):**
1. Registrarse en: https://uptimerobot.com
2. Agregar monitor HTTP(s)
3. URL: Tu frontend y backend
4. Recibirás alertas si caen

**Render Metrics:**
- CPU, Memory, Request Count
- Disponible en cada servicio

---

## 💰 Paso 9: Costos y Planes

### Plan Gratuito (Free)

**Incluye:**
- ✅ Static Sites ilimitados
- ✅ Web Services (con limitaciones)
- ✅ 750 horas de compute/mes
- ❌ Apps se duermen después de 15 min de inactividad
- ❌ MySQL no incluido en free tier

**Limitaciones:**
- Backend se dormirá y tardará ~30 segundos en "despertar"
- No recomendado para producción

### Plan Starter ($7/mes por servicio)

**Incluye:**
- ✅ Apps siempre activas
- ✅ Más recursos (512MB RAM)
- ✅ No se duermen
- ✅ Priority support

**Para este proyecto necesitas:**
- MySQL Database: $7-15/mes (según tamaño)
- Backend Web Service: $7/mes
- Frontend Static Site: Gratis
- **Total: ~$14-22/mes**

---

## 🔍 Paso 10: Troubleshooting

### Backend no inicia

**Ver logs:**
1. Ve a tu Web Service
2. Click en **"Logs"**
3. Busca errores

**Errores comunes:**

```
Error: Can't connect to MySQL
→ Verifica variables de entorno DB_HOST, DB_USER, DB_PASSWORD

Error: Port already in use
→ No uses puerto fijo, usa: --port $PORT

Error: Module not found
→ Verifica requirements.txt, redeploy
```

### Frontend no conecta al Backend

**Verificar CORS:**

En `backend/main.py`:

```python
origins = [
    "https://lavadero-frontend.onrender.com",  # Tu dominio frontend
    "https://*.onrender.com",
]
```

Redeploy backend después de cambiar.

### Base de Datos no conecta

**Verificar credenciales:**

```bash
# Desde tu computadora
mysql -h [HOST] -u [USER] -p [DATABASE]

# Si no conecta, verifica:
# - Host correcto
# - Puerto (3306)
# - Usuario y password
# - Que tu IP no esté bloqueada (Render permite todas)
```

### App muy lenta (Plan Free)

**Problema:** Apps gratis se duermen después de 15 minutos.

**Soluciones:**
1. Upgrade a plan Starter ($7/mes)
2. Usar un "keep-alive" service (ping cada 10 min)
3. Aceptar el delay de 30 segundos en primera carga

---

## 📊 Paso 11: Optimizaciones

### 11.1 Mejorar Tiempo de Build

Crear `.npmrc` en la raíz:

```
# Usar cache
cache=.npm
```

### 11.2 Comprimir Respuestas

En `backend/main.py`:

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

### 11.3 Configurar Redis (Opcional)

Para cache de sesiones:
1. Render → New → Redis
2. Conectar en el backend

---

## ✅ Checklist Final

- [ ] Cuenta de Render creada y conectada a GitHub
- [ ] Base de datos MySQL creada y schema importado
- [ ] Backend desplegado y funcionando
- [ ] Frontend desplegado y conectado al backend
- [ ] Login exitoso desde el frontend
- [ ] Contraseñas por defecto cambiadas
- [ ] Variables de entorno configuradas correctamente
- [ ] Dominio personalizado configurado (opcional)
- [ ] Monitoreo configurado (UptimeRobot)
- [ ] Backups configurados

---

## 🎉 ¡Listo!

Tu aplicación está en producción en Render.com:

- **Frontend**: `https://lavadero-frontend.onrender.com`
- **Backend**: `https://lavadero-backend.onrender.com`
- **API Docs**: `https://lavadero-backend.onrender.com/docs`

---

## 📚 Recursos Adicionales

- **Documentación Render**: https://render.com/docs
- **Soporte Render**: https://render.com/docs/support
- **Status Page**: https://status.render.com
- **Community**: https://community.render.com

---

## 🆘 Ayuda

Si tienes problemas:
1. Revisa los logs en Render Dashboard
2. Verifica variables de entorno
3. Consulta la documentación de Render
4. Abre un ticket de soporte en Render

---

**¿Preguntas?** Déjame saber si necesitas ayuda con algún paso específico.
