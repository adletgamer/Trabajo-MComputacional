# Componentes conexas de un grafo

Programa en Python para crear un grafo y ver, paso a paso, cómo el algoritmo BFS encuentra sus componentes conexas.

## Antes de empezar

Necesitas **Python 3.10 o posterior**, **Tkinter** y **VS Code**. Tkinter viene con la instalación habitual de Python para Windows. Este proyecto **no necesita paquetes de `pip`**.

Si vas a instalar Python, asegúrate de incluir **Tcl/Tk and IDLE** y la opción para agregar Python al `PATH`. En VS Code, instala la extensión **Python**.

## Abrir y ejecutar el programa en VS Code

1. Abre en VS Code la carpeta que contiene `main.py`.
2. Abre una terminal desde **Terminal > New Terminal**. Los siguientes comandos son para **PowerShell en Windows**.
3. Comprueba que Python está disponible:

   ```powershell
   python --version
   ```

   Si Windows no reconoce `python`, prueba `py --version` y usa `py` en el siguiente comando.

4. Crea un entorno virtual dentro de la carpeta del proyecto:

   ```powershell
   python -m venv .venv
   ```

5. Comprueba que Tkinter funciona:

   ```powershell
   .\.venv\Scripts\python.exe -m tkinter
   ```

   Debe aparecer una pequeña ventana de prueba. Ciérrala para continuar. Si aparece un error relacionado con `tkinter` o `init.tcl`, reinstala Python incluyendo **Tcl/Tk and IDLE** y vuelve a crear `.venv`.

6. Ejecuta la aplicación:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

No necesitas activar `.venv` ni instalar nada con `pip`. Para volver a abrir el programa otro día, solo abre esta carpeta y repite el comando del paso 6.

También puedes usar **F5** en VS Code: selecciona `.venv\Scripts\python.exe` con **Python: Select Interpreter** y elige la configuración **Componentes conexas**.

## Cómo usarlo

Al abrir, elige **Crear mi grafo** o **Ver demo de 10 nodos**.

- **Crear mi grafo:** indica entre 4 y 12 nodos, pulsa **Crear**, añade conexiones entre dos nodos y pulsa **Analizar**. **Quitar** permite corregir una conexión.
- **Ver demo de 10 nodos:** con un clic carga un grafo con tres componentes: una componente de seis nodos con ciclos, un triángulo y un nodo aislado. La demostración avanza automáticamente; **Anterior** o **Siguiente** detienen la reproducción y permiten explorar los pasos a mano.

Al terminar, aparece un certificado que comprueba que todos los vértices quedaron agrupados, que cada grupo tiene un árbol BFS y que no hay aristas que unan grupos diferentes. Las aristas sólidas forman el bosque BFS; las discontinuas pertenecen al grafo, pero no hicieron falta para descubrir nuevos vértices.

## Qué hace cada archivo

| Archivo | Función |
| --- | --- |
| `main.py` | Abre la aplicación. |
| `interfaz.py` | Muestra las pantallas, el grafo, la matriz y los pasos. |
| `grafo.py` | Guarda los nodos y conexiones; calcula la matriz de adyacencia. |
| `algoritmo.py` | Ejecuta BFS y registra cada paso. |
| `tests/test_proyecto.py` | Comprueba el grafo y el resultado del algoritmo. |
| `INVESTIGACION_BFS.md` | Resume la teoría, los proyectos revisados y el aporte diferencial. |

Para ejecutar las pruebas, si lo deseas:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
