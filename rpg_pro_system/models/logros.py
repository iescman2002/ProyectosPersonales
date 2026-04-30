from database.ConexionDB import conectar_bd


class Logros:
    def __init__(self, id, nombre, descripcion, icono, condicion):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.icono = icono
        self.condicion = condicion

def obtener_logros():
    logros_data = []  # Lista vacía para guardar los diccionarios
    with conectar_bd() as conexion:
        try:
            # 2. Usar un segundo 'with' para el cursor (se cierra solo)
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, descripcion, icono, condicion FROM LOGROS")
                filas = cursor.fetchall()
                # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                for fila in filas:
                    # 1. Sacamos los dates de la fila uno por uno (por orden)
                    id = fila[0]
                    nombre = fila[1]
                    descripcion = fila[2]
                    icono = fila[3]
                    condicion = fila[4]

                    # 2. Creamos el objeto Clase_RPG con esos datos
                    nuevo_l = Logros(id, nombre, descripcion, icono, condicion)
                    # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                    # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                    diccionario_l = {
                        "id": id,
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "icono": icono,
                        "condicion": condicion
                    }
                    # 4. Lo añadimos a nuestra lista final
                    logros_data.append(diccionario_l)
                    print(f"✅ Se han recuperado {len(logros_data)} logros.")
        except Exception as e:
            print(f"❌ Error al consultar los logros: {e}")
    return logros_data
