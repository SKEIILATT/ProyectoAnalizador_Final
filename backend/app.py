'''
Backend Flask para el analizador de código GO
'''

'''Importaciones básicas para el uso de flask'''
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

''' Importamos la función necesaria para el análisis de código '''
from lexico_go import analyze_code_string
from sintactico_go import analyze_syntax_string
from semantico_go import analyze_semantic_string

''' Creamos la aplicación flask con soporte para servir frontend '''
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app)

'''Ruta principal - Sirve el frontend'''
@app.route('/')
def serve_frontend():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return jsonify({'error': f'Error al cargar la aplicación: {str(e)}'}), 500

'''Ruta para servir archivos estáticos del frontend (JS, CSS, assets)'''
@app.route('/<path:path>')
def serve_static(path):
    # No servir archivos estáticos para rutas de API
    if path.startswith('api/'):
        return jsonify({'error': 'Endpoint no encontrado'}), 404
    
    try:
        # Intentar servir el archivo solicitado
        return send_from_directory(app.static_folder, path)
    except:
        # Si el archivo no existe, servir index.html (para SPA routing)
        return send_from_directory(app.static_folder, 'index.html')

'''Primer endpoint para analizar el código escrito en el editor'''
@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No se proporcionó ningún código'}), 400
        code = data["code"]

        if not code or not code.strip():
            return jsonify({'error': 'El código proporcionado está vacío'}), 400
        
        print(f"\n{'='*50}")
        print("Analizando código desde editor...")
        print(f"{'='*50}")

        lexico_result = analyze_code_string(code)
        sintactico_result = analyze_syntax_string(code)
        semantico_result = analyze_semantic_string(code)

        "Construyo las respuestas"
        response = {
            'lexico': {
                'tokens': lexico_result['tokens'],
                'errores': lexico_result['errors']
            },
            'sintactico': {
                'errores': sintactico_result['errors']
            },
            'semantico': {
                'errores': semantico_result['errors'],
                'tabla_simbolos': semantico_result['symbol_table']
            }
        }
        return jsonify(response), 200
    except Exception as e:
        print(f"Error en analyze_code: {str(e)}")
        return jsonify({'error': str(e)}), 500

"Creación del endpoint para analizar los archivos subidos por el usuario"
@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No se subió ningún archivo'
            }), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': 'Archivo sin nombre'
            }), 400
        if not file.filename.endswith('.go'):
            return jsonify({
                'error': 'El archivo debe tener extensión .go'
            }), 400
        code = file.read().decode('utf-8')
                
        lexico_result = analyze_code_string(code)
        sintactico_result = analyze_syntax_string(code)
        semantico_result = analyze_semantic_string(code)
        
        response = {
            'lexico': {
                'tokens': lexico_result['tokens'],
                'errores': lexico_result['errors']
            },
            'sintactico': {
                'errores': sintactico_result['errors']
            },
            'semantico': {
                'errores': semantico_result['errors'],
                'tabla_simbolos': semantico_result['symbol_table']
            },
            'filename': file.filename,
            'code': code  
        }
        
        return jsonify(response), 200
    
    except UnicodeDecodeError:
        return jsonify({
            'error': 'El archivo no está en formato UTF-8 válido'
        }), 400
    
    except Exception as e:
        print(f"Error en analyze_file: {str(e)}")
        return jsonify({
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

'''Endpoint de health check para verificar que el servidor está funcionando'''
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Analizador de Go funcionando correctamente'
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)