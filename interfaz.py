"""Interfaz de escritorio para explorar componentes conexas con BFS."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox, ttk

from algoritmo import (
    Paso,
    componentes_conexas_pasos,
    formatear_componente,
    verificar_componentes,
)
from grafo import Grafo


class Aplicacion(tk.Tk):
    FONDO = "#f4f7fb"
    TEXTO = "#243247"
    AZUL = "#2764a5"

    def __init__(self) -> None:
        super().__init__()
        self.title("Componentes conexas | Matemática Computacional")
        self.geometry("1120x760")
        self.minsize(940, 650)
        self.configure(bg=self.FONDO)
        self.grafo = Grafo(6)
        self.pasos: list[Paso] = []
        self.componentes: list[list[int]] = []
        self.indice = 0
        self.modo = ""
        self.demo_after_id: str | None = None
        self.n_var = tk.StringVar(value="6")
        self.u_var = tk.StringVar(value="1")
        self.v_var = tk.StringVar(value="2")
        self.estado_var = tk.StringVar()
        self.paso_var = tk.StringVar()
        self.cola_var = tk.StringVar(value="Cola: —")
        self.visitados_var = tk.StringVar(value="Visitados: —")
        self.componentes_var = tk.StringVar(value="Componentes: —")
        self.contador_var = tk.StringVar()
        self.info_grafo_var = tk.StringVar(value="")
        self._layout_cache_key: tuple | None = None
        self._layout_cache: dict[int, tuple[float, float]] = {}
        self._crear_portada()
        self._crear_area_trabajo()
        self._mostrar_portada()

    def _crear_portada(self) -> None:
        self.portada = tk.Frame(self, bg=self.FONDO)
        tarjeta = tk.Frame(self.portada, bg="white", padx=48, pady=38,
                           highlightbackground="#dce5ef", highlightthickness=1)
        tarjeta.place(relx=0.5, rely=0.48, anchor="center")
        tk.Label(tarjeta, text="Componentes conexas", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 25, "bold")).pack(pady=(0, 8))
        tk.Label(tarjeta, text="Elija cómo quiere comenzar", bg="white", fg="#53657a",
                 font=("Segoe UI", 12)).pack(pady=(0, 28))
        tk.Button(tarjeta, text="Crear mi grafo", command=self._iniciar_manual, width=28,
                  bg=self.AZUL, fg="white", activebackground="#174b80",
                  activeforeground="white", relief="flat", cursor="hand2",
                  font=("Segoe UI", 12, "bold"), pady=10).pack(pady=4)
        tk.Label(tarjeta, text="Definir nodos y conexiones", bg="white", fg="#64748b",
                 font=("Segoe UI", 10)).pack(pady=(0, 17))
        tk.Button(tarjeta, text="Ver demo de 10 nodos", command=self._iniciar_demo, width=28,
                  bg="#e6eef8", fg=self.AZUL, activebackground="#d4e4f5",
                  relief="flat", cursor="hand2", font=("Segoe UI", 12), pady=10).pack(pady=4)
        tk.Label(tarjeta, text="Se ejecuta automáticamente paso a paso", bg="white", fg="#64748b",
                 font=("Segoe UI", 10)).pack()

    def _crear_area_trabajo(self) -> None:
        self.area = tk.Frame(self, bg=self.FONDO)
        encabezado = tk.Frame(self.area, bg=self.FONDO, padx=20, pady=12)
        encabezado.pack(fill="x")
        tk.Button(encabezado, text="← Inicio", command=self._mostrar_portada,
                  bg="#e6eef8", fg=self.AZUL, relief="flat", cursor="hand2",
                  font=("Segoe UI", 10), padx=12, pady=6).pack(side="right")
        tk.Label(encabezado, text="Componentes conexas", bg=self.FONDO,
                 fg=self.TEXTO, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(encabezado, text="Explore cómo BFS recorre el grafo paso a paso.",
                 bg=self.FONDO, fg="#617085", font=("Segoe UI", 10)).pack(anchor="w")

        cuerpo = tk.Frame(self.area, bg=self.FONDO, padx=18)
        cuerpo.pack(fill="both", expand=True)
        lateral = tk.Frame(cuerpo, bg="white", width=352,
                           highlightbackground="#dce5ef", highlightthickness=1)
        lateral.pack(side="right", fill="y", padx=(12, 0))
        lateral.pack_propagate(False)
        marco_grafo = tk.Frame(cuerpo, bg="white", highlightbackground="#dce5ef",
                               highlightthickness=1)
        marco_grafo.pack(side="left", fill="both", expand=True)
        encabezado_grafo = tk.Frame(marco_grafo, bg="white", padx=16, pady=10)
        encabezado_grafo.pack(fill="x")
        tk.Label(encabezado_grafo, text="Grafo", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(encabezado_grafo, textvariable=self.info_grafo_var, bg="white", fg="#617085",
                 font=("Segoe UI", 9)).pack(side="right", padx=(0, 12))
        leyenda = tk.Frame(marco_grafo, bg="white", padx=12, pady=5)
        leyenda.pack(side="bottom", fill="x")
        fila_estados = tk.Frame(leyenda, bg="white")
        fila_estados.pack(fill="x")
        self._item_leyenda(fila_estados, "#e8eef5", "Sin visitar")
        self._item_leyenda(fila_estados, "#f4d778", "En cola")
        self._item_leyenda(fila_estados, "#f18a70", "Actual")
        self._item_leyenda(fila_estados, "#c7d5e5", "Visitado")
        self._item_leyenda(fila_estados, "#68bcc2", "Componente completa")
        tk.Label(leyenda, text="Aristas: ━ árbol BFS    ┄ fuera del árbol    coral: arista que se revisa",
                 bg="white", fg="#617085", font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 0))
        self.lienzo = tk.Canvas(marco_grafo, bg="white", bd=0, highlightthickness=0)
        self.lienzo.pack(fill="both", expand=True, padx=12, pady=(0, 4))
        self.lienzo.bind("<Configure>", lambda _evento: self._dibujar_grafo())

        # Panel manual: solo lo necesario para construir y corregir un grafo.
        self.manual = tk.Frame(lateral, bg="white", padx=14, pady=10)
        self.manual.pack(fill="x")
        tk.Label(self.manual, text="Crear grafo", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))
        fila_n = tk.Frame(self.manual, bg="white")
        fila_n.pack(fill="x", pady=(0, 7))
        tk.Label(fila_n, text="Nodos (4–12)", bg="white", fg=self.TEXTO).pack(side="left")
        ttk.Entry(fila_n, textvariable=self.n_var, width=5).pack(side="left", padx=8)
        ttk.Button(fila_n, text="Crear", command=self._crear_grafo).pack(side="right")
        fila_arista = tk.Frame(self.manual, bg="white")
        fila_arista.pack(fill="x", pady=(0, 7))
        tk.Label(fila_arista, text="Conectar", bg="white", fg=self.TEXTO).pack(side="left")
        self.u_combo = ttk.Combobox(fila_arista, textvariable=self.u_var, state="readonly", width=4)
        self.u_combo.pack(side="left", padx=(7, 4))
        tk.Label(fila_arista, text="con", bg="white", fg=self.TEXTO).pack(side="left")
        self.v_combo = ttk.Combobox(fila_arista, textvariable=self.v_var, state="readonly", width=4)
        self.v_combo.pack(side="left", padx=4)
        fila_botones = tk.Frame(self.manual, bg="white")
        fila_botones.pack(fill="x")
        ttk.Button(fila_botones, text="Agregar", command=self._agregar_arista).pack(side="left")
        ttk.Button(fila_botones, text="Quitar", command=self._quitar_arista).pack(side="left", padx=6)
        ttk.Button(fila_botones, text="Analizar", command=self._ejecutar).pack(side="right")

        self.demo_info = tk.Frame(lateral, bg="white", padx=14, pady=12)
        tk.Label(self.demo_info, text="Demo de 10 nodos", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 5))
        tk.Label(self.demo_info, text="Tres grupos: uno con ciclos, un triángulo y un nodo aislado.",
                  bg="white", fg="#53657a",
                  justify="left", wraplength=310).pack(anchor="w")

        self.separador = tk.Frame(lateral, bg="#e6ebf1", height=1)
        self.separador.pack(fill="x", padx=14, pady=7)
        tk.Label(lateral, text="Matriz de adyacencia", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 12, "bold"), padx=14).pack(anchor="w")
        matriz_marco = tk.Frame(lateral, bg="white")
        matriz_marco.pack(fill="x", padx=6, pady=(2, 0))
        matriz_marco.columnconfigure(0, weight=1)
        self.matriz_texto = tk.Text(matriz_marco, height=7, width=40, bg="white", fg="#344256",
                                    font=("Consolas", 9), relief="flat", padx=9, pady=5,
                                    wrap="none", state="disabled", takefocus=0)
        barra_matriz = ttk.Scrollbar(matriz_marco, orient="vertical", command=self.matriz_texto.yview)
        barra_horizontal = ttk.Scrollbar(matriz_marco, orient="horizontal", command=self.matriz_texto.xview)
        self.matriz_texto.grid(row=0, column=0, sticky="nsew")
        barra_matriz.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")
        self.matriz_texto.configure(yscrollcommand=barra_matriz.set, xscrollcommand=barra_horizontal.set)

        pie = tk.Frame(self.area, bg="white", padx=20, pady=10,
                       highlightbackground="#dce5ef", highlightthickness=1)
        pie.pack(fill="x", padx=18, pady=(9, 14))
        fila_pie = tk.Frame(pie, bg="white")
        fila_pie.pack(fill="x")
        tk.Label(fila_pie, text="Recorrido BFS", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Label(fila_pie, textvariable=self.contador_var, bg="white",
                 fg="#617085").pack(side="right")
        navegacion = tk.Frame(fila_pie, bg="white")
        navegacion.pack(side="right", padx=24)
        self.anterior_btn = ttk.Button(navegacion, text="← Anterior", command=self._anterior)
        self.anterior_btn.pack(side="left")
        self.siguiente_btn = ttk.Button(navegacion, text="Siguiente →", command=self._siguiente)
        self.siguiente_btn.pack(side="left", padx=8)
        self.final_btn = ttk.Button(navegacion, text="Ver resultado", command=self._final)
        self.final_btn.pack(side="left")
        tk.Label(pie, textvariable=self.paso_var, bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 11), anchor="w", justify="left",
                 wraplength=880).pack(fill="x", pady=(6, 3))
        datos_paso = tk.Frame(pie, bg="white")
        datos_paso.pack(anchor="w")
        tk.Label(datos_paso, textvariable=self.cola_var, bg="white", fg="#53657a").pack(side="left")
        tk.Label(datos_paso, textvariable=self.visitados_var, bg="white", fg="#53657a").pack(side="left", padx=(22, 0))
        tk.Label(pie, textvariable=self.componentes_var, bg="white", fg="#53657a",
                 wraplength=880, justify="left").pack(anchor="w")
        self._actualizar_botones()
        # Reservar primero el pie evita que el lienzo expansible lo recorte.
        cuerpo.pack_forget()
        pie.pack_forget()
        pie.pack(side="bottom", fill="x", padx=18, pady=(9, 14))
        cuerpo.pack(side="top", fill="both", expand=True)

    def _mostrar_portada(self) -> None:
        self._detener_demo()
        self.area.pack_forget()
        self.portada.pack(fill="both", expand=True)

    def _mostrar_area(self) -> None:
        self.portada.pack_forget()
        self.area.pack(fill="both", expand=True)

    def _iniciar_manual(self) -> None:
        self._detener_demo()
        self.modo = "manual"
        self.grafo = Grafo(6)
        self.n_var.set("6")
        self.demo_info.pack_forget()
        self.manual.pack(fill="x", before=self.separador)
        self._invalidar_pasos()
        self.estado_var.set("Agregue conexiones y pulse Analizar.")
        self.paso_var.set(self.estado_var.get())
        self._actualizar_grafo_y_matriz()
        self._mostrar_area()

    def _iniciar_demo(self) -> None:
        self._detener_demo()
        self.modo = "demo"
        self.grafo = Grafo(10)
        aristas_demo = (
            (1, 2), (1, 3), (2, 4), (2, 5), (3, 4), (3, 5), (4, 6), (5, 6),
            (7, 8), (8, 9), (7, 9),
        )
        for u, v in aristas_demo:
            self.grafo.agregar_arista(u, v)
        self.n_var.set("10")
        self.manual.pack_forget()
        self.demo_info.pack(fill="x", before=self.separador)
        self._invalidar_pasos()
        self._actualizar_grafo_y_matriz()
        self._ejecutar()
        self._mostrar_area()
        self._programar_paso_demo()

    def _crear_grafo(self) -> None:
        texto = self.n_var.get().strip()
        try:
            if not texto.isdecimal():
                raise ValueError("Ingrese un número entero entre 4 y 12.")
            self.grafo = Grafo(int(texto))
        except ValueError as exc:
            messagebox.showerror("Cantidad de nodos inválida", str(exc))
            return
        self._invalidar_pasos()
        self.estado_var.set(f"Grafo de {self.grafo.n} nodos. Agregue conexiones.")
        self.paso_var.set(self.estado_var.get())
        self._actualizar_grafo_y_matriz()

    def _extremos(self) -> tuple[int, int]:
        return int(self.u_var.get()), int(self.v_var.get())

    def _agregar_arista(self) -> None:
        try:
            u, v = self._extremos()
            cambio = self.grafo.agregar_arista(u, v)
        except ValueError as exc:
            messagebox.showerror("Conexión inválida", str(exc))
            return
        self.estado_var.set(f"Conexión {u}–{v} agregada." if cambio else "Esa conexión ya existe.")
        if cambio:
            self._invalidar_pasos()
            self._actualizar_grafo_y_matriz()
        self.paso_var.set(self.estado_var.get())

    def _quitar_arista(self) -> None:
        try:
            u, v = self._extremos()
            cambio = self.grafo.eliminar_arista(u, v)
        except ValueError as exc:
            messagebox.showerror("Conexión inválida", str(exc))
            return
        self.estado_var.set(f"Conexión {u}–{v} eliminada." if cambio else "Esa conexión no existe.")
        if cambio:
            self._invalidar_pasos()
            self._actualizar_grafo_y_matriz()
        self.paso_var.set(self.estado_var.get())

    def _invalidar_pasos(self) -> None:
        self.pasos = []
        self.componentes = []
        self.indice = 0
        self.paso_var.set("Agregue conexiones y pulse Analizar." if self.modo == "manual" else "")
        self.cola_var.set("Cola: —")
        self.visitados_var.set("Visitados: —")
        self.componentes_var.set("Componentes: —")
        self.contador_var.set("")
        self._actualizar_botones()

    def _ejecutar(self) -> None:
        self._detener_demo()
        self.pasos, self.componentes = componentes_conexas_pasos(self.grafo)
        self.indice = 0
        self._mostrar_paso()

    def _anterior(self) -> None:
        self._detener_demo()
        if self.indice > 0:
            self.indice -= 1
            self._mostrar_paso()

    def _siguiente(self) -> None:
        self._detener_demo()
        if self.indice < len(self.pasos) - 1:
            self.indice += 1
            self._mostrar_paso()

    def _final(self) -> None:
        self._detener_demo()
        if self.pasos:
            self.indice = len(self.pasos) - 1
            self._mostrar_paso()

    def _mostrar_paso(self) -> None:
        paso = self.pasos[self.indice]
        self.paso_var.set(paso.descripcion)
        self.cola_var.set("Cola: " + (" → ".join(map(str, paso.cola)) if paso.cola else "vacía"))
        self.visitados_var.set("Visitados: " + (", ".join(map(str, sorted(paso.visitados))) if paso.visitados else "ninguno"))
        texto = " · ".join(
            f"C{i} {formatear_componente(c)}" for i, c in enumerate(paso.componentes_completas, 1)
        )
        self.componentes_var.set("Componentes: " + (texto or "ninguna"))
        self.contador_var.set(f"Paso {self.indice + 1} de {len(self.pasos)}")
        if self.indice == len(self.pasos) - 1:
            certificado = verificar_componentes(self.grafo, self.componentes, paso.arboles_bfs)
            if certificado.valido:
                aristas_arbol = sum(len(arbol) for arbol in paso.arboles_bfs)
                self.paso_var.set(
                    f"Certificado: {self.grafo.n} vértices cubiertos, "
                    f"{aristas_arbol} aristas de árbol = n−c ({self.grafo.n}−{len(self.componentes)}), "
                    f"y {len(certificado.aristas_cruzadas)} aristas entre grupos."
                )
            else:
                self.paso_var.set("La comprobación del resultado encontró una inconsistencia.")
            self.estado_var.set(f"Resultado: {len(self.componentes)} componente(s) conexa(s).")
        self._actualizar_botones()
        self._dibujar_grafo()

    def _actualizar_botones(self) -> None:
        self.anterior_btn.configure(state="normal" if self.pasos and self.indice > 0 else "disabled")
        self.siguiente_btn.configure(state="normal" if self.pasos and self.indice < len(self.pasos) - 1 else "disabled")
        self.final_btn.configure(state="normal" if self.pasos and self.indice < len(self.pasos) - 1 else "disabled")

    def _actualizar_grafo_y_matriz(self) -> None:
        valores = [str(i) for i in range(1, self.grafo.n + 1)]
        self.u_combo.configure(values=valores)
        self.v_combo.configure(values=valores)
        if self.u_var.get() not in valores:
            self.u_var.set("1")
        if self.v_var.get() not in valores:
            self.v_var.set("2")
        ancho = 2
        lineas = ["    " + " ".join(f"{i:>{ancho}}" for i in range(1, self.grafo.n + 1))]
        for i, fila in enumerate(self.grafo.matriz_adyacencia(), 1):
            lineas.append(f"{i:>2}  " + " ".join(f"{valor:>{ancho}}" for valor in fila))
        self.matriz_texto.configure(state="normal")
        self.matriz_texto.delete("1.0", "end")
        self.matriz_texto.insert("1.0", "\n".join(lineas))
        self.matriz_texto.configure(state="disabled")
        self.info_grafo_var.set(
            f"{self.grafo.n} vértices  ·  {len(self.grafo.obtener_aristas())} aristas"
        )
        self._dibujar_grafo()

    def _dibujar_grafo(self) -> None:
        self.lienzo.delete("all")
        ancho, alto = self.lienzo.winfo_width(), self.lienzo.winfo_height()
        if ancho < 80 or alto < 80:
            return
        posiciones = self._obtener_posiciones(ancho, alto)
        paso = self.pasos[self.indice] if self.pasos else None
        paleta = ("#68bcc2", "#f3bd6e", "#b99add", "#e7a2a1", "#9bc77e", "#83a8df")
        colores = {i: "#e8eef5" for i in posiciones}
        if paso:
            for numero, componente in enumerate(paso.componentes_completas):
                for nodo in componente:
                    colores[nodo] = paleta[numero % len(paleta)]
            for nodo in paso.visitados:
                if colores[nodo] == "#e8eef5":
                    colores[nodo] = "#c7d5e5"
            for nodo in paso.cola:
                if colores[nodo] == "#e8eef5" or colores[nodo] == "#c7d5e5":
                    colores[nodo] = "#f4d778"
            if paso.actual is not None:
                colores[paso.actual] = "#f18a70"
        aristas_arbol = set()
        if paso:
            for arbol in paso.arboles_bfs:
                aristas_arbol.update((min(u, v), max(u, v)) for u, v in arbol)
            aristas_arbol.update((min(u, v), max(u, v)) for u, v in paso.arbol_actual)
        for u, v in self.grafo.obtener_aristas():
            resaltada = bool(paso and paso.arista and {u, v} == set(paso.arista))
            x1, y1 = posiciones[u]
            x2, y2 = posiciones[v]
            es_arbol = (u, v) in aristas_arbol
            self.lienzo.create_line(x1, y1, x2, y2,
                                    fill="#e3715c" if resaltada else ("#496c93" if es_arbol else "#c2ccd7"),
                                    width=4 if resaltada else (2.5 if es_arbol else 1.5),
                                    dash=() if es_arbol or resaltada else (4, 3))
        for nodo, (x, y) in posiciones.items():
            radio_nodo = max(18, min(25, min(ancho, alto) * 0.045))
            self.lienzo.create_oval(x - radio_nodo, y - radio_nodo,
                                    x + radio_nodo, y + radio_nodo,
                                    fill=colores[nodo], outline="#40556b", width=2)
            self.lienzo.create_text(x, y, text=str(nodo), fill=self.TEXTO,
                                    font=("Segoe UI", 11, "bold"))

    def _item_leyenda(self, contenedor: tk.Frame, color: str, texto: str) -> None:
        elemento = tk.Frame(contenedor, bg="white")
        elemento.pack(side="left", padx=(0, 8))
        punto = tk.Canvas(elemento, width=14, height=14, bg="white", highlightthickness=0)
        punto.pack(side="left", padx=(0, 3))
        punto.create_oval(2, 2, 12, 12, fill=color, outline="#66788a")
        tk.Label(elemento, text=texto, bg="white", fg="#53657a",
                 font=("Segoe UI", 8)).pack(side="left")

    def _obtener_posiciones(self, ancho: int, alto: int) -> dict[int, tuple[float, float]]:
        aristas = tuple(self.grafo.obtener_aristas())
        clave = (self.grafo.n, aristas, tuple(tuple(c) for c in self.componentes), ancho, alto)
        if clave == self._layout_cache_key:
            return self._layout_cache

        # Tras el análisis, cada componente ocupa su propia zona para distinguir
        # los grupos sin que los vértices se amontonen en el centro del lienzo.
        if self.componentes:
            columnas_grupo = (1 if len(self.componentes) == 1 else
                              max(1, math.ceil(math.sqrt(len(self.componentes) * ancho / alto))))
            filas_grupo = math.ceil(len(self.componentes) / columnas_grupo)
            margen_x, margen_y = 54, 38
            celda_x = (ancho - 2 * margen_x) / columnas_grupo
            celda_y = (alto - 2 * margen_y) / filas_grupo
            resultado: dict[int, tuple[float, float]] = {}
            for indice, componente in enumerate(self.componentes):
                columna, fila = indice % columnas_grupo, indice // columnas_grupo
                centro_x = margen_x + (columna + 0.5) * celda_x
                centro_y = margen_y + (fila + 0.5) * celda_y
                cantidad = len(componente)
                columnas_nodo = min(cantidad, max(1, math.ceil(math.sqrt(cantidad * celda_x / celda_y))))
                filas_nodo = math.ceil(cantidad / columnas_nodo)
                paso_x = min(76, (celda_x - 58) / max(1, columnas_nodo - 1)) if columnas_nodo > 1 else 0
                paso_y = min(76, (celda_y - 58) / max(1, filas_nodo - 1)) if filas_nodo > 1 else 0
                inicio_x = centro_x - paso_x * (columnas_nodo - 1) / 2
                inicio_y = centro_y - paso_y * (filas_nodo - 1) / 2
                for orden, nodo in enumerate(componente):
                    col_nodo, fila_nodo = orden % columnas_nodo, orden // columnas_nodo
                    resultado[nodo] = (inicio_x + col_nodo * paso_x,
                                       inicio_y + fila_nodo * paso_y)
            self._layout_cache_key, self._layout_cache = clave, resultado
            return resultado

        # Distribución de resortes determinista: atrae vecinos y separa vértices.
        posiciones = {
            nodo: [0.82 * math.cos(-math.pi / 2 + 2 * math.pi * (nodo - 1) / self.grafo.n),
                   0.82 * math.sin(-math.pi / 2 + 2 * math.pi * (nodo - 1) / self.grafo.n)]
            for nodo in range(1, self.grafo.n + 1)
        }
        ideal = math.sqrt(4.0 / self.grafo.n)
        iteraciones = 100
        temperatura = 0.12
        for iteracion in range(iteraciones):
            desplazamiento = {nodo: [0.0, 0.0] for nodo in posiciones}
            for u in posiciones:
                for v in posiciones:
                    if u >= v:
                        continue
                    dx = posiciones[u][0] - posiciones[v][0]
                    dy = posiciones[u][1] - posiciones[v][1]
                    distancia = max(math.hypot(dx, dy), 0.01)
                    fuerza = ideal * ideal / distancia
                    fx, fy = dx / distancia * fuerza, dy / distancia * fuerza
                    desplazamiento[u][0] += fx
                    desplazamiento[u][1] += fy
                    desplazamiento[v][0] -= fx
                    desplazamiento[v][1] -= fy
            for u, v in aristas:
                dx = posiciones[u][0] - posiciones[v][0]
                dy = posiciones[u][1] - posiciones[v][1]
                distancia = max(math.hypot(dx, dy), 0.01)
                fuerza = distancia * distancia / ideal
                fx, fy = dx / distancia * fuerza, dy / distancia * fuerza
                desplazamiento[u][0] -= fx
                desplazamiento[u][1] -= fy
                desplazamiento[v][0] += fx
                desplazamiento[v][1] += fy
            temperatura_iteracion = temperatura * (1 - iteracion / iteraciones)
            for nodo in posiciones:
                dx, dy = desplazamiento[nodo]
                dx -= posiciones[nodo][0] * 0.035
                dy -= posiciones[nodo][1] * 0.035
                magnitud = max(math.hypot(dx, dy), 0.01)
                movimiento = min(magnitud, temperatura_iteracion)
                posiciones[nodo][0] += dx / magnitud * movimiento
                posiciones[nodo][1] += dy / magnitud * movimiento
                posiciones[nodo][0] = max(-1.5, min(1.5, posiciones[nodo][0]))
                posiciones[nodo][1] = max(-1.5, min(1.5, posiciones[nodo][1]))

        min_x = min(p[0] for p in posiciones.values())
        max_x = max(p[0] for p in posiciones.values())
        min_y = min(p[1] for p in posiciones.values())
        max_y = max(p[1] for p in posiciones.values())
        espacio_x, espacio_y = ancho - 100, alto - 100
        escala_normal = min(espacio_x / max(max_x - min_x, 0.1),
                           espacio_y / max(max_y - min_y, 0.1))
        escala_girada = min(espacio_x / max(max_y - min_y, 0.1),
                           espacio_y / max(max_x - min_x, 0.1))
        if escala_girada > escala_normal:
            posiciones = {nodo: [-p[1], p[0]] for nodo, p in posiciones.items()}
            min_x = min(p[0] for p in posiciones.values())
            max_x = max(p[0] for p in posiciones.values())
            min_y = min(p[1] for p in posiciones.values())
            max_y = max(p[1] for p in posiciones.values())
        margen = 42
        escala = min((ancho - 2 * margen) / max(max_x - min_x, 0.1),
                     (alto - 2 * margen) / max(max_y - min_y, 0.1))
        cx, cy = ancho / 2, alto / 2
        resultado = {
            nodo: (cx + (p[0] - (min_x + max_x) / 2) * escala,
                   cy + (p[1] - (min_y + max_y) / 2) * escala)
            for nodo, p in posiciones.items()
        }
        self._layout_cache_key = clave
        self._layout_cache = resultado
        return resultado

    def _programar_paso_demo(self) -> None:
        if self.modo == "demo" and self.indice < len(self.pasos) - 1:
            self.demo_after_id = self.after(300, self._avanzar_demo)

    def _avanzar_demo(self) -> None:
        self.demo_after_id = None
        if self.modo != "demo" or self.indice >= len(self.pasos) - 1:
            return
        self.indice += 1
        self._mostrar_paso()
        self._programar_paso_demo()

    def _detener_demo(self) -> None:
        if self.demo_after_id is not None:
            try:
                self.after_cancel(self.demo_after_id)
            except tk.TclError:
                pass
            self.demo_after_id = None
