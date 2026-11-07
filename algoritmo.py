"""Componentes (fuertemente) conexas de un grafo dirigido: algoritmo de Kosaraju.

En un grafo dirigido, dos vértices u y v pertenecen a la misma componente
conexa cuando existe un camino de u a v **y** otro de v a u. El algoritmo de
Kosaraju las encuentra con dos recorridos en profundidad (DFS):

1. DFS sobre G, anotando el orden en que cada vértice *termina* (se vacía su
   lista de sucesores).
2. DFS sobre el grafo transpuesto Gᵀ (todas las aristas invertidas), iniciando
   desde los vértices en orden inverso de finalización. Cada árbol DFS de esta
   segunda fase es exactamente una componente.

Cada acción relevante queda registrada en un :class:`Paso` para que la interfaz
pueda mostrar el algoritmo paso a paso.
"""

from __future__ import annotations

from dataclasses import dataclass

from grafo import Grafo

FASE_DFS_G = 1
FASE_DFS_TRANSPUESTO = 2
FASE_RESULTADO = 3


@dataclass(frozen=True)
class Paso:
    fase: int
    descripcion: str
    visitados: frozenset[int]
    pila: tuple[int, ...]
    terminados: tuple[int, ...]            # orden de finalización (fase 1), cumulativo
    pendientes: tuple[int, ...]            # fase 2: vértices aún sin asignar, en orden de procesamiento
    actual: int | None
    componente_actual: tuple[int, ...]
    componentes_completas: tuple[tuple[int, ...], ...]
    arista: tuple[int, int] | None = None  # arista examinada, en la orientación del grafo de la fase
    tipo_arista: str = ""                  # "arbol" | "visitado"
    arbol: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class Certificado:
    vertices_cubiertos: bool
    fuertemente_conexas: bool
    sin_ciclos_entre_componentes: bool

    @property
    def valido(self) -> bool:
        return self.vertices_cubiertos and self.fuertemente_conexas and self.sin_ciclos_entre_componentes


def formatear_componente(componente: list[int] | tuple[int, ...]) -> str:
    return "{" + ", ".join(map(str, componente)) + "}"


def componentes_fuertes_pasos(grafo: Grafo) -> tuple[list[Paso], list[list[int]]]:
    """Ejecuta Kosaraju y devuelve (pasos, componentes)."""
    pasos: list[Paso] = []
    visitados: set[int] = set()
    pila: list[int] = []
    terminados: list[int] = []
    arbol: list[tuple[int, int]] = []
    componente: list[int] = []
    completas: list[list[int]] = []
    orden_fase2: list[int] = []
    fase = FASE_DFS_G

    def guardar(descripcion: str, actual: int | None = None,
                arista: tuple[int, int] | None = None, tipo: str = "") -> None:
        pendientes = tuple(v for v in orden_fase2 if v not in visitados) if fase == FASE_DFS_TRANSPUESTO else ()
        pasos.append(Paso(
            fase=fase,
            descripcion=descripcion,
            visitados=frozenset(visitados),
            pila=tuple(pila),
            terminados=tuple(terminados),
            pendientes=pendientes,
            actual=actual,
            componente_actual=tuple(sorted(componente)),
            componentes_completas=tuple(tuple(c) for c in completas),
            arista=arista,
            tipo_arista=tipo,
            arbol=tuple(arbol),
        ))

    def dfs(u: int) -> None:
        visitados.add(u)
        pila.append(u)
        if fase == FASE_DFS_TRANSPUESTO:
            componente.append(u)
            guardar(f"Se visita {u} sobre Gᵀ: entra en la componente actual.", u)
        else:
            guardar(f"Se visita {u}: entra en la pila de recursión del DFS.", u)
        vecinos = grafo.sucesores(u) if fase == FASE_DFS_G else grafo.predecesores(u)
        for v in vecinos:
            if v not in visitados:
                arbol.append((u, v))
                guardar(f"Se examina {u}→{v}: {v} no estaba visitado, se desciende a {v}.",
                        u, (u, v), "arbol")
                dfs(v)
            else:
                guardar(f"Se examina {u}→{v}: {v} ya estaba visitado, se ignora.",
                        u, (u, v), "visitado")
        pila.pop()
        if fase == FASE_DFS_G:
            terminados.append(u)
            guardar(f"{u} no tiene más sucesores por explorar: termina con orden de "
                    f"finalización #{len(terminados)}.", u)
        else:
            guardar(f"{u} no tiene más predecesores por explorar: se cierra su rama.", u)

    # ---- Fase 1: DFS sobre G, registrando el orden de finalización.
    guardar("Estado inicial. Fase 1: DFS sobre G para obtener el orden de finalización de los vértices.")
    for inicio in range(1, grafo.n + 1):
        if inicio in visitados:
            continue
        guardar(f"Fase 1: se inicia un nuevo árbol DFS desde {inicio} (aún sin visitar).", inicio)
        dfs(inicio)
    orden_fase2 = list(reversed(terminados))
    guardar("Fin de la fase 1. Orden de finalización: " + ", ".join(map(str, terminados)) + ".")

    # ---- Fase 2: DFS sobre Gᵀ en orden inverso de finalización.
    fase = FASE_DFS_TRANSPUESTO
    visitados.clear()
    arbol.clear()
    guardar("Fase 2: se invierten todas las aristas (Gᵀ) y se procesan los vértices en orden inverso "
            "al de finalización: " + ", ".join(map(str, orden_fase2)) + ".")
    for inicio in orden_fase2:
        if inicio in visitados:
            continue
        componente.clear()
        guardar(f"Fase 2: {inicio} es el siguiente vértice sin asignar; el DFS sobre Gᵀ desde {inicio} "
                f"recogerá una componente completa.", inicio)
        dfs(inicio)
        completas.append(sorted(componente))
        guardar(f"Componente C{len(completas)} completa: {formatear_componente(sorted(componente))}.")
        componente.clear()

    fase = FASE_RESULTADO
    visitados.clear()
    arbol.clear()
    guardar(f"Resultado: {len(completas)} componente(s) conexa(s) (fuertemente conexa/s).")
    return pasos, [list(c) for c in completas]


