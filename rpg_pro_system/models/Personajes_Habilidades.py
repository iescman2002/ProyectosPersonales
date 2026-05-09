from database.ConexionDB import conectar_bd
from models.Habilidades import Habilidades


class Personajes_Habilidades:
    def __init__(self, id_personaje,  id_habilidad, nivel_actual, exp_habilidad):
        self.id_personaje = id_personaje
        self.id_habilidad = id_habilidad
        self.nivel_actual = nivel_actual
        self.exp_habilidad = exp_habilidad

    @classmethod
    def obtener_personajes_habilidades(cls):
        personajes_habilidades_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute("""
                        SELECT ph.id_personaje, ph.id_habilidad, ph.nivel_actual, ph.exp_habilidad, 
                               hr.id_habilidad
                        FROM PERSONAJES_HABILIDADES ph
                        LEFT JOIN HABILIDADES_REQUISITOS hr ON ph.id_habilidad = hr.id_habilidad
                    """)
                    filas = cursor.fetchall()
                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        # 1. Sacamos los dates de la fila uno por uno (por orden)
                        id_personaje = fila[0]
                        id_habilidad = fila[1]
                        nivel_actual = fila[2]
                        exp_habilidad = fila[3]
                        habilidad_avanzada = fila[4] is not None # Pone true si existe y false si no
                        desbloqueada = nivel_actual > 0 # Si el nivel de la habilidad no es 0 entonces la habilidad estará desbloqueada, sino false
                        # 2. Creamos el objeto Clase_RPG con esos datos
                        nuevo_ph = Personajes_Habilidades(id_personaje, id_habilidad, nivel_actual, exp_habilidad)
                        # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                        # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                        diccionario_ph = {
                            "id_personaje": nuevo_ph.id_personaje,
                            "id_habilidad": nuevo_ph.id_habilidad,
                            "nivel_actual": nuevo_ph.nivel_actual,
                            "exp_habilidad": nuevo_ph.exp_habilidad,
                            # Comprobar si la habilidad del personaje es avanzada o no (True o false)
                            "habilidad_avanzada": habilidad_avanzada,
                            "habilidad_desbloqueada": desbloqueada,
                        }
                        # 4. Lo añadimos a nuestra lista final
                        personajes_habilidades_data.append(diccionario_ph)
                    print(f"✅ Se han recuperado {len(personajes_habilidades_data)} personajes_habilidades.")
            except Exception as e:
                print(f"❌ Error al consultar los personajes_habilidades: {e}")
        return personajes_habilidades_data

    @classmethod
    def mostrar_habilidades_pj(cls, id_personaje):
        diccionario_habilidades_pj = []
        with conectar_bd() as conexion:
            # Obtener id_habilidad
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute("""
                       SELECT DISTINCT
                       ON (ph.id_habilidad)
                           ph.id_habilidad,
                           ph.nivel_actual,
                           hr.id_habilidad AS es_avanzada
                       FROM PERSONAJES_HABILIDADES ph
                           LEFT JOIN HABILIDADES_REQUISITOS hr
                       ON ph.id_habilidad = hr.id_habilidad
                       WHERE ph.id_personaje = %s
                       """, (id_personaje,))
                    filas = cursor.fetchall()
                    for fila in filas:
                        id_habilidad= fila[0]
                        nivel_actual = fila[1]
                        habilidad_avanzada = fila[2] is not None
                        desbloqueada = nivel_actual > 0 # Si el nivel de la habilidad no es 0 entonces la habilidad estará desbloqueada, sino false
                        habilidad = Habilidades.mostrar_habilidad(id_habilidad)
                        if habilidad: # Si la habilidad existe
                            habilidad["nivel_actual"] = nivel_actual # Añado en el diccionario como nivel actual el nivel actual
                            habilidad["habilidad_avanzada"] = habilidad_avanzada
                            habilidad["habilidad_desbloqueada"] = desbloqueada
                            diccionario_habilidades_pj.append(habilidad)
                return diccionario_habilidades_pj
            except:
                print("Error al obtener el id_habilidad")

    @classmethod
    def mejorar_habilidad_pj(cls,id_personaje, id_habilidad):
        id_personaje = int(id_personaje)
        id_habilidad = int(id_habilidad)
        # Obtener el nivel actual de la habilidad
        nivel_habilidad_actual = cls.obtenerNivelHabilidadActual(id_personaje, id_habilidad)
    # 1era verificación: Que el nivel de la habilidad sea menor al nivel maximo de la habilidad
        if nivel_habilidad_actual is not None:
            if cls.verificarNivelMaximoHabilidad(nivel_habilidad_actual, id_habilidad):
        # Verificar si la habilidad es avanzada o no
                if Habilidades.es_habilidad_avanzada(id_habilidad):
        # Verificar que la habilidad esté ya desbloqueada (que el nivel no sea 0)
                    if Personajes_Habilidades.obtenerNivelHabilidadActual(id_personaje,id_habilidad)>0:
                        cls.subirNivelHabilidad(id_personaje,id_habilidad)
                        return True
                    else:
                        return False
        # Si la Habilidad no es avanzada, basta solo con comprobar que la habilidad no supere al nivel máximo.
                else:
                    cls.subirNivelHabilidad(id_personaje, id_habilidad)
                    return True # Mando verdadero como que si he mejorado la habilidad
        else:
            print("No se ha podido mejorar la habilidad, la habilidad está a nivel maximo")
            return False # Mando falso no he podido mejorar la habilidad
    @classmethod
    def obtenerNivelHabilidadActual(cls,id_personaje, id_habilidad) -> int | None:
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        'SELECT nivel_actual FROM PERSONAJES_HABILIDADES WHERE id_personaje = %s AND id_habilidad = %s',(id_personaje, id_habilidad)
                    )
                    nivel_habilidad_actual = cursor.fetchone()
                    return nivel_habilidad_actual[0] # Devuelve la primera tupla
            except Exception as e:
                print(f"Error al obtener el nivel actual de la habilidad: {e}")

    @classmethod
    def verificarNivelMaximoHabilidad(cls, nivel_actual, id_habilidad):
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        'SELECT nivel_maximo FROM HABILIDADES WHERE id = %s', (id_habilidad,)
                    )
                    nivel_maximo = cursor.fetchone()
                    return nivel_actual + 1 <= nivel_maximo[0] # Si al subir de nivel la habilidad no supera el nivel maximo devuelve True sino False
            except:
                print("Error al obtener el nivel maximo de la habilidad")

    @classmethod
    def subirNivelHabilidad(cls, id_personaje, id_habilidad):
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        'UPDATE PERSONAJES_HABILIDADES SET nivel_actual = nivel_actual + 1 WHERE id_personaje = %s AND id_habilidad = %s', (id_personaje, id_habilidad)
                    )
                    conexion.commit()
                print("Habilidad subida de nivel")
            except Exception as e:
                print(f"Error al subir el nivel de la habilidad: {e}")