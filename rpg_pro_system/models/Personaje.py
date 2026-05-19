from database.ConexionDB import conectar_bd

class Personaje:
    def __init__(self, id, nombre, nivel, exp, oro, vida_max, vida_actual, mana_max, mana_actual, fuerza, agilidad, inteligencia, id_raza, id_clase):
        self.id = id
        self.nombre = nombre
        self.nivel = nivel
        self.exp = exp
        self.oro = oro
        self.vida_max = vida_max
        self.vida_actual = vida_actual
        self.mana_max = mana_max
        self.mana_actual = mana_actual
        self.fuerza = fuerza
        self.agilidad = agilidad
        self.inteligencia = inteligencia
        self.id_raza = id_raza
        self.id_clase = id_clase
    @classmethod
    def obtener_personajes(cls):
        personajes_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute("""
                           SELECT 
                                p.id,
                                p.nombre,
                                p.nivel, 
                                p.exp, 
                                p.oro, 
                                p.id_raza, 
                                p.id_clase,
                                -- Vida total: (vida_base + mod_vida) * dado_vida
                                p.vida_max + r.mod_vida + c.dado_vida AS vida_total,
                                -- Mana total: mana_base + mod_mana
                                p.mana_max + r.mod_mana AS mana_total,
                                -- Fuerza total: (fuerza_base + mod_fuerza) * factor_dano
                                (p.fuerza + r.mod_fuerza) * c.factor_dano AS fuerza_total,
                                -- Agilidad total: agilidad_base + mod_agilidad
                                p.agilidad + r.mod_agilidad AS agilidad_total,
                                -- Inteligencia total: inteligencia_base + mod_inteligencia
                                p.inteligencia + r.mod_inteligencia AS inteligencia_total
                           FROM personajes p
                           JOIN razas r ON p.id_raza = r.id
                           JOIN clases_rpg c ON p.id_clase = c.id;
                                   """)
                    filas = cursor.fetchall()

                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        # 1. Sacamos los datos de la fila uno por uno (por orden)
                        id_pj = fila[0]
                        nombre = fila[1]
                        nivel = fila[2]
                        exp = fila[3]
                        oro = fila[4]
                        id_raza = fila[5]
                        id_clase = fila[6]
                        vida_max = fila[7]
                        vida_actual = vida_max
                        mana_max = fila[8]
                        mana_actual = mana_max
                        fuerza = fila[9]
                        agilidad = fila[10]
                        inteligencia = fila[11]
                        # 2. Creamos el objeto Personaje con esos datos
                        nuevo_p = Personaje(id_pj, nombre, nivel, exp, oro, vida_max, vida_actual, mana_max, mana_actual, fuerza, agilidad, inteligencia, id_raza, id_clase)
                        # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                        # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                        diccionario_p = {
                            "id_pj": int(nuevo_p.id),
                            "nombre": nuevo_p.nombre,
                            "nivel": int(nuevo_p.nivel),
                            "exp": int(nuevo_p.exp),
                            "oro": int(nuevo_p.oro),
                            "id_raza": int(nuevo_p.id_raza),
                            "id_clase": int(nuevo_p.id_clase),
                            "vida_max": float(nuevo_p.vida_max),
                            "vida_actual": float(nuevo_p.vida_actual),
                            "mana_max": float(nuevo_p.mana_max),
                            "mana_actual": float(nuevo_p.mana_actual),
                            "fuerza": float(nuevo_p.fuerza),
                            "agilidad": float(nuevo_p.agilidad),
                            "inteligencia": float(nuevo_p.inteligencia),
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