# --------------------------------------------------------------------------- resultados auxiliares
def componentes_debiles(grafo: Grafo) -> list[list[int]]:
    """Componentes débilmente conexas: ignoran el sentido de las aristas."""
    vecinos = {u: set(grafo.adyacencia[u]) for u in range(1, grafo.n + 1)}
    for u, v in grafo.obtener_aristas():
        vecinos[v].add(u)
    vistos: set[int] = set()
    grupos: list[list[int]] = []
    for inicio in range(1, grafo.n + 1):
        if inicio in vistos:
            continue
        grupo, pila = [], [inicio]
        vistos.add(inicio)
        while pila:
            actual = pila.pop()
            grupo.append(actual)
            for vecino in vecinos[actual] - vistos:
                vistos.add(vecino)
                pila.append(vecino)
        grupos.append(sorted(grupo))
    return grupos


def aristas_entre_componentes(grafo: Grafo, componentes: list[list[int]]) -> list[tuple[int, int]]:
    """Aristas del grafo condensado (índices de componente base 1, sin repetir)."""
    indice = {v: i for i, c in enumerate(componentes, 1) for v in c}
    return sorted({(indice[u], indice[v]) for u, v in grafo.obtener_aristas() if indice[u] != indice[v]})


def _alcanzables(grafo: Grafo) -> list[list[bool]]:
    """Cierre transitivo (Warshall)."""
    n = grafo.n
    r = [[(i == j) or (j + 1 in grafo.adyacencia[i + 1]) for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            if r[i][k]:
                for j in range(n):
                    if r[k][j]:
                        r[i][j] = True
    return r


def verificar_componentes(grafo: Grafo, componentes: list[list[int]]) -> Certificado:
    """Comprueba el resultado con un método independiente (cierre transitivo).

    * los vértices quedan particionados,
    * dentro de una componente todo par es mutuamente alcanzable,
    * entre componentes distintas nunca hay alcanzabilidad mutua.
    """
    vertices = [v for c in componentes for v in c]
    cubiertos = len(vertices) == grafo.n and set(vertices) == set(range(1, grafo.n + 1))
    if not cubiertos:
        return Certificado(False, False, False)
    r = _alcanzables(grafo)
    grupo = {v: i for i, c in enumerate(componentes) for v in c}
    fuertes = True
    sin_ciclos = True
    for u in range(1, grafo.n + 1):
        for v in range(u + 1, grafo.n + 1):
            mutuo = r[u - 1][v - 1] and r[v - 1][u - 1]
            if grupo[u] == grupo[v] and not mutuo:
                fuertes = False
            if grupo[u] != grupo[v] and mutuo:
                sin_ciclos = False
    return Certificado(True, fuertes, sin_ciclos)
