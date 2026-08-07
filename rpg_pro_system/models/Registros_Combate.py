from database.ConexionDB import conectar_bd


class Registros_Combate:
    def __init__(self, id, id_personaje, id_enemigo, turno, accion, dano_infligido, dano_received, resultado, fecha):
        self.id = id
        self.id_personaje = id_personaje
        self.id_enemigo = id_enemigo
        self.turno = turno
        self.accion = accion
        self.dano_infligido = dano_infligido
        self.dano_received = dano_received
        self.resultado = resultado
        self.fecha = fecha

    @classmethod
    def obtener_registros_combate(cls):
        registros_combate_data = []  # Lista vacía para guardar los diccionarios
        with conectar_bd() as conexion:
            try:
                # 2. Usar un segundo 'with' para el cursor (se cierra solo)
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, id_personaje, id_enemigo, turno, accion, dano_infligido, dano_received, resultado, fecha FROM REGISTROS_COMBATE")
                    filas = cursor.fetchall()
                    # 3. Mapeo de filas a objetos y luego a diccionarios (para el emit)
                    for fila in filas:
                        # 1. Sacamos los dates de la fila uno por uno (por orden)
                        id = fila[0]
                        id_personaje = fila[1]
                        id_enemigo = fila[2]
                        turno = fila[3]
                        accion = fila[4]
                        dano_infligido = fila[5]
                        dano_received = fila[6]
                        resultado = fila[7]
                        fecha = fila[8]
                        # 2. Creamos el objeto Clase_RPG con esos datos
                        nuevo_rc = Registros_Combate(id, id_personaje, id_enemigo, turno, accion, dano_infligido, dano_received, resultado, fecha)
                        # 3. Lo convertimos a un "diccionario" (formato clave: valor)
                        # Socket.io no sabe enviar objetos, pero sí sabe enviar diccionarios
                        diccionario_rc = {
                            "id": nuevo_rc.id,
                            "id_personaje": nuevo_rc.id_personaje,
                            "id_enemigo": nuevo_rc.id_enemigo,
                            "turno": nuevo_rc.turno,
                            "accion": nuevo_rc.accion,
                            "dano_infligido": nuevo_rc.dano_infligido,
                            "dano_received": nuevo_rc.dano_received,
                            "resultado": nuevo_rc.resultado,
                            "fecha": nuevo_rc.fecha,
                        }
                        # 4. Lo añadimos a nuestra lista final
                        registros_combate_data.append(diccionario_rc)
                        print(f"✅ Se han recuperado {len(registros_combate_data)} registros_combate.")
            except Exception as e:
                print(f"❌ Error al consultar los registros_combate: {e}")
        return registros_combate_data
