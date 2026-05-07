import os
from database.ConexionDB import conectar_bd  # importo la conexion de la base de datos
from models.Habilidades import Habilidades
from models.Clase_RPG import Clase_RPG
from models.Enemigos import Enemigos
from models.Inventario import Inventario
from models.Items import Items
from models.Personaje import Personaje
from models.Habilidades_Requisitos import Habilidades_Requisitos
from models.Personajes_Habilidades import Personajes_Habilidades
from models.Personajes_Logros import Personajes_Logros
from models.Razas import Razas
from models.Registros_Combate import Registros_Combate
from models.Tipos_Item import Tipos_Item
from models.Logros import Logros
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import psycopg2

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
@app.route('/')
def index():
    return render_template('index.html')

# CREAR APIS
@app.route('/api/clases')
def clases():
    return jsonify(Clase_RPG.obtener_clases())
@app.route('/api/enemigos')
def enemigos():
    return jsonify(Enemigos.obtener_enemigos())
@app.route('/api/habilidades')
def habilidades():
    return jsonify(Habilidades.obtener_habilidades())
@app.route('/api/habilidades_requisitos')
def habilidades_requisitos():
    return jsonify(Habilidades_Requisitos.obtener_habilidades_requisitos())
@app.route('/api/inventarios')
def inventarios():
    return jsonify(Inventario.obtener_inventarios())
@app.route('/api/items')
def items():
    return jsonify(Items.obtener_items())
@app.route('/api/logros')
def logros():
    return jsonify(Logros.obtener_logros())
@app.route('/api/personajes')
def personajes():
    return jsonify(Personaje.obtener_personajes())
@app.route('/api/personajes_habilidades')
def personajes_habilidades():
    return jsonify(Personajes_Habilidades.obtener_personajes_habilidades())
@app.route('/api/razas')
def razas():
    return jsonify(Razas.obtener_razas())
@app.route('/api/registros_combate')
def registros_combate():
    return jsonify(Registros_Combate.obtener_registros_combate())
@app.route('/api/tipos_item')
def tipos_item():
    return jsonify(Tipos_Item.obtener_tipos_item())

@socketio.on("comprobar_conexion")
def probar_conexion():
    """
    Usa el gestor de contexto importado para verificar la BD.
    """
    # Usamos el nombre exacto de la función que importamos
    with conectar_bd() as conexion:
        if conexion:
            emit("db_status", {"connected": True})
            print("✅ Estado de conexión enviado: Conectado")
        else:
            emit("db_status", {"connected": False})
            print("❌ Estado de conexión enviado: Desconectado")
    # Al salir del bloque 'with', la conexión se cierra sola automáticamente.

# Crear socket que muestre los personajes:
@socketio.on('personajes')
def mostrar_personajes():   # Esta función devolverá una List de los personajes actuales en la BD
    emit("personajes", Personaje.obtener_personajes())

@socketio.on('mostrar_habilidades')
def mostrar_habilidades(data):
    id_pj = data.get('id_personaje')
    emit("mostrar_habilidades", Personajes_Habilidades.mostrar_habilidades_pj(id_pj))

@socketio.on('mejorar_habilidades')
def mejorar_habilidades(data):
    id_pj = int(data.get('id_personaje'))
    id_hab = int(data.get('id_habilidad'))
    emit("mejorar_habilidades", Personajes_Habilidades.mejorar_habilidad_pj(id_pj, id_hab))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)