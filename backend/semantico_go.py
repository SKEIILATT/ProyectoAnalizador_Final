"""
Analizador Semántico para el Lenguaje Go
Proyecto: Implementación de un Analizador Semántico en Go
Integrantes:
- Jair Palaguachi (JairPalaguachi)
- Javier Gutiérrez (SKEIILATT)

"""

import ply.yacc as yacc
import ply.lex as lex
import lexico_go
from lexico_go import tokens
from datetime import datetime
import sys
import os

# ============================================================================
# TABLA DE SÍMBOLOS
# ============================================================================

class Symbol:
    def __init__(self, name, symbol_type, value=None, scope='global', line=0, is_const=False, return_type=None, params=None):
        self.name = name
        self.symbol_type = symbol_type
        self.value = value
        self.scope = scope
        self.line = line
        self.is_const = is_const
        self.return_type = return_type
        self.params = params if params is not None else []  # Lista de tipos de parámetros

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
        self.current_scope_level = 0
        
    def enter_scope(self):
        self.scopes.append({})
        self.current_scope_level += 1
    
    def exit_scope(self):
        if self.current_scope_level > 0:
            self.scopes.pop()
            self.current_scope_level -= 1
    
    def insert(self, symbol):
        self.scopes[self.current_scope_level][symbol.name] = symbol
    
    def lookup(self, name):
        for i in range(self.current_scope_level, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        return None
    
    def lookup_current_scope(self, name):
        return self.scopes[self.current_scope_level].get(name)
    
    def to_dict(self):
        result = []
        for level, scope in enumerate(self.scopes):
            scope_data = []
            for name, symbol in scope.items():
                scope_data.append({
                    'name': name,
                    'type': symbol.symbol_type,
                    'scope': symbol.scope,
                    'line': symbol.line,
                    'is_const': symbol.is_const,
                    'return_type': symbol.return_type
                })
            if scope_data:
                result.append({
                    'level': level,
                    'symbols': scope_data
                })
        return result

# Tipos compatibles
NUMERIC_TYPES = {'int', 'int8', 'int16', 'int32', 'int64', 
                 'uint', 'uint8', 'uint16', 'uint32', 'uint64',
                 'float32', 'float64'}

INTEGER_TYPES = {'int', 'int8', 'int16', 'int32', 'int64',
                 'uint', 'uint8', 'uint16', 'uint32', 'uint64'}

FLOAT_TYPES = {'float32', 'float64'}

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

# Variables globales
_semantic_errors = []
_symbol_table = None
_current_function = None
_inside_loop = 0

def add_error(message, line=0):
    global _semantic_errors
    _semantic_errors.append({
        'message': message,
        'line': line
    })

# ============================================================================
# PRECEDENCIA
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
    pass

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

def p_declaracion_var_global(p):
    '''declaracion_var_global : VAR ID tipo
                              | VAR ID tipo ASSIGN expresion
                              | VAR ID ASSIGN expresion'''
    global _symbol_table
    var_name = p[2]
    line = p.lineno(2)
    
    if _symbol_table.lookup_current_scope(var_name):
        add_error(f"Variable '{var_name}' ya declarada", line)
    else:
        if len(p) == 4:
            _symbol_table.insert(Symbol(var_name, p[3], None, 'global', line))
        elif len(p) == 6:
            _symbol_table.insert(Symbol(var_name, p[3], None, 'global', line))
        else:
            expr_type = p[4].get('type') if isinstance(p[4], dict) else 'unknown'
            _symbol_table.insert(Symbol(var_name, expr_type, None, 'global', line))

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
    global _symbol_table
    var_name = p[1]
    line = p.lineno(1)

    if _symbol_table.lookup_current_scope(var_name):
        add_error(f"Variable '{var_name}' ya declarada", line)
    else:
        if len(p) == 3:  # ID tipo
            _symbol_table.insert(Symbol(var_name, p[2], None, 'global', line))
        elif len(p) == 4:  # ID ASSIGN expresion
            expr_type = p[3].get('type') if isinstance(p[3], dict) else 'int'
            _symbol_table.insert(Symbol(var_name, expr_type, None, 'global', line))
        else:  # ID tipo ASSIGN expresion (len == 5)
            _symbol_table.insert(Symbol(var_name, p[2], None, 'global', line))

def p_declaracion_var(p):
    '''declaracion_var : VAR ID tipo
                       | VAR ID tipo ASSIGN expresion
                       | VAR ID ASSIGN expresion
                       | ID DECLARE_ASSIGN expresion'''
    global _symbol_table
    var_name = p[2] if p[1] == 'var' else p[1]
    line = p.lineno(2) if p[1] == 'var' else p.lineno(1)
    
    if _symbol_table.lookup_current_scope(var_name):
        add_error(f"Variable '{var_name}' ya declarada", line)
    else:
        if len(p) == 4 and p[1] == 'var':
            _symbol_table.insert(Symbol(var_name, p[3], None, 'local', line))
        elif len(p) == 4:
            expr_type = p[3].get('type') if isinstance(p[3], dict) else 'int'
            _symbol_table.insert(Symbol(var_name, expr_type, None, 'local', line))
        elif len(p) == 6:
            _symbol_table.insert(Symbol(var_name, p[3], None, 'local', line))
        else:
            expr_type = p[4].get('type') if isinstance(p[4], dict) else 'int'
            _symbol_table.insert(Symbol(var_name, expr_type, None, 'local', line))

def p_funcion(p):
    '''funcion : funcion_header bloque'''
    global _current_function, _symbol_table
    _symbol_table.exit_scope()
    _current_function = None

def p_funcion_header(p):
    '''funcion_header : FUNC ID LPAREN parametros RPAREN tipo_retorno
                      | FUNC ID LPAREN parametros RPAREN'''
    global _current_function, _symbol_table
    func_name = p[2]
    line = p.lineno(2)
    return_type = p[6] if len(p) == 7 else 'void'
    params = p[4] if p[4] is not None else []

    if not _symbol_table.lookup_current_scope(func_name):
        _symbol_table.insert(Symbol(func_name, 'func', None, 'global', line, return_type=return_type, params=params))

    _current_function = {'name': func_name, 'return_type': return_type, 'line': line, 'params': params}
    _symbol_table.enter_scope()

def p_bloque(p):
    '''bloque : LBRACE sentencias RBRACE
              | LBRACE RBRACE'''
    pass

def p_asignacion(p):
    '''asignacion : ID ASSIGN expresion
                  | ID PLUS_ASSIGN expresion
                  | ID MINUS_ASSIGN expresion
                  | ID TIMES_ASSIGN expresion
                  | ID DIVIDE_ASSIGN expresion
                  | ID LBRACKET expresion RBRACKET ASSIGN expresion
                  | TIMES ID ASSIGN expresion'''
    global _symbol_table
    var_name = p[2] if p[1] == '*' else p[1]
    line = p.lineno(2) if p[1] == '*' else p.lineno(1)
    
    symbol = _symbol_table.lookup(var_name)
    if not symbol:
        add_error(f"Variable '{var_name}' no declarada", line)

def p_declaracion_const(p):
    '''declaracion_const : CONST ID ASSIGN expresion
                         | CONST ID tipo ASSIGN expresion'''
    global _symbol_table
    const_name = p[2]
    line = p.lineno(2)
    
    if _symbol_table.lookup_current_scope(const_name):
        add_error(f"Constante '{const_name}' ya declarada", line)
    else:
        expr_type = 'int' if len(p) == 5 else p[3]
        _symbol_table.insert(Symbol(const_name, expr_type, None, 'global', line, is_const=True))

def p_declaracion_var_multiple(p):
    '''declaracion_var_multiple : VAR lista_ids tipo
                                | VAR lista_ids tipo ASSIGN lista_expresiones
                                | lista_ids DECLARE_ASSIGN lista_expresiones'''
    global _symbol_table

    if p[1] == 'var':
        # Casos: VAR lista_ids tipo o VAR lista_ids tipo ASSIGN lista_expresiones
        ids = p[2] if isinstance(p[2], list) else [p[2]]
        var_type = p[3]
        line = p.lineno(1)

        for var_id in ids:
            if var_id != '_':
                if _symbol_table.lookup_current_scope(var_id):
                    add_error(f"Variable '{var_id}' ya declarada", line)
                else:
                    _symbol_table.insert(Symbol(var_id, var_type, None, 'local', line))
    else:
        # Caso: lista_ids DECLARE_ASSIGN lista_expresiones
        ids = p[1] if isinstance(p[1], list) else [p[1]]
        line = p.lineno(2)

        for var_id in ids:
            if var_id != '_':
                if _symbol_table.lookup_current_scope(var_id):
                    add_error(f"Variable '{var_id}' ya declarada", line)
                else:
                    # Asumimos tipo int por defecto para declaraciones cortas sin tipo explícito
                    _symbol_table.insert(Symbol(var_id, 'int', None, 'local', line))

def p_lista_ids(p):
    '''lista_ids : lista_ids COMMA ID
                 | lista_ids COMMA UNDERSCORE
                 | ID
                 | UNDERSCORE'''
    if len(p) == 4:  # lista_ids COMMA ID/UNDERSCORE
        p[0] = p[1] + [p[3]]
    else:  # ID o UNDERSCORE
        p[0] = [p[1]]

def p_asignacion_multiple(p):
    '''asignacion_multiple : lista_ids ASSIGN lista_expresiones'''
    pass

def p_parametros(p):
    '''parametros : lista_parametros
                  | empty'''
    p[0] = p[1] if p[1] is not None else []

def p_lista_parametros(p):
    '''lista_parametros : lista_parametros COMMA parametro
                        | parametro'''
    if len(p) == 4:  # lista_parametros COMMA parametro
        p[0] = p[1] + p[3] if p[3] is not None else p[1]
    else:  # parametro
        p[0] = p[1] if p[1] is not None else []

def p_parametro(p):
    '''parametro : ID tipo
                 | ID COMMA ID tipo
                 | ID ELLIPSIS tipo
                 | TIMES ID
                 | UNDERSCORE tipo'''
    global _symbol_table

    if len(p) == 3:  # ID tipo o UNDERSCORE tipo
        param_name = p[1]
        param_type = p[2]
        line = p.lineno(1)

        if param_name != '_':
            if _symbol_table.lookup_current_scope(param_name):
                add_error(f"Parámetro '{param_name}' ya declarado", line)
            else:
                _symbol_table.insert(Symbol(param_name, param_type, None, 'parameter', line))

        # Retornar lista con el tipo del parámetro
        p[0] = [param_type]
    elif len(p) == 5 and p[2] == ',':  # ID COMMA ID tipo (dos parámetros del mismo tipo)
        param1 = p[1]
        param2 = p[3]
        param_type = p[4]
        line = p.lineno(1)

        for param_name in [param1, param2]:
            if param_name != '_':
                if _symbol_table.lookup_current_scope(param_name):
                    add_error(f"Parámetro '{param_name}' ya declarado", line)
                else:
                    _symbol_table.insert(Symbol(param_name, param_type, None, 'parameter', line))

        # Retornar lista con dos tipos (ambos del mismo tipo)
        p[0] = [param_type, param_type]
    else:
        # Otros casos (ELLIPSIS, TIMES)
        p[0] = ['unknown']

def p_tipo_retorno(p):
    '''tipo_retorno : tipo
                    | LPAREN lista_tipos RPAREN
                    | LPAREN lista_retornos_nombrados RPAREN'''
    p[0] = p[1] if len(p) == 2 else 'multiple'

def p_return_statement(p):
    '''return_statement : RETURN
                        | RETURN expresion
                        | RETURN lista_expresiones'''
    global _current_function
    if _current_function and _current_function['name'] != 'main':
        expected = _current_function.get('return_type', 'void')
        if len(p) == 2 and expected != 'void':
            add_error(f"Función '{_current_function['name']}' debe retornar valor", p.lineno(1))

def p_lista_retornos_nombrados(p):
    '''lista_retornos_nombrados : lista_retornos_nombrados COMMA ID tipo
                                | ID tipo'''
    pass

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
    p[0] = 'int' if len(p) == 2 else 'composite'

def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | sentencia'''
    pass

def p_if_statement(p):
    '''if_statement : IF condicion bloque
                    | IF condicion bloque ELSE bloque
                    | IF condicion bloque ELSE if_statement'''
    pass

def p_condicion(p):
    '''condicion : expresion
                 | declaracion_var_corta SEMICOLON expresion'''
    p[0] = p[1] if len(p) == 2 else p[3]

def p_declaracion_var_corta(p):
    '''declaracion_var_corta : ID DECLARE_ASSIGN expresion
                             | lista_ids DECLARE_ASSIGN expresion'''
    pass

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
    global _symbol_table, _inside_loop

    # Incrementar contador de loops
    _inside_loop += 1

    # Manejar for-range con declaración de variables
    if len(p) >= 8 and 'RANGE' in [str(x) for x in p[1:]]:
        # Buscar la posición de DECLARE_ASSIGN o ASSIGN
        if p[4] == ':=' or (len(p) > 6 and p[6] == ':='):
            # Declaración con :=
            if p[2] != '_':  # Primera variable (índice)
                line = p.lineno(2)
                if not _symbol_table.lookup_current_scope(p[2]):
                    _symbol_table.insert(Symbol(p[2], 'int', None, 'local', line))

            if len(p) > 6 and p[4] == ',' and p[5] != '_':  # Segunda variable (valor)
                line = p.lineno(5)
                if not _symbol_table.lookup_current_scope(p[5]):
                    # El tipo depende del tipo de la colección, asumimos int por simplicidad
                    _symbol_table.insert(Symbol(p[5], 'int', None, 'local', line))

    _inside_loop -= 1

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
    pass

def p_casos(p):
    '''casos : casos caso
             | caso'''
    pass

def p_caso(p):
    '''caso : CASE lista_expresiones COLON sentencias
            | DEFAULT COLON sentencias'''
    pass

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
                 | empty'''
    pass

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

    # Obtener tipos de los operandos
    left_type = p[1].get('type', 'unknown') if isinstance(p[1], dict) else 'unknown'
    right_type = p[3].get('type', 'unknown') if isinstance(p[3], dict) else 'unknown'
    operator = p[2]

    # Verificar compatibilidad de tipos
    if left_type != 'unknown' and right_type != 'unknown':
        if operator in ['<', '<=', '>', '>=', '==', '!=']:
            # Operadores de comparación requieren tipos compatibles
            if left_type != right_type:
                # Verificar si son tipos numéricos compatibles
                if not (left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES):
                    add_error(f"No se puede comparar tipo '{left_type}' con tipo '{right_type}'", p.lineno(2))
        elif operator in ['+', '-', '*', '/', '%']:
            # Operadores aritméticos requieren tipos numéricos
            if operator == '+' and (left_type == 'string' or right_type == 'string'):
                # Concatenación de strings permitida
                pass
            elif left_type != right_type:
                if not (left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES):
                    add_error(f"Operación '{operator}' no válida entre tipo '{left_type}' y tipo '{right_type}'", p.lineno(2))
        elif operator in ['&&', '||']:
            # Operadores lógicos requieren bool
            if left_type != 'bool' or right_type != 'bool':
                add_error(f"Operador lógico '{operator}' requiere operandos de tipo bool", p.lineno(2))

    p[0] = {'type': 'bool' if operator in ['&&', '||', '==', '!=', '<', '<=', '>', '>='] else left_type}

def p_expresion_unaria(p):
    '''expresion : NOT expresion
                 | MINUS expresion %prec UMINUS
                 | PLUS expresion %prec UMINUS
                 | BITXOR expresion
                 | BITNOT expresion
                 | ADDRESS expresion %prec ADDRESS
                 | BITAND expresion %prec ADDRESS
                 | TIMES expresion %prec POINTER'''
    p[0] = {'type': 'bool' if p[1] == '!' else 'int'}

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
    global _symbol_table
    
    if p.slice[1].type == 'ID':
        symbol = _symbol_table.lookup(p[1])
        if not symbol:
            add_error(f"Variable '{p[1]}' no declarada", p.lineno(1))
            p[0] = {'type': 'unknown'}
        else:
            p[0] = {'type': symbol.symbol_type}
    elif p.slice[1].type == 'INT_LITERAL':
        p[0] = {'type': 'int'}
    elif p.slice[1].type == 'FLOAT_LITERAL':
        p[0] = {'type': 'float64'}
    elif p.slice[1].type == 'STRING_LITERAL':
        p[0] = {'type': 'string'}
    elif p.slice[1].type == 'BOOL_LITERAL':
        p[0] = {'type': 'bool'}
    else:
        p[0] = {'type': 'unknown'}

def p_expresion_llamada(p):
    '''expresion : ID LPAREN lista_expresiones RPAREN
                 | ID LPAREN RPAREN
                 | ID DOT ID LPAREN lista_expresiones RPAREN
                 | ID DOT ID LPAREN RPAREN'''
    global _symbol_table

    # Determinar si es una llamada simple (ID(...)) o con punto (ID.ID(...))
    if len(p) == 5:  # ID LPAREN ... RPAREN
        func_name = p[1]
        args = p[3] if p[3] is not None else []
        line = p.lineno(1)

        # Buscar la función en la tabla de símbolos
        symbol = _symbol_table.lookup(func_name)
        if symbol and symbol.symbol_type == 'func':
            # Obtener tipos de los argumentos pasados
            arg_types = [arg.get('type', 'unknown') for arg in args] if isinstance(args, list) else []

            # Verificar número de argumentos
            if len(arg_types) != len(symbol.params):
                add_error(f"Función '{func_name}' espera {len(symbol.params)} argumentos, pero se pasaron {len(arg_types)}", line)
            else:
                # Verificar tipos de argumentos
                for i, (arg_type, param_type) in enumerate(zip(arg_types, symbol.params)):
                    if arg_type != 'unknown' and param_type != 'unknown':
                        if arg_type != param_type:
                            # Verificar si son tipos numéricos compatibles
                            if not (arg_type in NUMERIC_TYPES and param_type in NUMERIC_TYPES):
                                add_error(f"Argumento {i+1} de '{func_name}': se esperaba tipo '{param_type}', pero se recibió '{arg_type}'", line)

            p[0] = {'type': symbol.return_type if symbol.return_type else 'void'}
        elif not symbol:
            # La función no está declarada (pero puede ser una función integrada)
            p[0] = {'type': 'unknown'}
        else:
            p[0] = {'type': 'void'}
    else:  # ID DOT ID LPAREN ... RPAREN (llamada con punto, como fmt.Println)
        p[0] = {'type': 'void'}

def p_expresion_make(p):
    '''expresion : MAKE LPAREN tipo RPAREN
                 | MAKE LPAREN tipo COMMA expresion RPAREN
                 | MAKE LPAREN tipo COMMA expresion COMMA expresion RPAREN'''
    p[0] = {'type': 'slice'}

def p_expresion_append(p):
    '''expresion : APPEND LPAREN expresion COMMA lista_expresiones RPAREN
                 | APPEND LPAREN expresion COMMA expresion RPAREN'''
    p[0] = {'type': 'slice'}

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
    p[0] = {'type': 'int'}

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
    if len(p) == 4:  # lista_expresiones COMMA expresion
        prev_list = p[1] if isinstance(p[1], list) else [p[1]]
        expr_type = p[3].get('type', 'unknown') if isinstance(p[3], dict) else 'unknown'
        p[0] = prev_list + [{'type': expr_type}]
    else:  # expresion
        expr_type = p[1].get('type', 'unknown') if isinstance(p[1], dict) else 'unknown'
        p[0] = [{'type': expr_type}]

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    # No agregamos errores de sintaxis aquí ya que eso lo maneja sintactico_go.py
    # Solo manejamos la recuperación del parser
    if p and hasattr(p, 'parser'):
        p.parser.errok()

# Construir parser
parser = yacc.yacc()

# ============================================================================
# Para usar en API REST
# ============================================================================

def analyze_semantic_string(code_string):
    """
    Analiza semánticamente código Go recibido como string (para API).
    """
    global _semantic_errors, _symbol_table, _current_function, _inside_loop
    
    _semantic_errors = []
    _symbol_table = SymbolTable()
    _current_function = None
    _inside_loop = 0
    
    new_lexer = lex.lex(module=lexico_go)
    
    try:
        parser.parse(code_string, lexer=new_lexer)
    except Exception as e:
        _semantic_errors.append({
            'message': f"Error crítico: {str(e)}",
            'line': 0
        })
    
    return {
        'errors': _semantic_errors,
        'symbol_table': _symbol_table.to_dict()
    }

# ============================================================================
# Para usar en CLI
# ============================================================================

def analyze_file(filename):
    """Analiza semánticamente un archivo de código Go."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{filename}' no fue encontrado.")
        return
    
    print(f"\n{'='*80}")
    print(f"ANÁLISIS SEMÁNTICO DEL ARCHIVO: {filename}")
    print(f"{'='*80}\n")
    
    result = analyze_semantic_string(data)
    
    print(f"\n{'='*80}")
    print(f"RESUMEN DEL ANÁLISIS SEMÁNTICO")
    print(f"{'='*80}")
    print(f"Total de errores: {len(result['errors'])}")
    
    if result['errors']:
        print(f"\n{'='*80}")
        print(f"ERRORES SEMÁNTICOS")
        print(f"{'='*80}")
        for error in result['errors']:
            print(f"Línea {error['line']}: {error['message']}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python semantico_go.py <archivo.go>")
        sys.exit(1)
    
    filename = sys.argv[1]
    analyze_file(filename)