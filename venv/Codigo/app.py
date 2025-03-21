from flask import Flask, render_template, request, redirect, url_for
from baseDatos import db, Respuesta
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
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

    # Convertir respuestas a números
    respuestas_amor = convertir_a_numeros(respuestas_amor)
    respuestas_dinero = convertir_a_numeros(respuestas_dinero)
    respuestas_familia = convertir_a_numeros(respuestas_familia)
    respuestas_salud = convertir_a_numeros(respuestas_salud)

    # Calcular porcentajes
    porcentaje_amor = calcular_porcentaje(respuestas_amor)
    porcentaje_dinero = calcular_porcentaje(respuestas_dinero)
    porcentaje_familia = calcular_porcentaje(respuestas_familia)
    porcentaje_salud = calcular_porcentaje(respuestas_salud)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        nombre = request.form["nombre"]
        edad = request.form["edad"]
        departamento = request.form["departamento"]
        print(f"Datos recibidos: {nombre}, {edad} años, de {departamento}.")
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

@app.route("/final")
def form_final():
    procesar_datos()  # Convertir respuestas y calcular porcentajes antes de mostrar resultados
    print(f"✅ Respuestas de Amor: {respuestas_amor} -> Porcentaje: {porcentaje_amor}%")
    print(f"✅ Respuestas de Dinero: {respuestas_dinero} -> Porcentaje: {porcentaje_dinero}%")
    print(f"✅ Respuestas de Familia: {respuestas_familia} -> Porcentaje: {porcentaje_familia}%")
    print(f"✅ Respuestas de Salud: {respuestas_salud} -> Porcentaje: {porcentaje_salud}%")
    if request.method == "POST":
        nombre_completo = request.form["nombre"]
        edad = int(request.form["edad"])
        departamento = request.form["departamento"]

        # Guardar en la base de datos
        nueva_respuesta = Respuesta(
            nombre_completo=nombre_completo,
            edad=edad,
            departamento=departamento,
            amor=calcular_porcentaje(respuestas_amor),
            dinero=calcular_porcentaje(respuestas_dinero),
            familia=calcular_porcentaje(respuestas_familia),
            salud=calcular_porcentaje(respuestas_salud)
        )

        db.session.add(nueva_respuesta)
        db.session.commit()

        return redirect(url_for("ver_resultados"))
    return render_template("FormFinal.html")
    

if __name__ == "__main__":
    app.run(debug=True)
