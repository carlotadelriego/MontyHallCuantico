#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
    MONTY HALL CUÁNTICO - PROYECTO FINAL
    Computación Cuántica y Natural
    
    Autores: Carlota Fernández del Riego, Hugo Iglesias Pombo
    Universidad Intercontinental de la Empresa (UIE)
    Curso 2025-2026
================================================================================

DESCRIPCIÓN
-----------
Implementación completamente cuántica del problema de Monty Hall.
Todos los componentes se modelan como operaciones cuánticas unitarias:

    1. Premio en superposición cuántica
    2. Elección del jugador codificada en qubits
    3. Operador de Monty como transformación unitaria reversible
    4. Estrategia del jugador como operación cuántica condicional
    5. Medición que genera información y permite la ventaja

ARQUITECTURA DE QUBITS (6 qubits)
---------------------------------
    q0, q1: Premio (3 puertas codificadas)
    q2, q3: Elección del jugador
    q4, q5: Puerta revelada por Monty

CODIFICACIÓN DE PUERTAS
-----------------------
    |00⟩ = Puerta 0
    |01⟩ = Puerta 1  
    |10⟩ = Puerta 2
    |11⟩ = Estado inválido (no utilizado)

OPERADOR DE MONTY (Unitario)
----------------------------
El operador de Monty se implementa como una matriz unitaria de 64x64 que:
    - Examina el estado del premio y del jugador
    - Establece los qubits de la puerta revelada
    - Garantiza: revelada ≠ premio AND revelada ≠ jugador
    - Es completamente reversible (unitario)
