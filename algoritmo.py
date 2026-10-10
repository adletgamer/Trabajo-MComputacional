"""BFS propio para encontrar componentes conexas y registrar sus pasos."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from grafo import Grafo


@dataclass(frozen=True)
class Paso:
    descripcion: str
    visitados: frozenset[int]
    cola: tuple[int, ...]
    actual: int | None
    componente_actual: tuple[int, ...]
    componentes_completas: tuple[tuple[int, ...], ...]
    arista: tuple[int, int] | None = None
    arbol_actual: tuple[tuple[int, int], ...] = ()
    arboles_bfs: tuple[tuple[tuple[int, int], ...], ...] = ()


@dataclass(frozen=True)
class CertificadoComponentes:
    vertices_cubiertos: bool
    arboles_conexos: bool
    aristas_cruzadas: tuple[tuple[int, int], ...]

    @property
    def valido(self) -> bool:
        return self.vertices_cubiertos and self.arboles_conexos and not self.aristas_cruzadas


def componentes_conexas_pasos(grafo: Grafo) -> tuple[list[Paso], list[list[int]]]:
    visitados: set[int] = set()
    componentes: list[list[int]] = []
    pasos: list[Paso] = []
    arboles_bfs: list[list[tuple[int, int]]] = []
    cola: deque[int] = deque()
    componente: list[int] = []
    arbol_actual: list[tuple[int, int]] = []

    def guardar(descripcion: str, actual: int | None = None, arista: tuple[int, int] | None = None) -> None:
        pasos.append(Paso(
            descripcion=descripcion,
            visitados=frozenset(visitados),
            cola=tuple(cola),
            actual=actual,
            componente_actual=tuple(componente),
            componentes_completas=tuple(tuple(c) for c in componentes),
            arista=arista,
            arbol_actual=tuple(arbol_actual),
            arboles_bfs=tuple(tuple(arbol) for arbol in arboles_bfs),
        ))

    guardar("Estado inicial: aún no se ha visitado ningún vértice.")
    for inicio in range(1, grafo.n + 1):
        if inicio in visitados:
            continue
        componente = []
        arbol_actual = []
        cola.append(inicio)
        visitados.add(inicio)
        guardar(f"Se inicia una nueva componente desde el vértice {inicio}.", inicio)
        while cola:
            actual = cola.popleft()
            componente.append(actual)
            guardar(f"Se extrae el vértice {actual} de la cola y se procesa.", actual)
            for vecino in sorted(grafo.adyacencia[actual]):
                arista = (actual, vecino)
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)
                    arbol_actual.append(arista)
                    guardar(f"Se examina {actual}–{vecino}: se descubre {vecino} y entra en la cola.", actual, arista)
                else:
                    guardar(f"Se examina {actual}–{vecino}: {vecino} ya estaba descubierto.", actual, arista)
        componentes.append(componente.copy())
        arboles_bfs.append(arbol_actual.copy())
        guardar(f"Componente {len(componentes)} completa: {formatear_componente(componente)}.")
    guardar(f"Proceso terminado: {len(componentes)} componente(s) conexa(s).")
    return pasos, componentes


def verificar_componentes(
    grafo: Grafo,
    componentes: list[list[int]],
    arboles_bfs: tuple[tuple[tuple[int, int], ...], ...],
) -> CertificadoComponentes:
    """Comprueba la partición, sus árboles de búsqueda y la maximalidad."""
    vertices = [vertice for componente in componentes for vertice in componente]
    vertices_cubiertos = (
        len(vertices) == grafo.n
        and set(vertices) == set(range(1, grafo.n + 1))
    )
    arboles_conexos = (
        len(componentes) == len(arboles_bfs)
        and all(_es_arbol_cubriente(grafo, componente, arbol)
                for componente, arbol in zip(componentes, arboles_bfs))
    )

    grupo_de = {vertice: indice for indice, grupo in enumerate(componentes) for vertice in grupo}
    aristas_cruzadas = tuple(
        (u, v) for u, v in grafo.obtener_aristas()
        if u not in grupo_de or v not in grupo_de or grupo_de[u] != grupo_de[v]
    )
    return CertificadoComponentes(vertices_cubiertos, arboles_conexos, aristas_cruzadas)


def _es_arbol_cubriente(
    grafo: Grafo,
    vertices: list[int],
    aristas: tuple[tuple[int, int], ...],
) -> bool:
    if not vertices or len(aristas) != len(vertices) - 1:
        return False
    adyacencia = {vertice: set() for vertice in vertices}
    aristas_normalizadas = set()
    for u, v in aristas:
        if u not in adyacencia or v not in adyacencia or u == v or v not in grafo.adyacencia[u]:
            return False
        arista = (min(u, v), max(u, v))
        if arista in aristas_normalizadas:
            return False
        aristas_normalizadas.add(arista)
        adyacencia[u].add(v)
        adyacencia[v].add(u)
    alcanzados = {vertices[0]}
    pila = [vertices[0]]
    while pila:
        actual = pila.pop()
        for vecino in adyacencia[actual] - alcanzados:
            alcanzados.add(vecino)
            pila.append(vecino)
    return len(alcanzados) == len(vertices)


def formatear_componente(componente: list[int] | tuple[int, ...]) -> str:
    return "{" + ", ".join(map(str, componente)) + "}"
