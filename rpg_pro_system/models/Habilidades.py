from database.ConexionDB import conectar_bd

class Habilidades:
    def __init__(self, id, nombre, descripcion, tipo, nivel_maximo, costo_mana, dano_base, id_clase):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo = tipo
        self.nivel_maximo = nivel_maximo
        self.costo_mana = costo_mana
        self.dano_base = dano_base
        self.id_clase = id_clase
    @classmethod
    def obtener_habilidades(cls):
        habilidades_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, nombre, descripcion, tipo, nivel_maximo, costo_mana, dano_base, id_clase FROM HABILIDADES")
                    filas = cursor.fetchall()
                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        id = fila[0]
                        nombre = fila[1]
                        descripcion = fila[2]
                        tipo = fila[3]
                        nivel_maximo = fila[4]
                        costo_mana = fila[5]
                        dano_base = fila[6]
                        id_clase = fila[7]
                        nueva_h = Habilidades(id, nombre, descripcion, tipo, nivel_maximo, costo_mana, dano_base, id_clase)
                        diccionario_h = {
                            "id": nueva_h.id,
                            "nombre": nueva_h.nombre,
                            "descripcion": nueva_h.descripcion,
                            "tipo": nueva_h.tipo,
                            "nivel_maximo": nueva_h.nivel_maximo,
                            "costo_mana": nueva_h.costo_mana,
                            "dano_base": nueva_h.dano_base,
                            "id_clase": nueva_h.id_clase
                        }
                    # 4. Lo añadimos a nuestra lista final
                        habilidades_data.append(diccionario_h)
                        print(f"✅ Se han recuperado {len(habilidades_data)} habilidades.")
            except Exception as e:
                print(f"❌ Error al consultar los enemigos: {e}")
            return habilidades_data
    @classmethod
    def mostrar_habilidad(cls, id_habilidad):
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT id, nombre, descripcion, tipo, nivel_maximo, costo_mana, dano_base, id_clase FROM HABILIDADES WHERE id=%s", (id_habilidad,))
                    fila = cursor.fetchall()[0]
                    id = fila[0]
                    nombre = fila[1]
                    descripcion = fila[2]
                    tipo = fila[3]
                    nivel_maximo = fila[4]
                    costo_mana = fila[5]
                    dano_base = fila[6]
                    id_clase = fila[7]
                    habilidad = Habilidades(id, nombre, descripcion, tipo, nivel_maximo, costo_mana, dano_base, id_clase)
                    # Transformo a diccionario la habilidad para tener despues la lista de habilidades como un diccionario y poder trabajar con el
                    diccionario_habilidad = {
                        "id": habilidad.id,
                        "nombre": habilidad.nombre,
                        "descripcion": habilidad.descripcion,
                        "tipo": habilidad.tipo,
                        "nivel_maximo": habilidad.nivel_maximo,
                        "costo_mana": habilidad.costo_mana,
                        "dano_base": habilidad.dano_base,
                        "id_clase": habilidad.id_clase
                    }
                    return diccionario_habilidad
            except Exception as e:
                print(f'Error al obtener la habilidad: {e}')
    @classmethod
    def es_habilidad_avanzada(cls, id_habilidad):
        with conectar_bd() as conexion:
            with conexion.cursor() as cursor:
                # Si el id se encuentra en la tabla HABILIDADES_REQUISITOS, entonces es una habilidad avanzada
                cursor.execute("SELECT 1 FROM HABILIDADES_REQUISITOS WHERE id_habilidad = %s", (id_habilidad,))
                return cursor.fetchone() is not None # Devuelve true si se ha encontrado el id y false si no.