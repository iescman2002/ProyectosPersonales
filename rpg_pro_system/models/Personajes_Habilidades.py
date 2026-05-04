from database.ConexionDB import conectar_bd


class Logros:
    def __init__(self, id_personaje,  id_habilidad, nivel_actual, exp_habilidad):
        self.id_personaje = id_personaje
        self.id_habilidad = id_habilidad
        self.nivel_actual = nivel_actual
        self.exp_habilidad = exp_habilidad

def obtener_personajes_habilidades():
    personajes_habilidades_data = []  # Lista vacía para guardar los diccionarios
    with conectar_bd() as conexion:
        try:
            # 2. Usar un segundo 'with' para el cursor (se cierra solo)
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id_personaje,  id_habilidad, nivel_actual, exp_habilidad FROM PERSONAJES_HABILIDADES")
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
                    diccionario_ph = {
                        "id": id,
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "icono": icono,
                        "condicion": condicion
                    }
                    # 4. Lo añadimos a nuestra lista final
                    personajes_habilidades_data.append(diccionario_ph)
                    print(f"✅ Se han recuperado {len(personajes_habilidades_data)} personajes_habilidades.")
        except Exception as e:
            print(f"❌ Error al consultar los personajes_habilidades: {e}")
    return personajes_habilidades_data
