import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
    """Convierte respuestas a números."""
    global respuestas_amor, respuestas_dinero, respuestas_familia, respuestas_salud
    respuestas_amor = convertir_a_numeros(respuestas_amor)
    respuestas_dinero = convertir_a_numeros(respuestas_dinero)
    respuestas_familia = convertir_a_numeros(respuestas_familia)
    respuestas_salud = convertir_a_numeros(respuestas_salud)

# Ruta principal: Menú
@app.route("/")
def main():
    return render_template("Main.html")

# Ruta para datos personales
@app.route("/personal", methods=["GET", "POST"])
def personal():
    global global_nombre, global_edad, global_departamento
    if request.method == "POST":
        global_nombre = request.form["nombre"]
        global_edad = int(request.form["edad"])
        global_departamento = request.form["departamento"]
        return redirect(url_for("form_amor"))
    return render_template("FormInfoPersonal.html")

@app.route("/amor", methods=["GET", "POST"])
def form_amor():
    global respuestas_amor
    if request.method == "POST":
        respuestas_amor = [request.form.get(f"pregunta{i}") for i in range(1, 6)]
        return redirect(url_for("form_dinero"))
    return render_template("FormAmor.html")

@app.route("/dinero", methods=["GET", "POST"])
def form_dinero():
    global respuestas_dinero
    if request.method == "POST":
        respuestas_dinero = [request.form.get(f"pregunta{i}") for i in range(1, 6)]
        return redirect(url_for("form_familia"))
    return render_template("FormDinero.html")

@app.route("/familia", methods=["GET", "POST"])
def form_familia():
    global respuestas_familia
    if request.method == "POST":
        respuestas_familia = [request.form.get(f"pregunta{i}") for i in range(1, 6)]
        return redirect(url_for("form_salud"))
    return render_template("FormFamilia.html")

@app.route("/salud", methods=["GET", "POST"])
def form_salud():
    global respuestas_salud
    if request.method == "POST":
        respuestas_salud = [request.form.get(f"pregunta{i}") for i in range(1, 6)]
        return redirect(url_for("form_final"))
    return render_template("FormSalud.html")

# Ruta final: Guarda los datos y redirige al menú principal
@app.route("/final", methods=["GET", "POST"])
def form_final():
    global global_nombre, global_edad, global_departamento
    if request.method == "POST":
        procesar_datos()
        nueva_respuesta = Respuesta(
            nombre_completo=global_nombre,
            edad=global_edad,
            departamento=global_departamento,
            amor=calcular_porcentaje(respuestas_amor),
            dinero=calcular_porcentaje(respuestas_dinero),
            familia=calcular_porcentaje(respuestas_familia),
            salud=calcular_porcentaje(respuestas_salud)
        )
        db.session.add(nueva_respuesta)
        db.session.commit()
        return redirect(url_for("main"))
    return render_template("FormFinal.html")

# Ruta para visualizar resultados
@app.route("/resultados")
def ver_resultados():
    registros = Respuesta.query.all()
    return render_template("Resultados.html", respuestas=registros)

# Ruta para eliminar respuesta
@app.route("/eliminar/<int:respuesta_id>", methods=["POST"])
def eliminar_respuesta(respuesta_id):
    registro = Respuesta.query.get(respuesta_id)
    if registro:
        db.session.delete(registro)
        db.session.commit()
    return redirect(url_for("ver_resultados"))

# Ruta para métricas y gráficos
@app.route("/metricas")
def ver_metricas():
    registros = Respuesta.query.all()
    if not registros:
        return render_template("metricas.html", hay_datos=False)

    # Convertir registros a DataFrame con Pandas
    df = pd.DataFrame([{
        "edad": r.edad,
        "departamento": r.departamento,
        "amor": r.amor,
        "dinero": r.dinero,
        "familia": r.familia,
        "salud": r.salud
    } for r in registros])

    # Gráfico 1: Promedio general por categoría (barras)
    promedios = df[["amor", "dinero", "familia", "salud"]].mean()
    categorias = ["Amor", "Dinero", "Familia", "Salud"]
    plt.figure(figsize=(8, 5))
    plt.bar(categorias, promedios, color=['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9'])
    plt.ylim(0, 100)
    plt.title("Promedio General por Categoría")
    ruta_promedios = os.path.join(BASE_DIR, "static", "images", "promedios.png")
    plt.savefig(ruta_promedios)
    plt.close()

    # Gráfico 2: Histograma de edades
    plt.figure(figsize=(8, 5))
    plt.hist(df["edad"], bins=10, color='#BAE1FF', edgecolor='black')
    plt.xlabel("Edad")
    plt.ylabel("Cantidad de Personas")
    plt.title("Distribución de Edades")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    ruta_edades = os.path.join(BASE_DIR, "static", "images", "edades.png")
    plt.savefig(ruta_edades)
    plt.close()

    # Gráfico 3: Participantes por Departamento (barras)
    plt.figure(figsize=(8, 5))
    df["departamento"].value_counts().plot(kind="bar", color="#D5AAFF", edgecolor='black')
    plt.xlabel("Departamento")
    plt.ylabel("Cantidad de Participantes")
    plt.title("Participantes por Departamento")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    ruta_departamentos = os.path.join(BASE_DIR, "static", "images", "departamentos.png")
    plt.savefig(ruta_departamentos)
    plt.close()

    # Gráfico 4: Gráfica de torta (pie chart) de los promedios por categoría
    plt.figure(figsize=(8, 5))
    plt.pie(promedios.values, labels=categorias, autopct='%1.1f%%',
            colors=['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9'])
    plt.title("Distribución de Promedios por Categoría")
    ruta_torta = os.path.join(BASE_DIR, "static", "images", "torta.png")
    plt.savefig(ruta_torta)
    plt.close()

    # Gráfico 5: Scatter plot: correlación entre edad y amor
    plt.figure(figsize=(8, 5))
    plt.scatter(df["edad"], df["amor"], color="#B0E0E6", edgecolor="black")
    plt.xlabel("Edad")
    plt.ylabel("Puntuación Amor")
    plt.title("Correlación entre Edad y Amor")
    plt.grid(True, linestyle="--", alpha=0.7)
    ruta_scatter = os.path.join(BASE_DIR, "static", "images", "scatter.png")
    plt.savefig(ruta_scatter)
    plt.close()

    return render_template("metricas.html", hay_datos=True)

if __name__ == "__main__":
    app.run(debug=True)


