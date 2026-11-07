# Componentes conexas de un grafo dirigido

Aplicación de escritorio en Python (Tkinter) que construye un **grafo dirigido** de *n* nodos (4 ≤ *n* ≤ 12), de forma **manual** o **aleatoria**, muestra su matriz de adyacencia y ejecuta **paso a paso** el algoritmo de **Kosaraju** para hallar sus componentes conexas (fuertemente conexas).

## Versión web

La carpeta `web/` contiene la misma aplicación en HTML + JavaScript (sin dependencias), publicada con Vercel desde este repositorio (`vercel.json` apunta a `web/`). Se puede abrir también localmente: `web/index.html`.

## Requisitos

**Python 3.10 o posterior** con **Tkinter** (incluido en la instalación habitual de Python para Windows; al instalar marque *Tcl/Tk and IDLE*). No necesita paquetes de `pip`.

## Ejecutar

```powershell
python main.py
```

(o `py main.py`; en VS Code también con **F5**, configuración *Componentes conexas*).

## Generar el ejecutable (.exe) en Windows

Haga doble clic en `construir_exe.bat`. Crea `dist\ComponentesConexas.exe`, que funciona sin tener Python instalado.

## Cómo usarlo

1. Escriba la cantidad de nodos (4 a 12).
2. Elija **Manual** (usted agrega aristas dirigidas *u → v*) o **Aleatorio** (el programa sortea un grafo distinto cada vez; «Generar otro grafo» crea uno nuevo).
3. Se muestran el grafo con flechas y la matriz de adyacencia (fila → columna). En modo manual pulse **Analizar grafo**.
4. Avance con **Siguiente →** / **← Anterior**, o use **▶ Reproducir**. **Ver resultado** salta al final.
5. Al terminar se muestra la solución: número de componentes, los nodos de cada una, aristas entre componentes y una verificación independiente. El grafo final se pinta con un color por componente.

### Qué se ve en cada fase

| Fase | Qué ocurre | Qué se dibuja |
| --- | --- | --- |
| 1 | DFS sobre G; cada vértice recibe su orden de finalización `f=k` | G, pila de recursión, aristas de árbol |
| 2 | DFS sobre Gᵀ (aristas invertidas) en orden inverso de finalización; cada árbol es una componente | Gᵀ, componentes ya completas |
| Resultado | Solución final | G con un color por componente |

> En un grafo dirigido, u y v están en la misma componente conexa si hay camino de u a v **y** de v a u. La solución también informa cuántas componentes *débilmente* conexas hay (ignorando el sentido de las aristas).

## Archivos

| Archivo | Función |
| --- | --- |
| `main.py` | Abre la aplicación. |
| `interfaz.py` | Pantallas, dibujo del grafo con flechas, matriz y navegación paso a paso. |
| `grafo.py` | Grafo dirigido, matriz de adyacencia y generación aleatoria. |
| `algoritmo.py` | Kosaraju paso a paso, componentes débiles y verificación independiente. |
| `tests/test_proyecto.py` | 14 pruebas (incluye comparación con fuerza bruta en 400 grafos aleatorios). |
| `construir_exe.bat` | Genera el ejecutable con PyInstaller. |
| `web/` | Versión web (Vercel): `algoritmo.js` (grafo y Kosaraju), `app.js` (interfaz), `index.html`. |
| `docs/` | Informe, diagrama de flujo y presentación. |

Pruebas:

```powershell
python -m unittest discover -s tests -v
```
