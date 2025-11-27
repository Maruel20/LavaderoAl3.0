# Scripts de Deployment - Lavadero AL

Esta carpeta contiene scripts útiles para el deployment y mantenimiento del sistema en producción.

## 📜 Scripts Disponibles

### 1. `setup-vps.sh`

**Propósito**: Configuración inicial completa de un servidor VPS Ubuntu desde cero.

**Uso**:
```bash
sudo bash scripts/setup-vps.sh
```

**Qué hace**:
- ✅ Instala todas las dependencias del sistema (Python, Node.js, MySQL, Nginx)
- ✅ Crea usuario de aplicación
- ✅ Clona el repositorio
- ✅ Configura la base de datos MySQL
- ✅ Instala dependencias del backend y frontend
- ✅ Crea servicio systemd para el backend
- ✅ Configura Nginx como proxy reverso
- ✅ Configura el firewall (UFW)
- ✅ Configura backup automático diario

**Cuándo usarlo**: Al configurar un servidor nuevo por primera vez.

---

### 2. `deploy.sh`

**Propósito**: Actualizar la aplicación con los últimos cambios de Git.

**Uso**:
```bash
bash scripts/deploy.sh
```

**Qué hace**:
- ✅ Crea backup de la base de datos
- ✅ Obtiene últimos cambios desde Git (git pull)
- ✅ Actualiza dependencias del backend
- ✅ Actualiza dependencias del frontend y construye
- ✅ Reinicia servicios (backend y nginx)
- ✅ Verifica que los servicios estén corriendo

**Cuándo usarlo**: Cada vez que quieras desplegar nuevos cambios o actualizaciones.

---

### 3. `backup-db.sh`

**Propósito**: Crear backup de la base de datos.

**Uso**:
```bash
bash scripts/backup-db.sh
```

**Qué hace**:
- ✅ Crea un dump de la base de datos MySQL
- ✅ Comprime el backup con gzip
- ✅ Guarda el backup con timestamp
- ✅ Mantiene solo los últimos 7 días de backups
- ✅ Muestra información del backup creado

**Ubicación de backups**: `/home/lavadero/backups/`

**Formato**: `lavadero_al_YYYYMMDD_HHMMSS.sql.gz`

**Restaurar un backup**:
```bash
gunzip < /home/lavadero/backups/lavadero_al_20240120_140000.sql.gz | mysql -u lavadero_user -p lavadero_al
```

**Cuándo usarlo**:
- Antes de actualizaciones importantes
- Se ejecuta automáticamente todos los días a las 2 AM (configurado por setup-vps.sh)

---

### 4. `health-check.sh`

**Propósito**: Verificar el estado de salud de todos los servicios.

**Uso**:
```bash
bash scripts/health-check.sh
```

**Qué hace**:
- ✅ Verifica estado de servicios (backend, nginx, mysql)
- ✅ Verifica que los endpoints HTTP respondan correctamente
- ✅ Verifica conexión y existencia de la base de datos
- ✅ Muestra uso de recursos (CPU, memoria, disco)
- ✅ Proporciona comandos para ver logs en caso de error

**Cuándo usarlo**:
- Después de un deployment para verificar que todo funciona
- Cuando algo no funciona correctamente
- Como parte de monitoreo rutinario

---

## 🔧 Configuración de Crontab

El script `setup-vps.sh` configura automáticamente un backup diario. Si necesitas modificarlo:

```bash
# Editar crontab
crontab -e

# Ejemplo: backup diario a las 2 AM
0 2 * * * /home/lavadero/LavaderoAl3.0/scripts/backup-db.sh

# Ejemplo: health check cada hora
0 * * * * /home/lavadero/LavaderoAl3.0/scripts/health-check.sh >> /var/log/lavadero-health.log
```

---

## 🚨 Solución de Problemas

### Los scripts no son ejecutables

```bash
chmod +x scripts/*.sh
```

### Error de permisos al ejecutar

- `setup-vps.sh` requiere sudo/root
- Otros scripts deben ejecutarse como usuario `lavadero` o con los permisos adecuados

### Script falla durante backup

Verifica las credenciales de MySQL. Puedes configurar un archivo `~/.my.cnf` para evitar ingresar la contraseña:

```ini
[client]
user=lavadero_user
password=tu_password
```

```bash
chmod 600 ~/.my.cnf
```

---

## 📝 Personalización

Puedes modificar las siguientes variables en los scripts:

### En `setup-vps.sh`:
- `APP_USER`: Usuario de la aplicación (default: `lavadero`)
- `REPO_URL`: URL del repositorio Git

### En `backup-db.sh`:
- `BACKUP_DIR`: Directorio de backups (default: `/home/lavadero/backups`)
- `DB_NAME`: Nombre de la base de datos
- `DB_USER`: Usuario de MySQL

### En `deploy.sh`:
- `APP_DIR`: Directorio de la aplicación

---

## 🔗 Referencias

- [Documentación de Deployment](../DEPLOYMENT.md)
- [Documentación de Instalación](../INSTALACION.md)
- [README Principal](../README.md)
