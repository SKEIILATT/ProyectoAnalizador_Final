'''
Backend Flask para el analizador de código GO
'''

'''Importaciones básicas para el uso de flask'''
from flask import Flask , request, jsonify
from flask_cors import CORS
import os

''' Importamos la función necesaría para el análisis de código '''
from lexico_go import analyze_code_string
from sintactico_go import analyze_syntax_string
from semantico_go import analyze_semantic_string

''' Creamos la aplicación flask '''
app = Flask(__name__)
CORS(app)

'''Primer endpoint para analizar el código escrito en el editor'''
@app.route('/api/analyze_code', methods=['POST'])
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
        sintactico_result = analyze_sintactico(code)
        semantico_result = analyze_semantico(code)

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
                
        lexico_result = analyze_lexico(code)
        sintactico_result = analyze_sintactico(code)
        semantico_result = analyze_semantico(code)
        
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
        return jsonify({
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

'''Creación del endpoint para analizar el archivo subido por el usuario'''
@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No se subió ningún archivo'
            }), 400
        file = request.files
        
        if file.filename == "":
            return jsonify({
                'error': 'Archivo sin nombre'
            }), 400
        if not file.filename.endswith(".go"):
            return jsonify({
                'error': 'El archivo debe tener extensión .go'
            }), 400
        code = file.read().decode('utf-8')
        
        lexico_result = analyze_lexico(code)
        sintactico_result = analyze_sintactico(code)
        semantico_result = analyze_semantico(code)

        "Construimos la respuesta "
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
        return jsonify({
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

