"""
app.py — Backend de la Galería de Arte
---------------------------------------
Estrategia de imágenes (dos campos separados en cada documento):
  imagen_thumbnail : Base64 de la imagen reducida (~400px ancho).
                     Se incluye en el listado → grid liviano.
  imagen_data      : Base64 de la imagen en resolución completa.
                     Solo se devuelve en el detalle individual → modal.
  imagen_url       : URL externa, usada como fallback para los datos
                     de inicialización que no tienen imagen subida.
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()   # Carga las variables del archivo .env en os.environ

app = Flask(__name__)
CORS(app)   # Permite peticiones cross-origin desde el frontend Vue

# Conexión a MongoDB usando el nombre de servicio "mongo" de docker-compose
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["galeria_db"]
coleccion = db["obras"]


# ── Serialización ────────────────────────────────────────────────────────────

def serializar(obra):
    """Convierte _id (ObjectId) a string para que sea serializable a JSON."""
    obra["_id"] = str(obra["_id"])
    return obra

def serializar_lista(obra):
    """
    Para listados: convierte _id y ELIMINA imagen_data (la versión pesada).
    Se conserva imagen_thumbnail (versión reducida) para mostrar en el grid.
    Se conserva imagen_url como fallback para las obras del seed.
    """
    obra["_id"] = str(obra["_id"])
    obra.pop("imagen_data", None)   # Excluye solo la versión completa, no el thumbnail
    return obra


# ════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def health():
    """Health check: confirma que el servidor está activo."""
    return jsonify({"estado": "OK", "servicio": "Galería de Arte API"}), 200


@app.route("/api/obras", methods=["GET"])
def obtener_obras():
    """
    Devuelve todas las obras SIN imagen_data (versión pesada).
    Incluye imagen_thumbnail (versión liviana) para mostrar en el grid.
    Acepta filtros opcionales: ?categoria=X  y/o  ?tipo=pintura
    """
    categoria = request.args.get("categoria")
    tipo = request.args.get("tipo")

    query = {}
    if categoria:
        query["categorias"] = categoria
    if tipo:
        query["tipo"] = tipo

    # Proyección: excluir solo imagen_data; el thumbnail SÍ se incluye
    proyeccion = {"imagen_data": 0}

    obras = list(coleccion.find(query, proyeccion).sort("año", -1))
    return jsonify([serializar_lista(o) for o in obras]), 200


@app.route("/api/obras/<id>", methods=["GET"])
def obtener_obra(id):
    """
    Devuelve TODOS los campos de una obra, incluyendo imagen_data completa.
    Se usa al abrir el modal de detalle o el formulario de edición.
    """
    try:
        obra = coleccion.find_one({"_id": ObjectId(id)})
    except Exception:
        return jsonify({"error": "ID inválido"}), 400

    if not obra:
        return jsonify({"error": "Obra no encontrada"}), 404

    return jsonify(serializar(obra)), 200


@app.route("/api/categorias", methods=["GET"])
def obtener_categorias():
    """Devuelve los valores únicos del campo 'categorias' en toda la colección."""
    categorias = coleccion.distinct("categorias")
    return jsonify(sorted(categorias)), 200


@app.route("/api/obras", methods=["POST"])
def crear_obra():
    """
    Crea una nueva obra. Espera los campos:
      imagen_thumbnail : Base64 de imagen reducida (para el grid)
      imagen_data      : Base64 de imagen completa (para el modal)
      imagen_url       : URL externa opcional (fallback)
    """
    datos = request.get_json()

    for campo in ["titulo", "artista", "año", "tipo"]:
        if campo not in datos or not str(datos[campo]).strip():
            return jsonify({"error": f"El campo '{campo}' es requerido"}), 400

    nueva_obra = {
        "titulo":           datos.get("titulo",      "").strip(),
        "artista":          datos.get("artista",     "").strip(),
        "año":              int(datos.get("año", 0)),
        "tipo":             datos.get("tipo",        "pintura"),
        "tecnica":          datos.get("tecnica",     "").strip(),
        "ubicacion":        datos.get("ubicacion",   "").strip(),
        "descripcion":      datos.get("descripcion", "").strip(),
        "imagen_url":       datos.get("imagen_url",  "").strip(),
        "imagen_thumbnail": datos.get("imagen_thumbnail", ""),   # Versión reducida para el grid
        "imagen_data":      datos.get("imagen_data",      ""),   # Versión completa para el modal
        "categorias":       datos.get("categorias",  []),
    }

    resultado = coleccion.insert_one(nueva_obra)
    return jsonify({
        "mensaje": "Obra registrada correctamente",
        "id": str(resultado.inserted_id)
    }), 201


@app.route("/api/obras/<id>", methods=["PUT"])
def editar_obra(id):
    """
    Actualiza los campos de una obra con $set (solo modifica lo enviado).
    Si viene imagen_thumbnail nueva, actualiza el grid.
    Si viene imagen_data nueva, actualiza el modal.
    """
    datos = request.get_json()

    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({"error": "ID inválido"}), 400

    if not coleccion.find_one({"_id": oid}):
        return jsonify({"error": "Obra no encontrada"}), 404

    campos = {}

    if "titulo"      in datos: campos["titulo"]      = datos["titulo"].strip()
    if "artista"     in datos: campos["artista"]     = datos["artista"].strip()
    if "año"         in datos: campos["año"]         = int(datos["año"])
    if "tipo"        in datos: campos["tipo"]        = datos["tipo"]
    if "tecnica"     in datos: campos["tecnica"]     = datos["tecnica"].strip()
    if "ubicacion"   in datos: campos["ubicacion"]   = datos["ubicacion"].strip()
    if "descripcion" in datos: campos["descripcion"] = datos["descripcion"].strip()
    if "imagen_url"  in datos: campos["imagen_url"]  = datos["imagen_url"].strip()
    if "categorias"  in datos: campos["categorias"]  = datos["categorias"]

    # Actualizar las dos versiones de imagen solo si vienen con valor
    if datos.get("imagen_thumbnail"):
        campos["imagen_thumbnail"] = datos["imagen_thumbnail"]
    if datos.get("imagen_data"):
        campos["imagen_data"] = datos["imagen_data"]

    if not campos:
        return jsonify({"error": "No se enviaron campos para actualizar"}), 400

    coleccion.update_one({"_id": oid}, {"$set": campos})

    # Devolver la obra actualizada sin imagen_data (para ahorrar ancho de banda)
    obra_actualizada = coleccion.find_one({"_id": oid}, {"imagen_data": 0})
    return jsonify(serializar(obra_actualizada)), 200


@app.route("/api/obras/<id>", methods=["DELETE"])
def eliminar_obra(id):
    """Elimina la obra y sus imágenes almacenadas en el documento."""
    try:
        resultado = coleccion.delete_one({"_id": ObjectId(id)})
    except Exception:
        return jsonify({"error": "ID inválido"}), 400

    if resultado.deleted_count == 0:
        return jsonify({"error": "Obra no encontrada"}), 404

    return jsonify({"mensaje": "Obra eliminada correctamente"}), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.environ.get("FLASK_ENV") == "development"
    )
