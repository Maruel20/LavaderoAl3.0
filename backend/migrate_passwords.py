import mysql.connector
from passlib.context import CryptContext

from backend.config import DB_CONFIG

# Configuración directa del contexto para el script
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def migrate_passwords():
    """Migra contraseñas a bcrypt manejando errores de longitud y versiones."""
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.autocommit = False # type: ignore # Importante para controlar la transacción
        cursor = conn.cursor(dictionary=True)

        print("Conectado a la base de datos...")

        # Obtener todos los usuarios
        cursor.execute("SELECT id, username, password FROM usuarios")
        usuarios = cursor.fetchall()

        print(f"=========================================")
        print(f"Encontrados {len(usuarios)} usuarios para procesar")
        print(f"=========================================\n")

        migrados = 0
        omitidos = 0
        errores = 0

        for usuario in usuarios:
            pwd_actual = usuario['password'] # type: ignore
            uid = usuario['id'] # type: ignore
            uname = usuario['username'] # type: ignore

            # 1. Verificar si ya es un hash de Bcrypt válido
            # Bcrypt puede empezar por $2b$, $2a$ o $2y$ y tiene 60 caracteres
            if pwd_actual and pwd_actual.startswith(('$2b$', '$2a$', '$2y$')) and len(pwd_actual) == 60:
                print(f"○ [OMITIDO] Usuario '{uname}' ya tiene hash Bcrypt.")
                omitidos += 1
                continue
            
            # 2. Intentar migrar
            try:
                # Verificar longitud antes de intentar (Bcrypt falla con > 72 bytes)
                if len(pwd_actual.encode('utf-8')) > 72:
                    print(f"⚠ [ERROR] Usuario '{uname}': La contraseña actual es demasiado larga (>72 bytes) para Bcrypt.")
                    print(f"          Acción: Se omite. Este usuario deberá resetear su contraseña.")
                    errores += 1
                    continue

                # Generar hash
                hashed_password = pwd_context.hash(pwd_actual)

                # Actualizar DB
                update_query = "UPDATE usuarios SET password = %s WHERE id = %s"
                cursor.execute(update_query, (hashed_password, uid))
                
                print(f"✓ [ÉXITO] Usuario '{uname}' migrado correctamente.")
                migrados += 1

            except Exception as e:
                print(f"✗ [FALLO] Error procesando usuario '{uname}': {str(e)}")
                errores += 1

        # Confirmar cambios solo si hubo migraciones exitosas
        if migrados > 0:
            conn.commit()
            print(f"\n=========================================")
            print(f"✅ COMMIT REALIZADO. Base de datos actualizada.")
        else:
            print(f"\n=========================================")
            print(f"⚠ No hubo cambios para guardar.")

        print(f"Resumen: {migrados} migrados, {omitidos} ya listos, {errores} errores.")

    except mysql.connector.Error as err:
        print(f"\n✗ Error crítico de Base de Datos: {err}")
        if conn: conn.rollback()
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    print("MIGRACIÓN SEGURA A BCRYPT (V2)")
    respuesta = input("¿Deseas iniciar la migración? (s/n): ")
    if respuesta.lower() == 's':
        migrate_passwords()
    else:
        print("Cancelado.")
