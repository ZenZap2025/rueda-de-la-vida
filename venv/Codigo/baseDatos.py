from flask_sqlalchemy import SQLAlchemy

# Crear instancia de SQLAlchemy
db = SQLAlchemy()

# Definir modelo de datos
class Respuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Agregar autoincrement=True
    nombre_completo = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    departamento = db.Column(db.String(100), nullable=False)
    amor = db.Column(db.Float, nullable=False)
    dinero = db.Column(db.Float, nullable=False)
    familia = db.Column(db.Float, nullable=False)
    salud = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Respuesta {self.nombre_completo} - Amor: {self.amor}% - Dinero: {self.dinero}% - Familia: {self.familia}% - Salud: {self.salud}%>'
