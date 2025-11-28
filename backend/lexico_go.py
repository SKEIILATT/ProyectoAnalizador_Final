"""
Analizador Léxico para el Lenguaje Go
Proyecto: Implementación de un Analizador Léxico en Go
Integrantes:
- Jair Palaguachi (JairPalaguachi)
- Javier Gutiérrez (SKEIILATT)
- Leonardo Macías (leodamac)

"""

import ply.lex as lex
from datetime import datetime
import sys
import os
import subprocess

# Palabras reservadas de Go
reserved = {
    'break': 'BREAK',
    'case': 'CASE',
    'chan': 'CHAN',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'defer': 'DEFER',
    'else': 'ELSE',
    'fallthrough': 'FALLTHROUGH',
    'for': 'FOR',
    'func': 'FUNC',
    'go': 'GO',
    'goto': 'GOTO',
    'if': 'IF',
    'import': 'IMPORT',
    'interface': 'INTERFACE',
    'map': 'MAP',
    'package': 'PACKAGE',
    'range': 'RANGE',
    'return': 'RETURN',
    'select': 'SELECT',
    'struct': 'STRUCT',
    'switch': 'SWITCH',
    'type': 'TYPE',
    'var': 'VAR',
    'make': 'MAKE',
    'append': 'APPEND',
    'len': 'LEN',
    'delete': 'DELETE',
    'nil': 'NIL',
}

# Lista de tokens
tokens = [
    'ID', 'UNDERSCORE', 'INT_LITERAL', 'FLOAT_LITERAL', 'STRING_LITERAL',
    'RUNE_LITERAL', 'BOOL_LITERAL', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'INCREMENT', 'DECREMENT', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'AND', 'OR', 'NOT',
    'ASSIGN', 'DECLARE_ASSIGN', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'TIMES_ASSIGN',
    'DIVIDE_ASSIGN', 'MOD_ASSIGN', 'AND_ASSIGN', 'OR_ASSIGN', 'XOR_ASSIGN',
    'LSHIFT_ASSIGN', 'RSHIFT_ASSIGN', 'BITAND', 'BITOR', 'BITXOR', 'BITNOT',
    'LSHIFT', 'RSHIFT', 'AND_NOT', 'ADDRESS', 'POINTER', 'CHANNEL_OP',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
    'SEMICOLON', 'COMMA', 'DOT', 'COLON', 'ELLIPSIS',
] + list(reserved.values())

# Tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COMMA = r','
t_DOT = r'\.'
t_COLON = r':'
t_EQ = r'=='
t_NE = r'!='
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_DECLARE_ASSIGN = r':='
t_PLUS_ASSIGN = r'\+='
t_MINUS_ASSIGN = r'-='
t_TIMES_ASSIGN = r'\*='
t_DIVIDE_ASSIGN = r'/='
t_MOD_ASSIGN = r'%='
t_LSHIFT_ASSIGN = r'<<='
t_RSHIFT_ASSIGN = r'>>='
t_LSHIFT = r'<<'
t_RSHIFT = r'>>'
t_AND_NOT = r'&\^'
t_BITAND = r'&'
t_BITOR = r'\|'
t_BITXOR = r'\^'
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'
t_CHANNEL_OP = r'<-'
t_ELLIPSIS = r'\.\.\.'
t_ASSIGN = r'='

# Literales booleanos
def t_BOOL_LITERAL(t):
    r'\b(true|false)\b'
    return t

# Literales flotantes
def t_FLOAT_LITERAL(t):
    r'\d+\.\d+([eE][+-]?\d+)?|\d+[eE][+-]?\d+'
    t.value = float(t.value)
    return t

