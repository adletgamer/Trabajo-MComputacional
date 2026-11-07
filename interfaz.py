"""Interfaz de escritorio (Tkinter) para explorar componentes conexas de un grafo dirigido."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox, ttk

from algoritmo import (
    FASE_DFS_G,
    FASE_DFS_TRANSPUESTO,
    FASE_RESULTADO,
    Paso,
    aristas_entre_componentes,
    componentes_debiles,
    componentes_fuertes_pasos,
    formatear_componente,
    verificar_componentes,
)
from grafo import N_MAX, N_MIN, Grafo

PALETA = ("#68bcc2", "#f3bd6e", "#b99add", "#e7a2a1", "#9bc77e", "#83a8df",
          "#e6a1c9", "#b5b56b", "#7fb0a0", "#d49b6a", "#9aa7e0", "#c2c2c2")
SIN_VISITAR = "#e8eef5"
EN_PILA = "#f4d778"
ACTUAL = "#f18a70"
TERMINADO = "#9fb8d6"
VISITADO_F2 = "#c7d5e5"
NOMBRE_FASE = {
    FASE_DFS_G: "Fase 1 · DFS sobre G (orden de finalización)",
    FASE_DFS_TRANSPUESTO: "Fase 2 · DFS sobre Gᵀ (una componente por árbol)",
    FASE_RESULTADO: "Resultado · grafo original con sus componentes",
}


class Aplicacion(tk.Tk):
    FONDO = "#f4f7fb"
    TEXTO = "#243247"
    AZUL = "#2764a5"
    GRIS = "#53657a"

    def __init__(self) -> None:
        super().__init__()
        self.title("Componentes conexas de un grafo dirigido | Matemática Computacional")
        self.geometry("1260x820")
        self.minsize(1000, 700)
        self.configure(bg=self.FONDO)
        self.grafo = Grafo(N_MIN)
        self.pasos: list[Paso] = []
        self.componentes: list[list[int]] = []
        self.indice = 0
        self.modo = ""
        self.auto_id: str | None = None
        self.n_var = tk.StringVar(value="8")
        self.u_var = tk.StringVar(value="1")
        self.v_var = tk.StringVar(value="2")
        self.titulo_grafo_var = tk.StringVar()
        self.info_grafo_var = tk.StringVar()
        self.aristas_var = tk.StringVar()
        self.fase_var = tk.StringVar()
        self.paso_var = tk.StringVar()
        self.pila_var = tk.StringVar()
        self.visitados_var = tk.StringVar()
        self.orden_var = tk.StringVar()
        self.componentes_var = tk.StringVar()
        self.contador_var = tk.StringVar()
        self._crear_portada()
        self._crear_area_trabajo()
        self._mostrar_portada()

    # ================================================================== construcción de pantallas
    def _boton(self, padre, texto, comando, principal=True, **kw):
        estilo = dict(bg=self.AZUL, fg="white", activebackground="#174b80", activeforeground="white") \
            if principal else dict(bg="#e6eef8", fg=self.AZUL, activebackground="#d4e4f5")
        return tk.Button(padre, text=texto, command=comando, relief="flat", cursor="hand2",
                         font=("Segoe UI", 12, "bold" if principal else "normal"), pady=9, **estilo, **kw)

    def _crear_portada(self) -> None:
        self.portada = tk.Frame(self, bg=self.FONDO)
        tarjeta = tk.Frame(self.portada, bg="white", padx=52, pady=38,
                           highlightbackground="#dce5ef", highlightthickness=1)
        tarjeta.place(relx=0.5, rely=0.48, anchor="center")
        tk.Label(tarjeta, text="Componentes conexas", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 25, "bold")).pack()
        tk.Label(tarjeta, text="de un grafo dirigido · algoritmo de Kosaraju", bg="white", fg=self.GRIS,
                 font=("Segoe UI", 11)).pack(pady=(2, 24))
        tk.Label(tarjeta, text=f"Modo manual: ¿cuántos nodos tendrá el grafo? ({N_MIN} a {N_MAX})", bg="white",
                 fg=self.TEXTO, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        fila = tk.Frame(tarjeta, bg="white")
        fila.pack(anchor="w", pady=(6, 20))
        self.n_spin = ttk.Spinbox(fila, from_=N_MIN, to=N_MAX, textvariable=self.n_var, width=6,
                                  font=("Segoe UI", 13), justify="center")
        self.n_spin.pack(side="left")
        tk.Label(fila, text="nodos", bg="white", fg=self.GRIS, font=("Segoe UI", 11)).pack(side="left", padx=8)
        tk.Label(tarjeta, text="¿Cómo quiere generar el grafo?", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self._boton(tarjeta, "Manual: definir las conexiones", self._iniciar_manual, width=34).pack(pady=(8, 2))
        tk.Label(tarjeta, text="Usted elige cada arista dirigida u → v", bg="white", fg="#64748b",
                 font=("Segoe UI", 10)).pack(pady=(0, 12))
        self._boton(tarjeta, "Aleatorio: generar automáticamente", self._iniciar_aleatorio, principal=False,
                    width=34).pack(pady=2)
        tk.Label(tarjeta, text=f"Sortea la cantidad de nodos ({N_MIN} a {N_MAX}) y las aristas: no hace falta ingresar nada", bg="white", fg="#64748b",
                 font=("Segoe UI", 10)).pack()

    def _crear_area_trabajo(self) -> None:
        self.area = tk.Frame(self, bg=self.FONDO)
        encabezado = tk.Frame(self.area, bg=self.FONDO, padx=20, pady=10)
        encabezado.pack(fill="x")
        tk.Button(encabezado, text="← Inicio", command=self._mostrar_portada, bg="#e6eef8", fg=self.AZUL,
                  relief="flat", cursor="hand2", font=("Segoe UI", 10), padx=12, pady=6).pack(side="right")
        tk.Label(encabezado, text="Componentes conexas de un grafo dirigido", bg=self.FONDO, fg=self.TEXTO,
                 font=("Segoe UI", 19, "bold")).pack(anchor="w")
        tk.Label(encabezado, text="Avance paso a paso por el algoritmo de Kosaraju (dos recorridos DFS).",
                 bg=self.FONDO, fg="#617085", font=("Segoe UI", 10)).pack(anchor="w")

        # El pie se reserva primero para que el lienzo expansible no lo recorte.
        pie = tk.Frame(self.area, bg="white", padx=20, pady=8,
                       highlightbackground="#dce5ef", highlightthickness=1)
        pie.pack(side="bottom", fill="x", padx=18, pady=(8, 12))
        cuerpo = tk.Frame(self.area, bg=self.FONDO, padx=18)
        cuerpo.pack(side="top", fill="both", expand=True)

        lateral = tk.Frame(cuerpo, bg="white", width=410, highlightbackground="#dce5ef", highlightthickness=1)
        lateral.pack(side="right", fill="y", padx=(12, 0))
        lateral.pack_propagate(False)
        marco_grafo = tk.Frame(cuerpo, bg="white", highlightbackground="#dce5ef", highlightthickness=1)
        marco_grafo.pack(side="left", fill="both", expand=True)

        # ---- zona del grafo
        cab = tk.Frame(marco_grafo, bg="white", padx=16, pady=8)
        cab.pack(fill="x")
        tk.Label(cab, textvariable=self.titulo_grafo_var, bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Label(cab, textvariable=self.info_grafo_var, bg="white", fg="#617085",
                 font=("Segoe UI", 9)).pack(side="right")
        leyenda = tk.Frame(marco_grafo, bg="white", padx=12, pady=4)
        leyenda.pack(side="bottom", fill="x")
        fila_estados = tk.Frame(leyenda, bg="white")
        fila_estados.pack(fill="x")
        for color, texto in ((SIN_VISITAR, "Sin visitar"), (EN_PILA, "En la pila DFS"), (ACTUAL, "Vértice actual"),
                             (TERMINADO, "Terminado (fase 1)"), (PALETA[0], "Componente (un color c/u)")):
            self._item_leyenda(fila_estados, color, texto)
        tk.Label(leyenda, text="Aristas:  ━ árbol DFS    ┄ ya visitada / fuera del árbol    coral = arista que se examina    "
                               "f=k: orden de finalización",
                 bg="white", fg="#617085", font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 0))
        self.lienzo = tk.Canvas(marco_grafo, bg="white", bd=0, highlightthickness=0)
        self.lienzo.pack(fill="both", expand=True, padx=12, pady=(0, 4))
        self.lienzo.bind("<Configure>", lambda _e: self._dibujar_grafo())

        # ---- panel lateral: construcción (manual) o regeneración (aleatorio)
        self.separador_top = tk.Frame(lateral, bg="white")
        self.separador_top.pack(fill="x")
        self.manual = tk.Frame(lateral, bg="white", padx=14, pady=10)
        tk.Label(self.manual, text="Construir el grafo", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        fila_arista = tk.Frame(self.manual, bg="white")
        fila_arista.pack(fill="x", pady=(0, 6))
        tk.Label(fila_arista, text="Arista", bg="white", fg=self.TEXTO).pack(side="left")
        self.u_combo = ttk.Combobox(fila_arista, textvariable=self.u_var, state="readonly", width=4)
        self.u_combo.pack(side="left", padx=(8, 4))
        tk.Label(fila_arista, text="→", bg="white", fg=self.TEXTO, font=("Segoe UI", 13, "bold")).pack(side="left")
        self.v_combo = ttk.Combobox(fila_arista, textvariable=self.v_var, state="readonly", width=4)
        self.v_combo.pack(side="left", padx=4)
        fila_botones = tk.Frame(self.manual, bg="white")
        fila_botones.pack(fill="x")
        ttk.Button(fila_botones, text="Agregar", command=self._agregar_arista).pack(side="left")
        ttk.Button(fila_botones, text="Quitar", command=self._quitar_arista).pack(side="left", padx=5)
        ttk.Button(fila_botones, text="Limpiar", command=self._limpiar).pack(side="left")
        ttk.Button(self.manual, text="Analizar grafo ▶", command=self._analizar).pack(fill="x", pady=(6, 0))
        tk.Label(self.manual, textvariable=self.aristas_var, bg="white", fg=self.GRIS, justify="left",
                 wraplength=375, font=("Segoe UI", 9)).pack(anchor="w", pady=(7, 0))

        self.aleatorio = tk.Frame(lateral, bg="white", padx=14, pady=10)
        tk.Label(self.aleatorio, text="Grafo aleatorio", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(self.aleatorio, text="La cantidad de nodos y las aristas se sortean en cada generación.", bg="white",
                 fg=self.GRIS, justify="left", wraplength=375).pack(anchor="w")
        fila_aleatorio = tk.Frame(self.aleatorio, bg="white")
        fila_aleatorio.pack(fill="x", pady=(8, 0))
        ttk.Button(fila_aleatorio, text="↻ Generar otro grafo", command=self._regenerar).pack(side="left")
        tk.Label(self.aleatorio, textvariable=self.aristas_var, bg="white", fg=self.GRIS, justify="left",
                 wraplength=375, font=("Segoe UI", 9)).pack(anchor="w", pady=(7, 0))

        self.sep = tk.Frame(lateral, bg="#e6ebf1", height=1)
        self.sep.pack(fill="x", padx=14, pady=5)
        tk.Label(lateral, text="Matriz de adyacencia  (fila → columna)", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 11, "bold"), padx=14).pack(anchor="w")
        marco_matriz = tk.Frame(lateral, bg="white")
        marco_matriz.pack(fill="x", padx=6, pady=(2, 0))
        marco_matriz.columnconfigure(0, weight=1)
        self.matriz_texto = tk.Text(marco_matriz, height=8, width=40, bg="white", fg="#344256",
                                    font=("Consolas", 9), relief="flat", padx=9, pady=4, wrap="none",
                                    state="disabled", takefocus=0)
        barra_v = ttk.Scrollbar(marco_matriz, orient="vertical", command=self.matriz_texto.yview)
        barra_h = ttk.Scrollbar(marco_matriz, orient="horizontal", command=self.matriz_texto.xview)
        self.matriz_texto.grid(row=0, column=0, sticky="nsew")
        barra_v.grid(row=0, column=1, sticky="ns")
        barra_h.grid(row=1, column=0, sticky="ew")
        self.matriz_texto.configure(yscrollcommand=barra_v.set, xscrollcommand=barra_h.set)

        tk.Frame(lateral, bg="#e6ebf1", height=1).pack(fill="x", padx=14, pady=5)
        tk.Label(lateral, text="Solución", bg="white", fg=self.TEXTO,
                 font=("Segoe UI", 11, "bold"), padx=14).pack(anchor="w")
        marco_res = tk.Frame(lateral, bg="white")
        marco_res.pack(fill="both", expand=True, padx=2, pady=(0, 6))
        self.resultado_texto = tk.Text(marco_res, height=6, bg="white", fg="#344256", font=("Segoe UI", 10),
                                       relief="flat", padx=12, pady=3, wrap="word", state="disabled",
                                       takefocus=0, cursor="arrow")
        barra_res = ttk.Scrollbar(marco_res, orient="vertical", command=self.resultado_texto.yview)
        self.resultado_texto.configure(yscrollcommand=barra_res.set)
        barra_res.pack(side="right", fill="y")
        self.resultado_texto.pack(side="left", fill="both", expand=True)

        # ---- pie: navegación y estado del algoritmo
        fila_pie = tk.Frame(pie, bg="white")
        fila_pie.pack(fill="x")
        tk.Label(fila_pie, textvariable=self.fase_var, bg="white", fg=self.AZUL,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(fila_pie, textvariable=self.contador_var, bg="white", fg="#617085").pack(side="right")
        nav = tk.Frame(fila_pie, bg="white")
        nav.pack(side="right", padx=22)
        self.inicio_btn = ttk.Button(nav, text="⏮", width=3, command=self._al_inicio)
        self.inicio_btn.pack(side="left")
        self.anterior_btn = ttk.Button(nav, text="← Anterior", command=self._anterior)
        self.anterior_btn.pack(side="left", padx=6)
        self.siguiente_btn = ttk.Button(nav, text="Siguiente →", command=self._siguiente)
        self.siguiente_btn.pack(side="left")
        self.auto_btn = ttk.Button(nav, text="▶ Reproducir", command=self._alternar_auto)
        self.auto_btn.pack(side="left", padx=6)
        self.final_btn = ttk.Button(nav, text="Ver resultado ⏭", command=self._final)
        self.final_btn.pack(side="left")
        tk.Label(pie, textvariable=self.paso_var, bg="white", fg=self.TEXTO, font=("Segoe UI", 11),
                 anchor="w", justify="left", wraplength=1100).pack(fill="x", pady=(5, 3))
        datos = tk.Frame(pie, bg="white")
        datos.pack(fill="x")
        for var in (self.pila_var, self.visitados_var, self.orden_var):
            tk.Label(datos, textvariable=var, bg="white", fg=self.GRIS, font=("Segoe UI", 9)).pack(
                side="left", padx=(0, 20))
        tk.Label(pie, textvariable=self.componentes_var, bg="white", fg=self.GRIS, font=("Segoe UI", 9),
                 wraplength=1100, justify="left").pack(anchor="w")

    def _item_leyenda(self, contenedor: tk.Frame, color: str, texto: str) -> None:
        elemento = tk.Frame(contenedor, bg="white")
        elemento.pack(side="left", padx=(0, 9))
        punto = tk.Canvas(elemento, width=14, height=14, bg="white", highlightthickness=0)
        punto.pack(side="left", padx=(0, 3))
        punto.create_oval(2, 2, 12, 12, fill=color, outline="#66788a")
        tk.Label(elemento, text=texto, bg="white", fg=self.GRIS, font=("Segoe UI", 8)).pack(side="left")

    # ================================================================== navegación entre pantallas
    def _mostrar_portada(self) -> None:
        self._detener_auto()
        self.area.pack_forget()
        self.portada.pack(fill="both", expand=True)

    def _mostrar_area(self) -> None:
        self.portada.pack_forget()
        self.area.pack(fill="both", expand=True)

    def _leer_n(self) -> int | None:
        texto = self.n_var.get().strip()
        if not texto.isdecimal() or not N_MIN <= int(texto) <= N_MAX:
            messagebox.showerror("Cantidad de nodos inválida",
                                 f"Ingrese un número entero entre {N_MIN} y {N_MAX}.")
            return None
        return int(texto)

    def _iniciar_manual(self) -> None:
        n = self._leer_n()
        if n is None:
            return
        self._detener_auto()
        self.modo = "manual"
        self.grafo = Grafo(n)
        self.aleatorio.pack_forget()
        self.manual.pack(fill="x", before=self.sep)
        self.u_var.set("1")
        self.v_var.set("2")
        self._grafo_modificado()
        self.paso_var.set("Agregue aristas dirigidas (u → v) y pulse «Analizar».")
        self._mostrar_area()

    def _iniciar_aleatorio(self) -> None:
        self._detener_auto()
        self.modo = "aleatorio"
        self.manual.pack_forget()
        self.aleatorio.pack(fill="x", before=self.sep)
        self.grafo = Grafo.generar_aleatorio_libre()
        self.n_var.set(str(self.grafo.n))
        self._grafo_modificado()
        self._analizar()
        self._mostrar_area()

    def _regenerar(self) -> None:
        self._detener_auto()
        self.grafo = Grafo.generar_aleatorio_libre()
        self.n_var.set(str(self.grafo.n))
        self._grafo_modificado()
        self._analizar()

    # ================================================================== edición manual
    def _extremos(self) -> tuple[int, int]:
        return int(self.u_var.get()), int(self.v_var.get())

    def _agregar_arista(self) -> None:
        try:
            u, v = self._extremos()
            cambio = self.grafo.agregar_arista(u, v)
        except ValueError as exc:
            messagebox.showerror("Arista inválida", str(exc))
            return
        if cambio:
            self._grafo_modificado()
        self.paso_var.set(f"Arista {u} → {v} agregada." if cambio else f"La arista {u} → {v} ya existe.")

    def _quitar_arista(self) -> None:
        try:
            u, v = self._extremos()
            cambio = self.grafo.eliminar_arista(u, v)
        except ValueError as exc:
            messagebox.showerror("Arista inválida", str(exc))
            return
        if cambio:
            self._grafo_modificado()
        self.paso_var.set(f"Arista {u} → {v} eliminada." if cambio else f"La arista {u} → {v} no existe.")

    def _limpiar(self) -> None:
        self.grafo.limpiar()
        self._grafo_modificado()
        self.paso_var.set("Se eliminaron todas las aristas.")

    def _grafo_modificado(self) -> None:
        """Descarta el análisis anterior y redibuja grafo, matriz y lista de aristas."""
        self._detener_auto()
        self.pasos, self.componentes, self.indice = [], [], 0
        valores = [str(i) for i in range(1, self.grafo.n + 1)]
        self.u_combo.configure(values=valores)
        self.v_combo.configure(values=valores)
        if self.u_var.get() not in valores:
            self.u_var.set("1")
        if self.v_var.get() not in valores:
            self.v_var.set("2")
        aristas = self.grafo.obtener_aristas()
        self.aristas_var.set("Aristas: " + (", ".join(f"{u}→{v}" for u, v in aristas) if aristas else "ninguna"))
        self.info_grafo_var.set(f"{self.grafo.n} vértices  ·  {len(aristas)} aristas dirigidas")
        self.titulo_grafo_var.set("Grafo G")
        self._escribir(self.matriz_texto, self._texto_matriz())
        self._escribir(self.resultado_texto, "Pulse «Analizar» o avance con «Siguiente» para ver la solución.")
        self.fase_var.set("")
        self.contador_var.set("")
        for var, texto in ((self.pila_var, "Pila DFS: —"), (self.visitados_var, "Visitados: —"),
                           (self.orden_var, "Orden de finalización: —"), (self.componentes_var, "Componentes: —")):
            var.set(texto)
        self._actualizar_botones()
        self._dibujar_grafo()

    def _texto_matriz(self) -> str:
        n = self.grafo.n
        lineas = ["     " + " ".join(f"{j:>2}" for j in range(1, n + 1)), "     " + "---" * n]
        for i, fila in enumerate(self.grafo.matriz_adyacencia(), 1):
            lineas.append(f"{i:>2} | " + " ".join(f"{x:>2}" for x in fila))
        return "\n".join(lineas)

    @staticmethod
    def _escribir(widget: tk.Text, texto: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", texto)
        widget.configure(state="disabled")

    # ================================================================== ejecución paso a paso
    def _analizar(self) -> None:
        self._detener_auto()
        self.pasos, self.componentes = componentes_fuertes_pasos(self.grafo)
        self.indice = 0
        self._mostrar_paso()

    def _al_inicio(self) -> None:
        self._detener_auto()
        if self.pasos:
            self.indice = 0
            self._mostrar_paso()

    def _anterior(self) -> None:
        self._detener_auto()
        if self.indice > 0:
            self.indice -= 1
            self._mostrar_paso()

    def _siguiente(self) -> None:
        self._detener_auto()
        if self.indice < len(self.pasos) - 1:
            self.indice += 1
            self._mostrar_paso()

    def _final(self) -> None:
        self._detener_auto()
        if self.pasos:
            self.indice = len(self.pasos) - 1
            self._mostrar_paso()

    def _alternar_auto(self) -> None:
        if self.auto_id is not None:
            self._detener_auto()
            return
        if not self.pasos:
            self._analizar()
        if self.indice >= len(self.pasos) - 1:
            self.indice = 0
            self._mostrar_paso()
        self.auto_btn.configure(text="⏸ Pausar")
        self.auto_id = self.after(650, self._tick_auto)

    def _tick_auto(self) -> None:
        self.auto_id = None
        if self.indice < len(self.pasos) - 1:
            self.indice += 1
            self._mostrar_paso()
            self.auto_id = self.after(650, self._tick_auto)
        else:
            self.auto_btn.configure(text="▶ Reproducir")

    def _detener_auto(self) -> None:
        if self.auto_id is not None:
            try:
                self.after_cancel(self.auto_id)
            except tk.TclError:
                pass
            self.auto_id = None
        if hasattr(self, "auto_btn"):
            self.auto_btn.configure(text="▶ Reproducir")

    def _mostrar_paso(self) -> None:
        paso = self.pasos[self.indice]
        self.fase_var.set(NOMBRE_FASE[paso.fase])
        self.titulo_grafo_var.set({FASE_DFS_G: "Grafo G", FASE_DFS_TRANSPUESTO: "Grafo transpuesto Gᵀ (aristas invertidas)",
                                   FASE_RESULTADO: "Grafo G con sus componentes"}[paso.fase])
        self.paso_var.set(paso.descripcion)
        self.contador_var.set(f"Paso {self.indice + 1} de {len(self.pasos)}")
        self.pila_var.set("Pila DFS: " + (" → ".join(map(str, paso.pila)) if paso.pila else "vacía"))
        self.visitados_var.set("Visitados: " + (", ".join(map(str, sorted(paso.visitados))) or "ninguno"))
        if paso.fase == FASE_DFS_TRANSPUESTO:
            self.orden_var.set("Por procesar (orden inverso): " + (", ".join(map(str, paso.pendientes)) or "—"))
        else:
            self.orden_var.set("Orden de finalización: " + (", ".join(map(str, paso.terminados)) or "—"))
        comps = " · ".join(f"C{i} {formatear_componente(c)}" for i, c in enumerate(paso.componentes_completas, 1))
        if paso.componente_actual:
            comps += (" · " if comps else "") + f"en construcción {formatear_componente(paso.componente_actual)}"
        self.componentes_var.set("Componentes: " + (comps or "ninguna aún"))
        if paso.fase == FASE_RESULTADO:
            self._escribir(self.resultado_texto, self._texto_solucion())
        else:
            self._escribir(self.resultado_texto, "La solución completa aparece al terminar la fase 2 "
                                                 "(use «Ver resultado» para saltar al final).")
        self._actualizar_botones()
        self._dibujar_grafo()

    def _texto_solucion(self) -> str:
        comps = self.componentes
        debiles = componentes_debiles(self.grafo)
        cruces = aristas_entre_componentes(self.grafo, comps)
        cert = verificar_componentes(self.grafo, comps)
        lineas = [f"Componentes conexas (fuertes): {len(comps)}"]
        lineas += [f"  C{i} = {formatear_componente(c)}" for i, c in enumerate(comps, 1)]
        lineas.append(f"Débilmente conexas (sin sentido): {len(debiles)}")
        if cruces:
            lineas.append("Aristas entre componentes: " + ", ".join(f"C{a}→C{b}" for a, b in cruces))
        else:
            lineas.append("No hay aristas entre componentes distintas.")
        lineas.append("Verificación (cierre transitivo): " + ("correcta ✓" if cert.valido else "¡inconsistente!"))
        return "\n".join(lineas)

    def _actualizar_botones(self) -> None:
        hay = bool(self.pasos)
        self.inicio_btn.configure(state="normal" if hay and self.indice > 0 else "disabled")
        self.anterior_btn.configure(state="normal" if hay and self.indice > 0 else "disabled")
        self.siguiente_btn.configure(state="normal" if hay and self.indice < len(self.pasos) - 1 else "disabled")
        self.final_btn.configure(state="normal" if hay and self.indice < len(self.pasos) - 1 else "disabled")

    # ================================================================== dibujo
    def _posiciones(self, ancho: int, alto: int) -> dict[int, tuple[float, float]]:
        n = self.grafo.n
        cx, cy = ancho / 2, alto / 2
        radio = max(60.0, min(ancho, alto) / 2 - 62)
        return {
            v: (cx + radio * math.cos(-math.pi / 2 + 2 * math.pi * (v - 1) / n),
                cy + radio * math.sin(-math.pi / 2 + 2 * math.pi * (v - 1) / n))
            for v in range(1, n + 1)
        }

    def _dibujar_grafo(self) -> None:
        lienzo = self.lienzo
        lienzo.delete("all")
        ancho, alto = lienzo.winfo_width(), lienzo.winfo_height()
        if ancho < 120 or alto < 120:
            return
        pos = self._posiciones(ancho, alto)
        radio_nodo = max(17.0, min(24.0, min(ancho, alto) * 0.05))
        paso = self.pasos[self.indice] if self.pasos else None
        fase = paso.fase if paso else FASE_DFS_G

        # ---- colores de los vértices
        grupo_de: dict[int, int] = {}
        if paso:
            for i, comp in enumerate(paso.componentes_completas):
                for v in comp:
                    grupo_de[v] = i
        colores = {v: SIN_VISITAR for v in pos}
        if paso and fase == FASE_DFS_G:
            for v in paso.terminados:
                colores[v] = TERMINADO
            for v in paso.pila:
                colores[v] = EN_PILA
        elif paso and fase == FASE_DFS_TRANSPUESTO:
            for v in paso.visitados:
                colores[v] = VISITADO_F2
            for v in paso.pila:
                colores[v] = EN_PILA
        if paso:
            for v, i in grupo_de.items():
                colores[v] = PALETA[i % len(PALETA)]
            if paso.actual is not None and fase != FASE_RESULTADO:
                colores[paso.actual] = ACTUAL

        # ---- aristas (en fase 2 se dibuja Gᵀ)
        aristas = self.grafo.obtener_aristas()
        if fase == FASE_DFS_TRANSPUESTO:
            aristas = [(v, u) for u, v in aristas]
        existentes = set(aristas)
        arbol = set(paso.arbol) if paso else set()
        for u, v in aristas:
            resaltada = bool(paso and paso.arista == (u, v))
            if fase == FASE_RESULTADO:
                misma = grupo_de.get(u) == grupo_de.get(v) and u in grupo_de
                color = PALETA[grupo_de[u] % len(PALETA)] if misma else "#8795a6"
                color = self._oscurecer(color) if misma else color
                ancho_l, dash = (2.6, ()) if misma else (1.6, (5, 3))
            elif resaltada:
                color, ancho_l, dash = "#e3715c", 4, ()
            elif (u, v) in arbol:
                color, ancho_l, dash = "#496c93", 2.6, ()
            else:
                color, ancho_l, dash = "#b9c4d0", 1.4, (4, 3)
            self._flecha(pos[u], pos[v], radio_nodo, color, ancho_l, dash, curva=(v, u) in existentes)

        # ---- vértices
        for v, (x, y) in pos.items():
            lienzo.create_oval(x - radio_nodo, y - radio_nodo, x + radio_nodo, y + radio_nodo,
                               fill=colores[v], outline="#40556b", width=2)
            lienzo.create_text(x, y, text=str(v), fill=self.TEXTO, font=("Segoe UI", 11, "bold"))
            if paso and fase != FASE_RESULTADO and v in paso.terminados:
                # Etiqueta hacia el exterior del círculo para no tapar aristas.
                dx, dy = x - ancho / 2, y - alto / 2
                norma = math.hypot(dx, dy) or 1
                lienzo.create_text(x + dx / norma * (radio_nodo + 16), y + dy / norma * (radio_nodo + 12),
                                   text=f"f={paso.terminados.index(v) + 1}", fill="#496c93",
                                   font=("Segoe UI", 9, "bold"))
            if paso and fase == FASE_RESULTADO and v in grupo_de:
                dx, dy = x - ancho / 2, y - alto / 2
                norma = math.hypot(dx, dy) or 1
                lienzo.create_text(x + dx / norma * (radio_nodo + 16), y + dy / norma * (radio_nodo + 12),
                                   text=f"C{grupo_de[v] + 1}", fill=self._oscurecer(PALETA[grupo_de[v] % len(PALETA)]),
                                   font=("Segoe UI", 10, "bold"))

    @staticmethod
    def _oscurecer(color: str, factor: float = 0.62) -> str:
        r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
        return "#%02x%02x%02x" % (int(r * factor), int(g * factor), int(b * factor))

    def _flecha(self, p, q, radio, color, grosor, dash, curva: bool) -> None:
        (x1, y1), (x2, y2) = p, q
        dx, dy = x2 - x1, y2 - y1
        largo = math.hypot(dx, dy) or 1
        ux, uy = dx / largo, dy / largo
        if curva:
            # Si existen u→v y v→u, cada una se curva hacia su lado para no solaparse.
            nx, ny = -uy, ux
            cx, cy = (x1 + x2) / 2 + nx * 0.16 * largo, (y1 + y2) / 2 + ny * 0.16 * largo
            ax, ay = cx - x1, cy - y1
            la = math.hypot(ax, ay) or 1
            bx, by = cx - x2, cy - y2
            lb = math.hypot(bx, by) or 1
            inicio = (x1 + ax / la * radio, y1 + ay / la * radio)
            fin = (x2 + bx / lb * (radio + 2), y2 + by / lb * (radio + 2))
            puntos = (*inicio, cx, cy, *fin)
            self.lienzo.create_line(*puntos, smooth=True, fill=color, width=grosor, dash=dash,
                                    arrow=tk.LAST, arrowshape=(11, 13, 5))
        else:
            self.lienzo.create_line(x1 + ux * radio, y1 + uy * radio, x2 - ux * (radio + 2), y2 - uy * (radio + 2),
                                    fill=color, width=grosor, dash=dash, arrow=tk.LAST, arrowshape=(11, 13, 5))
