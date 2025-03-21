from app import app
from baseDatos import db

with app.app_context():
    db.create_all()
    print("✅ Base de datos creada exitosamente.")