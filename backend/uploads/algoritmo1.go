// Algoritmo 1 - Prueba de Declaraciones de Variables
// Autor: Jair Palaguachi (JairPalaguachi)
// Descripción: Este algoritmo prueba diferentes formas de declaración de variables en Go

package main

import "fmt"

func main() {
    // Declaración con var y tipo explícito
    var nombre string
    var edad int = 25
    var precio float64 = 19.99
    var activo bool = true
    
    // Declaración con inferencia de tipo
    var ciudad = "Quito"
    var temperatura = 18.5
    
    // Declaración corta (dentro de funciones)
    contador := 0
    mensaje := "Hola Mundo"
    resultado := calcular(10, 20)
    
    // Declaración múltiple
    var x, y, z int
    a, b, c := 1, 2, 3
    
    // Bloque de declaraciones
    var (
        nombre_completo string = "Juan Pérez"
        codigo int = 12345
        habilitado bool = true
    )
    
    // Constantes
    const PI = 3.14159
    const MAX_USUARIOS = 100
    
    // Uso de operadores aritméticos
    suma := a + b
    resta := c - a
    multiplicacion := b * c
    division := edad / 5
    modulo := edad % 7
    
    // Incremento y decremento
    contador++
    edad--
    
    // Imprimir resultados
    fmt.Println("Nombre:", nombre)
    fmt.Println("Edad:", edad)
    fmt.Println("Precio:", precio)
    fmt.Println("Activo:", activo)
    fmt.Println("Ciudad:", ciudad)
    fmt.Println("Temperatura:", temperatura)
    fmt.Println("Contador:", contador)
    fmt.Println("Mensaje:", mensaje)
    fmt.Println("Resultado:", resultado)
    fmt.Println("Variables múltiples:", x, y, z)
    fmt.Println("Declaración corta:", a, b, c)
    fmt.Println("Nombre completo:", nombre_completo)
    fmt.Println("Código:", codigo)
    fmt.Println("Habilitado:", habilitado)
    fmt.Println("PI:", PI)
    fmt.Println("MAX_USUARIOS:", MAX_USUARIOS)
    fmt.Println("Operaciones:", suma, resta, multiplicacion, division, modulo)
}

func calcular(x int, y int) int {
    return x + y
}