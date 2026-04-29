import os
from database.ConexionDB import conectar_bd, list_personajes  # importo la conexion de la base de datos
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import psycopg2
from models import Guerrero, Mago, Personaje

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/personajes')
def personajes():
    return jsonify(list_personajes())

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
    emit("personajes", list_personajes())

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)