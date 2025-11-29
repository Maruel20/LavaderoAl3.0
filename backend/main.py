from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import ALLOWED_ORIGINS
from backend.routers import (
    auth,
    empleados,
    servicios,
    inventario,
    liquidaciones,
    convenios,
    tarifas,
    reportes,
    dashboard,
)

app = FastAPI(title="Lavadero AL API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir prefijo global para mantener el orden
api_prefix = "/api"

app.include_router(auth.router, prefix=api_prefix, tags=["auth"])
app.include_router(empleados.router, prefix=api_prefix, tags=["empleados"])
app.include_router(servicios.router, prefix=api_prefix, tags=["servicios"])
app.include_router(inventario.router, prefix=api_prefix, tags=["inventario"])
app.include_router(liquidaciones.router, prefix=api_prefix, tags=["liquidaciones"])
app.include_router(convenios.router, prefix=api_prefix, tags=["convenios"])
app.include_router(tarifas.router, prefix=api_prefix, tags=["tarifas"])
app.include_router(reportes.router, prefix=api_prefix, tags=["reportes"])
app.include_router(dashboard.router, prefix=api_prefix, tags=["dashboard"])

@app.get("/")
def root():
    return {
        "message": "API del Lavadero AL funcionando correctamente",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Lavadero AL API"
    }
# main.py
