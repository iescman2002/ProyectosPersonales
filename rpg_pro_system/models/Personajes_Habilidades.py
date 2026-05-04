from database import ConexionDB
from models.Habilidades import Habilidades


class Personajes_Habilidades:
    def __init__(self, id_personaje,  id_habilidad, nivel_actual, exp_habilidad):
        self.id_personaje = id_personaje
        self.id_habilidad = id_habilidad
        self.nivel_actual = nivel_actual
        self.exp_habilidad = exp_habilidad

    def obtener_personajes_habilidades(self):
        personajes_habilidades_data = []  # Lista vacía para guardar los diccionarios
        with ConexionDB.conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT id_personaje,  id_habilidad, nivel_actual, exp_habilidad FROM PERSONAJES_HABILIDADES")
                    filas = cursor.fetchall()
                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        # 1. Sacamos los dates de la fila uno por uno (por orden)
                        id_personaje = fila[0]
                        id_habilidad = fila[1]
                        nivel_actual = fila[2]
                        exp_habilidad = fila[3]
                        # 2. Creamos el objeto Clase_RPG con esos datos
                        nuevo_ph = Personajes_Habilidades(id_personaje,  id_habilidad, nivel_actual, exp_habilidad)
                        # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                        # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                        diccionario_ph = {
                            "id_personaje": nuevo_ph.id_personaje,
                            "id_habilidad": nuevo_ph.id_habilidad,
                            "nivel_actual": nuevo_ph.nivel_actual,
                            "exp_habilidad": nuevo_ph.exp_habilidad,
                        }
                        # 4. Lo añadimos a nuestra lista final
                        personajes_habilidades_data.append(diccionario_ph)
                        print(f"✅ Se han recuperado {len(personajes_habilidades_data)} personajes_habilidades.")
            except Exception as e:
                print(f"❌ Error al consultar los personajes_habilidades: {e}")
        return personajes_habilidades_data

    def mostrar_habilidades_pj(self, id_personaje):
        ids_habilidades_pj = []
        habilidades_pj = []
        with ConexionDB.conectar_bd() as conexion:
            # Obtener id_habilidad
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT id_habilidad FROM PERSONAJES_HABILIDADES WHERE id_personaje = %s", id_personaje)
                    filas = cursor.fetchall()
                    for fila in filas:
                        id_habilidad= fila[0]
                        ids_habilidades_pj.append(id_habilidad)
                    for id_habilidad in ids_habilidades_pj:
                        habilidades_pj.append(Habilidades().mostrar_habilidad(id_habilidad))
                return habilidades_pj
            except:
                print("Error al obtener el id_habilidad")

    def mejorar_habilidad_pj(self,id_personaje, id_habilidad):
        # Obtener el nivel actual de la habilidad
        nivel_habilidad_actual = self.obtenerNivelHabilidadActual(id_personaje, id_habilidad)
        # Verificar que al subir 1 nivel a la habilidad, no supere el nivel maximo
        if self.verificarNivelMaximo(nivel_habilidad_actual, id_habilidad):
            self.subirNivelHabilidad(id_personaje, id_habilidad)
        else:
            print("No se ha podido mejorar la habilidad, la habilidad está a nivel maximo")

    def obtenerNivelHabilidadActual(self,id_personaje, id_habilidad):
        with ConexionDB.conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        'SELECT nivel_actual FROM PERSONAJES_HABILIDADES WHERE id_personaje = %s AND id_habilidad = %s',(id_personaje, id_habilidad)
                    )
                    nivel_habilidad_actual = cursor.fetchall()[0]
                    return nivel_habilidad_actual
            except Exception as e:
                print(f"Error al obtener el nivel actual de la habilidad: {e}")

    def verificarNivelMaximo(self, nivel_actual, id_habilidad):
        with ConexionDB.conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        'SELECT nivel_maximo FROM HABILIDADES WHERE id_habilidad = %s', (id_habilidad)
                    )
                nivel_maximo = cursor.fetchall()[0]
                return nivel_actual + 1 >= nivel_maximo # Si al subir de nivel la habilidad no supera el nivel maximo devuelve True sino False
            except:
                print("Error al obtener el nivel maximo de la habilidad")

    def subirNivelHabilidad(self, id_personaje, id_habilidad):
        with ConexionDB.conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        'UPDATE PERSONAJES_HABILIDADES SET nivel_actual = nivel_actual + 1 WHERE id_personaje = %s AND id_habilidad = %s', (id_personaje, id_habilidad)
                    )
                    conexion.commit()
                    print("Habilidad subida de nivel")
            except Exception as e:
                print(f"Error al subir el nivel de la habilidad: {e}")