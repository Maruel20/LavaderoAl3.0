# ⚡ Quick Start - Docker

Guía ultra-rápida para desplegar Lavadero AL con Docker en **menos de 5 minutos**.

## 🚀 Inicio Rápido (3 comandos)

```bash
# 1. Configurar variables de entorno
cp .env.docker.example .env
nano .env  # Editar passwords y SECRET_KEY

# 2. Levantar todo
docker compose up -d --build

# 3. Acceder
# Frontend: http://localhost
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 📋 Requisitos Previos

- Docker instalado ([Guía de instalación](https://docs.docker.com/get-docker/))
- Docker Compose instalado
- Puertos 80, 8000, 3306 disponibles

## ⚙️ Configuración Mínima del .env

```bash
MYSQL_ROOT_PASSWORD=tu_password_root
DB_USER=lavadero_user
DB_PASSWORD=tu_password_seguro
DB_NAME=lavadero_al
SECRET_KEY=$(openssl rand -hex 32)  # Genera uno único
ENVIRONMENT=production
```

## 🔑 Credenciales por Defecto

**Admin**: `admin` / `admin123`
**Empleado**: `empleado1` / `emp123`

> ⚠️ Cambiar inmediatamente en producción

## 📊 Comandos Esenciales

```bash
# Ver estado
docker compose ps

# Ver logs
docker compose logs -f

# Reiniciar
docker compose restart

# Detener
docker compose down

# Actualizar
git pull && docker compose up -d --build
```

## 💾 Backup Rápido

```bash
docker compose exec mysql mysqldump -u root -p lavadero_al > backup.sql
```

## 🔧 Troubleshooting

```bash
# Problema: Backend no inicia
docker compose logs backend

# Problema: MySQL no conecta
docker compose restart mysql
docker compose logs mysql | grep "ready for connections"

# Problema: Puerto en uso
sudo lsof -i :80
sudo lsof -i :8000
```

## 📚 Documentación Completa

- **Guía Detallada Docker**: [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Paso a paso completo
- **Guía Completa Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md) - Todas las opciones
- **Instalación Local**: [INSTALACION.md](INSTALACION.md) - Desarrollo local

## ✅ Verificación

```bash
# Backend responde
curl http://localhost:8000
# Debe retornar: {"message":"API del Lavadero funcionando correctamente 🚀"}

# Frontend accesible
curl -I http://localhost
# Debe retornar: HTTP/1.1 200 OK
```

## 🌍 Acceso Remoto

Si tu servidor tiene IP pública (ej: 192.168.1.100):

- Frontend: `http://192.168.1.100`
- Backend: `http://192.168.1.100:8000`
- Docs: `http://192.168.1.100:8000/docs`

---

**¿Necesitas más detalle?** → Lee [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