# Literales enteros
def t_INT_LITERAL(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Literales de cadena
def t_STRING_LITERAL(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]
    return t

# Literales de runa
def t_RUNE_LITERAL(t):
    r"'([^'\\]|\\.)'"
    return t

# Identificador underscore
def t_UNDERSCORE(t):
    r'_(?![a-zA-Z0-9_])'
    return t

# Identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Comentarios de una línea
def t_COMMENT_SINGLE(t):
    r'//[^\n]*'
    pass

# Comentarios multilínea
def t_COMMENT_MULTI(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

# Saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Espacios, tabulaciones y retornos de carro (Windows)
t_ignore = ' \t\r'

# Manejo de errores - CORREGIDO
def t_error(t):
    column = find_column(t)
    error_obj = {
        'char': t.value[0],
        'line': t.lineno,
        'column': column,
        'message': f"Carácter ilegal '{t.value[0]}'"
    }
    
    if hasattr(t.lexer, 'errors_list'):
        t.lexer.errors_list.append(error_obj)
    
    t.lexer.skip(1)

# Función auxiliar para encontrar la columna - CORREGIDA
def find_column(token):
    if hasattr(token, 'lexer') and hasattr(token.lexer, 'source_code'):
        lexer_data = token.lexer.source_code
        line_start = lexer_data.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1
    else:
        return 0

# ============================================================================
# Para usar en API REST
# ============================================================================

def analyze_code_string(code_string):
    """
    Analiza código Go recibido como string (para API).
    Devuelve un diccionario con tokens y errores estructurados.
    """
    # Crear un nuevo lexer para esta petición
    import lexico_go
    new_lexer = lex.lex(module=lexico_go)
    
    # Inicializamos atributos personalizados
    new_lexer.tokens_list = []
    new_lexer.errors_list = []
    new_lexer.source_code = code_string
    
    # Reiniciamos el lexer
    new_lexer.lineno = 1
    new_lexer.input(code_string)
    
    # Tokenizar
    while True:
        tok = new_lexer.token()
        if not tok:
            break
        
        column = find_column(tok)
        token_obj = {
            'type': tok.type,
            'value': str(tok.value),
            'line': tok.lineno,
            'column': column
        }
        new_lexer.tokens_list.append(token_obj)
    
    # Devolver datos 
    return {
        'tokens': new_lexer.tokens_list,
        'errors': new_lexer.errors_list
    }

# ============================================================================
# Para usar en CLI
# ============================================================================

def get_git_username():
    """Obtiene el nombre de usuario de Git configurado localmente."""
    try:
        username = subprocess.check_output(
            ['git', 'config', 'user.name'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        return username if username else 'usergit'
    except:
        return 'usergit'

def analyze_file(filename):
    """Analiza un archivo de código Go (para CLI)."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{filename}' no fue encontrado.")
        return
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return
    
    result = analyze_code_string(data)
    
    # Crear carpeta de logs si no existe
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Obtener nombre de usuario de Git
    git_username = get_git_username()
    
    # Extraer nombre del archivo sin extensión
    file_base = os.path.splitext(os.path.basename(filename))[0]
    
    # Generar nombre del archivo de log: lexico-usergit-algoritmo#-fecha-hora.log
    timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    log_filename = os.path.join(logs_dir, f'lexico-{git_username}-{file_base}-{timestamp}.log')
    
    # Preparar contenido del log
    log_content = f"\n{'='*80}\n"
    log_content += f"ANÁLISIS LÉXICO DEL ARCHIVO: {filename}\n"
    log_content += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    log_content += f"Usuario: {git_username}\n"
    log_content += f"{'='*80}\n\n"
    
    for token in result['tokens']:
        log_content += f"Token: {token['type']:20} | Valor: {token['value']:30} | Línea: {token['line']:4} | Columna: {token['column']:4}\n"
    
    log_content += f"\n{'='*80}\n"
    log_content += f"RESUMEN DEL ANÁLISIS\n"
    log_content += f"{'='*80}\n"
    log_content += f"Total de tokens reconocidos: {len(result['tokens'])}\n"
    log_content += f"Total de errores encontrados: {len(result['errors'])}\n"
    
    if result['errors']:
        log_content += f"\n{'='*80}\n"
        log_content += f"ERRORES ENCONTRADOS\n"
        log_content += f"{'='*80}\n"
        for error in result['errors']:
            log_content += f"Carácter ilegal '{error['char']}' en línea {error['line']}, columna {error['column']}\n"
    
    # Escribir en archivo de log
    try:
        with open(log_filename, 'w', encoding='utf-8') as log_file:
            log_file.write(log_content)
        print(log_content)
        print(f"\n✓ Log guardado en: {log_filename}")
    except Exception as e:
        print(f"Error al guardar el log: {e}")
        print(log_content)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python lexico_go.py <archivo.go>")
        sys.exit(1)
    
    filename = sys.argv[1]
    analyze_file(filename)