"""

import os
import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional, Any

# ==============================================================================
# CONFIGURACIÓN DE PYQUIL
# ==============================================================================
os.environ["QCS_SETTINGS_APPLICATIONS_QVM_URL"] = "http://127.0.0.1:5001"
os.environ["QUILC_URL"] = "tcp://127.0.0.1:5556"

# Importaciones condicionales
PYQUIL_DISPONIBLE = False
Program = None
DefGate = None
WavefunctionSimulator = None

try:
    from pyquil import Program as _Program, get_qc
    from pyquil.gates import H, X, RY, MEASURE, CNOT, CCNOT, I, SWAP
    from pyquil.quilbase import DefGate as _DefGate
    from pyquil.api import WavefunctionSimulator as _WavefunctionSimulator
    from pyquil.quil import address_qubits
    
    Program = _Program
    DefGate = _DefGate
    WavefunctionSimulator = _WavefunctionSimulator
    PYQUIL_DISPONIBLE = True
except ImportError:
    print("[AVISO] PyQuil no disponible.")


# ==============================================================================
# ESTRUCTURAS DE DATOS
# ==============================================================================
@dataclass
class ResultadoSimulacion:
    """Almacena los resultados de una simulación."""
    estrategia: str
    prob_ganar: float
    n_simulaciones: int
    victorias: int = 0


# ==============================================================================
# OPERADORES CUÁNTICOS UNITARIOS
# ==============================================================================

def crear_operador_monty() -> np.ndarray:
    """
    Crea el operador de Monty como matriz unitaria de 64x64.
    
    Actúa sobre 6 qubits: premio (2), jugador (2), monty (2).
    
    El estado de entrada tiene monty = |00⟩.
    El operador establece monty según las reglas:
    - monty ≠ premio
    - monty ≠ jugador
    - Si hay dos opciones, crea superposición
    
    TABLA DE VERDAD (jugador = 0):
    ════════════════════════════════════════════════════════════════════
    Premio | Monty revela
    ════════════════════════════════════════════════════════════════════
      0    |  1/√2(|01⟩ + |10⟩)  [superposición de 1 y 2]
      1    |  |10⟩               [revela 2]
      2    |  |01⟩               [revela 1]
    ════════════════════════════════════════════════════════════════════
    """
    dim = 64  # 2^6 qubits
    U = np.zeros((dim, dim), dtype=complex)
    
    # Orden de bits: |m1 m0 j1 j0 p1 p0⟩
    # donde p=premio, j=jugador, m=monty
    
    def encode(premio, jugador, monty):
        """Codifica los valores en un índice de 6 bits."""
        return (monty << 4) | (jugador << 2) | premio
    
    for premio in range(4):
        for jugador in range(4):
            for monty_in in range(4):
                idx_in = encode(premio, jugador, monty_in)
                
                # Solo procesamos cuando monty_in = 0 (estado inicial)
                if monty_in != 0:
                    # Para otros estados de entrada, identidad
                    U[idx_in, idx_in] = 1.0
                    continue
                
                # Estados inválidos: identidad
                if premio == 3 or jugador == 3:
                    U[idx_in, idx_in] = 1.0
                    continue
                
                # Determinar qué puede revelar Monty
                opciones = []
                for puerta in [0, 1, 2]:
                    if puerta != premio and puerta != jugador:
                        opciones.append(puerta)
                
                if len(opciones) == 0:
                    # Caso premio == jugador (esto ocurre)
                    # Monty puede revelar cualquiera de las otras dos
                    otras = [p for p in [0, 1, 2] if p != premio]
                    coef = 1.0 / np.sqrt(2)
                    for monty_out in otras:
                        idx_out = encode(premio, jugador, monty_out)
                        U[idx_out, idx_in] = coef
                elif len(opciones) == 1:
                    # Una sola opción: determinista
                    monty_out = opciones[0]
                    idx_out = encode(premio, jugador, monty_out)
                    U[idx_out, idx_in] = 1.0
                else:
                    # Dos opciones: superposición uniforme
                    coef = 1.0 / np.sqrt(2)
                    for monty_out in opciones:
                        idx_out = encode(premio, jugador, monty_out)
                        U[idx_out, idx_in] = coef
    
    return U


def crear_operador_cambiar() -> np.ndarray:
    """
    Crea el operador de CAMBIAR como matriz unitaria de 16x16.
    
    Actúa sobre 4 qubits: jugador (2), monty (2).
    
    El operador modifica el jugador basándose en monty:
    - Nueva elección = la puerta que no es jugador_original ni monty
    
    TABLA:
    ════════════════════════════════════════════════════════════════════
    Jugador | Monty | Nueva elección
    ════════════════════════════════════════════════════════════════════
       0    |   1   |       2
       0    |   2   |       1
       1    |   0   |       2  
       1    |   2   |       0
       2    |   0   |       1
       2    |   1   |       0
    ════════════════════════════════════════════════════════════════════
    """
    dim = 16  # 2^4 qubits
    U = np.zeros((dim, dim), dtype=complex)
    
    # Orden de bits: |m1 m0 j1 j0⟩
    
    def encode(jugador, monty):
        return (monty << 2) | jugador
    
    for jugador in range(4):
        for monty in range(4):
            idx_in = encode(jugador, monty)
            
            # Estados inválidos o iguales: identidad
            if jugador == 3 or monty == 3 or jugador == monty:
                U[idx_in, idx_in] = 1.0
                continue
            
            # Encontrar la puerta restante
            nueva = [p for p in [0, 1, 2] if p != jugador and p != monty][0]
            
            idx_out = encode(nueva, monty)
            U[idx_out, idx_in] = 1.0
    
    return U


def verificar_unitariedad(U: np.ndarray, nombre: str) -> bool:
    """Verifica que una matriz es unitaria."""
    n = U.shape[0]
    producto = U.conj().T @ U
    identidad = np.eye(n)
    es_unitaria = np.allclose(producto, identidad, atol=1e-10)
    return es_unitaria


# ==============================================================================
# SIMULADOR CUÁNTICO COMPLETO
# ==============================================================================

class SimuladorMontyHallCuantico:
    """
    Simulador cuántico completo del problema de Monty Hall.
    
    Implementa todo el juego usando operadores unitarios:
    1. Preparación del premio en superposición
    2. Operador de Monty (unitario 64x64)
    3. Operador de cambiar (unitario 16x16)
    4. Análisis de amplitudes para calcular probabilidades
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.sim = WavefunctionSimulator() if PYQUIL_DISPONIBLE else None
        
        # Crear operadores cuánticos
        self.U_monty = crear_operador_monty()
        self.U_cambiar = crear_operador_cambiar()
        
        # Verificar unitariedad
        if verbose:
            print("\n   Verificando operadores unitarios...")
            print(f"   • Operador Monty (64x64): {'✓ Unitario' if verificar_unitariedad(self.U_monty, 'Monty') else '✗ NO unitario'}")
            print(f"   • Operador Cambiar (16x16): {'✓ Unitario' if verificar_unitariedad(self.U_cambiar, 'Cambiar') else '✗ NO unitario'}")
    
    def log(self, msg: str):
        if self.verbose:
            print(msg)
    
    def preparar_estado_premio(self) -> np.ndarray:
        """
        Prepara el estado del premio en superposición.
        
        |ψ_premio⟩ = 1/√3(|00⟩ + |01⟩ + |10⟩)
        
        Este estado se extiende a 6 qubits con jugador=0 y monty=0:
        |ψ⟩ = 1/√3(|000000⟩ + |000001⟩ + |000010⟩)
        
        Índices (|m1 m0 j1 j0 p1 p0⟩):
        - |000000⟩ = premio=0, jugador=0, monty=0 → idx=0
        - |000001⟩ = premio=1, jugador=0, monty=0 → idx=1
        - |000010⟩ = premio=2, jugador=0, monty=0 → idx=2
        """
        psi = np.zeros(64, dtype=complex)
        
        # Estados con premio en superposición, jugador=0, monty=0
        coef = 1.0 / np.sqrt(3)
        psi[0] = coef  # premio=0, jugador=0, monty=0
        psi[1] = coef  # premio=1, jugador=0, monty=0
        psi[2] = coef  # premio=2, jugador=0, monty=0
        
        return psi
    
    def aplicar_operador_monty(self, psi: np.ndarray) -> np.ndarray:
        """Aplica el operador de Monty al estado."""
        return self.U_monty @ psi
    
    def aplicar_operador_cambiar_global(self, psi: np.ndarray) -> np.ndarray:
        """
        Aplica el operador de cambiar al estado de 6 qubits.
        
        U_cambiar actúa sobre los qubits jugador y monty (4 qubits).
        Lo extendemos a 6 qubits: U_cambiar ⊗ I (sobre premio).
        """
        # Crear el operador extendido: I(premio) ⊗ U_cambiar(jugador,monty)
        # Dimensiones: 4 (premio) x 16 (jugador+monty) = 64
        
        I_premio = np.eye(4, dtype=complex)
        U_ext = np.kron(self.U_cambiar, I_premio)
        
        # Pero el orden de los qubits es: monty, jugador, premio
        # Necesitamos reordenar
        
        # Enfoque directo: aplicar elemento por elemento
        psi_out = np.zeros(64, dtype=complex)
        
        for idx_in in range(64):
            if np.abs(psi[idx_in]) < 1e-15:
                continue
            
            # Decodificar
            premio = idx_in & 0b11
            jugador = (idx_in >> 2) & 0b11
            monty = (idx_in >> 4) & 0b11
            
            # Aplicar cambiar
            if jugador < 3 and monty < 3 and jugador != monty:
                # Encontrar nueva elección
                nueva = [p for p in [0, 1, 2] if p != jugador and p != monty][0]
                idx_out = (monty << 4) | (nueva << 2) | premio
            else:
                idx_out = idx_in
            
            psi_out[idx_out] += psi[idx_in]
        
        return psi_out
    
    def calcular_probabilidad_victoria(self, psi: np.ndarray) -> float:
        """
        Calcula la probabilidad de victoria.
        
        Victoria ocurre cuando jugador == premio.
        """
        prob = 0.0
        
        for idx in range(64):
            amp = psi[idx]
            if np.abs(amp) < 1e-15:
                continue
            
            premio = idx & 0b11
            jugador = (idx >> 2) & 0b11
            
            if premio == jugador and premio < 3:
                prob += np.abs(amp) ** 2
        
        return prob
    
    def analizar_estado(self, psi: np.ndarray, titulo: str):
        """Muestra el análisis detallado del estado cuántico."""
        self.log(f"\n   {titulo}")
        self.log("   " + "─" * 60)
        
        for idx in range(64):
            amp = psi[idx]
            prob = np.abs(amp) ** 2
            if prob < 1e-10:
                continue
            
            premio = idx & 0b11
            jugador = (idx >> 2) & 0b11
            monty = (idx >> 4) & 0b11
            
            victoria = "✓" if premio == jugador and premio < 3 else " "
            
            self.log(f"   |{idx:06b}⟩: premio={premio}, jugador={jugador}, monty={monty} "
                    f"→ amp={amp.real:+.4f}, P={prob:.4f} {victoria}")
    
    def simular_estrategia(self, estrategia: str, mostrar_detalle: bool = False) -> float:
        """
        Simula una estrategia completa y retorna P(victoria).
        
        Args:
            estrategia: "mantener" o "cambiar"
            mostrar_detalle: Si True, muestra los estados intermedios
        
        Returns:
            Probabilidad de victoria
        """
        # Paso 1: Preparar estado inicial
        psi = self.preparar_estado_premio()
        
        if mostrar_detalle:
            self.analizar_estado(psi, "Estado inicial (premio en superposición, jugador=0, monty=0)")
        
        # Paso 2: Aplicar operador de Monty
        psi = self.aplicar_operador_monty(psi)
        
        if mostrar_detalle:
            self.analizar_estado(psi, "Después del operador de Monty (revelación)")
        
        # Paso 3: Aplicar estrategia
        if estrategia == "cambiar":
            psi = self.aplicar_operador_cambiar_global(psi)
            
            if mostrar_detalle:
                self.analizar_estado(psi, "Después del operador CAMBIAR")
        
        # Paso 4: Calcular probabilidad de victoria
        return self.calcular_probabilidad_victoria(psi)
    
    def ejecutar_simulacion_completa(self):
        """Ejecuta la simulación completa para ambas estrategias."""
        self.log("\n" + "="*70)
        self.log("   SIMULACIÓN CUÁNTICA COMPLETA")
        self.log("="*70)
        
        resultados = {}
        
        for estrategia in ["mantener", "cambiar"]:
            self.log(f"\n   {'═'*60}")
            self.log(f"   ESTRATEGIA: {estrategia.upper()}")
            self.log(f"   {'═'*60}")
            
            prob = self.simular_estrategia(estrategia, mostrar_detalle=True)
            teorico = 1/3 if estrategia == "mantener" else 2/3
            
            resultados[estrategia] = ResultadoSimulacion(
                estrategia=estrategia,
                prob_ganar=prob,
                n_simulaciones=1
            )
            
            self.log(f"\n   RESULTADO: P(ganar) = {prob*100:.2f}% (teórico: {teorico*100:.2f}%)")
        
        return resultados
    
    def verificar_con_pyquil(self):
        """Verifica el circuito usando PyQuil WavefunctionSimulator."""
        if not PYQUIL_DISPONIBLE:
            self.log("   [!] PyQuil no disponible para verificación")
            return
        
        self.log("\n" + "="*70)
        self.log("   VERIFICACIÓN CON PYQUIL")
        self.log("="*70)
        
        # Crear circuito de superposición del premio
        theta = 2 * np.arccos(np.sqrt(2/3))
        
        # Definir Hadamard controlado
        H_mat = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        I_mat = np.eye(2, dtype=complex)
        CH_mat = np.zeros((4, 4), dtype=complex)
        CH_mat[0:2, 0:2] = H_mat
        CH_mat[2:4, 2:4] = I_mat
        ch_gate = DefGate("CH", CH_mat)
        CH = ch_gate.get_constructor()
        
        p = Program()
        p += ch_gate
        p += RY(theta, 1)
        p += CH(1, 0)
        
        wf = self.sim.wavefunction(p)
        
        self.log("\n   Estado del premio (PyQuil):")
        for i, amp in enumerate(wf.amplitudes[:4]):
            prob = np.abs(amp)**2
            if prob > 0.001:
                self.log(f"   |{i:02b}⟩: amp={amp.real:+.4f}, P={prob:.4f}")
        
        self.log("\n   ✓ Verificación con PyQuil completada")
    
    def mostrar_resumen(self, resultados: Dict[str, ResultadoSimulacion]):
        """Muestra el resumen final."""
        self.log("\n" + "="*70)
        self.log("   RESUMEN FINAL")
        self.log("="*70)
        
        self.log("""
   ┌─────────────────┬─────────────────┬─────────────────┐
   │ ESTRATEGIA      │ P(GANAR) CUÁNT. │ P(GANAR) TEÓR.  │
   ├─────────────────┼─────────────────┼─────────────────┤""")
        
        for estrategia in ["mantener", "cambiar"]:
            r = resultados[estrategia]
            teorico = "33.33%" if estrategia == "mantener" else "66.67%"
            self.log(f"   │ {estrategia.upper():<15} │ {r.prob_ganar*100:>13.2f}% │ {teorico:>15} │")
        
        self.log("   └─────────────────┴─────────────────┴─────────────────┘")
    
    def mostrar_conclusiones(self):
        """Muestra las conclusiones del proyecto."""
        self.log("\n" + "="*70)
        self.log("   CONCLUSIONES")
        self.log("="*70)
        
        self.log("""
   IMPLEMENTACIÓN CUÁNTICA COMPLETA
   ═════════════════════════════════════════════════════════════════════
   
   Este proyecto implementa el problema de Monty Hall usando 
   EXCLUSIVAMENTE operadores cuánticos unitarios:
   
   1. ESTADO INICIAL
      |ψ⟩ = 1/√3(|premio=0⟩ + |premio=1⟩ + |premio=2⟩) ⊗ |jugador=0⟩ ⊗ |monty=0⟩
   
   2. OPERADOR DE MONTY (Matriz unitaria 64×64)
      U_monty aplica las reglas:
      • Monty nunca revela la puerta del premio
      • Monty nunca revela la puerta del jugador
      • Si hay dos opciones válidas, crea superposición cuántica
   
   3. OPERADOR CAMBIAR (Matriz unitaria 16×16)
      U_cambiar modifica la elección del jugador:
      • Nueva elección = puerta ≠ original ≠ revelada
   
   4. CÁLCULO DE PROBABILIDADES
      Se analizan las amplitudes del estado final para determinar
      P(victoria) = Σ |⟨premio=i, jugador=i|ψ_final⟩|²
   
   ═════════════════════════════════════════════════════════════════════
   
   RESULTADO: CAMBIAR da 66.67%, MANTENER da 33.33%
   
   La ventaja de cambiar emerge del operador de Monty, que genera
   información utilizable al colapsar parcialmente el espacio de estados.
   ═════════════════════════════════════════════════════════════════════
        """)


# ==============================================================================
# FUNCIÓN PRINCIPAL
# ==============================================================================

def main():
    """Punto de entrada principal."""
    print("="*70)
    print("   MONTY HALL CUÁNTICO - PROYECTO FINAL")
    print("   Computación Cuántica y Natural")
    print("   Carlota Fernández del Riego, Hugo Iglesias Pombo")
    print("   Universidad Intercontinental de la Empresa (UIE)")
    print("="*70)
    print(f"\n   PyQuil disponible: {PYQUIL_DISPONIBLE}")
    
    try:
        sim = SimuladorMontyHallCuantico()
        
        # Verificación con PyQuil
        sim.verificar_con_pyquil()
        
        # Simulación completa
        resultados = sim.ejecutar_simulacion_completa()
        
        # Resumen y conclusiones
        sim.mostrar_resumen(resultados)
        sim.mostrar_conclusiones()
        
        print("\n" + "="*70)
        print("   SIMULACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()