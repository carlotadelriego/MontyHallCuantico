# importar librerías necesarias
import random

def jugar_montyhall(cambiar: bool) -> bool:
    """
    Simula una partida del problema clásico de Monty Hall con 3 puertas.
    Devuelve True si el jugador gana el premio, False si no.
    """
    premio = random.randint(0, 2)       # puerta donde está el premio
    eleccion = random.randint(0, 2)     # puerta que elige el jugador

    # El presentador abre una puerta distinta a la del jugador y sin premio
    opciones = [0, 1, 2]
    opciones.remove(eleccion)
    if premio in opciones:
        opciones.remove(premio)
    puerta_abierta = random.choice(opciones)

    if cambiar:
        # El jugador cambia a la única puerta que queda cerrada
        opciones = [0, 1, 2]
        opciones.remove(eleccion)
        opciones.remove(puerta_abierta)
        eleccion = opciones[0]

    return eleccion == premio


def simular(num_partidas: int = 1000) -> tuple[float, float]:
    """
    Ejecuta muchas partidas para estimar las probabilidades de éxito
    manteniendo y cambiando.
    """
    victorias_mantener = 0
    victorias_cambiar = 0

    for _ in range(num_partidas):
        if jugar_montyhall(cambiar=False):
            victorias_mantener += 1
        if jugar_montyhall(cambiar=True):
            victorias_cambiar += 1

    prob_mantener = victorias_mantener / num_partidas
    prob_cambiar = victorias_cambiar / num_partidas
    return prob_mantener, prob_cambiar


if __name__ == "__main__":
    partidas = 10000
    p_mantener, p_cambiar = simular(partidas)
    print(f"Número de partidas: {partidas}")
    print(f"Probabilidad de ganar manteniendo: {p_mantener:.4f}")
    print(f"Probabilidad de ganar cambiando:   {p_cambiar:.4f}")
