from database.ConexionDB import conectar_bd


class Items:
    def __init__(self, id, nombre, descripcion, precio, tipo, mod_vida, mod_mana, mod_fuerza, mod_agilidad, mod_inteligencia, dano_bonus, rareza):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.tipo = tipo
        self.mod_vida = mod_vida
        self.mod_mana = mod_mana
        self.mod_fuerza = mod_fuerza
        self.mod_agilidad = mod_agilidad
        self.mod_inteligencia = mod_inteligencia
        self.dano_bonus = dano_bonus
        self.rareza = rareza
    @classmethod
    def obtener_items(cls):
        items_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute("""
                       SELECT i.id,
                              i.nombre,
                              i.descripcion,
                              i.precio,
                              i.tipo,
                              t.nombre,
                              i.mod_vida,
                              i.mod_mana,
                              i.mod_fuerza,
                              i.mod_agilidad,
                              i.mod_inteligencia,
                              i.dano_bonus,
                              i.rareza
                       FROM ITEMS i
                       INNER JOIN TIPOS_ITEM t ON i.tipo = t.id
                                   """)
                    filas = cursor.fetchall()
                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        # 1. Sacamos los dates de la fila uno por uno (por orden)
                        id = fila[0]
                        nombre = fila[1]
                        descripcion = fila[2]
                        precio = fila[3]
                        id_tipo = fila[4]
                        tipo = fila[5]
                        mod_vida = fila[6]
                        mod_mana = fila[7]
                        mod_fuerza = fila[8]
                        mod_agilidad = fila[9]
                        mod_inteligencia = fila[10]
                        dano_bonus = fila[11]
                        rareza = fila[12]
                        # 2. Creamos el objeto Clase_RPG con esos datos
                        nuevo_i = Items(id, nombre, descripcion, precio, id_tipo, mod_vida, mod_mana, mod_fuerza, mod_agilidad, mod_inteligencia, dano_bonus, rareza)
                        # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                        # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                        diccionario_i = {
                            "id": id,
                            "nombre": nombre,
                            "descripcion": descripcion,
                            "precio": precio,
                            "id_tipo": id_tipo,
                            "tipo": tipo,
                            "mod_vida": mod_vida,
                            "mod_mana": mod_mana,
                            "mod_fuerza": mod_fuerza,
                            "mod_agilidad": mod_agilidad,
                            "mod_inteligencia": mod_inteligencia,
                            "dano_bonus": dano_bonus,
                            "rareza": rareza
                        }
                        # 4. Lo añadimos a nuestra lista final
                        items_data.append(diccionario_i)
                        print(f"✅ Se han recuperado {len(items_data)} items.")
            except Exception as e:
                print(f"❌ Error al consultar los items: {e}")
        return items_data