# Deployment - Lavadero AL

Esta carpeta contiene todos los archivos necesarios para deployar la aplicación Lavadero AL en un VPS Ubuntu (Hostinger o similar).

## Archivos Incluidos

### Documentación
- **`DEPLOYMENT_VPS.md`** (en raíz): Guía completa paso a paso para deployment manual

### Configuración del Sistema
- **`lavadero-backend.service`**: Archivo de servicio systemd para el backend FastAPI
- **`nginx-lavadero.conf`**: Configuración de Nginx (reverse proxy + archivos estáticos)
- **`.env.production.example`**: Ejemplo de archivo de variables de entorno para producción

### Scripts Automatizados
- **`deploy.sh`**: Script de deployment automático completo (primera instalación)
- **`update.sh`**: Script para actualizar la aplicación (después del deployment inicial)
- **`backup.sh`**: Script para crear backups de la base de datos y código
- **`restore.sh`**: Script para restaurar backups de la base de datos

## Uso Rápido

### Opción 1: Deployment Automatizado (Recomendado)

1. Sube todos los archivos del proyecto a tu VPS
2. Haz ejecutable el script de deployment:
   ```bash
   chmod +x deployment/deploy.sh
   ```
3. Ejecuta el script como root:
   ```bash
   sudo ./deployment/deploy.sh
   ```
4. Sigue las instrucciones en pantalla

### Opción 2: Deployment Manual

Sigue la guía detallada en `/DEPLOYMENT_VPS.md` en la raíz del proyecto.

## Mantenimiento

### Actualizar la aplicación
```bash
chmod +x deployment/update.sh
sudo ./deployment/update.sh
```

### Crear backup
```bash
chmod +x deployment/backup.sh
sudo ./deployment/backup.sh
```

### Restaurar desde backup
```bash
chmod +x deployment/restore.sh
sudo ./deployment/restore.sh /ruta/al/backup.sql.gz
```

## Requisitos del Servidor

- **SO**: Ubuntu 20.04 LTS o superior
- **RAM**: Mínimo 1GB (recomendado 2GB)
- **Espacio**: Mínimo 10GB
- **Acceso**: SSH con permisos root

## Arquitectura del Deployment

```
Internet
    |
    v
[Nginx :80/:443]
    |
    +---> /api/  --> [Uvicorn Backend :8000] --> [MySQL :3306]
    |
    +---> /      --> [Frontend estático (dist/)]
```

## Puertos Utilizados

- **80**: HTTP (Nginx)
- **443**: HTTPS (Nginx)
- **8000**: Backend FastAPI (solo localhost)
- **3306**: MySQL (solo localhost)

## Comandos Útiles

### Ver logs del backend
```bash
journalctl -u lavadero-backend -f
```

### Ver estado del servicio
```bash
systemctl status lavadero-backend
```

### Reiniciar servicios
```bash
systemctl restart lavadero-backend
systemctl restart nginx
```

### Ver logs de Nginx
```bash
tail -f /var/log/nginx/lavadero_error.log
tail -f /var/log/nginx/lavadero_access.log
```

### Verificar configuración de Nginx
```bash
nginx -t
```

## Troubleshooting

### El backend no inicia
```bash
journalctl -u lavadero-backend -n 100 --no-pager
```

### Error de permisos
```bash
chown -R lavadero:lavadero /home/lavadero/LavaderoAl3.0
```

### Error de conexión a MySQL
```bash
mysql -u lavadero_user -p lavadero_al
```

## Seguridad

- Las variables de entorno sensibles se guardan en `.env` con permisos 600
- El servicio se ejecuta con un usuario no privilegiado (`lavadero`)
- Nginx actúa como reverse proxy, el backend no está expuesto directamente
- Se recomienda configurar SSL/TLS con Let's Encrypt
- El firewall (ufw) está configurado para permitir solo puertos necesarios

## Soporte

Para más información, consulta:
- Documentación completa: `/DEPLOYMENT_VPS.md`
- Logs del sistema: `/var/log/nginx/` y `journalctl`
