"""
Analizador Sintáctico para el Lenguaje Go
Proyecto: Implementación de un Analizador Sintáctico en Go
Integrantes:
- Jair Palaguachi (JairPalaguachi)
- Javier Gutiérrez (SKEIILATT)
- Leonardo Macías (leodamac)
"""

import ply.yacc as yacc
from lexico_go import tokens, lexer
from datetime import datetime
import sys
import os

# Variables globales para logging
log_errors = []

# Definir precedencia de operadores
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
    ('right', 'ADDRESS', 'POINTER'),
)

# ============================================================================
# REGLAS BÁSICAS DE ESTRUCTURA DEL PROGRAMA
# ============================================================================

def p_programa(p):
    '''programa : package_decl imports declaraciones'''
    print("Programa analizado correctamente")

def p_package_decl(p):
    '''package_decl : PACKAGE ID'''
    pass

# ============================================================================
# IMPORTS - Soporta múltiples formas
# ============================================================================

def p_imports(p):
    '''imports : import_decl imports
               | import_decl
               | empty'''
    pass

def p_import_decl(p):
    '''import_decl : IMPORT STRING_LITERAL
                   | IMPORT LPAREN lista_imports RPAREN
                   | empty'''
    pass

def p_lista_imports(p):
    '''lista_imports : lista_imports STRING_LITERAL
                     | STRING_LITERAL'''
    pass

# ============================================================================
# DECLARACIONES A NIVEL DE PROGRAMA
# ============================================================================

def p_declaraciones(p):
    '''declaraciones : declaraciones declaracion
                     | declaracion'''
    pass

def p_declaracion(p):
    '''declaracion : funcion
                   | declaracion_var_global
                   | bloque_var
                   | bloque_const
                   | declaracion_const
                   | empty'''
    pass

# ============================================================================
# CONTRIBUCIÓN: Leonardo Macías (leodamac)
# Sección: Declaraciones de Variables
# ============================================================================

def p_declaracion_var_global(p):
    '''declaracion_var_global : VAR ID tipo
                              | VAR ID tipo ASSIGN expresion
                              | VAR ID ASSIGN expresion'''
    pass

def p_bloque_var(p):
    '''bloque_var : VAR LPAREN lista_decl_bloque RPAREN'''
    pass

def p_lista_decl_bloque(p):
    '''lista_decl_bloque : lista_decl_bloque decl_var_bloque
                         | decl_var_bloque'''
    pass

def p_decl_var_bloque(p):
    '''decl_var_bloque : ID tipo
                       | ID tipo ASSIGN expresion
                       | ID ASSIGN expresion'''
    pass

def p_declaracion_var(p):
    '''declaracion_var : VAR ID tipo
                       | VAR ID tipo ASSIGN expresion
                       | VAR ID ASSIGN expresion
                       | ID DECLARE_ASSIGN expresion'''
    pass

def p_declaracion_var_multiple(p):
    '''declaracion_var_multiple : VAR lista_ids tipo
                                | VAR lista_ids tipo ASSIGN lista_expresiones
                                | lista_ids DECLARE_ASSIGN lista_expresiones'''
    pass

def p_lista_ids(p):
    '''lista_ids : lista_ids COMMA ID
                 | lista_ids COMMA UNDERSCORE
                 | ID
                 | UNDERSCORE'''
    pass

# ============================================================================
# FIN CONTRIBUCIÓN: Leonardo Macías
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Javier Gutiérrez (SKEIILATT)
# Sección: Asignaciones
# ============================================================================

def p_asignacion(p):
    '''asignacion : ID ASSIGN expresion
                  | ID PLUS_ASSIGN expresion
                  | ID MINUS_ASSIGN expresion
                  | ID TIMES_ASSIGN expresion
                  | ID DIVIDE_ASSIGN expresion
                  | ID LBRACKET expresion RBRACKET ASSIGN expresion
                  | TIMES ID ASSIGN expresion'''
    pass

