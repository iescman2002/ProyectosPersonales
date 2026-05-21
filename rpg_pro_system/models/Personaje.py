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
                                r.nombre,
                                c.nombre,
                                -- Vida total: vida_base + mod_vida + dado_vida + bono_vida_item
                                p.vida_max + r.mod_vida + c.dado_vida + COALESCE(stats_items.bono_vida_items, 0) AS vida_total,
                                -- Mana total: mana_base + mod_mana + bono_mana_item
                                p.mana_max + r.mod_mana + COALESCE(stats_items.bono_mana_items, 0) AS mana_total,
                                -- Fuerza total: (fuerza_base + mod_fuerza) * factor_dano + bono_fuerza_item
                                (p.fuerza + r.mod_fuerza) * c.factor_dano + COALESCE(stats_items.bono_fuerza_items, 0) AS fuerza_total,
                                -- Agilidad total: agilidad_base + mod_agilidad + bono_agilidad_item
                                p.agilidad + r.mod_agilidad + COALESCE(stats_items.bono_agilidad_items, 0) AS agilidad_total,
                                -- Inteligencia total: inteligencia_base + mod_inteligencia + bono_inteligencia_item
                                p.inteligencia + r.mod_inteligencia + COALESCE(stats_items.bono_inteligencia_items, 0) AS inteligencia_total
                           FROM personajes p
                           JOIN razas r ON p.id_raza = r.id
                           JOIN clases_rpg c ON p.id_clase = c.id
                           LEFT JOIN (
                                SELECT
                                    I.id_personaje,
                                    COALESCE(SUM(IT.MOD_VIDA*I.CANTIDAD),0) AS BONO_VIDA_ITEMS,
                                    COALESCE(SUM(IT.mod_mana * I.cantidad), 0) AS BONO_MANA_ITEMS,
                                    COALESCE(SUM((IT.mod_fuerza + IT.dano_bonus) * I.cantidad), 0) AS BONO_FUERZA_ITEMS,
                                    COALESCE(SUM(IT.mod_agilidad * I.cantidad), 0) AS BONO_AGILIDAD_ITEMS,
                                    COALESCE(SUM(IT.mod_inteligencia * I.cantidad), 0) AS BONO_INTELIGENCIA_ITEMS
                               FROM inventarios I
                               JOIN ITEMS IT ON IT.ID = I.ID_ITEM
                               WHERE I.EQUIPADO = TRUE
                               GROUP BY I.ID_PERSONAJE
                           ) STATS_ITEMS
                           ON STATS_ITEMS.ID_PERSONAJE = P.ID
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
                        nombre_raza = fila[7]
                        nombre_clase = fila[8]
                        vida_max = fila[9]
                        vida_actual = vida_max
                        mana_max = fila[10]
                        mana_actual = mana_max
                        fuerza = fila[11]
                        agilidad = fila[12]
                        inteligencia = fila[13]
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
                            "nombre_raza":nombre_raza,
                            "nombre_clase":nombre_clase,
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