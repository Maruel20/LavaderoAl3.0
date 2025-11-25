import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de Base de Datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),  # Vacío por defecto en XAMPP
    'database': os.getenv('DB_NAME', 'lavadero_al'),
    'port': int(os.getenv('DB_PORT', '3306'))
}
#
# Configuración de JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'tu_clave_secreta_super_segura_cambiala_en_produccion_2024')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas