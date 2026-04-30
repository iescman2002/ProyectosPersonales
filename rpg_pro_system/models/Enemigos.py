from database.ConexionDB import conectar_bd

class Enemigos:
    def __init__(self, id, nombre, nivel, vida_max, dano_base, exp_recom, oro_recom, descripcion):
        self.id = id
        self.nombre = nombre
        self.nivel = nivel
        self.vida_max = vida_max
        self.dano_base = dano_base
        self.exp_recom = exp_recom
        self.oro_recom = oro_recom
        self.descripcion = descripcion

def obtener_enemigos():
    enemigos_data = []  # Lista vacía para guardar los diccionarios
    with conectar_bd() as conexion:
        try:
            # 2. Usar un segundo 'with' para el cursor (se cierra solo)
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, nivel, vida_max, dano_base, exp_recom, oro_recom, descripcion FROM ENEMIGOS")
                filas = cursor.fetchall()
                # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                for fila in filas:
                    # 1. Sacamos los dates de la fila uno por uno (por orden)
                    id = fila[0]
                    nombre = fila[1]
                    nivel = fila[2]
                    vida_max = fila[3]
                    dano_base = fila[4]
                    exp_recom = fila[5]
                    oro_recom = fila[6]
                    descripcion = fila[7]
                    # 2. Creamos el objeto Clase_RPG con esos datos
                    nuevo_e = Enemigos(id, nombre, nivel, vida_max, dano_base, exp_recom, oro_recom, descripcion)
                    # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                    # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                    diccionario_e = {
                        "id": nuevo_e.id,
                        "nombre": nuevo_e.nombre,
                        "nivel": nuevo_e.nivel,
                        "vida_max": nuevo_e.vida_max,
                        "dano_base": nuevo_e.dano_base,
                        "exp_recom": nuevo_e.exp_recom,
                        "oro_recom": nuevo_e.oro_recom,
                        "descripcion": nuevo_e.descripcion
                    }
                    # 4. Lo añadimos a nuestra lista final
                    enemigos_data.append(diccionario_e)
                print(f"✅ Se han recuperado {len(enemigos_data)} enemigos.")
        except Exception as e:
                print(f"❌ Error al consultar los enemigos: {e}")
    return enemigos_data