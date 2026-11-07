import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from algoritmo import (  # noqa: E402
    FASE_DFS_G,
    FASE_DFS_TRANSPUESTO,
    FASE_RESULTADO,
    aristas_entre_componentes,
    componentes_debiles,
    componentes_fuertes_pasos,
    verificar_componentes,
)
from grafo import Grafo  # noqa: E402


def construir(n, aristas):
    g = Grafo(n)
    for u, v in aristas:
        g.agregar_arista(u, v)
    return g


def componentes_por_fuerza_bruta(g):
    """Referencia independiente: u~v si se alcanzan mutuamente (BFS desde cada vértice)."""
    def alcanza(origen):
        vistos, cola = {origen}, [origen]
        while cola:
            x = cola.pop()
            for y in g.adyacencia[x]:
                if y not in vistos:
                    vistos.add(y)
                    cola.append(y)
        return vistos

    alc = {v: alcanza(v) for v in range(1, g.n + 1)}
    grupos = {frozenset(w for w in alc[v] if v in alc[w]) for v in range(1, g.n + 1)}
    return sorted(sorted(c) for c in grupos)


class PruebasGrafo(unittest.TestCase):
    def test_matriz_dirigida_no_simetrica(self):
        g = Grafo(4)
        self.assertTrue(g.agregar_arista(1, 3))
        self.assertTrue(g.agregar_arista(3, 1))
        self.assertTrue(g.agregar_arista(2, 4))
        self.assertFalse(g.agregar_arista(2, 4))
        self.assertEqual(g.obtener_aristas(), [(1, 3), (2, 4), (3, 1)])
        self.assertEqual(g.matriz_adyacencia(), [
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [1, 0, 0, 0],
            [0, 0, 0, 0],
        ])

    def test_eliminar_solo_un_sentido(self):
        g = construir(4, [(1, 2), (2, 1)])
        self.assertTrue(g.eliminar_arista(1, 2))
        self.assertEqual(g.obtener_aristas(), [(2, 1)])
        self.assertFalse(g.eliminar_arista(1, 2))

    def test_validacion(self):
        for malo in (3, 13, True, "5", 4.0):
            with self.assertRaises(ValueError):
                Grafo(malo)
        g = Grafo(4)
        with self.assertRaises(ValueError):
            g.agregar_arista(1, 1)
        with self.assertRaises(ValueError):
            g.agregar_arista(1, 5)

    def test_generacion_aleatoria_respeta_rango_y_varia(self):
        distintos = set()
        for n in range(4, 13):
            for _ in range(30):
                g = Grafo.generar_aleatorio(n)
                self.assertEqual(g.n, n)
                aristas = g.obtener_aristas()
                self.assertEqual(len(aristas), len(set(aristas)))
                self.assertTrue(all(u != v for u, v in aristas))
                self.assertGreaterEqual(len(aristas), 3)
                distintos.add((n, tuple(aristas)))
        self.assertGreater(len(distintos), 200)

    def test_generacion_aleatoria_es_variada_e_ilustrativa(self):
        rng = random.Random(11)
        con_ciclos = 0
        for _ in range(300):
            n = rng.randint(4, 12)
            _, comps = componentes_fuertes_pasos(Grafo.generar_aleatorio(n, rng))
            if len(comps) >= 2 and max(map(len, comps)) >= 2:
                con_ciclos += 1
        self.assertGreater(con_ciclos, 285)  # casi siempre ilustrativo

    def test_generacion_libre_sortea_n_en_rango(self):
        rng = random.Random(3)
        tamanos = {Grafo.generar_aleatorio_libre(rng).n for _ in range(300)}
        self.assertEqual(tamanos, set(range(4, 13)))

    def test_generacion_reproducible_con_semilla(self):
        a = Grafo.generar_aleatorio(8, random.Random(7)).obtener_aristas()
        b = Grafo.generar_aleatorio(8, random.Random(7)).obtener_aristas()
        self.assertEqual(a, b)


