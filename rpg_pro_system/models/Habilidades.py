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
def obtener_habilidades():
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