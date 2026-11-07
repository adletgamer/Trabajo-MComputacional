"""Modelo de un grafo dirigido simple con vértices numerados desde 1."""

from __future__ import annotations

import random

N_MIN = 4
N_MAX = 12


class Grafo:
    """Grafo dirigido sin lazos ni aristas repetidas.

    ``adyacencia[u]`` contiene los sucesores de ``u``: la arista u → v existe
    si y solo si ``v in adyacencia[u]``.
    """

    def __init__(self, n: int):
        if isinstance(n, bool) or not isinstance(n, int) or not N_MIN <= n <= N_MAX:
            raise ValueError(f"La cantidad de nodos debe ser un entero entre {N_MIN} y {N_MAX}.")
        self.n = n
        self.adyacencia: dict[int, set[int]] = {i: set() for i in range(1, n + 1)}

    # ------------------------------------------------------------------ validación
    def _validar_extremos(self, u: int, v: int) -> None:
        if isinstance(u, bool) or isinstance(v, bool) or not isinstance(u, int) or not isinstance(v, int):
            raise ValueError("Los vértices deben ser enteros.")
        if not 1 <= u <= self.n or not 1 <= v <= self.n:
            raise ValueError(f"Los vértices deben estar entre 1 y {self.n}.")
        if u == v:
            raise ValueError("No se permiten lazos: elija dos vértices distintos.")

    # ------------------------------------------------------------------ edición
    def agregar_arista(self, u: int, v: int) -> bool:
        """Agrega u → v. Devuelve False si ya existía."""
        self._validar_extremos(u, v)
        if v in self.adyacencia[u]:
            return False
        self.adyacencia[u].add(v)
        return True

    def eliminar_arista(self, u: int, v: int) -> bool:
        """Quita u → v. Devuelve False si no existía."""
        self._validar_extremos(u, v)
        if v not in self.adyacencia[u]:
            return False
        self.adyacencia[u].remove(v)
        return True

    def limpiar(self) -> None:
        for sucesores in self.adyacencia.values():
            sucesores.clear()

    # ------------------------------------------------------------------ consultas
    def tiene_arista(self, u: int, v: int) -> bool:
        return v in self.adyacencia[u]

    def sucesores(self, u: int) -> list[int]:
        return sorted(self.adyacencia[u])

    def predecesores(self, v: int) -> list[int]:
        return sorted(u for u in self.adyacencia if v in self.adyacencia[u])

    def obtener_aristas(self) -> list[tuple[int, int]]:
        """Lista ordenada de aristas dirigidas (u, v) que representan u → v."""
        return [(u, v) for u in range(1, self.n + 1) for v in sorted(self.adyacencia[u])]

    def matriz_adyacencia(self) -> list[list[int]]:
        """A[i-1][j-1] = 1 si existe la arista i → j (no es simétrica en general)."""
        return [
            [int(v in self.adyacencia[u]) for v in range(1, self.n + 1)]
            for u in range(1, self.n + 1)
        ]

    # ------------------------------------------------------------------ generación
    @classmethod
    def generar_aleatorio(cls, n: int, rng: random.Random | None = None) -> "Grafo":
        """Grafo dirigido aleatorio (entre n y ~1.6n aristas sorteadas al azar).

        Cada llamada produce un grafo distinto (si no se pasa ``rng`` se usa un
        generador nuevo sembrado por el sistema). Para que la demostración sea
        ilustrativa se descartan, hasta 50 veces, los sorteos cuyo resultado es
        poco ilustrativo: una sola componente, o menos de 3 vértices dentro de
        componentes con ciclos.
        """
        rng = rng or random.Random()
        pares = [(u, v) for u in range(1, n + 1) for v in range(1, n + 1) if u != v]
        minimo = max(4, n)
        maximo = min(len(pares), max(minimo, round(1.6 * n)))
        grafo = cls(n)
        for _ in range(50):
            grafo = cls(n)
            for u, v in rng.sample(pares, rng.randint(minimo, maximo)):
                grafo.agregar_arista(u, v)
            if grafo._es_interesante():
                break
        return grafo

    def _es_interesante(self) -> bool:
        """Al menos 2 componentes fuertes y >= 3 vértices en componentes de tamaño >= 2."""
        alcanza = {}
        for origen in self.adyacencia:
            vistos, pila = {origen}, [origen]
            while pila:
                x = pila.pop()
                for y in self.adyacencia[x]:
                    if y not in vistos:
                        vistos.add(y)
                        pila.append(y)
            alcanza[origen] = vistos
        grupos = {frozenset(w for w in alcanza[v] if v in alcanza[w]) for v in alcanza}
        return len(grupos) >= 2 and sum(len(g) for g in grupos if len(g) >= 2) >= 3
