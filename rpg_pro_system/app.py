import os
from database.ConexionDB import conectar_bd  # importo la conexion de la base de datos
from models.Clase_RPG import obtener_clases
from models.Enemigos import obtener_enemigos
from models.Habilidades import obtener_habilidades
from models.Inventarios import obtener_inventario
from models.Items import obtener_items
from models.Personajes_Habilidades import obtener_personajes_habilidades
from models.Personaje import obtener_personajes
from models.Habilidades_Requisitos import obtener_habilidades_requisitos
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import psycopg2

from models.Razas import obtener_razas
from models.logros import obtener_logros

# from models import Guerrero, Mago, Personaje

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
@app.route('/')
def index():
    return render_template('index.html')

# CREAR APIS
@app.route('/api/clases')
def clases():
    return jsonify(obtener_clases())
@app.route('/api/enemigos')
def enemigos():
    return jsonify(obtener_enemigos())
@app.route('/api/habilidades')
def habilidades():
    return jsonify(obtener_habilidades())

@app.route('/api/habilidades_requisitos')
def habilidades_requisitos():
    return jsonify(obtener_habilidades_requisitos())

@app.route('/api/inventarios')
def inventarios():
    return jsonify(obtener_inventario())

@app.route('/api/items')
def items():
    return jsonify(obtener_items())

@app.route('/api/logros')
def logros():
    return jsonify(obtener_logros())
@app.route('/api/personajes')
def personajes():
    return jsonify(obtener_personajes())
@app.route('/api/personajes_habilidades')
def personajes_habilidades():
    return jsonify(obtener_personajes_habilidades())
@app.route('/api/razas')
def razas():
    return jsonify(obtener_razas())

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
    emit("personajes", obtener_personajes())

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)