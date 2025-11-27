# Analizador de Código Go

Herramienta web para analizar código escrito en lenguaje Go. Realiza análisis léxico, sintáctico y semántico mostrando tokens, errores y la tabla de símbolos del código.

## Descripción

Este proyecto surge de la necesidad de contar con una herramienta educativa que permita entender cómo funcionan los compiladores por dentro. Implementa las tres fases principales de análisis de código:

- **Análisis Léxico**: Identifica tokens (palabras reservadas, identificadores, operadores, literales)
- **Análisis Sintáctico**: Valida que la estructura del código cumpla con la gramática de Go
- **Análisis Semántico**: Verifica reglas de tipos, uso de variables, ámbitos y más

La interfaz web permite escribir código directamente o cargar archivos `.go`, facilitando el aprendizaje de conceptos de compiladores de forma visual e interactiva.

## Tecnologías Utilizadas

### Backend
- **Python 3.x**: Lenguaje principal del backend
- **Flask**: Framework web para crear la API REST
- **Flask-CORS**: Manejo de peticiones entre dominios
- **PLY (Python Lex-Yacc)**: Biblioteca para construir analizadores léxicos y sintácticos
  - `lex`: Generador de analizadores léxicos
  - `yacc`: Generador de analizadores sintácticos

### Frontend
- **React**: Biblioteca para construir la interfaz de usuario
- **TypeScript**: Superset de JavaScript con tipado estático
- **Vite**: Herramienta de construcción y desarrollo rápido
- **Axios**: Cliente HTTP para comunicación con el backend
- **CSS3**: Estilos personalizados

## Estructura del Proyecto

```
ProyectoAnalizador_Final/
├── backend/
│   ├── app.py                  # Servidor Flask con endpoints
│   ├── lexico_go.py            # Analizador léxico
│   ├── sintactico_go.py        # Analizador sintáctico
│   ├── semantico_go.py         # Analizador semántico
│   ├── requirements.txt        # Dependencias Python
│   ├── algoritmo1.go           # Archivo de prueba
│   ├── algoritmo2.go           # Archivo de prueba
│   └── algoritmo3.go           # Archivo de prueba
│
└── frontend/AnalizadorFinal/
    ├── src/
    │   ├── components/
    │   │   ├── Analyzer.tsx    # Componente principal
    │   │   └── Analyzer.css    # Estilos del componente
    │   ├── services/
    │   │   └── types.ts        # Interfaces TypeScript
    │   ├── App.tsx             # Componente raíz
    │   └── main.tsx            # Punto de entrada
    ├── package.json            # Dependencias Node
    └── vite.config.ts          # Configuración de Vite
```

## Instalación

### Requisitos Previos
- Python 3.8 o superior
- Node.js 16 o superior
- npm o yarn

### Configuración del Backend

1. Navega a la carpeta backend:
```bash
cd backend
```

2. Crea un entorno virtual (recomendado):
```bash
python -m venv .venv
```

3. Activa el entorno virtual:
- Windows:
```bash
.venv\Scripts\activate
```
- Linux/Mac:
```bash
source .venv/bin/activate
```

4. Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Configuración del Frontend

1. Navega a la carpeta del frontend:
```bash
cd frontend/
```

2. Instala las dependencias:
```bash
npm install
```

## Uso

### Iniciar el Backend

Desde la carpeta `backend`:
```bash
python app.py
```

El servidor estará disponible en `http://localhost:5000`

### Iniciar el Frontend

Desde la carpeta `frontend/`:
```bash
npm run dev
```

La aplicación web estará disponible en `http://localhost:5173`

### Usando la Aplicación

1. **Escribir código**: Usa el editor de la izquierda para escribir código Go
2. **Cargar archivo**: Haz clic en "Abrir Archivo" para cargar un archivo `.go`
3. **Analizar**: Presiona el botón "Analizar" para procesar el código
4. **Ver resultados**: Navega entre las pestañas:
   - **Errores**: Muestra errores léxicos, sintácticos y semánticos
   - **Tokens**: Lista todos los tokens identificados
   - **Estructura**: Muestra la tabla de símbolos con variables y funciones
5. **Guardar**: Descarga el código editado como archivo `.go`

## Características del Analizador

### Análisis Léxico
El analizador léxico reconoce:
- Palabras reservadas de Go (func, var, if, for, etc.)
- Identificadores y variables
- Literales (números, strings, booleanos, runas)
- Operadores aritméticos, lógicos y de asignación
- Delimitadores (paréntesis, llaves, corchetes)
- Comentarios de línea y multilínea

### Análisis Sintáctico
Valida la estructura del código:
- Declaraciones de paquetes e importaciones
- Definición de funciones con parámetros y retornos
- Declaración de variables (var, const, :=)
- Estructuras de control (if, for, switch)
- Expresiones aritméticas y lógicas
- Arrays, slices y maps
- Llamadas a funciones

### Análisis Semántico
Verifica reglas semánticas:
- Variables declaradas antes de usarse
- No redeclaración de variables en el mismo ámbito
- Gestión de ámbitos (global, local, bloques)
- Tipos de datos y operaciones válidas
- Retornos de funciones coherentes
- Constantes correctamente definidas

## API Endpoints

### POST /api/analyze
Analiza código enviado como texto.

**Request Body:**
```json
{
  "code": "package main\n\nfunc main() {\n    var x int = 10\n}"
}
```

**Response:**
```json
{
  "lexico": {
    "tokens": [...],
    "errores": [...]
  },
  "sintactico": {
    "errores": [...]
  },
  "semantico": {
    "errores": [...],
    "tabla_simbolos": [...]
  }
}
```

### POST /api/analyze-file
Analiza un archivo `.go` subido.

**Request:** FormData con campo `file`

**Response:** Igual al anterior más:
```json
{
  "filename": "algoritmo.go",
  "code": "contenido del archivo..."
}
```

## Ejemplos de Código Go Soportado

```go
package main

import "fmt"

func main() {
    // Declaración de variables
    var nombre string = "Juan"
    edad := 25

    // Constantes
    const PI = 3.14159

    // Estructuras de control
    if edad >= 18 {
        fmt.Println("Mayor de edad")
    }

    // Bucles
    for i := 0; i < 10; i++ {
        fmt.Println(i)
    }

    // Arrays y slices
    numeros := []int{1, 2, 3, 4, 5}

    // Funciones
    resultado := sumar(10, 20)
}

func sumar(a int, b int) int {
    return a + b
}
```

## Uso desde Línea de Comandos

Los analizadores también pueden usarse directamente desde la terminal:

```bash
# Análisis léxico
python lexico_go.py algoritmo1.go

# Análisis sintáctico
python sintactico_go.py algoritmo1.go

# Análisis semántico
python semantico_go.py algoritmo1.go
```

## Limitaciones Conocidas

- No soporta todas las características avanzadas de Go (goroutines, interfaces complejas)
- El análisis semántico es básico (no valida todos los casos de tipos)
- No genera código máquina ni bytecode
- Diseñado con fines educativos, no para producción

## Integrantes del Proyecto

- Jair Palaguachi ([@JairPalaguachi](https://github.com/JairPalaguachi))
- Javier Gutiérrez ([@SKEIILATT](https://github.com/SKEIILATT))

