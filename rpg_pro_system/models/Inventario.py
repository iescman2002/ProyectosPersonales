from database.ConexionDB import conectar_bd


class Inventario:
    def __init__(self, id, id_personaje, id_item, cantidad, equipado):
        self.id = id
        self.id_personaje = id_personaje
        self.id_item = id_item
        self.cantidad = cantidad
        self.equipado = equipado

    @classmethod
    def obtener_inventarios(cls):
        inventarios_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT id,  id_personaje, id_item, cantidad, equipado FROM INVENTARIOS")
                    filas = cursor.fetchall()
                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        # 1. Sacamos los dates de la fila uno por uno (por orden)
                        id = fila[0]
                        id_personaje = fila[1]
                        id_item = fila[2]
                        cantidad = fila[3]
                        equipado = fila[4]
                        # 2. Creamos el objeto Clase_RPG con esos datos
                        nuevo_i = Inventario(id, id_personaje, id_item, cantidad, equipado)
                        # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                        # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                        diccionario_i = {
                            "id": id,
                            "id_personaje": id_personaje,
                            "id_item": id_item,
                            "cantidad": cantidad,
                            "equipado": equipado
                        }
                        # 4. Lo añadimos a nuestra lista final
                        inventarios_data.append(diccionario_i)
                        print(f"✅ Se han recuperado {len(inventarios_data)} inventarios.")
            except Exception as e:
                print(f"❌ Error al consultar los enemigos: {e}")
        return inventarios_data