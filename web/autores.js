/* Datos de grupo, autores y carrusel. Edite GRUPO con los datos reales (si empieza con "[" no se muestra). */
(function () {
  const GRUPO = { seccion: "[SWxx]", grupo: "[N]", integrantes: "[Integrantes]", docente: "[Docente]" };
  const llenos = Object.values(GRUPO).every(v => !String(v).startsWith("["));
  if (llenos) document.getElementById("grupoInfo").innerHTML =
    `Sección ${GRUPO.seccion} · Grupo ${GRUPO.grupo}<br>${GRUPO.integrantes}`;

  const AUTORES = [
    { id: "euler", nombre: "Leonhard Euler", rol: "Padre de la teoría de grafos", ano: "1736", vida: "1707 – 1783", color: ["#6d3fa6", "#b04a9a"],
      aporte: "Resolvió el problema de los siete puentes de Königsberg modelando la ciudad como un conjunto de puntos y conexiones: el primer razonamiento de la teoría de grafos.",
      proyecto: "Sin la idea de modelar relaciones como vértices y aristas no existirían los grafos dirigidos con los que trabaja este programa.",
      ref: "Euler, L. (1741). Solutio problematis ad geometriam situs pertinentis. <i>Commentarii academiae scientiarum Petropolitanae, 8</i>, 128–140.",
      url: "https://scholarlycommons.pacific.edu/euler-works/53/", etiqueta: "Ver obra original" },
    { id: "tarjan", nombre: "Robert E. Tarjan", rol: "DFS y componentes en tiempo lineal", ano: "1972", vida: "n. 1948 · Premio Turing 1986", color: ["#1f5fa6", "#2aa7b8"],
      aporte: "Mostró que el recorrido en profundidad (DFS) resuelve en tiempo lineal problemas de conectividad, entre ellos hallar las componentes fuertemente conexas con una sola pasada.",
      proyecto: "Su trabajo es la base teórica del DFS que usan las dos fases del programa y de la comparación con Kosaraju.",
      ref: "Tarjan, R. (1972). Depth-first search and linear graph algorithms. <i>SIAM Journal on Computing, 1</i>(2), 146–160.",
      url: "https://doi.org/10.1137/0201010", etiqueta: "Ver publicación" },
    { id: "eswaran", nombre: "Kapali P. Eswaran", rol: "Aumento de conectividad", ano: "1976", vida: "con R. E. Tarjan", color: ["#b3541e", "#e0953a"],
      aporte: "Junto con Tarjan resolvió el problema de aumento: cuál es el mínimo de aristas que hay que añadir a un grafo dirigido para volverlo fuertemente conexo, y cómo construirlas.",
      proyecto: "Es el fundamento del asistente de conectividad: la cota máx(fuentes, sumideros) que el programa calcula y comprueba.",
      ref: "Eswaran, K. P., &amp; Tarjan, R. E. (1976). Augmentation problems. <i>SIAM Journal on Computing, 5</i>(4), 653–665.",
      url: "https://doi.org/10.1137/0205044", etiqueta: "Ver publicación" },
    { id: "kosaraju", nombre: "S. Rao Kosaraju", rol: "Algoritmo de dos recorridos", ano: "1978", vida: "idea no publicada", color: ["#a3241f", "#e3622a"],
      aporte: "Propuso en 1978 el método de dos DFS (uno sobre el grafo y otro sobre su transpuesto) para obtener las componentes fuertemente conexas, de forma sencilla y en tiempo lineal.",
      proyecto: "Es el algoritmo central del simulador: las fases 1 y 2 reproducen su idea paso a paso.",
      ref: "Cormen, T. H., Leiserson, C. E., Rivest, R. L., &amp; Stein, C. (2022). <i>Introduction to algorithms</i> (4.ª ed., sec. 22.5). MIT Press.",
      url: "https://en.wikipedia.org/wiki/Kosaraju%27s_algorithm", etiqueta: "Ver historia del algoritmo" },
    { id: "sharir", nombre: "Micha Sharir", rol: "Primera publicación del algoritmo", ano: "1981", vida: "Universidad de Tel Aviv", color: ["#1d7a5a", "#3bb58a"],
      aporte: "Descubrió de forma independiente el mismo algoritmo y fue el primero en publicarlo, aplicándolo al análisis de flujo de datos; por eso se le conoce como algoritmo de Kosaraju–Sharir.",
      proyecto: "Su artículo es la referencia formal del método implementado en este proyecto.",
      ref: "Sharir, M. (1981). A strong-connectivity algorithm and its applications in data flow analysis. <i>Computers &amp; Mathematics with Applications, 7</i>(1), 67–72.",
      url: "https://doi.org/10.1016/0898-1221(81)90008-0", etiqueta: "Ver publicación" },
    { id: "gabow", nombre: "Harold N. Gabow", rol: "Algoritmo basado en caminos", ano: "2000", vida: "Universidad de Colorado Boulder", color: ["#3b4a9e", "#7a6fd1"],
      aporte: "Propuso una variante que halla las componentes fuertes con un solo DFS y dos pilas, sin necesidad de valores «lowlink»: una alternativa moderna a Kosaraju y Tarjan.",
      proyecto: "Muestra que el problema sigue vivo: una posible extensión del programa es comparar los tres algoritmos.",
      ref: "Gabow, H. N. (2000). Path-based depth-first search for strong and biconnected components. <i>Information Processing Letters, 74</i>(3–4), 107–114.",
      url: "https://doi.org/10.1016/S0020-0190(00)00051-X", etiqueta: "Ver publicación" },
  ];

  const pista = document.getElementById("pista"), puntos = document.getElementById("puntos"),
        linea = document.querySelector("#linea ol"), biblio = document.getElementById("biblio");
  const ini = n => n.split(" ").filter(w => /^[A-ZÁÉÍÓÚ]/.test(w)).slice(0, 2).map(w => w[0]).join("");
  let act = 0;

  AUTORES.forEach((a, i) => {
    const t = document.createElement("article");
    t.className = "tarj"; t.id = "a-" + a.id; t.setAttribute("aria-label", a.nombre);
    t.innerHTML = `
      <div class="foto" style="background:linear-gradient(135deg,${a.color[0]},${a.color[1]})">
        <span class="mono" aria-hidden="true">${ini(a.nombre)}</span>
        <img src="img/autores/${a.id}.jpg" alt="Retrato de ${a.nombre}" loading="lazy" onerror="this.remove()">
        <span class="ano">${a.ano}</span><span class="vida">${a.vida}</span>
      </div>
      <div class="cuerpo2">
        <span class="rol">${a.rol}</span><h3>${a.nombre}</h3>
        <p>${a.aporte}</p>
        <p class="proy"><b>En este proyecto:</b> ${a.proyecto}</p>
        <p class="bib"><b>Referencia:</b> ${a.ref}</p>
        <div class="acc"><a href="${a.url}" target="_blank" rel="noopener noreferrer">${a.etiqueta} ↗</a>
          <button class="sec" data-copiar="${i}">Copiar cita</button></div>
      </div>`;
    pista.appendChild(t);
    const p = document.createElement("button"); p.setAttribute("aria-label", `Ir a ${a.nombre}`); p.onclick = () => ir(i); puntos.appendChild(p);
    const li = document.createElement("li"); li.innerHTML = `<button aria-label="${a.nombre}, ${a.ano}"><i></i><span>${a.ano}</span></button>`;
    li.firstChild.onclick = () => ir(i); linea.appendChild(li);
    const b = document.createElement("li"); b.innerHTML = a.ref; biblio.appendChild(b);
  });

  function marcar(i) {
    act = i;
    [...pista.children].forEach((c, k) => c.classList.toggle("act", k === i));
    [...puntos.children].forEach((c, k) => k === i ? c.setAttribute("aria-current", "true") : c.removeAttribute("aria-current"));
    [...linea.children].forEach((c, k) => k === i ? c.firstChild.setAttribute("aria-current", "true") : c.firstChild.removeAttribute("aria-current"));
  }
  function ir(i) {
    i = Math.max(0, Math.min(AUTORES.length - 1, i));
    const c = pista.children[i]; if (!c) return;
    pista.scrollTo({ left: c.offsetLeft - (pista.clientWidth - c.offsetWidth) / 2, behavior: "smooth" }); marcar(i);
  }
  let tmo;
  pista.addEventListener("scroll", () => {
    clearTimeout(tmo);
    tmo = setTimeout(() => {
      const centro = pista.scrollLeft + pista.clientWidth / 2;
      let mejor = 0, d = 1e9;
      [...pista.children].forEach((c, k) => { const x = Math.abs(c.offsetLeft + c.offsetWidth / 2 - centro); if (x < d) { d = x; mejor = k; } });
      if (mejor !== act) marcar(mejor);
    }, 40);
  }, { passive: true });
  document.getElementById("cPrev").onclick = () => ir(act - 1);
  document.getElementById("cNext").onclick = () => ir(act + 1);
  document.getElementById("carr").addEventListener("keydown", e => { if (e.key === "ArrowRight") { ir(act + 1); e.preventDefault(); } if (e.key === "ArrowLeft") { ir(act - 1); e.preventDefault(); } });
  pista.addEventListener("click", e => {
    const b = e.target.closest("[data-copiar]"); if (!b) return;
    const txt = AUTORES[+b.dataset.copiar].ref.replace(/<[^>]+>/g, "").replace(/&amp;/g, "&");
    (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(() => { b.textContent = "¡Copiada!"; setTimeout(() => (b.textContent = "Copiar cita"), 1400); }, () => { b.textContent = "No se pudo copiar"; });
  });
  window.Autores = { ir: () => setTimeout(() => ir(act), 60) };
  marcar(0);
})();
