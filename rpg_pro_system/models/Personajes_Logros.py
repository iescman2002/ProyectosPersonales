from database.ConexionDB import conectar_bd


class Personajes_Logros:
    def __init__(self, id_personaje,  id_logro, desbloqueado_en):
        self.id_personaje = id_personaje
        self.id_logro = id_logro
        self.desbloqueado_en = desbloqueado_en

    @classmethod
    def obtener_personajes_logros(cls):
        personajes_logros_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT id_personaje,  id_logro, desbloqueado_en FROM PERSONAJES_LOGROS")
                    filas = cursor.fetchall()
                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        # 1. Sacamos los dates de la fila uno por uno (por orden)
                        id_personaje = fila[0]
                        id_logro = fila[1]
                        desbloqueado_en = fila[2]

                        # 2. Creamos el objeto Clase_RPG con esos datos
                        nuevo_pl = Personajes_Logros(id_personaje, id_logro, desbloqueado_en)
                        # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                        # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                        diccionario_pl = {
                            "id_personaje": nuevo_pl.id_personaje,
                            "id_logro": nuevo_pl.id_logro,
                            "desbloqueado_en": nuevo_pl.desbloqueado_en
                        }
                        # 4. Lo añadimos a nuestra lista final
                        personajes_logros_data.append(diccionario_pl)
                        print(f"✅ Se han recuperado {len(personajes_logros_data)} personajes_logros.")
            except Exception as e:
                print(f"❌ Error al consultar los personajes_logros: {e}")
        return personajes_logros_data
