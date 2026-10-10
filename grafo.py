"""Modelo de un grafo simple, no dirigido, con vértices numerados desde 1."""

from __future__ import annotations

class Grafo:
    def __init__(self, n: int):
        if isinstance(n, bool) or not isinstance(n, int) or not 4 <= n <= 12:
            raise ValueError("La cantidad de nodos debe ser un entero entre 4 y 12.")
        self.n = n
        self.adyacencia: dict[int, set[int]] = {i: set() for i in range(1, n + 1)}

    def _validar_extremos(self, u: int, v: int) -> None:
        if isinstance(u, bool) or isinstance(v, bool) or not isinstance(u, int) or not isinstance(v, int):
            raise ValueError("Los vértices deben ser enteros.")
        if not 1 <= u <= self.n or not 1 <= v <= self.n:
            raise ValueError(f"Los vértices deben estar entre 1 y {self.n}.")
        if u == v:
            raise ValueError("No se permiten lazos: elija dos vértices distintos.")

    def agregar_arista(self, u: int, v: int) -> bool:
        self._validar_extremos(u, v)
        if v in self.adyacencia[u]:
            return False
        self.adyacencia[u].add(v)
        self.adyacencia[v].add(u)
        return True

    def eliminar_arista(self, u: int, v: int) -> bool:
        self._validar_extremos(u, v)
        if v not in self.adyacencia[u]:
            return False
        self.adyacencia[u].remove(v)
        self.adyacencia[v].remove(u)
        return True

    def limpiar(self) -> None:
        for vecinos in self.adyacencia.values():
            vecinos.clear()

    def matriz_adyacencia(self) -> list[list[int]]:
        return [
            [int(v in self.adyacencia[u]) for v in range(1, self.n + 1)]
            for u in range(1, self.n + 1)
        ]

    def obtener_aristas(self) -> list[tuple[int, int]]:
        return [(u, v) for u in range(1, self.n + 1) for v in sorted(self.adyacencia[u]) if u < v]
