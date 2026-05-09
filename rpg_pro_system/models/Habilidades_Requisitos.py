from database.ConexionDB import conectar_bd
from models.Personajes_Habilidades import Personajes_Habilidades


class Habilidades_Requisitos:
    def __init__(self, id_habilidad, id_requisito, nivel_requisito_necesario):
        self.id_habilidad = id_habilidad
        self.id_requisito = id_requisito
        self.nivel_requisito_necesario = nivel_requisito_necesario

    @classmethod
    def obtener_habilidades_requisitos(cls):
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

    @classmethod
    def cumple_requisitos(cls, id_personaje, id_habilidad):

        # Guardo los requisitos de la habilidad que quiero desbloquear (Ej: habilidad1 al nivel 2 y habilidad2 al nivel3):
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("""
                        SELECT id_requisito, nivel_requisito_necesario
                        FROM HABILIDADES_REQUISITOS
                        WHERE id_habilidad = %s
                    """, (id_habilidad,))
                    requisitos = cursor.fetchall()
            # Recorro los requisitos de la habilidad para ver si mi personaje los cumple
                    for id_requisito, nivel_necesario in requisitos:
                        cursor.execute("""
                        SELECT nivel_actual
                        FROM PERSONAJES_HABILIDADES
                        WHERE id_personaje = %s AND id_habilidad= %s
                       """, (id_personaje, id_requisito))
            # Si cumple el requisito sigue revisando el resto de requisitos (por si tiene +1 requisito)
                        fila = cursor.fetchone()
            # Si no cumple uno de los requisitos, devuelve false (no los cumple)
                        if fila is None or fila[0] < nivel_necesario:
                            return False
            # Si cumple todos los requisitos devuelve true (si los cumple)
                    return True
            except Exception as e:
                print(f"Error al comprobar requisitos: {e}")
                return False
    @classmethod
    def desbloquearHabilidad(cls, id_personaje, id_habilidad):
        if cls.cumple_requisitos(id_personaje, id_habilidad):
        # Si cumple con los  requisitos, actualizo el nivel de la habilidad al nivel 1
            Personajes_Habilidades.subirNivelHabilidad(id_personaje,id_habilidad)
            print(f" Habilidad {id_habilidad} desbloqueada para personaje {id_personaje}.")
            return True
        else:
            print("No se ha podido desbloquear la habilidad")
            return False

    @classmethod
    def obtener_requisitos_habilidad(cls,id_personaje, id_habilidad):
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("""
                                   SELECT hr.id_requisito,
                                          h.nombre,
                                          hr.nivel_requisito_necesario,
                                          COALESCE(ph.nivel_actual, 0) AS nivel_actual_pj
                                   FROM HABILIDADES_REQUISITOS hr
                                            JOIN HABILIDADES h ON h.id = hr.id_requisito
                                            LEFT JOIN PERSONAJES_HABILIDADES ph
                                                      ON ph.id_habilidad = hr.id_requisito
                                                          AND ph.id_personaje = %s
                                   WHERE hr.id_habilidad = %s
                                   """, (id_personaje, id_habilidad))
                    filas = cursor.fetchall()
                    return [
                        {
                            "id_requisito": fila[0],
                            "nombre": fila[1],
                            "nivel_necesario": fila[2],
                            "nivel_actual_pj": fila[3],
                            "cumplido": fila[3] >= fila[2]
                        }
                        for fila in filas
                    ]
            except Exception as e:
                print(f"Error al obtener requisitos con progreso: {e}")
                return []