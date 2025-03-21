import os
from flask import Flask, render_template, request, redirect, url_for
from baseDatos import db, Respuesta

# Define la ruta base del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configuración con ruta absoluta para la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos con la aplicación
db.init_app(app)

# Variables globales para almacenar respuestas
respuestas_amor = []
respuestas_dinero = []
respuestas_familia = []
respuestas_salud = []

# Variables globales para los porcentajes
porcentaje_amor = 0
porcentaje_dinero = 0
porcentaje_familia = 0
porcentaje_salud = 0

# Variables globales para los datos personales
global_nombre = ""
global_edad = 0
global_departamento = ""

def convertir_a_numeros(lista):
    """Convierte una lista de strings en una lista de enteros."""
    return [int(x) for x in lista if x and x.isdigit()]

def calcular_porcentaje(lista):
    """Calcula el porcentaje de una categoría."""
    if not lista:
        return 0
    return (sum(lista) / 50) * 25  # 50 es el máximo puntaje posible

def procesar_datos():
    """Convierte respuestas a números y calcula los porcentajes."""
    global respuestas_amor, respuestas_dinero, respuestas_familia, respuestas_salud
    global porcentaje_amor, porcentaje_dinero, porcentaje_familia, porcentaje_salud

    respuestas_amor = convertir_a_numeros(respuestas_amor)
    respuestas_dinero = convertir_a_numeros(respuestas_dinero)
    respuestas_familia = convertir_a_numeros(respuestas_familia)
    respuestas_salud = convertir_a_numeros(respuestas_salud)

    porcentaje_amor = calcular_porcentaje(respuestas_amor)
    porcentaje_dinero = calcular_porcentaje(respuestas_dinero)
    porcentaje_familia = calcular_porcentaje(respuestas_familia)
    porcentaje_salud = calcular_porcentaje(respuestas_salud)

# Ruta principal: formulario de menú
@app.route("/")
def main():
    return render_template("Main.html")

# Nueva ruta para datos personales (antes era "/")
@app.route("/personal", methods=["GET", "POST"])
def personal():
    global global_nombre, global_edad, global_departamento
    if request.method == "POST":
        global_nombre = request.form["nombre"]
        global_edad = int(request.form["edad"])
        global_departamento = request.form["departamento"]
        print(f"Datos personales: {global_nombre}, {global_edad}, {global_departamento}")
        return redirect(url_for("form_amor"))
    return render_template("FormInfoPersonal.html")

@app.route("/amor", methods=["GET", "POST"])
def form_amor():
    global respuestas_amor
    if request.method == "POST":
        respuestas_amor = [
            request.form.get("pregunta1"),
            request.form.get("pregunta2"),
            request.form.get("pregunta3"),
            request.form.get("pregunta4"),
            request.form.get("pregunta5")
        ]
        return redirect(url_for("form_dinero"))
    return render_template("FormAmor.html")

@app.route("/dinero", methods=["GET", "POST"])
def form_dinero():
    global respuestas_dinero
    if request.method == "POST":
        respuestas_dinero = [
            request.form.get("pregunta1"),
            request.form.get("pregunta2"),
            request.form.get("pregunta3"),
            request.form.get("pregunta4"),
            request.form.get("pregunta5")
        ]
        return redirect(url_for("form_familia"))
    return render_template("FormDinero.html")

@app.route("/familia", methods=["GET", "POST"])
def form_familia():
    global respuestas_familia
    if request.method == "POST":
        respuestas_familia = [
            request.form.get("pregunta1"),
            request.form.get("pregunta2"),
            request.form.get("pregunta3"),
            request.form.get("pregunta4"),
            request.form.get("pregunta5")
        ]
        return redirect(url_for("form_salud"))
    return render_template("FormFamilia.html")

@app.route("/salud", methods=["GET", "POST"])
def form_salud():
    global respuestas_salud
    if request.method == "POST":
        respuestas_salud = [
            request.form.get("pregunta1"),
            request.form.get("pregunta2"),
            request.form.get("pregunta3"),
            request.form.get("pregunta4"),
            request.form.get("pregunta5")
        ]
        return redirect(url_for("form_final"))
    return render_template("FormSalud.html")

# Ruta final: guarda datos y redirige al menú principal
@app.route("/final", methods=["GET", "POST"])
def form_final():
    global global_nombre, global_edad, global_departamento
    if request.method == "POST":
        procesar_datos()
        nueva_respuesta = Respuesta(
            nombre_completo=global_nombre,
            edad=global_edad,
            departamento=global_departamento,
            amor=porcentaje_amor,
            dinero=porcentaje_dinero,
            familia=porcentaje_familia,
            salud=porcentaje_salud
        )
        db.session.add(nueva_respuesta)
        db.session.commit()
        print("✅ Respuesta guardada en la base de datos.")
        # Tras guardar, redirigimos al menú principal
        return redirect(url_for("main"))
    return render_template("FormFinal.html")

# Ruta para visualizar resultados
@app.route("/resultados")
def ver_resultados():
    respuestas = Respuesta.query.all()
    print(f"📋 Se encontraron {len(respuestas)} registro(s) en la base de datos.")
    return render_template("Resultados.html", respuestas=respuestas)

@app.route("/eliminar/<int:respuesta_id>", methods=["POST"])
def eliminar_respuesta(respuesta_id):
    registro = Respuesta.query.get(respuesta_id)
    if registro:
        db.session.delete(registro)
        db.session.commit()
        print(f"Registro con ID {respuesta_id} eliminado.")
    else:
        print(f"No se encontró registro con ID {respuesta_id}.")
    return redirect(url_for("ver_resultados"))


if __name__ == "__main__":
    app.run(debug=True)
