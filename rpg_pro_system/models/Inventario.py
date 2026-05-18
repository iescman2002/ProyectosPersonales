from database.ConexionDB import conectar_bd
from models.Personaje import Personaje


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
    @classmethod
    def obtener_inventario_pj(cls, id_personaje):
        inventarios_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute("""
                       SELECT inv.id,
                          inv.id_personaje,
                          inv.id_item,
                          inv.cantidad,
                          inv.equipado,
                          it.nombre,
                          it.descripcion,
                          it.precio,
                          it.rareza,
                          it.mod_vida,
                          it.mod_mana,
                          it.mod_fuerza,
                          it.mod_agilidad,
                          it.mod_inteligencia,
                          it.dano_bonus,
                          ti.nombre AS tipo_nombre
                       FROM INVENTARIOS inv
                            JOIN ITEMS it ON it.id = inv.id_item
                            JOIN TIPOS_ITEM ti ON ti.id = it.tipo
                       WHERE inv.id_personaje = %s
                       """, (id_personaje,))
                    filas = cursor.fetchall()
                    for fila in filas:
                        diccionario_i = {
                            "id": fila[0],
                            "id_personaje": fila[1],
                            "id_item": fila[2],
                            "cantidad": fila[3],
                            "equipado": fila[4],
                            "nombre": fila[5],
                            "descripcion": fila[6],
                            "precio": fila[7],
                            "rareza": fila[8],
                            "mod_vida": fila[9],
                            "mod_mana": fila[10],
                            "mod_fuerza": fila[11],
                            "mod_agilidad": fila[12],
                            "mod_inteligencia": fila[13],
                            "dano_bonus": fila[14],
                            "tipo": fila[15]
                        }
                        inventarios_data.append(diccionario_i)
                    print(f"✅ Se han recuperado {len(inventarios_data)} items del inventario.")
            except Exception as e:
                print(f"❌ Error al consultar el inventario: {e}")
            return inventarios_data
    @classmethod
    def comprar_item(cls, id_item, id_personaje, precio_item):
        # Primero actualizo el oro del personaje tras comprar el item
        Personaje.actualizar_oro_pj(id_personaje, -precio_item) # Pasamos el precio del item como negativo porque resta
        # Después, verifico si el item que quiero comprar lo tengo ya guardado en el inventario
        if cls.verificar_item_en_inventario(id_item,id_personaje):
        # Si ya existe en el inventario, actualizamos solo su cantidad a +1
            cls.insertar_item_existente(id_item,id_personaje)
            # Sino, insertamos como cantidad 1 el nuevo item
        else:
            cls.insertar_nuevo_item(id_item,id_personaje)
        return True
    @classmethod
    def verificar_item_en_inventario(cls, id_item, id_personaje):
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1 FROM INVENTARIOS WHERE id_item = %s AND id_personaje = %s", (id_item, id_personaje)
                    )
                    resultado = cursor.fetchone()
                    # Ternaria donde devuelvo true si se encuentra en la bd y false si no
                    return resultado is not None
            except Exception as e:
                print(f"Error al verificar el item en el inventario: {e}")
                return False
    @classmethod
    def insertar_item_existente(cls,id_item,id_personaje):
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "UPDATE INVENTARIOS SET cantidad = cantidad + 1 WHERE id_item = %s AND id_personaje = %s", (id_item, id_personaje)
                    )
                    conexion.commit()
            except Exception as e:
                print(f"Error al insertar el item en el inventario: {e}")
    @classmethod
    def insertar_nuevo_item(cls,id_item,id_personaje):
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO INVENTARIOS (id_item, id_personaje, cantidad) VALUES (%s, %s, 1)", (id_item, id_personaje)
                    )
                    conexion.commit()
            except Exception as e:
                print(f"Error al insertar el item en el inventario: {e}")
    @classmethod
    def equipar_desequipar_item(cls, id_item, id_personaje, equipado):
        # Si esta equipada y llamo al metodo lo desequipo (Activado True -> False)
        if equipado is True:
            with conectar_bd() as conexion:
                try:
                    with conexion.cursor() as cursor:
                        cursor.execute(
                            "UPDATE INVENTARIOS SET equipado = FALSE WHERE id_item = %s AND id_personaje = %s", (id_item, id_personaje)
                        )
                        conexion.commit()
                        return True
                except Exception as e:
                    print(f"Error al desequipar el item: {e}")
                    return False
        # Y si no esta equipada lo equipo (Activado False -> True)
        else:
            with conectar_bd() as conexion:
                try:
                    with conexion.cursor() as cursor:
                        cursor.execute(
                            "UPDATE INVENTARIOS SET equipado = TRUE WHERE id_item = %s AND id_personaje = %s",(id_item, id_personaje)
                        )
                        conexion.commit()
                        return True
                except Exception as e:
                    print(f"Error al equipar el item: {e}")
                    return False