class PruebasAlgoritmo(unittest.TestCase):
    def test_ejemplo_conocido(self):
        # 1→2→3→1 (ciclo), 3→4, 4→5→4 (ciclo), 6 aislado
        g = construir(6, [(1, 2), (2, 3), (3, 1), (3, 4), (4, 5), (5, 4)])
        pasos, comps = componentes_fuertes_pasos(g)
        self.assertEqual(sorted(comps), [[1, 2, 3], [4, 5], [6]])
        self.assertEqual(pasos[-1].fase, FASE_RESULTADO)
        self.assertEqual(pasos[-1].componentes_completas, tuple(tuple(c) for c in comps))

    def test_camino_dirigido_no_es_componente(self):
        # En un grafo dirigido 1→2→3→4 cada vértice es su propia componente.
        g = construir(4, [(1, 2), (2, 3), (3, 4)])
        _, comps = componentes_fuertes_pasos(g)
        self.assertEqual(sorted(comps), [[1], [2], [3], [4]])
        self.assertEqual(componentes_debiles(g), [[1, 2, 3, 4]])

    def test_ciclo_completo_es_una_componente(self):
        g = construir(5, [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)])
        _, comps = componentes_fuertes_pasos(g)
        self.assertEqual(comps, [[1, 2, 3, 4, 5]])

    def test_sin_aristas(self):
        _, comps = componentes_fuertes_pasos(Grafo(4))
        self.assertEqual(sorted(comps), [[1], [2], [3], [4]])

    def test_coincide_con_fuerza_bruta_en_grafos_aleatorios(self):
        rng = random.Random(2026)
        for _ in range(400):
            n = rng.randint(4, 12)
            g = Grafo.generar_aleatorio(n, rng)
            _, comps = componentes_fuertes_pasos(g)
            self.assertEqual(sorted(sorted(c) for c in comps), componentes_por_fuerza_bruta(g))
            self.assertTrue(verificar_componentes(g, comps).valido)

    def test_pasos_consistentes(self):
        rng = random.Random(5)
        for _ in range(60):
            g = Grafo.generar_aleatorio(rng.randint(4, 12), rng)
            pasos, comps = componentes_fuertes_pasos(g)
            self.assertEqual(pasos[0].visitados, frozenset())
            fases = [p.fase for p in pasos]
            self.assertEqual(fases, sorted(fases))
            self.assertEqual({FASE_DFS_G, FASE_DFS_TRANSPUESTO, FASE_RESULTADO}, set(fases))
            # orden de finalización completo al terminar la fase 1
            ultimo_f1 = [p for p in pasos if p.fase == FASE_DFS_G][-1]
            self.assertEqual(sorted(ultimo_f1.terminados), list(range(1, g.n + 1)))
            # las aristas examinadas existen en la orientación de su fase
            for p in pasos:
                if p.arista is None:
                    continue
                u, v = p.arista
                existe = g.tiene_arista(u, v) if p.fase == FASE_DFS_G else g.tiene_arista(v, u)
                self.assertTrue(existe)
            # componentes completas solo crecen
            previas = 0
            for p in pasos:
                self.assertGreaterEqual(len(p.componentes_completas), previas)
                previas = len(p.componentes_completas)

    def test_verificador_detecta_errores(self):
        g = construir(4, [(1, 2), (2, 1), (3, 4)])
        self.assertTrue(verificar_componentes(g, [[1, 2], [3], [4]]).valido)
        self.assertFalse(verificar_componentes(g, [[1, 2, 3], [4]]).valido)   # no es fuertemente conexa
        self.assertFalse(verificar_componentes(g, [[1], [2], [3], [4]]).valido)  # 1 y 2 se alcanzan mutuamente
        self.assertFalse(verificar_componentes(g, [[1, 2], [3]]).valido)       # falta el vértice 4

    def test_aristas_entre_componentes_y_debiles(self):
        g = construir(6, [(1, 2), (2, 1), (2, 3), (4, 5)])
        _, comps = componentes_fuertes_pasos(g)
        self.assertEqual(sorted(comps), [[1, 2], [3], [4], [5], [6]])
        indice = {v: i for i, c in enumerate(comps, 1) for v in c}
        self.assertIn((indice[2], indice[3]), aristas_entre_componentes(g, comps))
        self.assertEqual(componentes_debiles(g), [[1, 2, 3], [4, 5], [6]])


if __name__ == "__main__":
    unittest.main()
