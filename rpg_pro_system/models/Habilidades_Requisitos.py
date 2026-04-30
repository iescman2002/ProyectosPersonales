from database.ConexionDB import conectar_bd


class Habilidades_Requisitos:
    def __init__(self, id_habilidad, id_requisito, nivel_requisito_necesario):
        self.id_habilidad = id_habilidad
        self.id_requisito = id_requisito
        self.nivel_requisito_necesario = nivel_requisito_necesario

def obtener_habilidades_requisitos():
    habilidades_requisitos_data = []  # Lista vacía para guardar los diccionarios
    with conectar_bd() as conexion:
        try:
            # 2. Usar un segundo 'with' para el cursor (se cierra solo)
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id_habilidad, id_requisito, nivel_requisito_necesario FROM HABILIDADES_REQUISITOS")
                filas = cursor.fetchall()
                # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                for fila in filas:
                    # 1. Sacamos los dates de la fila uno por uno (por orden)
                    id_habilidad = fila[0]
                    id_requisito = fila[1]
                    nivel_requisito_necesario = fila[2]

                    # 2. Creamos el objeto Clase_RPG con esos datos
                    nueva_hr = Habilidades_Requisitos(id_habilidad, id_requisito, nivel_requisito_necesario)
                    # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                    # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                    diccionario_hr = {
                        "id_habilidad": nueva_hr.id_habilidad,
                        "id_requisito": nueva_hr.id_requisito,
                        "nivel_requisito_necesario": nivel_requisito_necesario
                    }
                    # 4. Lo añadimos a nuestra lista final
                    habilidades_requisitos_data.append(diccionario_hr)
                print(f"✅ Se han recuperado {len(habilidades_requisitos_data)} habilidades_requisitos.")
        except Exception as e:
            print(f"❌ Error al consultar las habilidades_requisitos: {e}")
    return habilidades_requisitos_data