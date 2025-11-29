# Quick Start - Deployment en 5 Minutos

Esta guía te permite deployar Lavadero AL en un VPS Ubuntu de la forma más rápida posible.

## Prerrequisitos

- VPS Ubuntu 20.04+ con acceso SSH como root
- Dominio apuntando a la IP del VPS (opcional pero recomendado)
- Al menos 1GB RAM y 10GB de espacio en disco

## Deployment Automático en 1 Comando

### Paso 1: Conéctate a tu VPS

```bash
ssh root@tu_ip_del_vps
```

### Paso 2: Clona el repositorio

```bash
git clone https://github.com/Maruel20/LavaderoAl3.0.git
cd LavaderoAl3.0
```

### Paso 3: Ejecuta el script de deployment

```bash
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

### Paso 4: Sigue las instrucciones

El script te pedirá:
- Nombre de la base de datos (presiona Enter para usar el default)
- Usuario de la base de datos (presiona Enter para usar el default)
- Contraseña para la base de datos (¡usa una segura!)
- Tu dominio (ej: milavadero.com)
- SECRET_KEY para JWT (genera una segura de al menos 32 caracteres)
- Si quieres configurar SSL ahora (recomendado: s)

### Paso 5: ¡Listo!

Tu aplicación estará disponible en:
- **Frontend**: https://tudominio.com
- **API**: https://tudominio.com/api
- **Health Check**: https://tudominio.com/health

## Verificación Rápida

```bash
# Verificar estado de los servicios
systemctl status lavadero-backend
systemctl status nginx
systemctl status mysql

# Verificar que el API responda
curl http://localhost:8000/health

# Ver logs en tiempo real
journalctl -u lavadero-backend -f
```

## Actualizar la Aplicación

```bash
cd /home/lavadero/LavaderoAl3.0
chmod +x deployment/update.sh
./deployment/update.sh
```

## Crear Backups

```bash
cd /home/lavadero/LavaderoAl3.0
chmod +x deployment/backup.sh
./deployment/backup.sh
```

## Comandos Útiles

```bash
# Reiniciar backend
systemctl restart lavadero-backend

# Reiniciar Nginx
systemctl restart nginx

# Ver logs del backend
journalctl -u lavadero-backend -n 50

# Ver logs de Nginx
tail -f /var/log/nginx/lavadero_error.log

# Monitorear estado del sistema
./deployment/monitor.sh
```

## Solución de Problemas Comunes

### Error 502 Bad Gateway
```bash
# Verificar que el backend esté corriendo
systemctl status lavadero-backend

# Ver logs para identificar el problema
journalctl -u lavadero-backend -n 100
```

### No puedo conectarme a la base de datos
```bash
# Verificar MySQL
systemctl status mysql

# Probar conexión manual
mysql -u lavadero_user -p lavadero_al
```

### El servicio no inicia
```bash
# Ver logs detallados
journalctl -u lavadero-backend -n 100 --no-pager

# Verificar permisos
chown -R lavadero:lavadero /home/lavadero/LavaderoAl3.0
```

## ¿Necesitas Más Ayuda?

- **Guía completa**: Ver `/DEPLOYMENT_VPS.md`
- **Documentación de deployment**: Ver `/deployment/README.md`
- **Logs**: `journalctl -u lavadero-backend -f`

## Próximos Pasos

1. Configura un dominio personalizado
2. Configura backups automáticos con cron
3. Configura monitoreo automático
4. Importa tus datos existentes
5. Configura usuarios y permisos

¡Tu aplicación ya está en producción! 🚀
