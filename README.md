# Monty Hall Cuántico

Este repositorio contiene el desarrollo completo del proyecto final en el que se analiza el problema clásico de Monty Hall y su extensión al dominio cuántico. El objetivo es estudiar cómo la superposición cuántica y el colapso por medición alteran las estrategias óptimas del experimento.

---


## Descripción del problema

El experimento original plantea tres puertas:

- Una contiene un premio  
- Dos no contienen nada  

El jugador escoge una puerta y el presentador revela una puerta que no contiene premio. Finalmente, el jugador decide entre:

- Mantener su elección inicial  
- Cambiar a la otra puerta posible  

En el enfoque clásico, cambiar conduce a una probabilidad de éxito cercana a **2/3**, mientras que mantener se queda en aproximadamente **1/3**.

Este proyecto reformula el problema dentro del formalismo cuántico utilizando superposición y medición, lo que permite observar cómo cambia la estrategia óptima en función del momento en el que se obtiene información sobre el sistema.

---


## Representación cuántica

Las puertas se codifican mediante estados de dos qubits:

| Puerta | Representación |
|---------|----------------|
|    0    |     `|00⟩`     |
|    1    |     `|01⟩`     |
|    2    |     `|10⟩`     |

El premio se inicializa en superposición uniforme: |P⟩ = 1/sqrt(3) ( |00⟩ + |01⟩ + |10⟩ )


Se analizan dos versiones del experimento:

### 1. Sin medición intermedia

- El sistema se mantiene coherente hasta la medición final.
- No se colapsa la ubicación del premio de forma anticipada.
- Resultados experimentales:

| Estrategia | Probabilidad |
|------------|--------------|
|  Mantener  |    0.3333    |
|  Cambiar   |    0.3333    |

La ventaja clásica desaparece.

---

### 2. Con medición intermedia

- Se mide el registro del premio antes de la decisión final.
- La superposición colapsa.
- Resultados experimentales:

| Estrategia | Probabilidad |
|------------|--------------|
|  Mantener  |    0.3246    |
|  Cambiar   |    0.6617    |

Se recupera el comportamiento clásico.

---


## Estructura del repositorio

├── simulacion_clasica.py
├── simulacion_cuantica_pyquil.py
├── simulacion_cuantica_con_medicion.py
├── README.md


---


## Ejecución

### Requisitos previos

- Python 3.10+
- PyQuil instalado
- Simulador WavefunctionSimulator activo

Instalación típica: pip install pyquil
Simulación clásica: python3 simulacion_clasica.py
Simulación cuántica sin medición intermedia: python3 simulacion_cuantica_pyquil.py
Simulación cuántica con medición intermedia: python3 simulacion_cuantica_con_medicion.py

---


## Tabla comparativa final

|          Modelo         |   Estrategia  |  Probabilidad |
|-------------------------|---------------|---------------|
|          Clásico        |    Mantener   |     0.3379    |
|          Clásico        |    Cambiar    |     0.6654    |
| Cuántico sin medición   |    Mantener   |     0.3333    |
| Cuántico sin medicición |    Cambiar    |     0.3333    |
| Cuántico con medición   |    Mantener   |     0.3246    |
| Cuántico con medición   |    Cambiar    |     0.6617    |

---


## Conclusión

Cuando no existe medición intermedia, la elección del jugador no recibe información relevante y las probabilidades de éxito se igualan. Sin embargo, al medir previamente el estado del premio, el sistema colapsa y reaparece la ventaja estratégica de cambiar, coincidiendo con el modelo clásico.

Este proyecto evidencia de forma cuantitativa que **la medición es la responsable de modificar el estado físico del sistema y con ello la estrategia óptima**, mostrando una diferencia clara entre información clásica y cuántica.

