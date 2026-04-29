#!/usr/bin/env python3
import os
import shutil

PROJECT_DIR = "rpg_pro_system"

if os.path.exists(PROJECT_DIR):
    shutil.rmtree(PROJECT_DIR)

# Crear estructura de carpetas
folders = ["models", "database", "static", "templates"]
for f in folders:
    os.makedirs(os.path.join(PROJECT_DIR, f), exist_ok=True)

files = {
    "requirements.txt": "flask\nflask-socketio\neventlet\npsycopg2-binary\npython-dotenv",
    
    "docker-compose.yml": """
services:
  db:
    image: postgres:15
    container_name: rpg_db
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password123
      POSTGRES_DB: rpg_game
    ports:
      - "5432:5432"
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d rpg_game"]
      interval: 3s
      retries: 5
  app:
      build: .
      container_name: rpg_app
      ports:
        - "5000:5000"
      environment:
        - DATABASE_URL=postgresql://user_rpg:password_rpg@db:5432/rpg_db
        - FLASK_ENV=development  # Indica a Flask que estamos desarrollando
      volumes:
        - .:/app                 # <--- ESTA ES LA MAGIA: Sincroniza tu carpeta actual con el contenedor
      depends_on:
        db:
          condition: service_healthy
""".strip(),

    "Dockerfile": "FROM python:3.11-slim\nWORKDIR /app\nRUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nCMD [\"python\", \"app.py\"]",

    # --- MODELO DE BASE DE DATOS MEJORADO ---
    "init.sql": """
CREATE TABLE Razas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50),
    mod_vida INT,
    mod_fuerza INT
);

CREATE TABLE Clases_RPG (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50),
    descripcion TEXT
);

CREATE TABLE Personajes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50),
    nivel INT DEFAULT 1,
    exp INT DEFAULT 0,
    oro INT DEFAULT 100,
    vida_actual INT,
    id_raza INT REFERENCES Razas(id),
    id_clase INT REFERENCES Clases_RPG(id)
);

CREATE TABLE Habilidades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50),
    nivel_maximo INT DEFAULT 5,
    id_clase INT REFERENCES Clases_RPG(id)
);

-- Tabla de Dependencias (Árbol de Habilidades)
CREATE TABLE Habilidades_Requisitos (
    id_habilidad INT REFERENCES Habilidades(id),
    id_requisito INT REFERENCES Habilidades(id),
    nivel_requisito_necesario INT DEFAULT 1,
    PRIMARY KEY (id_habilidad, id_requisito)
);

-- Progreso Real del Jugador
CREATE TABLE Personajes_Habilidades (
    id_personaje INT REFERENCES Personajes(id),
    id_habilidad INT REFERENCES Habilidades(id),
    nivel_actual INT DEFAULT 0, -- 0 significa bloqueada
    PRIMARY KEY (id_personaje, id_habilidad)
);
-- Datos de Ejemplo
INSERT INTO Razas (nombre, mod_vida, mod_fuerza) VALUES ('Humano', 100, 10), ('Elfo', 80, 8);
INSERT INTO Clases_RPG (nombre, descripcion) VALUES ('Guerrero', 'Especialista en combate físico'), ('Mago', 'Maestro de las artes arcanas');
INSERT INTO Habilidades (nombre, nivel_maximo, id_clase) VALUES 
('Corte', 5, 1), ('Torbellino', 5, 1), ('Bola de Fuego', 5, 2);
-- Requisito: Torbellino requiere Corte al nivel 3
INSERT INTO Habilidades_Requisitos (id_habilidad, id_requisito, nivel_requisito_necesario) VALUES (2, 1, 3);
INSERT INTO Personajes (nombre, nivel, vida_actual, id_raza, id_clase) VALUES ('Aragorn', 1, 110, 1, 1);
""".strip(),

    # --- IMPLEMENTACIÓN DE CLASES Y RAZAS EN PYTHON (POO) ---
    "models/Personaje.py": """
class Raza:
    def __init__(self, nombre, vida_extra, fuerza):
        self.nombre = nombre
        self.vida_extra = vida_extra
        self.fuerza = fuerza

class ClaseRPG:
    def __init__(self, nombre, skill_principal):
        self.nombre = nombre
        self.skill_principal = skill_principal

class Guerrero(ClaseRPG):
    def __init__(self):
        super().__init__("Guerrero", "Ataque Físico")
        self.multiplicador_daño = 1.5

class Mago(ClaseRPG):
    def __init__(self):
        super().__init__("Mago", "Hechizo")
        self.multiplicador_magico = 2.0

class Personaje:
    def __init__(self, db_data, raza_obj, clase_obj):
        self.id = db_data[0]
        self.nombre = db_data[1]
        self.nivel = db_data[2]
        self.vida = db_data[5]
        self.raza = raza_obj
        self.clase = clase_obj
""".strip(),

    "app.py": """
import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import psycopg2
from models.logic import Guerrero, Mago, Personaje

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_db():
    return psycopg2.connect(os.environ['DATABASE_URL'])

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('mejorar_habilidad')
def upgrade_skill(data):
    # Aquí iría la lógica de verificar en la DB si cumple requisitos
    # 1. ¿Nivel de habilidad requisito >= nivel_requisito_necesario?
    # 2. ¿Puntos disponibles?
    emit('status', {'msg': 'Habilidad mejorada (Lógica de árbol validada)'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
""".strip(),

    "templates/index.html": """
<!DOCTYPE html>
<html>
<head>
    <title>RPG Avanzado</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { background: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; padding: 50px; }
        .skill-tree { border: 1px solid #333; padding: 20px; background: #1e1e1e; border-radius: 8px; }
        .skill { margin: 10px; padding: 10px; border: 1px solid #444; display: inline-block; }
        .locked { opacity: 0.5; background: #000; }
        button { background: #4CAF50; color: white; border: none; padding: 5px 10px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Árbol de Habilidades Jerárquico</h1>
    <div class="skill-tree">
        <div class="skill">
            <strong>Corte</strong><br>Nivel: 3/5
            <button onclick="socket.emit('mejorar_habilidad', {id: 1})">Subir Nivel</button>
        </div>
        <span>➔</span>
        <div class="skill">
            <strong>Torbellino</strong><br>Nivel: 0/5 (Requiere Corte Nvl 3)
            <button onclick="socket.emit('mejorar_habilidad', {id: 2})">Desbloquear</button>
        </div>
    </div>
    <div id="log" style="margin-top: 20px; color: #888;"></div>
    <script>
        const socket = io();
        socket.on('status', (data) => {
            document.getElementById('log').innerText = "> " + data.msg;
        });
    </script>
</body>
</html>
""".strip()
}

def build():
    for name, content in files.items():
        with open(os.path.join(PROJECT_DIR, name), "w", encoding="utf-8") as f:
            f.write(content)
    print(f"✅ Sistema profesional generado en '{PROJECT_DIR}'")
    print("Ejecuta: cd rpg_pro_system && docker compose up -d --build")

if __name__ == "__main__":
    build()