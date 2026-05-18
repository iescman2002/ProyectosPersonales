from database.ConexionDB import conectar_bd


class Personaje:
    def __init__(self, id, nombre, nivel, exp, oro, vida_actual, id_raza, id_clase):
        self.id = id
        self.nombre = nombre
        self.nivel = nivel
        self.exp = exp
        self.oro = oro
        self.vida_actual = vida_actual
        self.id_raza = id_raza
        self.id_clase = id_clase
    @classmethod
    def obtener_personajes(cls):
        personajes_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT id, nombre, nivel, exp, oro, vida_actual, id_raza, id_clase FROM personajes")
                    filas = cursor.fetchall()

                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        # 1. Sacamos los dates de la fila uno por uno (por orden)
                        id_db = fila[0]
                        nombre = fila[1]
                        nivel = fila[2]
                        exp = fila[3]
                        oro = fila[4]
                        vida = fila[5]
                        raza = fila[6]
                        clase = fila[7]
                        # 2. Creamos el objeto Personaje con esos datos
                        nuevo_p = Personaje(id_db, nombre, nivel, exp, oro, vida, raza, clase)
                        # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                        # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                        diccionario_p = {
                            "id": nuevo_p.id,
                            "nombre": nuevo_p.nombre,
                            "nivel": nuevo_p.nivel,
                            "exp": nuevo_p.exp,
                            "oro": nuevo_p.oro,
                            "vida_actual": nuevo_p.vida_actual,
                            "id_raza": nuevo_p.id_raza,
                            "id_clase": nuevo_p.id_clase,
                        }
                        # 4. Lo añadimos a nuestra lista final
                        personajes_data.append(diccionario_p)
                    print(f"✅ Se han enviado {len(personajes_data)} personajes.")
            except Exception as e:
                print(f"❌ Error al consultar personajes: {e}")
        return personajes_data
    @classmethod
    def actualizar_oro_pj(cls, id_pj, oro_a_agregar):
        # Se actualiza el oro del personaje tras gastarlo o tras ganar (oro_a_agregar puede ser negativo y restar o positivo y sumar, es generico)
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("UPDATE personajes SET oro = oro + %s WHERE id = %s", (oro_a_agregar, id_pj))
                    conexion.commit()
            except Exception as e:
                print("Error actualizando el oro del personaje: ", e)