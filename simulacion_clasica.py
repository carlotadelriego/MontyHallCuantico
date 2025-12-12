"""
Simulación Clásica del Problema de Monty Hall
==============================================
Computación Cuántica y Natural - Proyecto Final
Hugo Iglesias Pombo, Carlota Fernández del Riego

Este módulo implementa la simulación clásica del problema de Monty Hall
usando el método Monte Carlo. Sirve como baseline para comparar con
las implementaciones cuánticas.

PROBLEMA DE MONTY HALL:
- 3 puertas: una tiene premio, dos están vacías
- El jugador elige una puerta
- El presentador revela UNA puerta vacía (distinta de la elegida)
- El jugador decide: mantener o cambiar

RESULTADO TEÓRICO:
- Mantener: P(ganar) = 1/3 ≈ 33.33%
- Cambiar:  P(ganar) = 2/3 ≈ 66.67%
"""

import random
from typing import Tuple, List, Dict
from dataclasses import dataclass


# ============================================================================
# ESTRUCTURAS DE DATOS
# ============================================================================
@dataclass
class ResultadoPartida:
    """Representa el resultado de una partida de Monty Hall."""
    premio: int           # Puerta donde está el premio (0, 1, 2)
    eleccion_inicial: int # Puerta elegida inicialmente
    puerta_revelada: int  # Puerta revelada por el presentador
    eleccion_final: int   # Puerta final del jugador
    estrategia: str       # "mantener" o "cambiar"
    victoria: bool        # True si ganó


# ============================================================================
# LÓGICA DEL JUEGO
# ============================================================================
def jugar_monty_hall(estrategia: str = "mantener") -> ResultadoPartida:
    """
    Simula una partida completa del problema de Monty Hall.
    
    Args:
        estrategia: "mantener" o "cambiar"
        
    Returns:
        ResultadoPartida con todos los detalles de la partida
    """
    # 1. El premio se coloca aleatoriamente
    premio = random.randint(0, 2)
    
    # 2. El jugador elige una puerta aleatoriamente
    eleccion_inicial = random.randint(0, 2)
    
    # 3. El presentador revela una puerta vacía (distinta de la elegida y sin premio)
    opciones_revelar = [0, 1, 2]
    opciones_revelar.remove(eleccion_inicial)
    if premio in opciones_revelar:
        opciones_revelar.remove(premio)
    puerta_revelada = random.choice(opciones_revelar)
    
    # 4. El jugador aplica su estrategia
    if estrategia == "cambiar":
        opciones_finales = [0, 1, 2]
        opciones_finales.remove(eleccion_inicial)
        opciones_finales.remove(puerta_revelada)
        eleccion_final = opciones_finales[0]
    else:  # mantener
        eleccion_final = eleccion_inicial
    
    # 5. Determinar resultado
    victoria = (eleccion_final == premio)
    
    return ResultadoPartida(
        premio=premio,
        eleccion_inicial=eleccion_inicial,
        puerta_revelada=puerta_revelada,
        eleccion_final=eleccion_final,
        estrategia=estrategia,
        victoria=victoria
    )


# ============================================================================
# SIMULACIÓN MONTE CARLO
# ============================================================================
def simular_monte_carlo(num_partidas: int = 10000) -> Dict[str, Dict]:
    """
    Ejecuta simulación Monte Carlo del problema de Monty Hall.
    
    Args:
        num_partidas: Número de partidas a simular por estrategia
        
    Returns:
        Diccionario con estadísticas por estrategia
    """
    resultados = {
        "mantener": {"victorias": 0, "derrotas": 0, "partidas": []},
        "cambiar": {"victorias": 0, "derrotas": 0, "partidas": []}
    }
    
    for estrategia in ["mantener", "cambiar"]:
        for _ in range(num_partidas):
            partida = jugar_monty_hall(estrategia)
            if partida.victoria:
                resultados[estrategia]["victorias"] += 1
            else:
                resultados[estrategia]["derrotas"] += 1
            
            # Guardar solo primeras 10 partidas para muestra
            if len(resultados[estrategia]["partidas"]) < 10:
                resultados[estrategia]["partidas"].append(partida)
    
    # Calcular probabilidades
    for estrategia in resultados:
        total = resultados[estrategia]["victorias"] + resultados[estrategia]["derrotas"]
        resultados[estrategia]["probabilidad"] = resultados[estrategia]["victorias"] / total
    
    return resultados


