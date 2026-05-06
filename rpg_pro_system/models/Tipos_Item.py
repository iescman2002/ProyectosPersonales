from database.ConexionDB import conectar_bd


class Tipos_Item:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    @classmethod
    def obtener_tipos_item(cls):
        tipos_item_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, nombre FROM TIPOS_ITEM")
                    filas = cursor.fetchall()
                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        # 1. Sacamos los dates de la fila uno por uno (por orden)
                        id = fila[0]
                        nombre = fila[1]
                        # 2. Creamos el objeto Clase_RPG con esos datos
                        nuevo_ti = Tipos_Item(id, nombre)
                        # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                        # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                        diccionario_ti = {
                            "id": nuevo_ti.id,
                            "nombre": nuevo_ti.nombre
                        }
                        # 4. Lo añadimos a nuestra lista final
                        tipos_item_data.append(diccionario_ti)
                        print(f"✅ Se han recuperado {len(tipos_item_data)} tipos_item.")
            except Exception as e:
                print(f"❌ Error al consultar los tipos_item: {e}")
        return tipos_item_data
