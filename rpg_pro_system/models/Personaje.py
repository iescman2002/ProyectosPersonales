from database.ConexionDB import conectar_bd

class Personaje:
    def __init__(self, id, nombre, nivel, exp, oro, vida_actual, mana_actual, fuerza, agilidad, inteligencia, id_raza, id_clase):
        self.id = id
        self.nombre = nombre
        self.nivel = nivel
        self.exp = exp
        self.oro = oro
        self.vida_actual = vida_actual
        self.mana_actual = mana_actual
        self.fuerza = fuerza
        self.agilidad = agilidad
        self.inteligencia = inteligencia
        self.id_raza = id_raza
        self.id_clase = id_clase
    @classmethod
    def obtener_personajes(cls):
        personajes_data = []
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("""
                        SELECT  p.id,
                                p.nombre,
                                p.nivel,
                                p.exp,
                                p.oro,
                                p.id_raza,
                                p.id_clase,
                                r.nombre                                               AS nombre_raza,
                                c.nombre                                               AS nombre_clase,
                                -- Vida_max: base + raza + clase + items equipados
                                p.vida_base + r.mod_vida + c.dado_vida + COALESCE(stats_items.bono_vida_items, 0) AS vida_max,
                                -- Mana_max: base + raza + items equipados
                                p.mana_base + r.mod_mana + COALESCE(stats_items.bono_mana_items, 0) AS mana_max,
                                p.vida_actual,
                                p.mana_actual,
                                -- Fuerza total: fuerza pj + mod_fuerza + factor_dano + bonos_item_fueza
                                (p.fuerza + r.mod_fuerza) * c.factor_dano + COALESCE(stats_items.bono_fuerza_items, 0) AS fuerza_total,
                                -- Agilidad total: agilidad pj + mod_agilidad + bonos_item_agggilidad
                                p.agilidad + r.mod_agilidad + COALESCE(stats_items.bono_agilidad_items, 0) AS agilidad_total,
                                -- Inteligencia total: Inteligencia pj + mod_inteli + bonos_item_inteligencia
                      p.inteligencia + r.mod_inteligencia+ COALESCE(stats_items.bono_inteligencia_items, 0) AS inteligencia_total
                        FROM personajes p
                        JOIN razas r ON p.id_raza = r.id
                        JOIN clases_rpg c ON p.id_clase = c.id
                        LEFT JOIN (SELECT i.id_personaje,
                                      COALESCE(SUM(it.mod_vida * i.cantidad), 0)                     AS bono_vida_items,
                                      COALESCE(SUM(it.mod_mana * i.cantidad), 0)                     AS bono_mana_items,
                                      COALESCE(SUM((it.mod_fuerza + it.dano_bonus) * i.cantidad), 0) AS bono_fuerza_items,
                                      COALESCE(SUM(it.mod_agilidad * i.cantidad), 0)                 AS bono_agilidad_items,
                                      COALESCE(SUM(it.mod_inteligencia * i.cantidad), 0)             AS bono_inteligencia_items
                                   FROM inventarios i
                                   JOIN items it ON it.id = i.id_item
                                   WHERE i.equipado = TRUE
                                   GROUP BY i.id_personaje) stats_items
                                  ON stats_items.id_personaje = p.id
                        ORDER BY P.ID
               """)
                    filas = cursor.fetchall()
                    for fila in filas:
                        nuevo_p = Personaje (
                            id= fila[0],
                            nombre=fila[1],
                            nivel=fila[2],
                            exp=fila[3],
                            oro=fila[4],
                            id_raza=fila[5],
                            id_clase=fila[6],
                            vida_actual=fila[11],
                            mana_actual=fila[12],
                            fuerza=fila[13],
                            agilidad=fila[14],
                            inteligencia=fila[15],
                        )
                        diccionario_p = {
                            "id_pj": int(nuevo_p.id),
                            "nombre": nuevo_p.nombre,
                            "nivel": int(nuevo_p.nivel),
                            "exp": int(nuevo_p.exp),
                            "oro": int(nuevo_p.oro),
                            "id_raza": int(nuevo_p.id_raza),
                            "id_clase": int(nuevo_p.id_clase),
                            "nombre_raza": fila[7],
                            "nombre_clase": fila[8],
                            "vida_max": float(fila[9]),
                            "mana_max": float(fila[10]),
                            "vida_actual": float(nuevo_p.vida_actual),
                            "mana_actual": float(nuevo_p.mana_actual),
                            "fuerza": float(nuevo_p.fuerza),
                            "agilidad": float(nuevo_p.agilidad),
                            "inteligencia": float(nuevo_p.inteligencia),
                        }
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

    @classmethod
    def actualizar_vida_mana(cls, id_personaje, bono_vida, bono_mana):
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("""
                                   UPDATE personajes
                                   SET vida_actual = GREATEST(0, LEAST(vida_actual + %s,
                                                                       (SELECT p.vida_base + r.mod_vida + c.dado_vida +
                                                                               COALESCE(SUM(it.mod_vida * i.cantidad) FILTER(WHERE i.equipado = TRUE), 0)
                                                                        FROM personajes p
                                                                                 JOIN razas r ON p.id_raza = r.id
                                                                                 JOIN clases_rpg c ON p.id_clase = c.id
                                                                                 LEFT JOIN inventarios i ON i.id_personaje = p.id
                                                                                 LEFT JOIN items it ON it.id = i.id_item
                                                                        WHERE p.id = %s
                                                                        GROUP BY p.id, r.mod_vida, c.dado_vida))),
                                       mana_actual = GREATEST(0, LEAST(mana_actual + %s,
                                                                       (SELECT p.mana_base + r.mod_mana +
                                                                               COALESCE(SUM(it.mod_mana * i.cantidad) FILTER(WHERE i.equipado = TRUE), 0)
                                                                        FROM personajes p
                                                                                 JOIN razas r ON p.id_raza = r.id
                                                                                 LEFT JOIN inventarios i ON i.id_personaje = p.id
                                                                                 LEFT JOIN items it ON it.id = i.id_item
                                                                        WHERE p.id = %s
                                                                        GROUP BY p.id, r.mod_mana)))
                                   WHERE id = %s;
                                   """, (bono_vida, id_personaje, bono_mana, id_personaje, id_personaje))
                    conexion.commit()
                    return True
            except Exception as e:
                print(f"Error al actualizar vida y maná: {e}")
                return False
    @classmethod
    def comprobar_vida_pj(cls, id_pj):
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT VIDA_ACTUAL FROM PERSONAJES WHERE ID=%s", (id_pj,))
                    resultado = cursor.fetchone()
                    if resultado and resultado[0] >= 0:
                        return True
                    else:
                        return False
            except Exception as e:
                print("Error comprobar el vida del personaje: ", e)
                return False
    # Actualizo la vida_actual y la mana_actual de personaje al cargar el programa
    @classmethod
    def resetear_vida_mana(cls):
        with conectar_bd() as conexion:
            try:
                with conexion.cursor() as cursor:
                    # Usamos una CTE unificada (calculo_totales) para evitar tocar la tabla 'p' en los JOINs
                    cursor.execute("""
                        WITH calculo_totales AS (
                            SELECT 
                                p.id AS personaje_id,
                                (
                                    p.vida_base 
                                    + r.mod_vida 
                                    + c.dado_vida 
                                    + COALESCE(SUM(it.mod_vida * i.cantidad) FILTER (WHERE i.equipado = TRUE), 0)
                                ) AS vida_total,
                                (
                                    p.mana_base 
                                    + r.mod_mana 
                                    + COALESCE(SUM(it.mod_mana * i.cantidad) FILTER (WHERE i.equipado = TRUE), 0)
                                ) AS mana_total
                            FROM personajes p
                            JOIN razas r ON p.id_raza = r.id
                            JOIN clases_rpg c ON p.id_clase = c.id
                            LEFT JOIN inventarios i ON i.id_personaje = p.id
                            LEFT JOIN items it ON it.id = i.id_item
                            GROUP BY p.id, r.mod_vida, c.dado_vida, r.mod_mana
                        )
                        UPDATE personajes p
                        SET 
                            vida_actual = ct.vida_total,
                            mana_actual = ct.mana_total
                        FROM calculo_totales ct
                        WHERE p.id = ct.personaje_id;
                    """)
                    conexion.commit()
                    print("✅ Vida y maná de todos los personajes reseteados con éxito.")
                    return True

            except Exception as e:
                print(f"❌ Error al resetear estadísticas: {e}")
                return False