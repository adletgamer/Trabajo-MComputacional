(function () {
  const A = window.Alg, $ = id => document.getElementById(id);
  const PALETA = ["#68bcc2", "#f3bd6e", "#b99add", "#e7a2a1", "#9bc77e", "#83a8df", "#e6a1c9", "#b5b56b", "#7fb0a0", "#d49b6a", "#9aa7e0", "#c2c2c2"];
  const SIN = "#e8eef5", PILA = "#f4d778", ACT = "#f18a70", TERM = "#9fb8d6", VIS2 = "#c7d5e5";
  const NOMBRE = { 1: "Fase 1 · DFS sobre G (orden de finalización)", 2: "Fase 2 · DFS sobre Gᵀ (una componente por árbol)", 3: "Resultado · grafo original con sus componentes" };
  const TITULO = { 1: "Grafo G", 2: "Grafo transpuesto Gᵀ (aristas invertidas)", 3: "Grafo G con sus componentes" };
  const W = 720, H = 560, R = 24;
  let g = null, modo = "", pasos = [], comps = [], idx = 0, timer = null;

  const oscurecer = c => "#" + [1, 3, 5].map(i => Math.round(parseInt(c.substr(i, 2), 16) * 0.62).toString(16).padStart(2, "0")).join("");
  const el = (tag, attrs = {}, txt) => { const e = document.createElementNS("http://www.w3.org/2000/svg", tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (txt !== undefined) e.textContent = txt; return e; };

  function leerN() {
    const t = $("n").value.trim();
    if (!/^\d+$/.test(t) || +t < A.N_MIN || +t > A.N_MAX) { $("err").textContent = `Ingrese un número entero entre ${A.N_MIN} y ${A.N_MAX}.`; return null; }
    $("err").textContent = ""; return +t;
  }
  function mostrar(trabajo) { $("portada").style.display = trabajo ? "none" : "grid"; $("trabajo").style.display = trabajo ? "block" : "none"; }

  function iniciarManual() {
    const n = leerN(); if (n === null) return;
    detener(); modo = "manual"; g = A.crearGrafo(n);
    $("manual").style.display = "block"; $("aleat").style.display = "none";
    const opts = Array.from({ length: n }, (_, i) => `<option>${i + 1}</option>`).join("");
    $("u").innerHTML = opts; $("v").innerHTML = opts; $("v").value = "2";
    modificado("Agregue aristas dirigidas (u → v) y pulse «Analizar grafo».");
    mostrar(true);
  }
  function iniciarAleatorio() {
    const n = leerN(); if (n === null) return;
    detener(); modo = "aleatorio"; g = A.generarAleatorio(n);
    $("manual").style.display = "none"; $("aleat").style.display = "block";
    modificado(""); analizar(); mostrar(true);
  }
  function regenerar() { detener(); g = A.generarAleatorio(g.n); modificado(""); analizar(); }

  function modificado(msg) {
    detener(); pasos = []; comps = []; idx = 0;
    const E = A.aristas(g);
    $("listaAristas").textContent = "Aristas: " + (E.length ? E.map(([u, v]) => `${u}→${v}`).join(", ") : "ninguna");
    $("infoG").textContent = `${g.n} vértices · ${E.length} aristas dirigidas`;
    $("tituloG").textContent = "Grafo G";
    $("sol").textContent = "Pulse «Analizar» o avance con «Siguiente» para ver la solución.";
    $("fase").textContent = ""; $("cont").textContent = ""; $("desc").textContent = msg;
    $("pila").textContent = "Pila DFS: —"; $("vis").textContent = "Visitados: —"; $("ord").textContent = "Orden de finalización: —"; $("comps").textContent = "Componentes: —";
    matriz(); botones(); dibujar();
  }
  function matriz() {
    const M = A.matriz(g); let h = "<table><tr><th></th>";
    for (let j = 1; j <= g.n; j++) h += `<th>${j}</th>`;
    h += "</tr>";
    M.forEach((f, i) => { h += `<tr><td class="u">${i + 1}</td>` + f.map(x => `<td>${x}</td>`).join("") + "</tr>"; });
    $("mat").innerHTML = h + "</table>";
  }

  function analizar() { detener(); const r = A.kosaraju(g); pasos = r.pasos; comps = r.componentes; idx = 0; paso(); }
  function ir(i) { detener(); if (pasos.length && i >= 0 && i < pasos.length) { idx = i; paso(); } }
  function detener() { if (timer) { clearInterval(timer); timer = null; } if ($("bPlay")) $("bPlay").textContent = "▶ Reproducir"; }
  function reproducir() {
    if (timer) return detener();
    if (!pasos.length) analizar();
    if (idx >= pasos.length - 1) { idx = 0; paso(); }
    $("bPlay").textContent = "⏸ Pausar";
    timer = setInterval(() => { if (idx < pasos.length - 1) { idx++; paso(); } else detener(); }, 650);
  }

  function paso() {
    const p = pasos[idx];
    $("fase").textContent = NOMBRE[p.fase]; $("tituloG").textContent = TITULO[p.fase]; $("desc").textContent = p.descripcion;
    $("cont").textContent = `Paso ${idx + 1} de ${pasos.length}`;
    $("pila").textContent = "Pila DFS: " + (p.pila.length ? p.pila.join(" → ") : "vacía");
    $("vis").textContent = "Visitados: " + ([...p.visitados].sort((a, b) => a - b).join(", ") || "ninguno");
    $("ord").textContent = p.fase === 2 ? "Por procesar (orden inverso): " + (p.pendientes.join(", ") || "—") : "Orden de finalización: " + (p.terminados.join(", ") || "—");
    let c = p.completas.map((x, i) => `C${i + 1} ${A.fmt(x)}`).join(" · ");
    if (p.componenteActual.length) c += (c ? " · " : "") + `en construcción ${A.fmt(p.componenteActual)}`;
    $("comps").textContent = "Componentes: " + (c || "ninguna aún");
    if (p.fase === 3) solucion(); else $("sol").textContent = "La solución completa aparece al terminar la fase 2 (use «Ver resultado» para saltar al final).";
    botones(); dibujar();
  }
  function solucion() {
    const deb = A.componentesDebiles(g), cruces = A.aristasEntre(g, comps), ok = A.verificar(g, comps);
    $("sol").innerHTML = `<b>Componentes conexas (fuertes): ${comps.length}</b>` +
      comps.map((c, i) => `<div class="c">C${i + 1} = ${A.fmt(c)}</div>`).join("") +
      `<div>Débilmente conexas (sin sentido): ${deb.length}</div>` +
      `<div>${cruces.length ? "Aristas entre componentes: " + cruces.map(([a, b]) => `C${a}→C${b}`).join(", ") : "No hay aristas entre componentes distintas."}</div>` +
      `<div>Verificación (cierre transitivo): ${ok ? "correcta ✓" : "¡inconsistente!"}</div>`;
  }
  function botones() {
    const hay = pasos.length > 0;
    $("bIni").disabled = $("bPrev").disabled = !(hay && idx > 0);
    $("bNext").disabled = $("bFin").disabled = !(hay && idx < pasos.length - 1);
  }

  function pos() {
    const cx = W / 2, cy = H / 2, r = Math.min(W, H) / 2 - 62, o = {};
    for (let v = 1; v <= g.n; v++) { const a = -Math.PI / 2 + 2 * Math.PI * (v - 1) / g.n; o[v] = [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }
    return o;
  }
  function flecha(svg, p, q, color, w, dash, curva) {
    const [x1, y1] = p, [x2, y2] = q, dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L;
    let ini, fin, ctrl = null;
    if (curva) {
      const cx = (x1 + x2) / 2 - uy * 0.16 * L, cy = (y1 + y2) / 2 + ux * 0.16 * L;
      const a = Math.hypot(cx - x1, cy - y1) || 1, b = Math.hypot(cx - x2, cy - y2) || 1;
      ini = [x1 + (cx - x1) / a * R, y1 + (cy - y1) / a * R]; fin = [x2 + (cx - x2) / b * (R + 2), y2 + (cy - y2) / b * (R + 2)]; ctrl = [cx, cy];
    } else { ini = [x1 + ux * R, y1 + uy * R]; fin = [x2 - ux * (R + 2), y2 - uy * (R + 2)]; }
    const d = ctrl ? `M${ini[0]},${ini[1]} Q${ctrl[0]},${ctrl[1]} ${fin[0]},${fin[1]}` : `M${ini[0]},${ini[1]} L${fin[0]},${fin[1]}`;
    svg.appendChild(el("path", { d, fill: "none", stroke: color, "stroke-width": w, "stroke-dasharray": dash || "" }));
    const t = ctrl || ini, ang = Math.atan2(fin[1] - t[1], fin[0] - t[0]), s = 11;
    const pt = (da, l) => [fin[0] - Math.cos(ang + da) * l, fin[1] - Math.sin(ang + da) * l];
    const a1 = pt(0.38, s), a2 = pt(-0.38, s);
    svg.appendChild(el("polygon", { points: `${fin[0]},${fin[1]} ${a1[0]},${a1[1]} ${a2[0]},${a2[1]}`, fill: color }));
  }
  function dibujar() {
    const svg = $("svg"); svg.innerHTML = ""; if (!g) return;
    const P = pos(), p = pasos[idx] || null, fase = p ? p.fase : 1, grupo = {};
    if (p) p.completas.forEach((c, i) => c.forEach(v => (grupo[v] = i)));
    const col = {}; for (let v = 1; v <= g.n; v++) col[v] = SIN;
    if (p && fase === 1) { p.terminados.forEach(v => (col[v] = TERM)); p.pila.forEach(v => (col[v] = PILA)); }
    if (p && fase === 2) { p.visitados.forEach(v => (col[v] = VIS2)); p.pila.forEach(v => (col[v] = PILA)); }
    if (p) { for (const v in grupo) col[v] = PALETA[grupo[v] % PALETA.length]; if (p.actual !== null && fase !== 3) col[p.actual] = ACT; }
    let E = A.aristas(g); if (fase === 2) E = E.map(([u, v]) => [v, u]);
    const ex = new Set(E.map(String)), arbol = new Set(p ? p.arbol.map(String) : []);
    for (const [u, v] of E) {
      const k = [u, v].toString(), curva = ex.has([v, u].toString());
      if (fase === 3) {
        const misma = grupo[u] === grupo[v];
        flecha(svg, P[u], P[v], misma ? oscurecer(PALETA[grupo[u] % PALETA.length]) : "#8795a6", misma ? 2.6 : 1.6, misma ? "" : "5 3", curva);
      } else if (p && p.arista && p.arista.toString() === k) flecha(svg, P[u], P[v], "#e3715c", 4, "", curva);
      else if (arbol.has(k)) flecha(svg, P[u], P[v], "#496c93", 2.6, "", curva);
      else flecha(svg, P[u], P[v], "#b9c4d0", 1.4, "4 3", curva);
    }
    for (let v = 1; v <= g.n; v++) {
      const [x, y] = P[v];
      svg.appendChild(el("circle", { cx: x, cy: y, r: R, fill: col[v], stroke: "#40556b", "stroke-width": 2 }));
      svg.appendChild(el("text", { x, y: y + 5, "text-anchor": "middle", "font-weight": 700, "font-size": 16, fill: "#243247" }, v));
      const dx = x - W / 2, dy = y - H / 2, nn = Math.hypot(dx, dy) || 1, lx = x + dx / nn * (R + 18), ly = y + dy / nn * (R + 14) + 4;
      if (p && fase !== 3 && p.terminados.includes(v)) svg.appendChild(el("text", { x: lx, y: ly, "text-anchor": "middle", "font-weight": 700, "font-size": 13, fill: "#496c93" }, `f=${p.terminados.indexOf(v) + 1}`));
      if (p && fase === 3 && v in grupo) svg.appendChild(el("text", { x: lx, y: ly, "text-anchor": "middle", "font-weight": 700, "font-size": 14, fill: oscurecer(PALETA[grupo[v] % PALETA.length]) }, `C${grupo[v] + 1}`));
    }
  }

  function arista(fn, ok, ya) {
    const u = +$("u").value, v = +$("v").value;
    try { const c = fn(g, u, v); if (c) modificado(ok(u, v)); else $("desc").textContent = ya(u, v); }
    catch (e) { $("desc").textContent = "⚠ " + e.message; }
  }
  $("bManual").onclick = iniciarManual; $("bAleat").onclick = iniciarAleatorio; $("bRegen").onclick = regenerar;
  $("bInicio").onclick = () => { detener(); mostrar(false); };
  $("bAdd").onclick = () => arista(A.agregar, (u, v) => `Arista ${u} → ${v} agregada.`, (u, v) => `La arista ${u} → ${v} ya existe.`);
  $("bDel").onclick = () => arista(A.eliminar, (u, v) => `Arista ${u} → ${v} eliminada.`, (u, v) => `La arista ${u} → ${v} no existe.`);
  $("bClr").onclick = () => { A.limpiar(g); modificado("Se eliminaron todas las aristas."); };
  $("bAna").onclick = analizar;
  $("bIni").onclick = () => ir(0); $("bPrev").onclick = () => ir(idx - 1); $("bNext").onclick = () => ir(idx + 1);
  $("bFin").onclick = () => ir(pasos.length - 1); $("bPlay").onclick = reproducir;
  $("n").addEventListener("keydown", e => { if (e.key === "Enter") iniciarAleatorio(); });
  window.addEventListener("keydown", e => { if ($("trabajo").style.display !== "block" || e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;
    if (e.key === "ArrowRight") ir(idx + 1); if (e.key === "ArrowLeft") ir(idx - 1); });
})();
