import unittest

from algoritmo import componentes_conexas_pasos
from grafo import Grafo


class PruebasGrafo(unittest.TestCase):
    def test_matriz_simetrica_y_aristas_sin_duplicados(self):
        grafo = Grafo(4)
        self.assertTrue(grafo.agregar_arista(1, 3))
        self.assertFalse(grafo.agregar_arista(3, 1))
        self.assertEqual(grafo.obtener_aristas(), [(1, 3)])
        self.assertEqual(grafo.matriz_adyacencia(), [
            [0, 0, 1, 0],
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 0],
        ])

    def test_validacion(self):
        with self.assertRaises(ValueError):
            Grafo(3)
        grafo = Grafo(4)
        with self.assertRaises(ValueError):
            grafo.agregar_arista(1, 1)
        with self.assertRaises(ValueError):
            grafo.agregar_arista(1, 5)

    def test_componentes_y_pasos(self):
        grafo = Grafo(6)
        for u, v in [(1, 2), (2, 3), (4, 5)]:
            grafo.agregar_arista(u, v)
        pasos, componentes = componentes_conexas_pasos(grafo)
        self.assertEqual(componentes, [[1, 2, 3], [4, 5], [6]])
        self.assertEqual(pasos[0].visitados, frozenset())
        self.assertEqual(pasos[-1].componentes_completas,
                         ((1, 2, 3), (4, 5), (6,)))
        self.assertEqual(pasos[-1].visitados, frozenset(range(1, 7)))
        self.assertTrue(any(p.cola for p in pasos))

    def test_nodos_aislados(self):
        grafo = Grafo(4)
        pasos, componentes = componentes_conexas_pasos(grafo)
        self.assertEqual(componentes, [[1], [2], [3], [4]])
        self.assertEqual(pasos[-1].componentes_completas, ((1,), (2,), (3,), (4,)))


if __name__ == "__main__":
    unittest.main()
