from database.ConexionDB import conectar_bd


class Razas:
    def __init__(self, id, nombre, descripcion, mod_vida, mod_mana, mod_fuerza, mod_agilidad, mod_inteligencia, habilidad_racial):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.mod_vida = mod_vida
        self.mod_mana = mod_mana
        self.mod_fuerza = mod_fuerza
        self.mod_agilidad = mod_agilidad
        self.mod_inteligencia = mod_inteligencia
        self.habilidad_racial = habilidad_racial

def obtener_razas():
    razas_data = []  # Lista vacía para guardar los diccionarios
    with conectar_bd() as conexion:
        try:
            # 2. Usar un segundo 'with' para el cursor (se cierra solo)
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, descripcion, mod_vida, mod_mana, mod_fuerza, mod_agilidad, mod_inteligencia, habilidad_racial FROM RAZAS")
                filas = cursor.fetchall()
                # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                for fila in filas:
                    # 1. Sacamos los dates de la fila uno por uno (por orden)
                    id = fila[0]
                    nombre = fila[1]
                    descripcion = fila[2]
                    mod_vida = fila[3]
                    mod_mana = fila[4]
                    mod_fuerza = fila[5]
                    mod_agilidad = fila[6]
                    mod_inteligencia = fila[7]
                    habilidad_racial = fila[8]
                    # 2. Creamos el objeto Clase_RPG con esos datos
                    nueva_r = Razas(id, nombre, descripcion, mod_vida, mod_mana, mod_fuerza, mod_agilidad, mod_inteligencia, habilidad_racial)
                    # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                    # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                    diccionario_r = {
                        "id": nueva_r.id,
                        "nombre": nueva_r.nombre,
                        "descripcion": nueva_r.descripcion,
                        "mod_vida": nueva_r.mod_vida,
                        "mod_mana": nueva_r.mod_mana,
                        "mod_fuerza": nueva_r.mod_fuerza,
                        "mod_agilidad": nueva_r.mod_agilidad,
                        "mod_inteligencia": nueva_r.mod_inteligencia,
                        "habilidad_racial": nueva_r.habilidad_racial
                    }
                    # 4. Lo añadimos a nuestra lista final
                    razas_data.append(diccionario_r)
                    print(f"✅ Se han recuperado {len(razas_data)} razas.")
        except Exception as e:
            print(f"❌ Error al consultar los razas: {e}")
    return razas_data
