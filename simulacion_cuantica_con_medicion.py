import random
import numpy as np


def jugar_monty_cuantico_con_medicion(cambiar: bool) -> bool:
    """
    Simula Monty Hall cuántico cuando se mide el premio antes
    de que el jugador decida cambiar o mantener.
    """

    # 1. Inicialmente el premio está en superposición real pero aquí realizamos la medición (colapso)
    # Por lo tanto, el resultado es equiprobable entre las 3 puertas
    premio = random.choice([0, 1, 2])

    # El jugador empieza eligiendo puerta 0
    eleccion = 0

    # El presentador revela una puerta distinta de la elegida y sin premio
    opciones = [0, 1, 2]
    opciones.remove(eleccion)

    if premio in opciones:
        opciones.remove(premio)

    puerta_revelada = random.choice(opciones)

    # 2. Estrategia del jugador
    if cambiar:
        opciones_restantes = [0, 1, 2]
        opciones_restantes.remove(eleccion)
        opciones_restantes.remove(puerta_revelada)
        eleccion = opciones_restantes[0]  # pasa a la otra puerta

    # 3. Resultado tras el colapso
    return eleccion == premio



def simular(n=5000):
    victorias_mantener = 0
    victorias_cambiar = 0

    for _ in range(n):
        if jugar_monty_cuantico_con_medicion(False):
            victorias_mantener += 1
        if jugar_monty_cuantico_con_medicion(True):
            victorias_cambiar += 1

    p_mantener = victorias_mantener / n
    p_cambiar = victorias_cambiar / n
    return p_mantener, p_cambiar



if __name__ == "__main__":
    p1, p2 = simular(10000)

    print("----- RESULTADOS CUÁNTICOS CON MEDICIÓN -----")
    print(f"Probabilidad de éxito manteniendo: {p1:.4f}")
    print(f"Probabilidad de éxito cambiando:   {p2:.4f}")