def p_asignacion_multiple(p):
    '''asignacion_multiple : lista_ids ASSIGN lista_expresiones'''
    pass

# ============================================================================
# FIN CONTRIBUCIÓN: Javier Gutiérrez
# ============================================================================

# ============================================================================
# DECLARACIONES DE CONSTANTES
# ============================================================================

def p_declaracion_const(p):
    '''declaracion_const : CONST ID ASSIGN expresion
                         | CONST ID tipo ASSIGN expresion'''
    pass

def p_bloque_const(p):
    '''bloque_const : CONST LPAREN lista_decl_const RPAREN'''
    pass

def p_lista_decl_const(p):
    '''lista_decl_const : lista_decl_const decl_const_bloque
                        | decl_const_bloque'''
    pass

def p_decl_const_bloque(p):
    '''decl_const_bloque : ID ASSIGN expresion
                         | ID tipo ASSIGN expresion'''
    pass

# ============================================================================
# FUNCIONES
# ============================================================================

def p_funcion(p):
    '''funcion : FUNC ID LPAREN parametros RPAREN tipo_retorno bloque
               | FUNC ID LPAREN parametros RPAREN bloque'''
    pass

def p_parametros(p):
    '''parametros : lista_parametros
                  | empty'''
    pass

def p_lista_parametros(p):
    '''lista_parametros : lista_parametros COMMA parametro
                        | parametro'''
    pass

def p_parametro(p):
    '''parametro : ID tipo
                 | ID COMMA ID tipo
                 | ID ELLIPSIS tipo
                 | TIMES ID
                 | UNDERSCORE tipo'''
    pass

def p_tipo_retorno(p):
    '''tipo_retorno : tipo
                    | LPAREN lista_tipos RPAREN
                    | LPAREN lista_retornos_nombrados RPAREN'''
    pass

def p_lista_retornos_nombrados(p):
    '''lista_retornos_nombrados : lista_retornos_nombrados COMMA ID tipo
                                 | ID tipo'''
    pass

def p_lista_tipos(p):
    '''lista_tipos : lista_tipos COMMA tipo
                   | tipo'''
    pass

# ============================================================================
# TIPOS DE DATOS
# ============================================================================

def p_tipo(p):
    '''tipo : ID
            | LBRACKET INT_LITERAL RBRACKET tipo
            | LBRACKET RBRACKET tipo
            | MAP LBRACKET tipo RBRACKET tipo
            | TIMES tipo'''
    pass

# ============================================================================
# BLOQUES Y SENTENCIAS
# ============================================================================

def p_bloque(p):
    '''bloque : LBRACE sentencias RBRACE
              | LBRACE RBRACE'''
    pass

