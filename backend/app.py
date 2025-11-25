'''
Backend Flask para el analizador de código GO
'''

'''Importaciones básicas para el uso de flask'''
from flask import Flask , request, jsonify
from flask_cors import CORS
import os

''' Importamos la función necesaría para el análisis de código '''
from lexico_go import analyze_code_string
from sintactico_go import analyze_sintactico
from semantico_go import analyze_semantico

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