# ============================================================================
# ANÁLISIS TEÓRICO
# ============================================================================
def explicar_probabilidades():
    """Explica matemáticamente por qué cambiar es mejor."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           ANÁLISIS TEÓRICO - PROBLEMA DE MONTY HALL          ║
╚══════════════════════════════════════════════════════════════╝

ESTRATEGIA "MANTENER":
┌──────────────────────────────────────────────────────────────┐
│ El jugador gana SI Y SOLO SI eligió correctamente al inicio │
│                                                              │
│ P(elegir correctamente) = 1/3                                │
│                                                              │
│ → P(ganar manteniendo) = 1/3 ≈ 33.33%                        │
└──────────────────────────────────────────────────────────────┘

ESTRATEGIA "CAMBIAR":
┌──────────────────────────────────────────────────────────────┐
│ El jugador gana SI Y SOLO SI eligió INCORRECTAMENTE al inicio│
│ (porque el presentador revela la otra puerta vacía)          │
│                                                              │
│ P(elegir incorrectamente) = 2/3                              │
│                                                              │
│ → P(ganar cambiando) = 2/3 ≈ 66.67%                          │
└──────────────────────────────────────────────────────────────┘

INTUICIÓN:
- Al inicio, hay 1/3 de probabilidad de que el premio esté en
  la puerta elegida, y 2/3 de que esté en "las otras dos".
- El presentador revela una puerta vacía de "las otras dos".
- Esa información de 2/3 ahora se concentra en UNA sola puerta.
- Por eso cambiar tiene probabilidad 2/3.
""")


# ============================================================================
# VISUALIZACIÓN DE RESULTADOS
# ============================================================================
def mostrar_resultados(resultados: Dict[str, Dict], num_partidas: int):
    """Muestra los resultados de la simulación de forma profesional."""
    
    print("\n" + "=" * 60)
    print("RESULTADOS DE LA SIMULACIÓN")
    print("=" * 60)
    
    print(f"\nNúmero de partidas por estrategia: {num_partidas:,}")
    
    print("""
┌─────────────┬────────────┬────────────┬─────────────┬────────────┐
│ Estrategia  │ Victorias  │ Derrotas   │ P(ganar)    │ Esperado   │
├─────────────┼────────────┼────────────┼─────────────┼────────────┤""")
    
    for estrategia in ["mantener", "cambiar"]:
        r = resultados[estrategia]
        esperado = "33.33%" if estrategia == "mantener" else "66.67%"
        print(f"│ {estrategia.upper():<11} │ {r['victorias']:>10,} │ {r['derrotas']:>10,} │ {r['probabilidad']:>10.2%} │ {esperado:>10} │")
    
    print("└─────────────┴────────────┴────────────┴─────────────┴────────────┘")
    
    # Mostrar algunas partidas de ejemplo
    print("\n" + "─" * 60)
    print("EJEMPLO DE PARTIDAS (primeras 5 de cada estrategia)")
    print("─" * 60)
    
    for estrategia in ["mantener", "cambiar"]:
        print(f"\n{estrategia.upper()}:")
        for i, p in enumerate(resultados[estrategia]["partidas"][:5], 1):
            resultado = "[OK] GANO" if p.victoria else "[X] Perdio"
            print(f"  {i}. Premio={p.premio}, Eligió={p.eleccion_inicial}, "
                  f"Revelada={p.puerta_revelada}, Final={p.eleccion_final} → {resultado}")


# ============================================================================
# COMPARACIÓN CON CUÁNTICO
# ============================================================================
def preparar_comparacion():
    """Genera datos para comparar con la versión cuántica."""
    print("\n" + "=" * 60)
    print("VALORES DE REFERENCIA PARA COMPARACIÓN CUÁNTICA")
    print("=" * 60)
    print("""
┌─────────────────────────────────────────────────────────────┐
│                    MODELO CLÁSICO                           │
├─────────────────────────────────────────────────────────────┤
│ Mantener: P = 1/3 = 0.3333...                               │
│ Cambiar:  P = 2/3 = 0.6666...                               │
│                                                             │
│ DIFERENCIA CLAVE: Existe información clásica (el            │
│ presentador revela una puerta) que el jugador puede usar.   │
├─────────────────────────────────────────────────────────────┤
│                  MODELO CUÁNTICO                            │
├─────────────────────────────────────────────────────────────┤
│ Sin medición intermedia:                                    │
│   Mantener: P ≈ 0.33 (sin ventaja)                          │
│   Cambiar:  P ≈ 0.33 (sin ventaja)                          │
│   → La superposición impide obtener información útil        │
│                                                             │
│ Con medición intermedia:                                    │
│   Mantener: P ≈ 0.33                                        │
│   Cambiar:  P ≈ 0.67                                        │
│   → El colapso restaura el comportamiento clásico           │
└─────────────────────────────────────────────────────────────┘

CONCLUSIÓN:
La MEDICIÓN CUÁNTICA es lo que permite extraer información
del sistema. Sin ella, no hay ventaja estratégica posible.
""")


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "MONTY HALL - SIMULACIÓN CLÁSICA" + " " * 17 + "║")
    print("║" + " " * 15 + "Computación Cuántica y Natural" + " " * 13 + "║")
    print("╚" + "═" * 58 + "╝")
    
    # Explicación teórica
    explicar_probabilidades()
    
    # Simulación Monte Carlo
    NUM_PARTIDAS = 10000
    print(f"\nEjecutando simulación Monte Carlo ({NUM_PARTIDAS:,} partidas)...")
    resultados = simular_monte_carlo(NUM_PARTIDAS)
    
    # Mostrar resultados
    mostrar_resultados(resultados, NUM_PARTIDAS)
    
    # Comparación con cuántico
    preparar_comparacion()
    
    print("\n" + "=" * 60)
    print("SIMULACIÓN CLÁSICA COMPLETADA")
    print("=" * 60)