def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | sentencia'''
    pass

def p_sentencia(p):
    '''sentencia : declaracion_var
                 | bloque_var
                 | bloque_const
                 | declaracion_const
                 | asignacion
                 | asignacion_multiple
                 | declaracion_var_multiple
                 | if_statement
                 | for_statement
                 | switch_statement
                 | return_statement
                 | expresion
                 | impresion
                 | ID INCREMENT
                 | ID DECREMENT
                 | empty'''
    pass

# ============================================================================
# CONTRIBUCIÓN: Leonardo Macías (leodamac)
# Sección: Estructura de Control IF-ELSE
# ============================================================================

def p_if_statement(p):
    '''if_statement : IF condicion bloque
                    | IF condicion bloque ELSE bloque
                    | IF condicion bloque ELSE if_statement'''
    pass

def p_condicion(p):
    '''condicion : expresion
                 | declaracion_var_corta SEMICOLON expresion'''
    pass

def p_declaracion_var_corta(p):
    '''declaracion_var_corta : ID DECLARE_ASSIGN expresion
                             | lista_ids DECLARE_ASSIGN expresion'''
    pass

# ============================================================================
# FIN CONTRIBUCIÓN: Leonardo Macías
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Javier Gutiérrez (SKEIILATT)
# Sección: Estructura de Control FOR
# ============================================================================

def p_for_statement(p):
    '''for_statement : FOR condicion bloque
                     | FOR bloque
                     | FOR inicializacion SEMICOLON condicion SEMICOLON incremento bloque
                     | FOR ID COMMA ID DECLARE_ASSIGN RANGE expresion bloque
                     | FOR ID DECLARE_ASSIGN RANGE expresion bloque
                     | FOR ID COMMA ID ASSIGN RANGE expresion bloque
                     | FOR UNDERSCORE COMMA ID DECLARE_ASSIGN RANGE expresion bloque
                     | FOR ID COMMA UNDERSCORE DECLARE_ASSIGN RANGE expresion bloque
                     | FOR UNDERSCORE COMMA UNDERSCORE DECLARE_ASSIGN RANGE expresion bloque'''
    pass

def p_inicializacion(p):
    '''inicializacion : declaracion_var
                      | asignacion
                      | empty'''
    pass

def p_incremento(p):
    '''incremento : asignacion
                  | ID INCREMENT
                  | ID DECREMENT
                  | empty'''
    pass

# ============================================================================
# FIN CONTRIBUCIÓN: Javier Gutiérrez
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Jair Palaguachi (JairPalaguachi)
# Sección: Estructura de Control SWITCH
# ============================================================================

def p_switch_statement(p):
    '''switch_statement : SWITCH expresion LBRACE casos RBRACE
                        | SWITCH LBRACE casos RBRACE
                        | SWITCH declaracion_var_corta SEMICOLON expresion LBRACE casos RBRACE'''
    pass

def p_casos(p):
    '''casos : casos caso
             | caso'''
    pass

def p_caso(p):
    '''caso : CASE lista_expresiones COLON sentencias
            | DEFAULT COLON sentencias'''
    pass

# ============================================================================
# FIN CONTRIBUCIÓN: Jair Palaguachi
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Leonardo Macías (leodamac)
# Sección: Return Statement
# ============================================================================

def p_return_statement(p):
    '''return_statement : RETURN
                        | RETURN expresion
                        | RETURN lista_expresiones'''
    pass

# ============================================================================
# FIN CONTRIBUCIÓN: Leonardo Macías
# ============================================================================

# ============================================================================
# IMPRESIÓN (Compartido)
# ============================================================================

def p_impresion(p):
    '''impresion : ID DOT ID LPAREN lista_expresiones RPAREN
                 | ID DOT ID LPAREN RPAREN'''
    pass

# ============================================================================
# CONTRIBUCIÓN: Jair Palaguachi (JairPalaguachi)
# Sección: Expresiones Aritméticas y Lógicas
# ============================================================================

def p_expresion_binaria(p):
    '''expresion : expresion PLUS expresion
                 | expresion MINUS expresion
                 | expresion TIMES expresion
                 | expresion DIVIDE expresion
                 | expresion MOD expresion
                 | expresion AND expresion
                 | expresion OR expresion
                 | expresion EQ expresion
                 | expresion NE expresion
                 | expresion LT expresion
                 | expresion LE expresion
                 | expresion GT expresion
                 | expresion GE expresion
                 | expresion BITAND expresion
                 | expresion BITOR expresion
                 | expresion BITXOR expresion
                 | expresion LSHIFT expresion
                 | expresion RSHIFT expresion
                 | expresion AND_NOT expresion'''
    pass

def p_expresion_unaria(p):
    '''expresion : NOT expresion
                 | MINUS expresion %prec UMINUS
                 | PLUS expresion %prec UMINUS
                 | BITXOR expresion
                 | BITNOT expresion
                 | ADDRESS expresion %prec ADDRESS
                 | BITAND expresion %prec ADDRESS
                 | TIMES expresion %prec POINTER'''
    pass
# ============================================================================
# FIN CONTRIBUCIÓN: Jair Palaguachi
# ============================================================================

def p_expresion_agrupada(p):
    '''expresion : LPAREN expresion RPAREN'''
    pass

def p_expresion_primaria(p):
    '''expresion : ID
                 | INT_LITERAL
                 | FLOAT_LITERAL
                 | STRING_LITERAL
                 | RUNE_LITERAL
                 | BOOL_LITERAL
                 | NIL'''
    pass

# ============================================================================
# FUNCIONES BUILT-IN Y LLAMADAS
# ============================================================================

def p_expresion_llamada(p):
    '''expresion : ID LPAREN lista_expresiones RPAREN
                 | ID LPAREN RPAREN
                 | ID DOT ID LPAREN lista_expresiones RPAREN
                 | ID DOT ID LPAREN RPAREN'''
    pass

def p_expresion_make(p):
    '''expresion : MAKE LPAREN tipo RPAREN
                 | MAKE LPAREN tipo COMMA expresion RPAREN
                 | MAKE LPAREN tipo COMMA expresion COMMA expresion RPAREN'''
    pass

def p_expresion_append(p):
    '''expresion : APPEND LPAREN expresion COMMA lista_expresiones RPAREN
                 | APPEND LPAREN expresion COMMA expresion RPAREN'''
    pass

def p_expresion_len(p):
    '''expresion : LEN LPAREN expresion RPAREN'''
    pass

def p_expresion_delete(p):
    '''expresion : DELETE LPAREN expresion COMMA expresion RPAREN'''
    pass

def p_expresion_new(p):
    '''expresion : ID DOT ID LPAREN STRING_LITERAL RPAREN'''
    pass

# ============================================================================
# CONTRIBUCIÓN: Leonardo Macías (leodamac)
# Sección: Arrays - Acceso e Inicialización
# ============================================================================

def p_expresion_array_acceso(p):
    '''expresion : ID LBRACKET expresion RBRACKET'''
    pass

def p_array_literal(p):
    '''expresion : LBRACKET INT_LITERAL RBRACKET tipo LBRACE lista_expresiones RBRACE
                 | LBRACKET INT_LITERAL RBRACKET tipo LBRACE RBRACE
                 | LBRACKET INT_LITERAL RBRACKET LBRACKET INT_LITERAL RBRACKET tipo LBRACE lista_filas_matriz RBRACE'''
    pass

def p_lista_filas_matriz(p):
    '''lista_filas_matriz : lista_filas_matriz COMMA fila_matriz
                          | fila_matriz'''
    pass

def p_fila_matriz(p):
    '''fila_matriz : LBRACE lista_expresiones RBRACE'''
    pass

# ============================================================================
# FIN CONTRIBUCIÓN: Leonardo Macías
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Javier Gutiérrez (SKEIILATT)
# Sección: Slices
# ============================================================================

def p_slice_literal(p):
    '''expresion : LBRACKET RBRACKET tipo LBRACE lista_expresiones RBRACE
                 | LBRACKET RBRACKET tipo LBRACE RBRACE'''
    pass

def p_slice_operacion(p):
    '''expresion : ID LBRACKET expresion COLON expresion RBRACKET
                 | ID LBRACKET COLON expresion RBRACKET
                 | ID LBRACKET expresion COLON RBRACKET
                 | ID LBRACKET COLON RBRACKET'''
    pass

# ============================================================================
# FIN CONTRIBUCIÓN: Javier Gutiérrez
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Jair Palaguachi (JairPalaguachi)
# Sección: Maps
# ============================================================================

def p_map_literal(p):
    '''expresion : MAP LBRACKET tipo RBRACKET tipo LBRACE pares_mapa RBRACE
                 | MAP LBRACKET tipo RBRACKET tipo LBRACE pares_mapa COMMA RBRACE
                 | MAP LBRACKET tipo RBRACKET tipo LBRACE RBRACE'''
    pass

def p_pares_mapa(p):
    '''pares_mapa : pares_mapa COMMA par_mapa
                  | par_mapa'''
    pass

def p_par_mapa(p):
    '''par_mapa : expresion COLON expresion'''
    pass

# ============================================================================
# FIN CONTRIBUCIÓN: Jair Palaguachi
# ============================================================================

def p_lista_expresiones(p):
    '''lista_expresiones : lista_expresiones COMMA expresion
                         | expresion'''
    pass

# Regla para producciones vacías
def p_empty(p):
    '''empty :'''
    pass

# ============================================================================
# MANEJO DE ERRORES SINTÁCTICOS
# ============================================================================

def p_error(p):
    global log_errors
    if p:
        error_msg = f"Error de sintaxis en '{p.value}' (Token: {p.type}, Línea: {p.lineno})"
        print(error_msg)
        log_errors.append(error_msg)
        # Intentar recuperarse
        parser.errok()
    else:
        error_msg = "Error de sintaxis: fin de archivo inesperado"
        print(error_msg)
        log_errors.append(error_msg)

# ============================================================================
# CONSTRUCCIÓN DEL PARSER
# ============================================================================

parser = yacc.yacc()

# ============================================================================
# FUNCIONES DE ANÁLISIS Y LOGGING
# ============================================================================

def analyze_file(filename):
    """
    Analiza sintácticamente un archivo de código Go.
    """
    global log_errors
    log_errors = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{filename}' no fue encontrado.")
        return
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return
    
    print(f"\n{'='*80}")
    print(f"ANÁLISIS SINTÁCTICO DEL ARCHIVO: {filename}")
    print(f"{'='*80}\n")
    
    # Realizar el análisis sintáctico
    result = parser.parse(data, lexer=lexer)
    
    # Resumen
    print(f"\n{'='*80}")
    print(f"RESUMEN DEL ANÁLISIS SINTÁCTICO")
    print(f"{'='*80}")
    print(f"Total de errores encontrados: {len(log_errors)}")
    
    if log_errors:
        print(f"\n{'='*80}")
        print(f"ERRORES SINTÁCTICOS")
        print(f"{'='*80}")
        for error in log_errors:
            print(error)
    
    # Generar archivo de log
    generate_log(filename)

def get_git_username():
    """
    Obtiene el nombre de usuario de Git configurado localmente.
    """
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            username = result.stdout.strip()
            username = username.replace(' ', '')
            return username
        else:
            return 'usuario'
    except:
        return 'usuario'

def generate_log(source_filename):
    """
    Genera un archivo de log con los errores sintácticos encontrados.
    """
    # Crear carpeta de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Obtener información del usuario de git
    git_user = get_git_username()
    
    # Generar nombre del archivo de log
    now = datetime.now()
    base = os.path.splitext(os.path.basename(source_filename))[0]
    timestamp = now.strftime('%d%m%Y-%Hh%M')
    log_filename = f"logs/sintactico-{git_user}-{base}-{timestamp}.txt"
    
    # Escribir el log
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        log_file.write("="*80 + "\n")
        log_file.write(f"ANÁLISIS SINTÁCTICO - LENGUAJE GO\n")
        log_file.write("="*80 + "\n")
        log_file.write(f"Archivo analizado: {source_filename}\n")
        log_file.write(f"Fecha y hora: {now.strftime('%d/%m/%Y %H:%M:%S')}\n")
        log_file.write(f"Usuario: {git_user}\n")
        log_file.write("="*80 + "\n\n")
        
        log_file.write(f"ERRORES SINTÁCTICOS ENCONTRADOS ({len(log_errors)})\n")
        log_file.write("-"*80 + "\n")
        if log_errors:
            for error in log_errors:
                log_file.write(error + "\n")
        else:
            log_file.write("No se encontraron errores sintácticos.\n")
        
        log_file.write("\n" + "="*80 + "\n")
        log_file.write("FIN DEL ANÁLISIS SINTÁCTICO\n")
        log_file.write("="*80 + "\n")
    
    print(f"\nLog generado exitosamente: {log_filename}")

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python sintactico_go.py <archivo.go>")
        print("Ejemplo: python sintactico_go.py algoritmo1.go")
        sys.exit(1)
    
    filename = sys.argv[1]
    analyze_file(filename)