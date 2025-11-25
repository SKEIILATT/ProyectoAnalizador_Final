// Algoritmo 2 - Prueba de Estructuras de Control
// Autor: Javier Gutiérrez (SKEIILATT)
// Descripción: Este algoritmo prueba condicionales, bucles y switch en Go

package main

import "fmt"

func main() {
    // Variables de prueba
    edad := 25
    puntuacion := 85
    dia := "lunes"
    numeros := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    
    // Condicional if-else
    if edad >= 18 {
        fmt.Println("Mayor de edad")
    } else {
        fmt.Println("Menor de edad")
    }
    
    // Condicional if-else if-else
    if puntuacion >= 90 {
        fmt.Println("Calificación: A")
    } else if puntuacion >= 80 {
        fmt.Println("Calificación: B")
    } else if puntuacion >= 70 {
        fmt.Println("Calificación: C")
    } else {
        fmt.Println("Calificación: Reprobado")
    }
    
    // If con inicialización
    if valor := calcularPromedio(80, 90); valor > 75 {
        fmt.Println("Promedio aprobado:", valor)
    }
    
    // Expresiones booleanas compuestas
    esAdulto := edad >= 18 && edad <= 65
    tieneAcceso := esAdulto || puntuacion > 80
    noEstaVacio := !(dia == "")
    
    fmt.Println("Es adulto:", esAdulto)
    fmt.Println("Tiene acceso:", tieneAcceso)
    fmt.Println("No está vacío:", noEstaVacio)
    
    // Bucle for tradicional
    fmt.Println("Conteo del 1 al 5:")
    for i := 1; i <= 5; i++ {
        fmt.Println(i)
    }
    
    // Bucle for estilo while
    contador := 0
    for contador < 3 {
        fmt.Println("Contador:", contador)
        contador++
    }
    
    // Bucle for con range
    fmt.Println("Números en el arreglo:")
    for indice, valor := range numeros {
        if valor % 2 == 0 {
            fmt.Println("Índice", indice, "- Número par:", valor)
        }
    }
    
    // Switch básico
    switch dia {
    case "lunes":
        fmt.Println("Inicio de semana")
    case "viernes":
        fmt.Println("Fin de semana laboral")
    case "sábado", "domingo":
        fmt.Println("Fin de semana")
    default:
        fmt.Println("Día de semana regular")
    }
    
    // Switch sin expresión (como if-else)
    switch {
    case edad < 13:
        fmt.Println("Categoría: Niño")
    case edad < 20:
        fmt.Println("Categoría: Adolescente")
    case edad < 60:
        fmt.Println("Categoría: Adulto")
    default:
        fmt.Println("Categoría: Adulto Mayor")
    }
    
    // Switch con inicialización
    switch resultado := evaluarNota(puntuacion); resultado {
    case "Excelente":
        fmt.Println("¡Felicitaciones!")
    case "Bueno":
        fmt.Println("Buen trabajo")
    default:
        fmt.Println("Puede mejorar")
    }
    
    // Operadores de comparación
    a := 10
    b := 20
    fmt.Println("a == b:", a == b)
    fmt.Println("a != b:", a != b)
    fmt.Println("a < b:", a < b)
    fmt.Println("a <= b:", a <= b)
    fmt.Println("a > b:", a > b)
    fmt.Println("a >= b:", a >= b)
}

func calcularPromedio(nota1 int, nota2 int) int {
    return (nota1 + nota2) / 2
}

func evaluarNota(puntos int) string {
    if puntos >= 90 {
        return "Excelente"
    } else if puntos >= 70 {
        return "Bueno"
    }
    return "Regular"
}