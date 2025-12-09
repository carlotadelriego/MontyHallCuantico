# CONFIGURACIÓN E IMPORTACIONES
import os
import numpy as np
from pyquil import Program
from pyquil.api import WavefunctionSimulator


# CONFIGURACIÓN DEL SIMULADOR
os.environ["QCS_SETTINGS_APPLICATIONS_QVM_URL"] = "http://127.0.0.1:15001"
os.environ["QUILC_URL"] = "tcp://127.0.0.1:5556"
sim = WavefunctionSimulator()


# ------------------------------------------------------
# - GENERACIÓN DEL ESTADO INICIAL
# Generamos estado inicial válido según:
# premio = superposición sobre 00,01,10
# jugador:
#   - mantener: |00>
#   - cambiar:  superposición |01> y |10>
# ------------------------------------------------------

def generar_estado_inicial(cambiar):
    """
    Representamos el estado como vector de tamaño 16 (2^4),
    ordenado como |q3 q2 q1 q0>.
    
    q3,q2 -> jugador
    q1,q0 -> premio
    """

    estado = np.zeros(16, dtype=complex)

    # Estados posibles para el premio
    premio_estados = ["00", "01", "10"]

    if cambiar:
        jugador_estados = ["01", "10"]
    else:
        jugador_estados = ["00"]

    # Amplitudes normales (igual para todos los estados)
    amplitud_premio = 1 / np.sqrt(3)
    amplitud_jugador = 1 / np.sqrt(len(jugador_estados))

    # Construimos el estado completo
    for p in premio_estados:
        for j in jugador_estados:
            # Formamos el estado completo como j+p
            bits = j + p
            pos = int(bits, 2)
            estado[pos] = amplitud_premio * amplitud_jugador

    return estado


def probabilidad_exito(estado_final):
    """
    Calcula probabilidad de éxito: jugador == premio
    """

    probs = np.abs(estado_final)**2
    exito = 0

    # Recorremos todas las probabilidades de los 16 estados
    for idx, prob in enumerate(probs):
        bits = format(idx, '04b')
        jugador = bits[:2]
        premio = bits[2:]

        # ignoramos estados 11
        if jugador == "11" or premio == "11":
            continue

        if jugador == premio:
            exito += prob

    return exito



# EJECUCIÓN DE LA SIMULACIÓN
def simular():
    # Creamos states como wavefunction "ficticia"
    estado_mantener = generar_estado_inicial(False)
    estado_cambiar   = generar_estado_inicial(True)

    prob_mantener = probabilidad_exito(estado_mantener)
    prob_cambiar  = probabilidad_exito(estado_cambiar)

    return prob_mantener, prob_cambiar



if __name__ == "__main__":
    p_mantener, p_cambiar = simular()

    print("----- RESULTADOS SIN MEDICIÓN INTERMEDIA -----")
    print(f"Probabilidad de éxito manteniendo: {p_mantener:.4f}")
    print(f"Probabilidad de éxito cambiando  : {p_cambiar:.4f}")
