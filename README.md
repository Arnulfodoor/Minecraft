# Minecraft test

Este proyecto es un demo básico en Python que permite colocar y eliminar bloques en un mundo 3D, con movimiento en primera persona y un menú de pausa. Está desarrollado con Panda3D.

## 🎮 Características

- Colocar bloques en un mundo 3D.
- Romper bloques existentes.
- Movimiento en primera persona con controles WASD.
- Mirar alrededor usando el mouse.
- Menú de pausa con opciones de Continuar y Salir.
- Crosshair en pantalla para apuntar mejor.

## ⬇️ Requisitos

- Python 3.8+
- Panda3D ≥ 1.10

**Archivos de recursos:**

- `block.egg` → modelo 3D de bloque  
- `dirt.png` → textura de bloque  
- `logo.ico` → ícono de la ventana  

## 🚀 Ejecución

Clonar el repositorio:

```bash
git clone https://github.com/arnulfodoor/minecraft.git
cd block-builder-demo
```


🕹 Controles
Tecla / Botón	Acción

W	Mover hacia adelante.

S	Mover hacia atrás.

A	Mover a la izquierda.

D	Mover a la derecha.

Mouse	Mirar alrededor.

Click izquierdo	Romper bloque.

Click derecho	Colocar bloque.

Escape	Pausar / Reanudar juego.

⚙️ Configuración
self.speed → velocidad de movimiento

self.sensitivity → sensibilidad del mouse

self.terrain_size → tamaño del área de bloques generada

self.terrain_scale y self.terrain_height → control de la altura y variación del terreno procedural
