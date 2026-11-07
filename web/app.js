(function () {
  const A = window.Alg, $ = id => document.getElementById(id);
  const PALETA = ["#68bcc2", "#f3bd6e", "#b99add", "#e7a2a1", "#9bc77e", "#83a8df", "#e6a1c9", "#b5b56b", "#7fb0a0", "#d49b6a", "#9aa7e0", "#c2c2c2"];
  const SIN = "#e8eef5", PILA = "#f4d778", ACT = "#f18a70", TERM = "#9fb8d6", VIS2 = "#c7d5e5";
  const NOMBRE = { 1: "Fase 1 · DFS sobre G (orden de finalización)", 2: "Fase 2 · DFS sobre Gᵀ (una componente por árbol)", 3: "Resultado · grafo original con sus componentes" };
  const TITULO = { 1: "Grafo G", 2: "Grafo transpuesto Gᵀ (aristas invertidas)", 3: "Grafo G con sus componentes" };
  const W = 720, H = 560, R = 24;
  let g = null, modo = "", pasos = [], comps = [], idx = 0, timer = null, sug = [], verSug = false, respaldo = null;

  const oscurecer = c => "#" + [1, 3, 5].map(i => Math.round(parseInt(c.substr(i, 2), 16) * 0.62).toString(16).padStart(2, "0")).join("");
  const el = (tag, attrs = {}, txt) => { const e = document.createElementNS("http://www.w3.org/2000/svg", tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (txt !== undefined) e.textContent = txt; return e; };
  const col = i => PALETA[i % PALETA.length];

  /* ---------- navegación entre vistas ---------- */
  function vista(nombre) {
    if (!["simulador", "guia", "autores"].includes(nombre)) nombre = "simulador";
    document.querySelectorAll(".vista").forEach(v => v.classList.toggle("on", v.id === "v-" + nombre));
    document.querySelectorAll("nav button").forEach(b => (b.dataset.vista === nombre ? b.setAttribute("aria-current", "page") : b.removeAttribute("aria-current")));
    if (nombre !== "simulador") detener();
    if (nombre === "autores" && window.Autores) window.Autores.ir();
    window.scrollTo({ top: 0 });
  }
  document.querySelectorAll("[data-vista]").forEach(b => b.addEventListener("click", e => { e.preventDefault(); history.replaceState(null, "", "#" + b.dataset.vista); vista(b.dataset.vista); }));
  window.addEventListener("hashchange", () => vista(location.hash.slice(1)));

  /* ---------- inicio ---------- */
  function leerN() {
    const t = $("n").value.trim();
    if (!/^\d+$/.test(t) || +t < A.N_MIN || +t > A.N_MAX) { $("err").textContent = `Ingrese un número entero entre ${A.N_MIN} y ${A.N_MAX}.`; return null; }
    $("err").textContent = ""; return +t;
  }
  $("nr").oninput = () => { $("n").value = $("nr").value; $("err").textContent = ""; };
  $("n").oninput = () => { if (/^\d+$/.test($("n").value) && +$("n").value >= 4 && +$("n").value <= 12) $("nr").value = $("n").value; };
  function mostrarTrabajo(si) { $("portada").style.display = si ? "none" : "block"; $("trabajo").style.display = si ? "block" : "none"; window.scrollTo({ top: 0 }); }

  function iniciarManual() {
    const n = leerN(); if (n === null) return;
    detener(); modo = "manual"; g = A.crearGrafo(n); respaldo = null;
    $("manual").style.display = "block"; $("aleat").style.display = "none";
    const opts = Array.from({ length: n }, (_, i) => `<option>${i + 1}</option>`).join("");
    $("u").innerHTML = opts; $("v").innerHTML = opts; $("v").value = "2";
    modificado("Agregue aristas dirigidas (u → v) y pulse «Analizar grafo».");
    mostrarTrabajo(true);
  }
  function iniciarAleatorio() {
    $("err").textContent = "";
    detener(); modo = "aleatorio"; g = A.generarAleatorioLibre(); respaldo = null;
    $("manual").style.display = "none"; $("aleat").style.display = "block";
    modificado(""); analizar(); mostrarTrabajo(true);
  }
  function regenerar() { detener(); respaldo = null; g = A.generarAleatorioLibre(); modificado(""); analizar(); }

  function modificado(msg) {
    detener(); pasos = []; comps = []; idx = 0; sug = []; verSug = false;
    const E = A.aristas(g);
    $("listaAristas").textContent = "Aristas: " + (E.length ? E.map(([u, v]) => `${u}→${v}`).join(", ") : "ninguna");
    $("infoG").textContent = `${g.n} vértices · ${E.length} aristas dirigidas`;
    $("tituloG").textContent = "Grafo G";
    $("sol").textContent = "Pulse «Analizar» o avance con «Siguiente» para ver la solución.";
    $("fase").textContent = ""; $("cont").textContent = ""; $("desc").textContent = msg;
    $("pila").textContent = "Pila DFS: —"; $("vis").textContent = "Visitados: —"; $("ord").textContent = "Orden de finalización: —"; $("comps").textContent = "Componentes: —";
    matriz(); botones(); dibujar(); avanzado();
  }
  function matriz() {
    const M = A.matriz(g); let h = "<table><tr><th></th>";
    for (let j = 1; j <= g.n; j++) h += `<th>${j}</th>`;
    h += "</tr>";
    M.forEach((f, i) => { h += `<tr><td class="u">${i + 1}</td>` + f.map(x => `<td${x ? ' class="uno"' : ""}>${x}</td>`).join("") + "</tr>"; });
    $("mat").innerHTML = h + "</table>";
  }

  /* ---------- ejecución ---------- */
  function analizar() { detener(); const r = A.kosaraju(g); pasos = r.pasos; comps = r.componentes; idx = 0; sug = A.sugerirAristas(g); verSug = false; $("scrub").max = pasos.length - 1; paso(); }
  function ir(i) { detener(); if (pasos.length && i >= 0 && i < pasos.length) { idx = i; paso(); } }
  function detener() { if (timer) { clearInterval(timer); timer = null; } $("bPlay").textContent = "▶ Reproducir"; }
  function reproducir() {
    if (timer) return detener();
    if (!pasos.length) analizar();
    if (idx >= pasos.length - 1) { idx = 0; paso(); }
    $("bPlay").textContent = "⏸ Pausar";
    timer = setInterval(() => { if (idx < pasos.length - 1) { idx++; paso(); } else detener(); }, +$("vel").value);
  }

  function paso() {
    const p = pasos[idx];
    $("fase").textContent = NOMBRE[p.fase]; $("tituloG").textContent = TITULO[p.fase]; $("desc").textContent = p.descripcion;
    $("cont").textContent = `Paso ${idx + 1} de ${pasos.length}`;
    $("barra").style.width = (pasos.length > 1 ? (idx / (pasos.length - 1)) * 100 : 0) + "%"; $("scrub").value = idx;
    $("pila").textContent = "Pila DFS: " + (p.pila.length ? p.pila.join(" → ") : "vacía");
    $("vis").textContent = "Visitados: " + ([...p.visitados].sort((a, b) => a - b).join(", ") || "ninguno");
    $("ord").textContent = p.fase === 2 ? "Por procesar (orden inverso): " + (p.pendientes.join(", ") || "—") : "Orden de finalización: " + (p.terminados.join(", ") || "—");
    let c = p.completas.map((x, i) => `C${i + 1} ${A.fmt(x)}`).join(" · ");
    if (p.componenteActual.length) c += (c ? " · " : "") + `en construcción ${A.fmt(p.componenteActual)}`;
    $("comps").textContent = "Componentes: " + (c || "ninguna aún");
    if (p.fase === 3) solucion(); else $("sol").textContent = "La solución completa aparece al terminar la fase 2 (use «Ver resultado» para saltar al final).";
    botones(); dibujar(); avanzado();
  }
  function solucion() {
    const deb = A.componentesDebiles(g), cruces = A.aristasEntre(g, comps), ok = A.verificar(g, comps);
    $("sol").innerHTML = `<b>Componentes conexas (fuertes): ${comps.length}</b>` +
      comps.map((c, i) => `<div class="c"><span class="chip" style="background:${oscurecer(col(i))}">C${i + 1}</span> ${A.fmt(c)}</div>`).join("") +
      `<div>Débilmente conexas (sin sentido): ${deb.length}</div>` +
      `<div>${cruces.length ? "Aristas entre componentes: " + cruces.map(([a, b]) => `C${a}→C${b}`).join(", ") : "No hay aristas entre componentes distintas."}</div>` +
      `<div>Verificación (cierre transitivo): ${ok ? "correcta ✓" : "¡inconsistente!"}</div>`;
  }
  function botones() {
    const hay = pasos.length > 0;
    $("bIni").disabled = $("bPrev").disabled = !(hay && idx > 0);
    $("bNext").disabled = $("bFin").disabled = !(hay && idx < pasos.length - 1);
    $("scrub").disabled = !hay;
  }

  /* ---------- dibujo del grafo ---------- */
  function pos() {
    const cx = W / 2, cy = H / 2, r = Math.min(W, H) / 2 - 62, o = {};
    for (let v = 1; v <= g.n; v++) { const a = -Math.PI / 2 + 2 * Math.PI * (v - 1) / g.n; o[v] = [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }
    return o;
  }
  function flecha(svg, p, q, color, w, dash, curva, radio = R) {
    const [x1, y1] = p, [x2, y2] = q, dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L;
    let ini, fin, ctrl = null;
    if (curva) {
      const cx = (x1 + x2) / 2 - uy * 0.16 * L, cy = (y1 + y2) / 2 + ux * 0.16 * L;
      const a = Math.hypot(cx - x1, cy - y1) || 1, b = Math.hypot(cx - x2, cy - y2) || 1;
      ini = [x1 + (cx - x1) / a * radio, y1 + (cy - y1) / a * radio]; fin = [x2 + (cx - x2) / b * (radio + 2), y2 + (cy - y2) / b * (radio + 2)]; ctrl = [cx, cy];
    } else { ini = [x1 + ux * radio, y1 + uy * radio]; fin = [x2 - ux * (radio + 2), y2 - uy * (radio + 2)]; }
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
    const cl = {}; for (let v = 1; v <= g.n; v++) cl[v] = SIN;
    if (p && fase === 1) { p.terminados.forEach(v => (cl[v] = TERM)); p.pila.forEach(v => (cl[v] = PILA)); }
    if (p && fase === 2) { p.visitados.forEach(v => (cl[v] = VIS2)); p.pila.forEach(v => (cl[v] = PILA)); }
    if (p) { for (const v in grupo) cl[v] = col(grupo[v]); if (p.actual !== null && fase !== 3) cl[p.actual] = ACT; }
    let E = A.aristas(g); if (fase === 2) E = E.map(([u, v]) => [v, u]);
    const ex = new Set(E.map(String)), arbol = new Set(p ? p.arbol.map(String) : []);
    for (const [u, v] of E) {
      const k = [u, v].toString(), curva = ex.has([v, u].toString());
      if (fase === 3) {
        const misma = grupo[u] === grupo[v];
        flecha(svg, P[u], P[v], misma ? oscurecer(col(grupo[u])) : "#8795a6", misma ? 2.6 : 1.6, misma ? "" : "5 3", curva);
      } else if (p && p.arista && p.arista.toString() === k) flecha(svg, P[u], P[v], "#e3715c", 4, "", curva);
      else if (arbol.has(k)) flecha(svg, P[u], P[v], "#496c93", 2.6, "", curva);
      else flecha(svg, P[u], P[v], "#b9c4d0", 1.4, "4 3", curva);
    }
    if (p && fase === 3 && verSug) for (const [u, v] of sug) flecha(svg, P[u], P[v], "#1e9e5a", 3.4, "9 5", A.aristas(g).some(([a, b]) => a === v && b === u) || sug.some(([a, b]) => a === v && b === u));
    for (let v = 1; v <= g.n; v++) {
      const [x, y] = P[v];
      svg.appendChild(el("circle", { cx: x, cy: y, r: R, fill: cl[v], stroke: "#40556b", "stroke-width": 2 }));
      svg.appendChild(el("text", { x, y: y + 5, "text-anchor": "middle", "font-weight": 700, "font-size": 16, fill: "#243247" }, v));
      const dx = x - W / 2, dy = y - H / 2, nn = Math.hypot(dx, dy) || 1, lx = x + dx / nn * (R + 18), ly = y + dy / nn * (R + 14) + 4;
      if (p && fase !== 3 && p.terminados.includes(v)) svg.appendChild(el("text", { x: lx, y: ly, "text-anchor": "middle", "font-weight": 700, "font-size": 13, fill: "#496c93" }, `f=${p.terminados.indexOf(v) + 1}`));
      if (p && fase === 3 && v in grupo) svg.appendChild(el("text", { x: lx, y: ly, "text-anchor": "middle", "font-weight": 700, "font-size": 14, fill: oscurecer(col(grupo[v])) }, `C${grupo[v] + 1}`));
    }
  }

  /* ---------- diferencial: grafo condensado + asistente de conectividad ---------- */
  function avanzado() {
    const cont = $("avzBody"), fin = pasos.length && pasos[idx].fase === 3;
    if (!fin) { cont.innerHTML = `<div class="vacio" style="grid-column:1/-1">Termine el algoritmo (botón «Ver resultado») para ver el grafo condensado y las aristas sugeridas.</div>`; return; }
    const C = A.condensacion(g, comps), m = A.cotaAumento(g, comps);
    const nom = i => `C${i + 1}`, lista = a => a.length ? a.map(nom).join(", ") : "—";
    const aislada = i => comps[i].length === 1 && !C.ent[i].size && !C.sal[i].size;
    const aislados = C.fuentes.filter(aislada).length;
    cont.innerHTML = `<div><h2 style="margin-bottom:.5rem">Grafo condensado (cada componente = un nodo)</h2><svg id="dag" viewBox="0 0 10 10" role="img" aria-label="Grafo condensado"></svg>
        <div class="mut" style="margin-top:.4rem">Orden topológico: <b>${C.orden.map(nom).join(" → ")}</b> · <span style="color:var(--ok);font-weight:700">● fuente</span> (sin entradas) · <span style="color:var(--warn);font-weight:700">● sumidero</span> (sin salidas)</div></div>
      <div id="asist"></div>`;
    dagSVG(C);
    const a = $("asist");
    if (comps.length === 1) {
      a.innerHTML = `<h2 style="margin-bottom:.5rem">Asistente de conectividad</h2><div class="estado bien"><b>✓ El grafo ya es fuertemente conexo.</b><br>Hay una única componente: desde cualquier vértice se llega a cualquier otro. No hace falta agregar aristas.</div>
        ${respaldo ? '<button class="sec" id="bUndo">↶ Deshacer: volver al grafo original</button>' : ""}`;
    } else {
      a.innerHTML = `<h2 style="margin-bottom:.5rem">Asistente de conectividad</h2>
        <div class="estado mal"><b>Faltan ${m} arista${m > 1 ? "s" : ""}</b> para que el grafo sea fuertemente conexo (hoy tiene ${comps.length} componentes).</div>
        <div class="mut">Aristas sugeridas (de un sumidero a una fuente):</div>
        <div class="sug">${sug.map(([u, v]) => `<span>${u} → ${v}</span>`).join("")}</div>
        <div class="fila"><button class="sec" id="bVer">${verSug ? "Ocultar en el grafo" : "Ver en el grafo"}</button><button class="ok" id="bApl">Aplicar y volver a analizar</button>
          ${respaldo ? '<button class="sec" id="bUndo">↶ Deshacer</button>' : ""}</div>
        <div class="formula">Fuentes: ${lista(C.fuentes)} · Sumideros: ${lista(C.sumideros)}${aislados ? ` · Aislados: ${aislados} (cuentan en ambos)` : ""}<br>
        Cota (Eswaran y Tarjan, 1976): máx(${C.fuentes.length}, ${C.sumideros.length}) = <b>${m}</b>${sug.length === m ? " — las aristas sugeridas alcanzan exactamente ese mínimo." : ""}</div>`;
    }
    const v = $("bVer"); if (v) v.onclick = () => { verSug = !verSug; dibujar(); avanzado(); };
    const ap = $("bApl"); if (ap) ap.onclick = aplicar;
    const un = $("bUndo"); if (un) un.onclick = deshacer;
  }
  function aplicar() {
    respaldo = A.aristas(g);
    for (const [u, v] of sug) A.agregar(g, u, v);
    modificado("Se agregaron las aristas sugeridas. Ejecutando de nuevo el algoritmo…");
    analizar(); ir(pasos.length - 1);
    $("avz").scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
  function deshacer() {
    const e = respaldo; respaldo = null; A.limpiar(g); for (const [u, v] of e) A.agregar(g, u, v);
    modificado("Se restauró el grafo original."); analizar(); ir(pasos.length - 1);
  }
  function dagSVG(C) {
    const svg = $("dag"), cw = 150, ch = 62, nw = 104, nh = 42, maxCapa = Math.max(...C.capa), filas = {};
    C.capa.forEach((c, i) => (filas[c] = filas[c] || []).push(i));
    const maxN = Math.max(...Object.values(filas).map(f => f.length)), Wd = (maxCapa + 1) * cw + 20, Hd = maxN * ch + 20, P = {};
    svg.setAttribute("viewBox", `0 0 ${Wd} ${Hd}`);
    for (const c in filas) filas[c].forEach((i, k) => { const off = (maxN - filas[c].length) * ch / 2; P[i] = [10 + c * cw + nw / 2 + 8, 10 + off + k * ch + ch / 2]; });
    for (const [i, j] of C.aristas) {
      const a = P[i], b = P[j];
      // sale por el borde derecho de i y entra por el izquierdo de j (las capas crecen hacia la derecha)
      flecha(svg, [a[0] + nw / 2, a[1]], [b[0] - nw / 2, b[1]], "#7b8aa0", 1.8, "", false, 0);
    }
    for (let i = 0; i < C.k; i++) {
      const [x, y] = P[i], f = C.fuentes.includes(i), s = C.sumideros.includes(i);
      svg.appendChild(el("rect", { x: x - nw / 2, y: y - nh / 2, width: nw, height: nh, rx: 10, fill: col(i), "fill-opacity": .85, stroke: f && s ? "#7a4fb5" : f ? "#2e8b57" : s ? "#d2691e" : "#52657a", "stroke-width": f || s ? 3 : 1.5 }));
      svg.appendChild(el("text", { x, y: y - 3, "text-anchor": "middle", "font-weight": 800, "font-size": 13, fill: "#1c2535" }, `C${i + 1}`));
      const m = A.fmt(comps[i]); svg.appendChild(el("text", { x, y: y + 12, "text-anchor": "middle", "font-size": 10.5, fill: "#1c2535" }, m.length > 15 ? m.slice(0, 13) + "…}" : m));
    }
  }

  /* ---------- aristas manuales ---------- */
  function arista(fn, ok, ya) {
    const u = +$("u").value, v = +$("v").value;
    try { const c = fn(g, u, v); if (c) modificado(ok(u, v)); else $("desc").textContent = ya(u, v); }
    catch (e) { $("desc").textContent = "⚠ " + e.message; }
  }
  $("bManual").onclick = iniciarManual; $("bAleat").onclick = iniciarAleatorio; $("bRegen").onclick = regenerar;
  $("bInicio").onclick = () => { detener(); mostrarTrabajo(false); };
  $("bAdd").onclick = () => arista(A.agregar, (u, v) => `Arista ${u} → ${v} agregada.`, (u, v) => `La arista ${u} → ${v} ya existe.`);
  $("bDel").onclick = () => arista(A.eliminar, (u, v) => `Arista ${u} → ${v} eliminada.`, (u, v) => `La arista ${u} → ${v} no existe.`);
  $("bClr").onclick = () => { A.limpiar(g); modificado("Se eliminaron todas las aristas."); };
  $("bAna").onclick = analizar;
  $("bIni").onclick = () => ir(0); $("bPrev").onclick = () => ir(idx - 1); $("bNext").onclick = () => ir(idx + 1);
  $("bFin").onclick = () => ir(pasos.length - 1); $("bPlay").onclick = reproducir;
  $("scrub").oninput = () => ir(+$("scrub").value);
  $("vel").onchange = () => { if (timer) { detener(); reproducir(); } };
  $("n").addEventListener("keydown", e => { if (e.key === "Enter") iniciarManual(); });
  window.addEventListener("keydown", e => {
    if (!$("v-simulador").classList.contains("on") || $("trabajo").style.display !== "block") return;
    const t = e.target.tagName; if (t === "INPUT" || t === "SELECT" || t === "TEXTAREA") return;
    if (e.key === "ArrowRight") ir(idx + 1); else if (e.key === "ArrowLeft") ir(idx - 1);
    else if (e.key === " " && t !== "BUTTON") { e.preventDefault(); reproducir(); }
  });
  vista(location.hash.slice(1));
})();
