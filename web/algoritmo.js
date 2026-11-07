/* Núcleo del programa (equivale a grafo.py + algoritmo.py): grafo dirigido y Kosaraju paso a paso. */
(function (root) {
  const N_MIN = 4, N_MAX = 12;
  const FASE_G = 1, FASE_GT = 2, FASE_RES = 3;

  function crearGrafo(n) {
    if (!Number.isInteger(n) || n < N_MIN || n > N_MAX)
      throw new Error(`La cantidad de nodos debe ser un entero entre ${N_MIN} y ${N_MAX}.`);
    const adj = {};
    for (let i = 1; i <= n; i++) adj[i] = new Set();
    return { n, adj };
  }
  function validar(g, u, v) {
    if (!Number.isInteger(u) || !Number.isInteger(v)) throw new Error("Los vértices deben ser enteros.");
    if (u < 1 || v < 1 || u > g.n || v > g.n) throw new Error(`Los vértices deben estar entre 1 y ${g.n}.`);
    if (u === v) throw new Error("No se permiten lazos: elija dos vértices distintos.");
  }
  function agregar(g, u, v) { validar(g, u, v); if (g.adj[u].has(v)) return false; g.adj[u].add(v); return true; }
  function eliminar(g, u, v) { validar(g, u, v); return g.adj[u].delete(v); }
  function limpiar(g) { for (const k in g.adj) g.adj[k].clear(); }
  function sucesores(g, u) { return [...g.adj[u]].sort((a, b) => a - b); }
  function predecesores(g, v) {
    const r = [];
    for (let u = 1; u <= g.n; u++) if (g.adj[u].has(v)) r.push(u);
    return r;
  }
  function aristas(g) {
    const r = [];
    for (let u = 1; u <= g.n; u++) for (const v of sucesores(g, u)) r.push([u, v]);
    return r;
  }
  function matriz(g) {
    return Array.from({ length: g.n }, (_, i) => Array.from({ length: g.n }, (_, j) => (g.adj[i + 1].has(j + 1) ? 1 : 0)));
  }
  function alcanzables(g) {
    const n = g.n, r = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => i === j || g.adj[i + 1].has(j + 1)));
    for (let k = 0; k < n; k++) for (let i = 0; i < n; i++) if (r[i][k]) for (let j = 0; j < n; j++) if (r[k][j]) r[i][j] = true;
    return r;
  }
  function esInteresante(g) {
    const r = alcanzables(g), vistos = new Set(), grupos = [];
    for (let i = 0; i < g.n; i++) {
      if (vistos.has(i)) continue;
      const gr = [];
      for (let j = 0; j < g.n; j++) if (r[i][j] && r[j][i]) { gr.push(j); vistos.add(j); }
      grupos.push(gr);
    }
    return grupos.length >= 2 && grupos.filter(x => x.length >= 2).reduce((s, x) => s + x.length, 0) >= 3;
  }
  /* Entre n y ~1.6n aristas sorteadas al azar; se descartan (hasta 50 veces) los sorteos poco ilustrativos. */
  function generarAleatorio(n, rnd = Math.random) {
    const pares = [];
    for (let u = 1; u <= n; u++) for (let v = 1; v <= n; v++) if (u !== v) pares.push([u, v]);
    const minimo = Math.max(4, n), maximo = Math.min(pares.length, Math.max(minimo, Math.round(1.6 * n)));
    let g;
    for (let intento = 0; intento < 50; intento++) {
      g = crearGrafo(n);
      const cant = minimo + Math.floor(rnd() * (maximo - minimo + 1));
      const copia = pares.slice();
      for (let i = 0; i < cant; i++) { // Fisher-Yates parcial
        const j = i + Math.floor(rnd() * (copia.length - i));
        [copia[i], copia[j]] = [copia[j], copia[i]];
        agregar(g, copia[i][0], copia[i][1]);
      }
      if (esInteresante(g)) break;
    }
    return g;
  }

  const fmt = c => "{" + c.join(", ") + "}";

  function kosaraju(g) {
    const pasos = [], visitados = new Set(), pila = [], terminados = [], arbol = [], completas = [];
    let componente = [], orden2 = [], fase = FASE_G;
    function guardar(descripcion, actual = null, arista = null, tipo = "") {
      pasos.push({
        fase, descripcion, visitados: new Set(visitados), pila: pila.slice(), terminados: terminados.slice(),
        pendientes: fase === FASE_GT ? orden2.filter(v => !visitados.has(v)) : [],
        actual, componenteActual: componente.slice().sort((a, b) => a - b),
        completas: completas.map(c => c.slice()), arista, tipo, arbol: arbol.map(e => e.slice()),
      });
    }
    function dfs(u) {
      visitados.add(u); pila.push(u);
      if (fase === FASE_GT) { componente.push(u); guardar(`Se visita ${u} sobre Gᵀ: entra en la componente actual.`, u); }
      else guardar(`Se visita ${u}: entra en la pila de recursión del DFS.`, u);
      const vecinos = fase === FASE_G ? sucesores(g, u) : predecesores(g, u);
      for (const v of vecinos) {
        if (!visitados.has(v)) {
          arbol.push([u, v]);
          guardar(`Se examina ${u}→${v}: ${v} no estaba visitado, se desciende a ${v}.`, u, [u, v], "arbol");
          dfs(v);
        } else guardar(`Se examina ${u}→${v}: ${v} ya estaba visitado, se ignora.`, u, [u, v], "visitado");
      }
      pila.pop();
      if (fase === FASE_G) {
        terminados.push(u);
        guardar(`${u} no tiene más sucesores por explorar: termina con orden de finalización #${terminados.length}.`, u);
      } else guardar(`${u} no tiene más predecesores por explorar: se cierra su rama.`, u);
    }
    guardar("Estado inicial. Fase 1: DFS sobre G para obtener el orden de finalización de los vértices.");
    for (let s = 1; s <= g.n; s++) {
      if (visitados.has(s)) continue;
      guardar(`Fase 1: se inicia un nuevo árbol DFS desde ${s} (aún sin visitar).`, s);
      dfs(s);
    }
    orden2 = terminados.slice().reverse();
    guardar("Fin de la fase 1. Orden de finalización: " + terminados.join(", ") + ".");
    fase = FASE_GT; visitados.clear(); arbol.length = 0;
    guardar("Fase 2: se invierten todas las aristas (Gᵀ) y se procesan los vértices en orden inverso al de finalización: " + orden2.join(", ") + ".");
    for (const s of orden2) {
      if (visitados.has(s)) continue;
      componente = [];
      guardar(`Fase 2: ${s} es el siguiente vértice sin asignar; el DFS sobre Gᵀ desde ${s} recogerá una componente completa.`, s);
      dfs(s);
      completas.push(componente.slice().sort((a, b) => a - b));
      guardar(`Componente C${completas.length} completa: ${fmt(componente.slice().sort((a, b) => a - b))}.`);
      componente = [];
    }
    fase = FASE_RES; visitados.clear(); arbol.length = 0;
    guardar(`Resultado: ${completas.length} componente(s) conexa(s) (fuertemente conexa/s).`);
    return { pasos, componentes: completas.map(c => c.slice()) };
  }

  function componentesDebiles(g) {
    const vec = {};
    for (let u = 1; u <= g.n; u++) vec[u] = new Set(g.adj[u]);
    for (const [u, v] of aristas(g)) vec[v].add(u);
    const vistos = new Set(), grupos = [];
    for (let s = 1; s <= g.n; s++) {
      if (vistos.has(s)) continue;
      const gr = [], st = [s]; vistos.add(s);
      while (st.length) { const a = st.pop(); gr.push(a); for (const b of vec[a]) if (!vistos.has(b)) { vistos.add(b); st.push(b); } }
      grupos.push(gr.sort((a, b) => a - b));
    }
    return grupos;
  }
  function aristasEntre(g, comps) {
    const idx = {}; comps.forEach((c, i) => c.forEach(v => (idx[v] = i + 1)));
    const s = new Set();
    for (const [u, v] of aristas(g)) if (idx[u] !== idx[v]) s.add(idx[u] + "," + idx[v]);
    return [...s].map(x => x.split(",").map(Number)).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  }
  function verificar(g, comps) {
    const vs = comps.flat();
    if (vs.length !== g.n || new Set(vs).size !== g.n) return false;
    const r = alcanzables(g), grupo = {};
    comps.forEach((c, i) => c.forEach(v => (grupo[v] = i)));
    for (let u = 1; u <= g.n; u++) for (let v = u + 1; v <= g.n; v++) {
      const mutuo = r[u - 1][v - 1] && r[v - 1][u - 1];
      if ((grupo[u] === grupo[v]) !== mutuo) return false;
    }
    return true;
  }

  const api = { N_MIN, N_MAX, FASE_G, FASE_GT, FASE_RES, crearGrafo, agregar, eliminar, limpiar, aristas, matriz,
    sucesores, predecesores, generarAleatorio, kosaraju, componentesDebiles, aristasEntre, verificar, fmt };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.Alg = api;
})(typeof window !== "undefined" ? window : globalThis);
