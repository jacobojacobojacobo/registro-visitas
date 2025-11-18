from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import requests
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Cargar variables del .env
load_dotenv()

app = Flask(__name__)

# Verificar que DATABASE_URL sí se cargó
print("USANDO DB:", os.getenv("DATABASE_URL"))

# Configurar DB Neon con pool_pre_ping y pool_recycle
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,     # verifica que la conexión siga viva antes de usarla
    "pool_recycle": 1800       # reinicia conexiones cada 30 minutos
}

db = SQLAlchemy(app)

# Tu URL de Google Sheets Webhook
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxeQkL5HXrKar2KSbjmChYuouQUIItGVIt67OEhimSaJfLVOdttBFybTkcHRYhOD81c/exec"

# Modelo en Neon
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

# Crear tabla si no existe
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Crear nuevo registro
    nuevo = Registro()
    db.session.add(nuevo)
    db.session.commit()

    # Fecha formateada para Sheets
    fecha_formateada = nuevo.fecha.strftime("%Y-%m-%d %H:%M:%S")

    # Enviar a Sheets
    try:
        requests.post(WEBHOOK_URL, json={"fecha": fecha_formateada})
    except Exception as e:
        print("Error enviando a Google Sheets:", e)

    return render_template('index.html', fecha=fecha_formateada)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
