import os
from contextlib import contextmanager
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://rpguser:rpgpassword@localhost:5432/rpg_db")

@contextmanager
def conectar_bd():

    conexion = None
    try:
        # Intentamos conectar
        conexion = psycopg2.connect(DATABASE_URL)
        yield conexion # Aquí es donde el código del "with" se ejecuta
    except Exception as e:
        print(f"❌ Error crítico de base de datos: {e}")
        yield None # Si falla, devolvemos None para que el programa no explote
    finally:
        # Pase lo que pase (error o éxito), cerramos
        if conexion:
            conexion.close()
            print("🔌 Conexión a DB cerrada.")