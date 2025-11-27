# ⚡ Render.com - Quick Start

Guía ultra-rápida para desplegar Lavadero AL en Render.com

---

## 🚀 Opción 1: Deploy con Blueprint (Un Click)

### Paso 1: Preparar
```bash
# Push del código a GitHub (si no lo has hecho)
git push origin main
```

### Paso 2: Deploy en Render
1. Ve a: https://dashboard.render.com/blueprints
2. Click en **"New Blueprint Instance"**
3. Conecta tu repositorio `LavaderoAl3.0`
4. Render detectará `render.yaml`
5. Click en **"Apply"**
6. ¡Listo! 🎉

Render creará automáticamente:
- ✅ Base de datos MySQL
- ✅ Backend API
- ✅ Frontend estático

---

## 🔧 Opción 2: Deploy Manual (Más Control)

### Paso 1: Crear Base de Datos
1. Dashboard → **"New +"** → **"MySQL"**
2. Name: `lavadero-db`
3. Plan: **Starter** ($7/mes)
4. **Create Database**
5. Importar schema:
   ```bash
   mysql -h [HOST] -u [USER] -p lavadero_al < backend/schema.sql
   ```

### Paso 2: Backend
1. **"New +"** → **"Web Service"**
2. Conectar repo `LavaderoAl3.0`
3. Configurar:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   ```
   DB_HOST=[desde la base de datos]
   DB_PORT=3306
   DB_USER=lavadero_user
   DB_PASSWORD=[desde la base de datos]
   DB_NAME=lavadero_al
   SECRET_KEY=[generar con: openssl rand -hex 32]
   ENVIRONMENT=production
   ```
5. **Create Web Service**

### Paso 3: Frontend
1. **"New +"** → **"Static Site"**
2. Conectar repo `LavaderoAl3.0`
3. Configurar:
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. **Environment Variables**:
   ```
   VITE_API_URL=https://[tu-backend].onrender.com/api
   NODE_VERSION=20.19.0
   ```
5. **Create Static Site**

---

## ✅ Verificar

```bash
# Backend
curl https://[tu-backend].onrender.com

# Frontend
# Abrir: https://[tu-frontend].onrender.com
# Login: admin / admin123
```

---

## 💰 Costos

| Servicio | Plan Free | Plan Starter |
|----------|-----------|--------------|
| Frontend | ✅ Gratis | ✅ Gratis |
| Backend | Limitado* | $7/mes |
| MySQL | ❌ No disponible | $7+/mes |
| **Total** | No viable | **~$14/mes** |

*Apps gratis se duermen después de 15 min de inactividad

---

## 🔄 Actualizar

```bash
# Auto-deploy está activado por defecto
git push origin main
# Render desplegará automáticamente
```

---

## 🆘 Troubleshooting

### Backend no inicia
```bash
# Ver logs en: Dashboard → Tu servicio → "Logs"
# Verificar variables de entorno en: "Environment"
```

### Frontend no conecta
```bash
# Verificar CORS en backend/main.py:
origins = ["https://[tu-frontend].onrender.com"]

# Verificar VITE_API_URL en frontend
```

### Base de datos no conecta
```bash
# Probar conexión desde tu PC:
mysql -h [HOST] -u [USER] -p [DATABASE]
```

---

## 📚 Documentación Completa

- **Guía Detallada**: [RENDER_GUIDE.md](RENDER_GUIDE.md)
- **Todas las Opciones**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🔗 URLs Útiles

- **Dashboard**: https://dashboard.render.com
- **Docs**: https://render.com/docs
- **Status**: https://status.render.com
- **Soporte**: https://render.com/docs/support

---

## 🎯 Recomendación

**Para Producción:**
- Plan Starter Backend ($7/mes)
- MySQL Starter ($7/mes)
- Static Site (Gratis)
- **Total: ~$14/mes**

**Para Pruebas:**
- Usar plan Free del backend
- Considerar otra base de datos gratuita (ej: Railway, PlanetScale)

---

**¿Primera vez?** → Lee [RENDER_GUIDE.md](RENDER_GUIDE.md) completo
