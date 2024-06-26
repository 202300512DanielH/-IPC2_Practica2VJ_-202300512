from flask import Flask, request, jsonify, Response
import xml.etree.ElementTree as ET
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'cargas/'  # Especifica la carpeta donde se guardarán los archivos cargados

libros = None  # Inicializar libros como None o como una lista vacía []

# Cargar libros desde el XML cargado mediante una solicitud POST
@app.route('/cargarLibros', methods=['POST'])
def cargar_libros():
    # Verifica si el post request tiene el archivo parte
    if 'file' not in request.files:
        return jsonify({"mensaje": "No file part"}), 400
    file = request.files['file']
    # Si el usuario no selecciona un archivo, el navegador puede
    # enviar una parte sin nombre de archivo
    if file.filename == '':
        return jsonify({"mensaje": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Cargar el archivo XML
        tree = ET.parse(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        global libros
        libros = tree.getroot()
        return jsonify({"mensaje": "Libros cargados exitosamente"}), 200

# Ver todos los libros en formato JSON
@app.route('/verLibros', methods=['GET'])
def ver_libros():
    lista_libros = []
    for libro in libros:
        lista_libros.append({
            "id": libro.get('id'),
            "titulo": libro.find('titulo').text,
            "autor": libro.find('autor').text,
            "idioma": libro.find('idioma').text,
            "categoria": libro.find('categoria').text,
            "editorial": libro.find('editorial').text,
            "copias": libro.find('copias').text
        })
    return jsonify(lista_libros)

# Ver un libro por ID en formato XML
@app.route('/verLibro/<id>', methods=['GET'])
def ver_libro(id):
    for libro in libros:
        if libro.get('id') == id:
            return Response(ET.tostring(libro, encoding='utf8', method='xml'), mimetype='text/xml')
    return jsonify({"mensaje": "Libro no encontrado"}), 404

# Filtrar libros por categoría en formato JSON
@app.route('/libros/<categoria>', methods=['GET'])
def libros_categoria(categoria):
    lista_libros = []
    for libro in libros:
        if libro.find('categoria').text == categoria:
            # Extraer todos los detalles relevantes del libro
            datos_libro = {
                "id": libro.get('id'),
                "titulo": libro.find('titulo').text,
                "autor": libro.find('autor').text,
                "idioma": libro.find('idioma').text,
                "categoria": libro.find('categoria').text,
                "editorial": libro.find('editorial').text,
                "copias": libro.find('copias').text
            }
            lista_libros.append(datos_libro)
    return jsonify(lista_libros)

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"mensaje": "Método no permitido"}), 405


if __name__ == '__main__':
    app.run(debug=True)
