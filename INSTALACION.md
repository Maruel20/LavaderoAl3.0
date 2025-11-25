# Guía de Instalación - Lavadero AL

## Requisitos Previos

- **Python 3.8+** con pip
- **Node.js 20.19+** con npm
- **MySQL 5.7+** o **MariaDB 10.3+**
- **XAMPP** (recomendado para desarrollo local) o servidor MySQL independiente

## 1. Configuración de la Base de Datos

### Opción A: Usar XAMPP (Recomendado para desarrollo)

1. Inicia XAMPP y arranca los servicios de Apache y MySQL
2. Abre phpMyAdmin en `http://localhost/phpmyadmin`
3. Ejecuta el script SQL ubicado en `/backend/schema.sql`
   - Puedes usar la pestaña "SQL" en phpMyAdmin
   - O ejecutar: `mysql -u root -p < backend/schema.sql`

### Opción B: MySQL independiente

1. Asegúrate de que MySQL esté corriendo en `localhost:3306`
2. Ejecuta el siguiente comando:
   ```bash
   mysql -u root -p < backend/schema.sql
   ```
3. Ingresa tu contraseña de MySQL cuando se solicite

### Verificar la creación de la base de datos

```sql
USE lavadero_al;
SHOW TABLES;
```

Deberías ver las siguientes tablas:
- usuarios
- empleados
- servicios
- convenios
- vehiculos_convenio
- tarifas
- inventario
- movimientos_inventario
- liquidaciones
- detalle_liquidaciones

## 2. Configuración del Backend (FastAPI)

1. Navega a la carpeta del backend:
   ```bash
   cd backend
   ```

2. Crea un entorno virtual (recomendado):
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install fastapi uvicorn mysql-connector-python pydantic
   ```

4. Verifica la configuración de la base de datos en `config.py`:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': '',  # Cambia esto si tu MySQL tiene contraseña
       'database': 'lavadero_al',
       'port': 3306
   }
   ```

5. Inicia el servidor backend:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

6. Verifica que funcione accediendo a:
   - API: `http://localhost:8000`
   - Documentación interactiva: `http://localhost:8000/docs`

## 3. Configuración del Frontend (Vue 3)

1. Regresa a la carpeta raíz del proyecto:
   ```bash
   cd ..
   ```

2. Instala las dependencias de Node:
   ```bash
   npm install
   ```

3. Verifica que la URL del API esté correcta en `src/services/api.js`:
   ```javascript
   const API_URL = 'http://localhost:8000/api';
   ```

4. Inicia el servidor de desarrollo:
   ```bash
   npm run dev
   ```

5. Abre tu navegador en: `http://localhost:5173`

## 4. Credenciales de Acceso Iniciales

### Usuario Administrador
- **Usuario:** `admin`
- **Contraseña:** `admin123`

### Usuario Empleado
- **Usuario:** `empleado1`
- **Contraseña:** `emp123`

**IMPORTANTE:** Cambia estas contraseñas en producción.

## 5. Estructura del Proyecto

```
LavaderoAl/
├── backend/
│   ├── routers/          # Endpoints de la API
│   │   ├── auth.py       # Autenticación
│   │   ├── empleados.py  # Gestión de empleados
│   │   ├── servicios.py  # Gestión de servicios
│   │   ├── inventario.py # Gestión de inventario
│   │   ├── liquidaciones.py
│   │   ├── convenios.py
│   │   ├── tarifas.py
│   │   ├── reportes.py
│   │   └── dashboard.py
│   ├── config.py         # Configuración de BD
│   ├── database.py       # Conexión a BD
│   ├── schemas.py        # Modelos Pydantic
│   ├── main.py           # Aplicación principal
│   └── schema.sql        # Script de creación de BD
├── src/
│   ├── views/            # Vistas de Vue
│   ├── components/       # Componentes reutilizables
│   ├── services/
│   │   └── api.js        # Cliente HTTP
│   └── router/
│       └── index.js      # Configuración de rutas
└── package.json
```

## 6. Verificación de la Instalación

### Backend
```bash
curl http://localhost:8000
# Debería retornar: {"message": "API del Lavadero funcionando correctamente 🚀"}
```

### Probar endpoints específicos
```bash
# Listar empleados
curl http://localhost:8000/api/empleados

# Listar servicios
curl http://localhost:8000/api/servicios

# Métricas del dashboard
curl http://localhost:8000/api/dashboard/metricas
```

## 7. Datos de Prueba

El script `schema.sql` ya incluye datos de prueba:
- 4 empleados (3 activos, 1 inactivo)
- 6 servicios registrados
- Tarifas para 4 tipos de vehículos
- 10 insumos en inventario
- 3 convenios con vehículos asociados
- 3 liquidaciones (2 pagadas, 1 pendiente)

## 8. Solución de Problemas Comunes

### Error: "Can't connect to MySQL server"
- Verifica que MySQL esté corriendo
- Revisa el puerto en `config.py`
- Confirma usuario y contraseña

### Error: "Table doesn't exist"
- Asegúrate de haber ejecutado `schema.sql`
- Verifica que estés usando la base de datos correcta: `USE lavadero_al;`

### Error: "Module not found" (Python)
- Activa el entorno virtual
- Reinstala dependencias: `pip install -r requirements.txt`

### Error: "Cannot find module" (Node)
- Elimina `node_modules` y ejecuta `npm install` nuevamente
- Verifica la versión de Node: `node --version`

### El frontend no se conecta al backend
- Verifica que ambos servidores estén corriendo
- Revisa la URL en `api.js`
- Abre la consola del navegador para ver errores de CORS

## 9. Desarrollo

### Ejecutar en modo desarrollo

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### Acceder a la documentación de la API
```
http://localhost:8000/docs
```

## 10. Próximos Pasos

1. Cambiar las contraseñas por defecto
2. Implementar autenticación JWT real (actualmente es simulada)
3. Agregar validación de RUT chileno
4. Implementar subida de imágenes de vehículos
5. Agregar exportación de reportes a Excel/PDF
6. Configurar backup automático de la base de datos

## Soporte

Si encuentras algún problema:
1. Revisa los logs del backend en la consola
2. Revisa la consola del navegador para errores del frontend
3. Verifica que todos los servicios estén corriendo
4. Consulta la documentación de FastAPI: https://fastapi.tiangolo.com/
5. Consulta la documentación de Vue 3: https://vuejs.org/
