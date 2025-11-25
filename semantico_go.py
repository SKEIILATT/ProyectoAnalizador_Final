"""
Analizador Semántico para el Lenguaje Go
Proyecto: Implementación de un Analizador Semántico en Go
Integrantes:
- Jair Palaguachi (JairPalaguachi)
- Javier Gutiérrez (SKEIILATT)
"""

import ply.yacc as yacc
from lexico_go import tokens, lexer
from datetime import datetime
import sys
import os

# ============================================================================
# TABLA DE SÍMBOLOS Y ESTRUCTURAS DE DATOS
# ============================================================================

class Symbol:
    """Representa un símbolo en la tabla de símbolos"""
    def __init__(self, name, symbol_type, value=None, scope='global', line=0, is_const=False, return_type=None):
        self.name = name
        self.symbol_type = symbol_type
        self.value = value
        self.scope = scope
        self.line = line
        self.is_const = is_const
        self.return_type = return_type  # Para funciones

class SymbolTable:
    """Tabla de símbolos con soporte para ámbitos anidados"""
    def __init__(self):
        self.scopes = [{}]  # Stack de ámbitos
        self.current_scope_level = 0
        
    def enter_scope(self):
        """Entra a un nuevo ámbito"""
        self.scopes.append({})
        self.current_scope_level += 1
    
    def exit_scope(self):
        """Sale del ámbito actual"""
        if self.current_scope_level > 0:
            self.scopes.pop()
            self.current_scope_level -= 1
    
    def insert(self, symbol):
        """Inserta un símbolo en el ámbito actual"""
        self.scopes[self.current_scope_level][symbol.name] = symbol
    
    def lookup(self, name):
        """Busca un símbolo en todos los ámbitos (de interno a externo)"""
        for i in range(self.current_scope_level, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        return None
    
    def lookup_current_scope(self, name):
        """Busca un símbolo solo en el ámbito actual"""
        return self.scopes[self.current_scope_level].get(name)

# Variables globales
symbol_table = SymbolTable()
semantic_errors = []
current_function = None
function_stack = []  # Pila de funciones para manejar funciones anidadas
inside_loop = 0  # Contador para detectar bucles anidados

# Tipos compatibles para operaciones
NUMERIC_TYPES = {'int', 'int8', 'int16', 'int32', 'int64', 
                 'uint', 'uint8', 'uint16', 'uint32', 'uint64',
                 'float32', 'float64'}

INTEGER_TYPES = {'int', 'int8', 'int16', 'int32', 'int64',
                 'uint', 'uint8', 'uint16', 'uint32', 'uint64'}

FLOAT_TYPES = {'float32', 'float64'}

# Conversiones permitidas (tipo_origen -> tipos_destino_permitidos)
ALLOWED_CONVERSIONS = {
    'int': NUMERIC_TYPES,
    'int8': NUMERIC_TYPES,
    'int16': NUMERIC_TYPES,
    'int32': NUMERIC_TYPES,
    'int64': NUMERIC_TYPES,
    'uint': NUMERIC_TYPES,
    'uint8': NUMERIC_TYPES,
    'uint16': NUMERIC_TYPES,
    'uint32': NUMERIC_TYPES,
    'uint64': NUMERIC_TYPES,
    'float32': NUMERIC_TYPES,
    'float64': NUMERIC_TYPES,
    'string': {'string', 'rune', 'byte'},
    'bool': {'bool'},
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def add_error(message, line=0):
    """Agrega un error semántico"""
    error_msg = f"Error semántico en línea {line}: {message}"
    semantic_errors.append(error_msg)
    print(error_msg)

def get_type_from_literal(value):
    """Determina el tipo de un literal"""
    if isinstance(value, bool):
        return 'bool'
    elif isinstance(value, int):
        return 'int'
    elif isinstance(value, float):
        return 'float64'
    elif isinstance(value, str):
        return 'string'
    return 'unknown'

# ============================================================================
# PRECEDENCIA DE OPERADORES
# ============================================================================

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
# REGLAS GRAMATICALES CON ANÁLISIS SEMÁNTICO
# ============================================================================

def p_programa(p):
    '''programa : package_decl imports declaraciones'''
    print("+ Programa analizado correctamente")
    print(f"+ Total de simbolos declarados: {sum(len(scope) for scope in symbol_table.scopes)}")

def p_package_decl(p):
    '''package_decl : PACKAGE ID'''
    pass

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

def p_declaraciones(p):
    '''declaraciones : declaraciones declaracion
                     | declaracion'''
    pass

def p_declaracion(p):
    '''declaracion : funcion
                   | declaracion_var_global
                   | bloque_var
                   | declaracion_const
                   | empty'''
    pass

# ============================================================================
# CONTRIBUCIÓN: Jair Palaguachi (JairPalaguachi)
# IDENTIFICADORES - REGLA 1: Validación de declaración previa
# Toda variable, función, constante o tipo debe estar declarada antes de ser utilizada
# ============================================================================

def p_declaracion_var_global(p):
    '''declaracion_var_global : VAR ID tipo
                              | VAR ID tipo ASSIGN expresion
                              | VAR ID ASSIGN expresion'''
    var_name = p[2]
    line = p.lineno(2)
    
    # Verificar si ya existe en el ámbito actual
    if symbol_table.lookup_current_scope(var_name):
        add_error(f"Variable '{var_name}' ya declarada en este ámbito", line)
    else:
        # Determinar el tipo
        if len(p) == 4:  # VAR ID tipo
            var_type = p[3]
            symbol_table.insert(Symbol(var_name, var_type, None, 'global', line))
        elif len(p) == 6:  # VAR ID tipo ASSIGN expresion
            var_type = p[3]
            expr_type = p[5].get('type') if isinstance(p[5], dict) else 'unknown'
            
            # JAIR - REGLA 3: Verificación de tipos en asignación
            if expr_type != 'unknown' and var_type != expr_type:
                if not (var_type in NUMERIC_TYPES and expr_type in NUMERIC_TYPES):
                    add_error(f"Incompatibilidad de tipos: no se puede asignar '{expr_type}' a '{var_type}'", line)
            
            symbol_table.insert(Symbol(var_name, var_type, None, 'global', line))
        else:  # VAR ID ASSIGN expresion
            expr_type = p[4].get('type') if isinstance(p[4], dict) else 'unknown'
            symbol_table.insert(Symbol(var_name, expr_type, None, 'global', line))

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
    var_name = p[1]
    line = p.lineno(1)
    
    if symbol_table.lookup_current_scope(var_name):
        add_error(f"Variable '{var_name}' ya declarada en este ámbito", line)
    else:
        if len(p) == 3:  # ID tipo
            var_type = p[2]
            symbol_table.insert(Symbol(var_name, var_type, None, 'local', line))
        elif len(p) == 5:  # ID tipo ASSIGN expresion
            var_type = p[2]
            symbol_table.insert(Symbol(var_name, var_type, None, 'local', line))
        else:  # ID ASSIGN expresion
            expr_type = p[3].get('type') if isinstance(p[3], dict) else 'unknown'
            symbol_table.insert(Symbol(var_name, expr_type, None, 'local', line))

def p_declaracion_var(p):
    '''declaracion_var : VAR ID tipo
                       | VAR ID tipo ASSIGN expresion
                       | VAR ID ASSIGN expresion
                       | ID DECLARE_ASSIGN expresion'''
    var_name = p[2] if p[1] == 'var' else p[1]
    line = p.lineno(2) if p[1] == 'var' else p.lineno(1)
    
    if symbol_table.lookup_current_scope(var_name):
        add_error(f"Variable '{var_name}' ya declarada en este ámbito", line)
    else:
        if len(p) == 4 and p[1] == 'var':  # VAR ID tipo
            var_type = p[3]
            symbol_table.insert(Symbol(var_name, var_type, None, 'local', line))
        elif len(p) == 4:  # ID DECLARE_ASSIGN expresion
            expr_info = p[3]
            expr_type = expr_info.get('type') if isinstance(expr_info, dict) else 'unknown'
            
            # DETERMINAR TIPO CORRECTAMENTE PARA LITERALES
            if expr_type == 'unknown' and hasattr(p.slice[3], 'type'):
                token_type = p.slice[3].type
                if token_type == 'STRING_LITERAL':
                    expr_type = 'string'
                elif token_type == 'INT_LITERAL':
                    expr_type = 'int'
                elif token_type == 'FLOAT_LITERAL':
                    expr_type = 'float64'
                elif token_type == 'BOOL_LITERAL':
                    expr_type = 'bool'
                    
            symbol_table.insert(Symbol(var_name, expr_type, None, 'local', line))
        elif len(p) == 6:  # VAR ID tipo ASSIGN expresion
            var_type = p[3]
            symbol_table.insert(Symbol(var_name, var_type, None, 'local', line))
        else:  # VAR ID ASSIGN expresion
            expr_info = p[4]
            expr_type = expr_info.get('type') if isinstance(expr_info, dict) else 'unknown'
            
            # DETERMINAR TIPO CORRECTAMENTE PARA LITERALES
            if expr_type == 'unknown' and hasattr(p.slice[4], 'type'):
                token_type = p.slice[4].type
                if token_type == 'STRING_LITERAL':
                    expr_type = 'string'
                elif token_type == 'INT_LITERAL':
                    expr_type = 'int'
                elif token_type == 'FLOAT_LITERAL':
                    expr_type = 'float64'
                elif token_type == 'BOOL_LITERAL':
                    expr_type = 'bool'
                    
            symbol_table.insert(Symbol(var_name, expr_type, None, 'local', line))

# ============================================================================
# FIN CONTRIBUCIÓN: Jair Palaguachi - REGLA 1
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Jair Palaguachi (JairPalaguachi)
# IDENTIFICADORES - REGLA 2: Validación de alcance de variables
# Variables declaradas dentro de un bloque solo son accesibles dentro de ese bloque
# ============================================================================

def p_funcion(p):
    '''funcion : funcion_header bloque'''
    global current_function
    # Al terminar la función, salir del scope y limpiar el contexto
    symbol_table.exit_scope()
    current_function = None

def p_funcion_header(p):
    '''funcion_header : FUNC ID LPAREN parametros RPAREN tipo_retorno
                      | FUNC ID LPAREN parametros RPAREN'''
    global current_function
    func_name = p[2]
    line = p.lineno(2)

    # LEONARDO - REGLA 1: Guardar tipo de retorno de la función
    if len(p) == 7:  # Con tipo de retorno
        return_type = p[6]
    else:  # Sin tipo de retorno explícito (void)
        return_type = 'void'

    # Insertar función con su tipo de retorno
    if not symbol_table.lookup_current_scope(func_name):
        symbol_table.insert(Symbol(func_name, 'func', None, 'global', line, return_type=return_type))

    # Establecer función actual y entrar a un nuevo scope ANTES de procesar el bloque
    current_function = {
        'name': func_name,
        'return_type': return_type,
        'line': line
    }
    symbol_table.enter_scope()

def p_bloque(p):
    '''bloque : LBRACE sentencias RBRACE
              | LBRACE RBRACE'''
    # El manejo del scope se hace en p_funcion
    pass

# ============================================================================
# FIN CONTRIBUCIÓN: Jair Palaguachi - REGLA 2
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Jair Palaguachi (JairPalaguachi)
# ASIGNACIÓN DE TIPO - REGLA 3: Verificación de tipos en asignación
# El tipo del valor asignado debe coincidir con el tipo de la variable
# Go no permite conversiones implícitas entre tipos numéricos
# ============================================================================

def p_asignacion(p):
    '''asignacion : ID ASSIGN expresion
                  | ID PLUS_ASSIGN expresion
                  | ID MINUS_ASSIGN expresion
                  | ID TIMES_ASSIGN expresion
                  | ID DIVIDE_ASSIGN expresion
                  | ID LBRACKET expresion RBRACKET ASSIGN expresion
                  | TIMES ID ASSIGN expresion'''

    if len(p) == 4 and p[1] == '*':  # TIMES ID ASSIGN expresion (desreferenciación de puntero)
        var_name = p[2]
        line = p.lineno(2)

        # Verificar que la variable (puntero) esté declarada
        symbol = symbol_table.lookup(var_name)
        if not symbol:
            add_error(f"Variable '{var_name}' utilizada sin declaración previa", line)
        else:
            # Verificar que sea un puntero
            if not symbol.symbol_type.startswith('*'):
                add_error(f"No se puede desreferenciar '{var_name}' que no es un puntero", line)

    elif len(p) == 4 and p[2] == '=':  # ID ASSIGN expresion
        var_name = p[1]
        line = p.lineno(1)

        # JAIR - REGLA 1: Verificar que la variable esté declarada
        symbol = symbol_table.lookup(var_name)
        if not symbol:
            add_error(f"Variable '{var_name}' utilizada sin declaración previa", line)
        else:
            # JAIR - REGLA 3: Verificar tipos
            expr_type = p[3].get('type') if isinstance(p[3], dict) else 'unknown'
            if expr_type != 'unknown' and symbol.symbol_type != expr_type:
                if not (symbol.symbol_type in NUMERIC_TYPES and expr_type in NUMERIC_TYPES):
                    add_error(f"Incompatibilidad de tipos: no se puede asignar '{expr_type}' a '{symbol.symbol_type}'", line)

            # JAIR - REGLA 4: Verificar si es constante
            if symbol.is_const:
                add_error(f"No se puede asignar valor a constante '{var_name}'", line)

    elif len(p) == 4:  # Operadores compuestos
        var_name = p[1]
        line = p.lineno(1)

        # JAIR - REGLA 1: Verificar declaración
        symbol = symbol_table.lookup(var_name)
        if not symbol:
            add_error(f"Variable '{var_name}' utilizada sin declaración previa", line)
        else:
            # JAIR - REGLA 4: Verificar constante
            if symbol.is_const:
                add_error(f"No se puede modificar constante '{var_name}'", line)

# ============================================================================
# FIN CONTRIBUCIÓN: Jair Palaguachi - REGLA 3
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Jair Palaguachi (JairPalaguachi)
# ASIGNACIÓN DE TIPO - REGLA 4: Inmutabilidad de constantes
# Las constantes no pueden ser modificadas después de su declaración
# ============================================================================

def p_declaracion_const(p):
    '''declaracion_const : CONST ID ASSIGN expresion
                         | CONST ID tipo ASSIGN expresion'''
    const_name = p[2]
    line = p.lineno(2)
    
    if symbol_table.lookup_current_scope(const_name):
        add_error(f"Constante '{const_name}' ya declarada en este ámbito", line)
    else:
        if len(p) == 5:  # CONST ID ASSIGN expresion
            expr_info = p[4]
            expr_type = expr_info.get('type') if isinstance(expr_info, dict) else 'unknown'
            
            # DETERMINAR TIPO CORRECTAMENTE PARA LITERALES
            if expr_type == 'unknown' and hasattr(p.slice[4], 'type'):
                token_type = p.slice[4].type
                if token_type == 'STRING_LITERAL':
                    expr_type = 'string'
                elif token_type == 'INT_LITERAL':
                    expr_type = 'int'
                elif token_type == 'FLOAT_LITERAL':
                    expr_type = 'float64'
                elif token_type == 'BOOL_LITERAL':
                    expr_type = 'bool'
                    
            symbol_table.insert(Symbol(const_name, expr_type, None, 'global', line, is_const=True))
        else:  # CONST ID tipo ASSIGN expresion
            const_type = p[3]
            symbol_table.insert(Symbol(const_name, const_type, None, 'global', line, is_const=True))

# ============================================================================
# FIN CONTRIBUCIÓN: Jair Palaguachi - REGLA 4
# ============================================================================

# DECLARACIONES MÚLTIPLES Y ASIGNACIONES MÚLTIPLES
def p_declaracion_var_multiple(p):
    '''declaracion_var_multiple : VAR lista_ids tipo
                                | VAR lista_ids tipo ASSIGN lista_expresiones
                                | lista_ids DECLARE_ASSIGN lista_expresiones'''
    
    if p[1] == 'var':  # Declaración con VAR
        var_names = p[2]
        line = p.lineno(2)
        
        if len(p) == 4:  # VAR lista_ids tipo
            var_type = p[3]
            for var_name in var_names:
                if symbol_table.lookup_current_scope(var_name):
                    add_error(f"Variable '{var_name}' ya declarada en este ámbito", line)
                else:
                    symbol_table.insert(Symbol(var_name, var_type, None, 'local', line))
        
        elif len(p) == 6:  # VAR lista_ids tipo ASSIGN lista_expresiones
            var_type = p[3]
            for var_name in var_names:
                if symbol_table.lookup_current_scope(var_name):
                    add_error(f"Variable '{var_name}' ya declarada en este ámbito", line)
                else:
                    symbol_table.insert(Symbol(var_name, var_type, None, 'local', line))
    
    else:  # Declaración corta: lista_ids DECLARE_ASSIGN lista_expresiones
        var_names = p[1]
        line = p.lineno(1)
        for var_name in var_names:
            if symbol_table.lookup_current_scope(var_name):
                add_error(f"Variable '{var_name}' ya declarada en este ámbito", line)
            else:
                symbol_table.insert(Symbol(var_name, 'unknown', None, 'local', line))

def p_lista_ids(p):
    '''lista_ids : lista_ids COMMA ID
                 | lista_ids COMMA UNDERSCORE
                 | ID
                 | UNDERSCORE'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] != '_' else []
    else:
        p[0] = p[1] + ([p[3]] if p[3] != '_' else [])

def p_asignacion_multiple(p):
    '''asignacion_multiple : lista_ids ASSIGN lista_expresiones'''
    # Para asignaciones múltiples, verificar que las variables estén declaradas
    var_names = p[1]
    line = p.lineno(1)
    
    for var_name in var_names:
        if var_name != '_':  # Ignorar blank identifier
            symbol = symbol_table.lookup(var_name)
            if not symbol:
                add_error(f"Variable '{var_name}' utilizada sin declaración previa", line)

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
    const_name = p[1]
    line = p.lineno(1)
    
    if symbol_table.lookup_current_scope(const_name):
        add_error(f"Constante '{const_name}' ya declarada en este ámbito", line)
    else:
        if len(p) == 4:  # ID ASSIGN expresion
            expr_type = p[3].get('type') if isinstance(p[3], dict) else 'unknown'
            symbol_table.insert(Symbol(const_name, expr_type, None, 'local', line, is_const=True))
        else:  # ID tipo ASSIGN expresion
            const_type = p[2]
            symbol_table.insert(Symbol(const_name, const_type, None, 'local', line, is_const=True))



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
    if len(p) == 3 and p[1] != '_' and p[2] != '...':  # ID tipo
        param_name = p[1]
        param_type = p[2]
        line = p.lineno(1)
        # Insertar parámetro en el ámbito actual (de la función)
        symbol_table.insert(Symbol(param_name, param_type, None, 'local', line))
    elif len(p) == 4 and p[2] == '...':  # ID ELLIPSIS tipo (parámetro variádico)
        param_name = p[1]
        param_type = f'[]{p[3]}'  # Los parámetros variádicos son slices
        line = p.lineno(1)
        # Insertar parámetro variádico en el ámbito actual
        symbol_table.insert(Symbol(param_name, param_type, None, 'local', line))

def p_tipo_retorno(p):
    '''tipo_retorno : tipo
                    | LPAREN lista_tipos RPAREN
                    | LPAREN lista_retornos_nombrados RPAREN'''
    if len(p) == 2:
        p[0] = p[1]  # Tipo simple
    elif len(p) == 4:  # LPAREN lista_tipos RPAREN
        p[0] = 'multiple'  # Múltiples retornos
    else:  # LPAREN lista_retornos_nombrados RPAREN
        p[0] = 'multiple'  # Múltiples retornos nombrados

# ============================================================================
# CONTRIBUCIÓN: Jair Palaguachi (JairPalaguachi)
# RETORNO DE FUNCIONES - REGLA 1: El valor de retorno debe coincidir con el tipo declarado
# ============================================================================

def p_return_statement(p):
    '''return_statement : RETURN
                        | RETURN expresion
                        | RETURN lista_expresiones'''
    global current_function
    line = p.lineno(1)
    
    if not current_function:
        add_error(f"Return fuera de una función", line)
        return
    
    # EXCEPCIÓN: FUNCIÓN main NO NECESITA RETORNO EN GO
    if current_function['name'] == 'main':
        return
    
    expected_type = current_function.get('return_type', 'void')
    
    if len(p) == 2:  # RETURN sin valor
        # En Go, los retornos nombrados permiten return vacío
        if expected_type != 'void' and expected_type != 'multiple':
            add_error(f"Función '{current_function['name']}' debe retornar un valor de tipo '{expected_type}'", line)
    
    elif len(p) == 3 and p.slice[2].type != 'lista_expresiones':  # RETURN expresion
        return_type = p[2].get('type') if isinstance(p[2], dict) else 'unknown'
        
        if expected_type == 'void':
            add_error(f"Función '{current_function['name']}' no debe retornar ningún valor", line)
        elif return_type != 'unknown' and return_type != expected_type:
            if not (return_type in NUMERIC_TYPES and expected_type in NUMERIC_TYPES):
                add_error(f"Tipo de retorno incorrecto en función '{current_function['name']}'. Esperado: '{expected_type}', Encontrado: '{return_type}'", line)
    
    else:  # RETURN lista_expresiones (múltiples retornos)
        # Para múltiples retornos, la función debe esperar múltiples retornos
        if expected_type != 'multiple':
            add_error(f"Función '{current_function['name']}' retorna un solo valor, no múltiples", line)
        else:
            pass

# ============================================================================
# FIN CONTRIBUCIÓN: Jair Palaguachi (JairPalaguachi) - REGLAS 1 y 2
# ============================================================================

# MÚLTIPLES RETORNOS NOMBRADOS

def p_lista_retornos_nombrados(p):
    '''lista_retornos_nombrados : lista_retornos_nombrados COMMA ID tipo
                                | ID tipo'''
    # Insertar variables de retorno nombradas en el ámbito de la función
    if len(p) == 3:  # ID tipo
        ret_name = p[1]
        ret_type = p[2]
        line = p.lineno(1)
        symbol_table.insert(Symbol(ret_name, ret_type, None, 'local', line))
    else:  # lista_retornos_nombrados COMMA ID tipo
        ret_name = p[3]
        ret_type = p[4]
        line = p.lineno(3)
        symbol_table.insert(Symbol(ret_name, ret_type, None, 'local', line))

def p_lista_tipos(p):
    '''lista_tipos : lista_tipos COMMA tipo
                   | tipo'''
    pass

def p_tipo(p):
    '''tipo : ID
            | LBRACKET INT_LITERAL RBRACKET tipo
            | LBRACKET RBRACKET tipo
            | MAP LBRACKET tipo RBRACKET tipo
            | TIMES tipo'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4 and p[1] == '[' and p[2] == ']':  # slice
        p[0] = f'[]{p[3]}'
    elif len(p) == 5 and p[1] == '[':  # array
        p[0] = f'[{p[2]}]{p[4]}'
    elif len(p) == 6 and p[1] == 'map':  # map
        p[0] = f'map[{p[3]}]{p[5]}'
    else:
        p[0] = 'composite'

def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | sentencia'''
    pass

# ===============================================================a=============
# CONTRIBUCIÓN: Javier Gutiérrez (SKEIILATT)
# ESTRUCTURAS DE CONTROL - REGLA 3: Validación de condiciones booleanas
# Las condiciones en if, for y switch deben ser expresiones booleanas
# ============================================================================

def p_if_statement(p):
    '''if_statement : IF condicion bloque
                    | IF condicion bloque ELSE bloque
                    | IF condicion bloque ELSE if_statement'''
    pass

def p_condicion(p):
    '''condicion : expresion
                 | declaracion_var_corta SEMICOLON expresion'''
    
    if len(p) == 2:  # Solo expresion
        expr_type = p[1].get('type') if isinstance(p[1], dict) else 'unknown'
        if expr_type != 'unknown' and expr_type != 'bool':
            add_error(f"La condición debe ser de tipo 'bool', se encontró '{expr_type}'", p.lineno(1))
        p[0] = p[1]
    else:  # declaracion_var_corta ; expresion
        # La declaración corta ya insertó la variable en la tabla de símbolos
        expr_type = p[3].get('type') if isinstance(p[3], dict) else 'unknown'
        if expr_type != 'unknown' and expr_type != 'bool':
            add_error(f"La condición debe ser de tipo 'bool', se encontró '{expr_type}'", p.lineno(3))
        p[0] = p[3]

def p_declaracion_var_corta(p):
    '''declaracion_var_corta : ID DECLARE_ASSIGN expresion
                             | lista_ids DECLARE_ASSIGN expresion'''
    # Insertar variables declaradas en el ámbito actual
    if len(p) == 4 and isinstance(p[1], str):  # ID DECLARE_ASSIGN expresion
        var_name = p[1]
        line = p.lineno(1)
        expr_info = p[3]
        expr_type = expr_info.get('type') if isinstance(expr_info, dict) else 'unknown'

        # No verificar si ya existe, ya que esto es una declaración corta válida
        symbol_table.insert(Symbol(var_name, expr_type, None, 'local', line))
    elif len(p) == 4:  # lista_ids DECLARE_ASSIGN expresion
        var_names = p[1]
        line = p.lineno(1)
        for var_name in var_names:
            if var_name != '_':
                symbol_table.insert(Symbol(var_name, 'unknown', None, 'local', line))

def p_for_statement(p):
    '''for_statement : FOR condicion bloque
                     | FOR bloque
                     | FOR inicializacion SEMICOLON condicion SEMICOLON incremento bloque
                     | for_range_header bloque
                     | FOR ID COMMA ID ASSIGN RANGE expresion bloque'''
    global inside_loop
    inside_loop -= 1

def p_for_range_header(p):
    '''for_range_header : FOR ID COMMA ID DECLARE_ASSIGN RANGE expresion
                        | FOR ID DECLARE_ASSIGN RANGE expresion
                        | FOR UNDERSCORE COMMA ID DECLARE_ASSIGN RANGE expresion
                        | FOR ID COMMA UNDERSCORE DECLARE_ASSIGN RANGE expresion
                        | FOR UNDERSCORE COMMA UNDERSCORE DECLARE_ASSIGN RANGE expresion'''
    global inside_loop
    inside_loop += 1

    # FOR ID DECLARE_ASSIGN RANGE expresion (len=6)
    if len(p) == 6:
        var_name = p[2]
        if var_name != '_':
            symbol_table.insert(Symbol(var_name, 'int', None, 'local', p.lineno(2)))

    # FOR ID COMMA ID DECLARE_ASSIGN RANGE expresion (len=8)
    elif len(p) == 8:
        var1_name = p[2]
        var2_name = p[4]

        if var1_name != '_':
            symbol_table.insert(Symbol(var1_name, 'int', None, 'local', p.lineno(2)))
        if var2_name != '_':
            symbol_table.insert(Symbol(var2_name, 'int', None, 'local', p.lineno(4)))

# ============================================================================
# FIN CONTRIBUCIÓN: Javier Gutiérrez (SKEIILATT)- REGLA 3
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Javier Gutiérrez (SKEIILATT)
# ESTRUCTURAS DE CONTROL - REGLA 4: Uso correcto de break y continue
# Break y continue solo pueden usarse dentro de bucles
# ============================================================================

def p_sentencia(p):
    '''sentencia : declaracion_var
                 | bloque_var
                 | declaracion_const
                 | asignacion
                 | asignacion_multiple
                 | declaracion_var_multiple
                 | if_statement
                 | for_statement
                 | switch_statement
                 | return_statement
                 | expresion
                 | ID INCREMENT
                 | ID DECREMENT
                 | BREAK
                 | CONTINUE
                 | empty'''
    
    # Validar uso de variables en incremento/decremento
    if len(p) == 3 and p[2] in ('++', '--'):
        var_name = p[1]
        line = p.lineno(1)
        symbol = symbol_table.lookup(var_name)
        if not symbol:
            add_error(f"Variable '{var_name}' utilizada sin declaración previa", line)
    
    # LEONARDO - REGLA 4: Verificar break y continue
    if len(p) == 2 and p[1] in ('break', 'continue'):
        if inside_loop == 0:
            add_error(f"'{p[1]}' solo puede usarse dentro de un bucle (for/switch)", p.lineno(1))
# ============================================================================
# FIN CONTRIBUCIÓN: Javier Gutiérrez (SKEIILATT) - REGLA 4
# ============================================================================



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

def p_switch_statement(p):
    '''switch_statement : SWITCH expresion LBRACE casos RBRACE
                        | SWITCH LBRACE casos RBRACE
                        | SWITCH declaracion_var_corta SEMICOLON expresion LBRACE casos RBRACE'''
    global inside_loop
    
    # Si hay declaración var corta, ya se insertó en la tabla de símbolos
    inside_loop += 1
    # Procesar switch (permite break)
    inside_loop -= 1

def p_casos(p):
    '''casos : casos caso
             | caso'''
    pass

def p_caso(p):
    '''caso : CASE lista_expresiones COLON sentencias
            | DEFAULT COLON sentencias'''
    pass

def p_impresion(p):
    '''impresion : ID DOT ID LPAREN lista_expresiones RPAREN
                 | ID DOT ID LPAREN RPAREN'''
    pass

# ============================================================================
# CONTRIBUCIÓN: Javier Gutiérrez (SKEIILATT)
# OPERACIONES PERMITIDAS - REGLA 1: Homogeneidad de tipos en operaciones aritméticas
# Los operandos de operaciones aritméticas deben ser del mismo tipo
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
    
    left_type = p[1].get('type') if isinstance(p[1], dict) else 'unknown'
    right_type = p[3].get('type') if isinstance(p[3], dict) else 'unknown'
    operator = p[2]
    
    # JAVIER - REGLA 1: Homogeneidad de tipos en operaciones aritméticas
    if operator in ['+', '-', '*', '/', '%']:
        # Para +, verificar concatenación (REGLA 2 de Javier)
        if operator == '+' and (left_type == 'string' or right_type == 'string'):
            # JAVIER - REGLA 2: Concatenación solo con strings
            if left_type != 'string' or right_type != 'string':
                add_error(f"No se puede concatenar '{left_type}' con '{right_type}'. Ambos deben ser string", p.lineno(2))
            p[0] = {'type': 'string'}
        else:
            # Operaciones aritméticas
            # Ignorar si uno de los tipos es un puntero (podría ser desreferenciación en asignación)
            is_pointer_context = (left_type.startswith('*') if isinstance(left_type, str) else False) or \
                                 (right_type.startswith('*') if isinstance(right_type, str) else False)

            if not is_pointer_context and left_type != 'unknown' and right_type != 'unknown':
                if left_type not in NUMERIC_TYPES or right_type not in NUMERIC_TYPES:
                    add_error(f"Operación aritmética '{operator}' requiere tipos numéricos. Se encontró '{left_type}' y '{right_type}'", p.lineno(2))
                elif left_type != right_type:
                    add_error(f"Los operandos de '{operator}' deben ser del mismo tipo. Se encontró '{left_type}' y '{right_type}'", p.lineno(2))
            p[0] = {'type': left_type if left_type in NUMERIC_TYPES else 'unknown'}
    
    elif operator in ['&&', '||']:
        p[0] = {'type': 'bool'}
    elif operator in ['==', '!=', '<', '<=', '>', '>=']:
        p[0] = {'type': 'bool'}
    else:
        p[0] = {'type': left_type}

# ============================================================================
# FIN CONTRIBUCIÓN: Javier Gutiérrez - REGLA 1 y 2
# ============================================================================

# ============================================================================
# CONTRIBUCIÓN: Javier Gutiérrez (SKEIILATT)
# CONVERSIÓN - REGLA 3: Los tipos deben ser convertibles
# Solo se permiten conversiones entre tipos compatibles
# ============================================================================

def p_expresion_conversion(p):
    '''expresion : tipo LPAREN expresion RPAREN'''
    target_type = p[1]
    expr_type = p[3].get('type') if isinstance(p[3], dict) else 'unknown'
    line = p.lineno(1)
    
    # JAVIER - REGLA 3: Verificar que la conversión es permitida
    if expr_type != 'unknown':
        if expr_type not in ALLOWED_CONVERSIONS:
            add_error(f"El tipo '{expr_type}' no puede ser convertido", line)
        elif target_type not in ALLOWED_CONVERSIONS.get(expr_type, set()):
            add_error(f"No se puede convertir de '{expr_type}' a '{target_type}'", line)
        else:
            # JAVIER - REGLA 4: Advertir sobre truncamiento en conversiones
            if expr_type in FLOAT_TYPES and target_type in INTEGER_TYPES:
                print(f"Advertencia línea {line}: Conversión de '{expr_type}' a '{target_type}' puede truncar decimales")
    
    p[0] = {'type': target_type}

# ============================================================================
# FIN CONTRIBUCIÓN: Javier Gutiérrez - REGLAS 3 y 4
# ============================================================================

def p_expresion_unaria(p):
    '''expresion : NOT expresion
                 | MINUS expresion %prec UMINUS
                 | PLUS expresion %prec UMINUS
                 | BITXOR expresion
                 | BITNOT expresion
                 | ADDRESS expresion %prec ADDRESS
                 | BITAND expresion %prec ADDRESS
                 | TIMES expresion %prec POINTER'''
    
    expr_type = p[2].get('type') if isinstance(p[2], dict) else 'unknown'
    
    if p[1] == '!':
        p[0] = {'type': 'bool'}
    elif p[1] == '&':
        p[0] = {'type': f'*{expr_type}'}
    elif p[1] == '*':
        p[0] = {'type': expr_type[1:] if expr_type.startswith('*') else 'unknown'}
    else:
        p[0] = {'type': expr_type}

def p_expresion_agrupada(p):
    '''expresion : LPAREN expresion RPAREN'''
    p[0] = p[2]

def p_expresion_primaria(p):
    '''expresion : ID
                 | INT_LITERAL
                 | FLOAT_LITERAL
                 | STRING_LITERAL
                 | RUNE_LITERAL
                 | BOOL_LITERAL
                 | NIL'''
    
    # SI ES UN LITERAL, NO VERIFICAR COMO VARIABLE
    if p.slice[1].type == 'STRING_LITERAL':
        p[0] = {'type': 'string'}
    elif p.slice[1].type == 'INT_LITERAL':
        p[0] = {'type': 'int'}
    elif p.slice[1].type == 'FLOAT_LITERAL':
        p[0] = {'type': 'float64'}
    elif p.slice[1].type == 'BOOL_LITERAL':
        p[0] = {'type': 'bool'}
    elif p.slice[1].type == 'RUNE_LITERAL':
        p[0] = {'type': 'rune'}
    elif p[1] == 'nil':
        p[0] = {'type': 'nil'}
    else:
        # SOLO VERIFICAR COMO VARIABLE SI ES UN ID
        var_name = p[1]
        line = p.lineno(1)
        symbol = symbol_table.lookup(var_name)
        if not symbol:
            add_error(f"Variable '{var_name}' utilizada sin declaración previa", line)
            p[0] = {'type': 'unknown'}
        else:
            p[0] = {'type': symbol.symbol_type}

def p_expresion_llamada(p):
    '''expresion : ID LPAREN lista_expresiones RPAREN
                 | ID LPAREN RPAREN
                 | ID DOT ID LPAREN lista_expresiones RPAREN
                 | ID DOT ID LPAREN RPAREN'''
    
    # PARA FUNCIONES DE IMPRESIÓN COMO fmt.Println, NO VERIFICAR ARGUMENTOS COMO VARIABLES
    if len(p) >= 5 and isinstance(p[1], str) and isinstance(p[3], str):
        if p[1] == 'fmt' and p[3] == 'Println':
            p[0] = {'type': 'void'}
            return
    
    # Para funciones normales, obtener el tipo de retorno
    func_name = p[1]
    symbol = symbol_table.lookup(func_name)
    if symbol and symbol.return_type:
        p[0] = {'type': symbol.return_type}
    else:
        p[0] = {'type': 'unknown'}

def p_expresion_make(p):
    '''expresion : MAKE LPAREN tipo RPAREN
                 | MAKE LPAREN tipo COMMA expresion RPAREN
                 | MAKE LPAREN tipo COMMA expresion COMMA expresion RPAREN'''
    p[0] = {'type': p[3]}

def p_expresion_append(p):
    '''expresion : APPEND LPAREN expresion COMMA lista_expresiones RPAREN
                 | APPEND LPAREN expresion COMMA expresion RPAREN'''
    # append retorna el mismo tipo de slice que recibe como primer argumento
    slice_type = p[3].get('type') if isinstance(p[3], dict) else '[]int'
    p[0] = {'type': slice_type}

def p_expresion_len(p):
    '''expresion : LEN LPAREN expresion RPAREN'''
    p[0] = {'type': 'int'}

def p_expresion_delete(p):
    '''expresion : DELETE LPAREN expresion COMMA expresion RPAREN'''
    p[0] = {'type': 'void'}

def p_expresion_new(p):
    '''expresion : ID DOT ID LPAREN STRING_LITERAL RPAREN'''
    p[0] = {'type': 'unknown'}

def p_expresion_array_acceso(p):
    '''expresion : ID LBRACKET expresion RBRACKET'''
    p[0] = {'type': 'unknown'}

def p_array_literal(p):
    '''expresion : LBRACKET INT_LITERAL RBRACKET tipo LBRACE lista_expresiones RBRACE
                 | LBRACKET INT_LITERAL RBRACKET tipo LBRACE RBRACE
                 | LBRACKET INT_LITERAL RBRACKET LBRACKET INT_LITERAL RBRACKET tipo LBRACE lista_filas_matriz RBRACE'''
    p[0] = {'type': 'array'}

def p_lista_filas_matriz(p):
    '''lista_filas_matriz : lista_filas_matriz COMMA fila_matriz
                          | fila_matriz'''
    pass

def p_fila_matriz(p):
    '''fila_matriz : LBRACE lista_expresiones RBRACE'''
    pass

def p_slice_literal(p):
    '''expresion : LBRACKET RBRACKET tipo LBRACE lista_expresiones RBRACE
                 | LBRACKET RBRACKET tipo LBRACE RBRACE'''
    p[0] = {'type': 'slice'}

def p_slice_operacion(p):
    '''expresion : ID LBRACKET expresion COLON expresion RBRACKET
                 | ID LBRACKET COLON expresion RBRACKET
                 | ID LBRACKET expresion COLON RBRACKET
                 | ID LBRACKET COLON RBRACKET'''
    p[0] = {'type': 'slice'}

def p_map_literal(p):
    '''expresion : MAP LBRACKET tipo RBRACKET tipo LBRACE pares_mapa RBRACE
                 | MAP LBRACKET tipo RBRACKET tipo LBRACE pares_mapa COMMA RBRACE
                 | MAP LBRACKET tipo RBRACKET tipo LBRACE RBRACE'''
    p[0] = {'type': 'map'}

def p_pares_mapa(p):
    '''pares_mapa : pares_mapa COMMA par_mapa
                  | par_mapa'''
    pass

def p_par_mapa(p):
    '''par_mapa : expresion COLON expresion'''
    pass

def p_lista_expresiones(p):
    '''lista_expresiones : lista_expresiones COMMA expresion
                         | expresion'''
    pass

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p:
        error_msg = f"Error de sintaxis en '{p.value}' (Token: {p.type}, Línea: {p.lineno})"
        print(error_msg)
        parser.errok()
    else:
        print("Error de sintaxis: fin de archivo inesperado")

# ============================================================================
# CONSTRUCCIÓN DEL PARSER
# ============================================================================

parser = yacc.yacc()

# ============================================================================
# FUNCIONES DE ANÁLISIS Y LOGGING
# ============================================================================

def analyze_file(filename):
    """
    Analiza semánticamente un archivo de código Go.
    """
    global semantic_errors, symbol_table
    semantic_errors = []
    symbol_table = SymbolTable()
    
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
    print(f"ANÁLISIS SEMÁNTICO DEL ARCHIVO: {filename}")
    print(f"{'='*80}\n")
    
    # Realizar el análisis semántico
    result = parser.parse(data, lexer=lexer)
    
    # Resumen
    print(f"\n{'='*80}")
    print(f"RESUMEN DEL ANÁLISIS SEMÁNTICO")
    print(f"{'='*80}")
    print(f"Total de errores semánticos encontrados: {len(semantic_errors)}")
    
    if semantic_errors:
        print(f"\n{'='*80}")
        print(f"ERRORES SEMÁNTICOS DETECTADOS")
        print(f"{'='*80}")
        for error in semantic_errors:
            print(error)
    else:
        print("\n+ No se encontraron errores semanticos")
    
    # Mostrar tabla de símbolos
    print(f"\n{'='*80}")
    print(f"TABLA DE SÍMBOLOS")
    print(f"{'='*80}")
    for level, scope in enumerate(symbol_table.scopes):
        if scope:
            print(f"\nÁmbito {level}:")
            for name, symbol in scope.items():
                const_str = " [CONST]" if symbol.is_const else ""
                print(f"  - {name}: {symbol.symbol_type}{const_str} (línea {symbol.line})")
    
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
    Genera un archivo de log con los errores semánticos encontrados.
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
    log_filename = f"logs/semantico-{git_user}-{base}-{timestamp}.txt"
    
    # Escribir el log
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        log_file.write("="*80 + "\n")
        log_file.write(f"ANÁLISIS SEMÁNTICO - LENGUAJE GO\n")
        log_file.write("="*80 + "\n")
        log_file.write(f"Archivo analizado: {source_filename}\n")
        log_file.write(f"Fecha y hora: {now.strftime('%d/%m/%Y %H:%M:%S')}\n")
        log_file.write(f"Usuario: {git_user}\n")
        log_file.write("="*80 + "\n\n")
        
        # Reglas semánticas implementadas
        log_file.write("REGLAS SEMÁNTICAS IMPLEMENTADAS\n")
        log_file.write("-"*80 + "\n")
        
        log_file.write("="*80 + "\n")
        log_file.write(f"ERRORES SEMÁNTICOS ENCONTRADOS ({len(semantic_errors)})\n")
        log_file.write("-"*80 + "\n")
        if semantic_errors:
            for error in semantic_errors:
                log_file.write(error + "\n")
        else:
            log_file.write("No se encontraron errores semánticos.\n")
        
        # Tabla de símbolos
        log_file.write("\n" + "="*80 + "\n")
        log_file.write("TABLA DE SÍMBOLOS\n")
        log_file.write("-"*80 + "\n")
        total_symbols = 0
        for level, scope in enumerate(symbol_table.scopes):
            if scope:
                log_file.write(f"\nÁmbito {level}:\n")
                for name, symbol in scope.items():
                    const_str = " [CONST]" if symbol.is_const else ""
                    log_file.write(f"  - {name}: {symbol.symbol_type}{const_str} (línea {symbol.line})\n")
                    total_symbols += 1
        
        log_file.write(f"\nTotal de símbolos: {total_symbols}\n")
        
        log_file.write("\n" + "="*80 + "\n")
        log_file.write("FIN DEL ANÁLISIS SEMÁNTICO\n")
        log_file.write("="*80 + "\n")
    
    print(f"\n+ Log generado exitosamente: {log_filename}")

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python semantico_go.py <archivo.go>")
        print("Ejemplo: python semantico_go.py algoritmo1.go")
        sys.exit(1)
    
    filename = sys.argv[1]
    analyze_file(filename)
    