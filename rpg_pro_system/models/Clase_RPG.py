from database.ConexionDB import conectar_bd

class Clase_RPG:
    def __init__(self, id, nombre, descripcion, factor_dano, dado_vida, recurso_primario):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.factor_dano = factor_dano
        self.dado_vida = dado_vida
        self.recurso_primario = recurso_primario
    @classmethod
    def obtener_clases(cls):
        clases_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT id, nombre, descripcion, factor_dano, dado_vida, recurso_primario FROM CLASES_RPG")
                    filas = cursor.fetchall()
                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        # 1. Sacamos los dates de la fila uno por uno (por orden)
                        id = fila[0]
                        nombre = fila[1]
                        descripcion = fila[2]
                        factor_dano = fila[3]
                        dado_vida = fila[4]
                        recurso_primario = fila[5]
                        # 2. Creamos el objeto Clase_RPG con esos datos
                        nueva_c = Clase_RPG(id, nombre, descripcion, factor_dano, dado_vida,recurso_primario)
                        # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                        # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                        diccionario_c = {
                            "id": nueva_c.id,
                            "nombre": nueva_c.nombre,
                            "descripcion": nueva_c.descripcion,
                            "factor_dano": nueva_c.factor_dano,
                            "dado_vida": nueva_c.dado_vida,
                            "recurso_primario": nueva_c.recurso_primario
                        }
                        # 4. Lo añadimos a nuestra lista final
                        clases_data.append(diccionario_c)
                    print(f"✅ Se han recuperado {len(clases_data)} clases de RPG.")
            except Exception as e:
                    print(f"❌ Error al consultar las clases: {e}")
        return clases_data