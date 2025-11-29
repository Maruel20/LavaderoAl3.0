# Importar Base de Datos en el VPS

Esta guía te ayudará a importar tu base de datos existente al VPS de producción.

## Paso 1: Exportar la Base de Datos desde tu Entorno Local

Desde tu computadora local (donde tienes XAMPP o MySQL instalado):

```bash
mysqldump -u root -p lavadero_al > lavadero_al_export.sql
```

Ingresa tu contraseña cuando se te solicite.

## Paso 2: Transferir el Archivo al VPS

### Opción A: Usando SCP (Secure Copy)

Desde tu computadora local:

```bash
scp lavadero_al_export.sql root@tu_ip_del_vps:/tmp/
```

### Opción B: Usando SFTP

1. Usa un cliente SFTP como FileZilla o WinSCP
2. Conecta al VPS con tus credenciales SSH
3. Sube el archivo `lavadero_al_export.sql` a `/tmp/`

### Opción C: Copiar y Pegar (para bases de datos pequeñas)

1. Abre el archivo `.sql` en un editor de texto
2. Copia todo el contenido
3. Conéctate al VPS por SSH
4. Crea el archivo: `nano /tmp/lavadero_al_export.sql`
5. Pega el contenido
6. Guarda: `Ctrl+O`, `Enter`, `Ctrl+X`

## Paso 3: Importar en el VPS

Conéctate al VPS por SSH:

```bash
ssh root@tu_ip_del_vps
```

Importa la base de datos:

```bash
# Cargar variables de entorno
cd /home/lavadero/LavaderoAl3.0
source .env

# Importar la base de datos
mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME < /tmp/lavadero_al_export.sql
```

O si prefieres hacerlo manualmente:

```bash
mysql -u lavadero_user -p lavadero_al < /tmp/lavadero_al_export.sql
```

## Paso 4: Verificar la Importación

```bash
# Conectar a MySQL
mysql -u lavadero_user -p

# Seleccionar la base de datos
USE lavadero_al;

# Ver las tablas
SHOW TABLES;

# Ver algunos registros de ejemplo
SELECT * FROM empleados LIMIT 5;
SELECT * FROM servicios LIMIT 5;

# Salir
EXIT;
```

## Paso 5: Limpiar Archivos Temporales

```bash
rm /tmp/lavadero_al_export.sql
```

## Paso 6: Reiniciar el Servicio Backend

```bash
systemctl restart lavadero-backend
systemctl status lavadero-backend
```

## Troubleshooting

### Error: Access denied for user

Verifica que las credenciales en el archivo `.env` sean correctas:

```bash
cat /home/lavadero/LavaderoAl3.0/.env | grep DB_
```

### Error: Unknown database

Asegúrate de que la base de datos exista:

```bash
mysql -u root -p -e "SHOW DATABASES;"
```

Si no existe, créala:

```bash
mysql -u root -p -e "CREATE DATABASE lavadero_al CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Error: Table already exists

Si necesitas reimportar la base de datos, primero elimina todas las tablas:

```bash
mysql -u lavadero_user -p lavadero_al

# Dentro de MySQL:
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS empleados;
DROP TABLE IF EXISTS servicios;
DROP TABLE IF EXISTS inventario;
DROP TABLE IF EXISTS liquidaciones;
DROP TABLE IF EXISTS convenios;
DROP TABLE IF EXISTS tarifas;
-- Agrega todas tus tablas aquí
SET FOREIGN_KEY_CHECKS = 1;
EXIT;
```

O elimina y recrea la base de datos completa:

```bash
mysql -u root -p -e "DROP DATABASE lavadero_al;"
mysql -u root -p -e "CREATE DATABASE lavadero_al CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON lavadero_al.* TO 'lavadero_user'@'localhost';"
```

## Importación Automatizada

Si vas a hacer esto frecuentemente, puedes usar el script de restauración:

```bash
# Primero sube tu archivo .sql al VPS
# Luego usa el script de restore
./deployment/restore.sh /tmp/lavadero_al_export.sql
```

## Backup Regular

Una vez que tu base de datos esté en producción, es importante hacer backups regulares:

```bash
# Crear backup manualmente
./deployment/backup.sh

# O configurar backups automáticos con cron
crontab -e

# Agregar esta línea para backup diario a las 2 AM:
0 2 * * * /home/lavadero/LavaderoAl3.0/deployment/backup.sh
```

Los backups se guardarán en `/home/lavadero/backups/`
