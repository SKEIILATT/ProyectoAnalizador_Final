// Algoritmo 3 - Prueba de Estructuras de Datos y Funciones
// Autores: Jair Palaguachi - Javier Gutiérrez
// Descripción: Este algoritmo prueba arreglos, slices, mapas y funciones en Go

package main

import (
    "fmt"
    "errors"
)

func main() {
    // Arreglos de tamaño fijo
    var numeros [5]int
    numeros[0] = 10
    numeros[1] = 20
    numeros[2] = 30
    numeros[3] = 40
    numeros[4] = 50
    
    diasSemana := [7]string{"Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"}
    matriz := [3][3]int{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}
    
    fmt.Println("Arreglo de números:", numeros)
    fmt.Println("Días de la semana:", diasSemana)
    fmt.Println("Matriz 3x3:", matriz)
    
    // Slices (arreglos dinámicos)
    var lista []int
    nombres := []string{"Ana", "Luis", "Carlos", "María"}
    datos := make([]float64, 5, 10)
    
    // Operaciones con slices
    lista = append(lista, 1)
    lista = append(lista, 2, 3, 4, 5)
    subslice := nombres[1:3]
    
    fmt.Println("Lista:", lista)
    fmt.Println("Nombres:", nombres)
    fmt.Println("Datos:", datos)
    fmt.Println("Subslice:", subslice)
    
    // Mapas (diccionarios)
    edades := make(map[string]int)
    edades["Juan"] = 25
    edades["Ana"] = 30
    edades["Pedro"] = 28
    
    // Mapa con inicialización literal
    precios := map[string]float64{
        "manzana": 0.50,
        "banana": 0.30,
        "naranja": 0.75,
    }
    
    fmt.Println("Edades:", edades)
    fmt.Println("Precios:", precios)
    fmt.Println("Edad de Juan:", edades["Juan"])
    
    // Eliminar elemento del mapa
    delete(edades, "Pedro")
    fmt.Println("Edades después de eliminar Pedro:", edades)
    
    // Verificar si una clave existe
    edad, existe := edades["Maria"]
    if existe {
        fmt.Println("Edad de María:", edad)
    } else {
        fmt.Println("María no está en el mapa")
    }
    
    // Funciones básicas
    resultado := sumar(10, 20)
    fmt.Println("Suma:", resultado)
    
    // Función con múltiples retornos
    cociente, err := dividir(10.0, 2.0)
    if err != nil {
        fmt.Println("Error:", err)
    } else {
        fmt.Println("Cociente:", cociente)
    }
    
    // División por cero
    _, err2 := dividir(10.0, 0.0)
    if err2 != nil {
        fmt.Println("Error capturado:", err2)
    }
    
    // Función con retorno nombrado
    s, p := calcularOperaciones(5, 3)
    fmt.Println("Suma:", s, "Producto:", p)
    
    // Función variádica
    total := sumarTodos(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    fmt.Println("Total de la suma:", total)
    
    promedioNotas := promediar(85.5, 90.0, 78.5, 92.0)
    fmt.Println("Promedio de notas:", promedioNotas)
    
    // Operaciones con punteros
    valor := 42
    puntero := &valor
    fmt.Println("Valor:", valor)
    fmt.Println("Dirección de memoria:", puntero)
    fmt.Println("Valor a través del puntero:", *puntero)
    
    // Modificar valor a través del puntero
    *puntero = 100
    fmt.Println("Nuevo valor:", valor)
    
    // Función que modifica mediante puntero
    incrementar(&valor)
    fmt.Println("Valor después de incrementar:", valor)
    
    // Operadores bit a bit
    a := 12  // 1100 en binario
    b := 10  // 1010 en binario
    
    fmt.Println("AND bit a bit:", a & b)     // 1000 = 8
    fmt.Println("OR bit a bit:", a | b)      // 1110 = 14
    fmt.Println("XOR bit a bit:", a ^ b)     // 0110 = 6
    fmt.Println("Desplazamiento izq:", a << 2)  // 110000 = 48
    fmt.Println("Desplazamiento der:", a >> 2)  // 0011 = 3
}

// Función simple de suma
func sumar(a int, b int) int {
    return a + b
}

// Función con múltiples retornos (incluyendo error)
func dividir(a float64, b float64) (float64, error) {
    if b == 0.0 {
        return 0.0, errors.New("división por cero no permitida")
    }
    return a / b, nil
}

// Función con retornos nombrados
func calcularOperaciones(x int, y int) (suma int, producto int) {
    suma = x + y
    producto = x * y
    return  // Return implícito
}

// Función variádica (acepta número variable de argumentos)
func sumarTodos(numeros ...int) int {
    total := 0
    for _, num := range numeros {
        total += num
    }
    return total
}

func promediar(valores ...float64) float64 {
    if len(valores) == 0 {
        return 0.0
    }
    suma := 0.0
    for _, v := range valores {
        suma += v
    }
    return suma / float64(len(valores))
}

// Función que modifica mediante puntero
func incrementar(num *int) {
    *num = *num + 1
}
