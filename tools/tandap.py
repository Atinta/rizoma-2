"""Prueba de la tanda P: la copia pública (tools/ui/publico.py) abre como visitante fuera de claude.ai.
Se le pasa la carpeta donde publico.py dejó index.html (la copia local del repositorio; por defecto, /home/claude/work/publico-prueba). Sin
simular nada —a diferencia de las demás pruebas, aquí no se pone S.noEdit por código—: la página tiene que nacer visitante por sí sola.
Comprueba: modo visitante fijo (S.noEdit, .app.noedit, Lectura, sin Taller ni «Publicar cambios» ni exportar ni el segmento de
disposiciones, perla, portada); la cabecera propia (lang, título, descripción, canonical, og:*, icono) y ninguna petición a cdnjs ni a
claude.ai (D3 desde el mismo sitio); la marca rizoma-publico; que el mapa funciona (abrir, elegir, vecindario, tiempo, ayuda de diez verbos,
Lámina PNG sin error) sin errores de JS; que la tecla T y P/R/C no hacen nada; y lo mismo con un localStorage que trae «taller». Falla
(ERRORES) si algo no se cumple. Viaja copiada a tools/tandap.py del repositorio (la corre su tools/publicar.sh); las capturas van a una
carpeta temporal que se imprime al final."""
import asyncio, os, sys, json, tempfile
from playwright.async_api import async_playwright
DEST = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/work/publico-prueba"); URL = "file://" + os.path.join(DEST, "index.html")
OUT = tempfile.mkdtemp(prefix="rizoma-tandap-")

ESTADO = """() => { const vis = sel => { const e = document.querySelector(sel); if (!e) return null; const cs = getComputedStyle(e); return cs.display !== 'none' && cs.visibility !== 'hidden' && e.getClientRects().length > 0; };
  return { noEdit: S.noEdit, cls: document.querySelector('.app').className, mode: S.mode, theme: document.documentElement.dataset.theme, lang: document.documentElement.lang,
    portada: vis('#ui-portada'), taller: vis('#mode-taller'), lectura: vis('#mode-lectura'), publicar: vis('#btn-save'), layPan: vis('#lay-panorama'), layForce: vis('#lay-force'), exportar: vis('#btn-export'),
    ayuda: vis('#ui-help'), cob: vis('#btn-cobertura'), d3: typeof d3 !== 'undefined' && d3.version, d3src: (document.querySelector('script[src*="d3"]') || {}).getAttribute ? document.querySelector('script[src*="d3"]').getAttribute('src') : null,
    title: document.title, head: { descr: (document.querySelector('head meta[name=description]') || {}).content || null, canon: (document.querySelector('head link[rel=canonical]') || {}).href || null, og: !!document.querySelector('head meta[property="og:title"]'), icon: !!document.querySelector('head link[rel=icon]'), styles: document.querySelectorAll('head style').length, links: document.querySelectorAll('head link[rel=stylesheet]').length, titulosEnBody: document.querySelectorAll('body title').length },
    marca: /rizoma-publico:ui\\.\\d+/.test(document.documentElement.outerHTML.slice(-300)), n: V.nodes.length, hidden: document.querySelectorAll('[hidden]').length, hiddenVisibles: [...document.querySelectorAll('[hidden]')].filter(e => getComputedStyle(e).display !== 'none').length }; }"""

async def sesion(pw, w, h, pre_storage=None):
    b = await pw.chromium.launch(); pg = await b.new_page(viewport={"width": w, "height": h})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); fuera = []
    async def route(r):
        u = r.request.url
        if u.startswith("file://"): await r.continue_()
        else: fuera.append(u); await r.fulfill(status=200, content_type="text/css", body="")
    await pg.route("**/*", route)
    await pg.add_init_script("try { localStorage.clear(); } catch (e) {}" + (f" try {{ {pre_storage} }} catch (e) {{}}" if pre_storage else ""))
    await pg.goto(URL); await pg.wait_for_function("() => typeof G !== 'undefined' && typeof V !== 'undefined'"); await pg.wait_for_timeout(1800)
    return b, pg, errs, fuera

def chk(errs, ok, msg):
    print(("   ok  " if ok else "   MAL ") + msg)
    if not ok: errs.append(msg)

async def main():
    async with async_playwright() as pw:
        b, pg, errs, fuera = await sesion(pw, 1440, 900)
        e = await pg.evaluate(ESTADO); print("1 al abrir", json.dumps({k: e[k] for k in ('noEdit', 'cls', 'mode', 'theme', 'lang', 'portada', 'taller', 'publicar', 'layPan', 'exportar', 'd3', 'd3src', 'n', 'marca')}, ensure_ascii=False))
        print("   peticiones fuera del sitio:", sorted(set(u.split('?')[0] for u in fuera)))
        await pg.screenshot(path=OUT + "/p_portada.png")
        chk(errs, e["noEdit"] is True and "noedit" in e["cls"] and e["mode"] == "lectura", "nace como visitante: S.noEdit, .app.noedit, Lectura")
        chk(errs, e["theme"] == "perla" and e["portada"], "abre en perla y con portada")
        chk(errs, not e["taller"] and not e["publicar"] and not e["layPan"] and not e["layForce"] and not e["exportar"], "sin Taller, sin «Publicar cambios», sin exportar, sin el segmento Panorama · Rizoma · Canva")
        chk(errs, e["ayuda"] and e["cob"], "el «?» y «Qué hay y qué no hay» siguen")
        chk(errs, e["lang"] == "es" and e["title"].startswith("Rizoma 2.0 · Quién") and e["head"]["descr"] and "benjawilson.com/rizoma" in (e["head"]["canon"] or "") and e["head"]["og"] and e["head"]["icon"] and e["head"]["styles"] >= 2 and e["head"]["links"] >= 1 and e["head"]["titulosEnBody"] == 0, f"la cabecera es propia (título, descripción, canonical, og, icono; estilos en head: {e['head']['styles']})")
        chk(errs, e["d3"] and e["d3src"] == "d3.v7.9.0.min.js" and not any("cdnjs" in u or "claude.ai" in u for u in fuera), f"D3 desde el mismo sitio (v{e['d3']}); ninguna petición a cdnjs ni a claude.ai")
        chk(errs, e["marca"] and e["n"] > 2000, f"la marca rizoma-publico está y el mapa dibuja {e['n']} nodos")
        chk(errs, e["hiddenVisibles"] == 0, f"la regla [hidden] sigue valiendo ({e['hidden']} elementos ocultos, {e['hiddenVisibles']} visibles)")
        # 2 · las teclas del editor no hacen nada; el mapa funciona
        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400)
        for k in ["t", "r", "c"]: await pg.keyboard.press(k); await pg.wait_for_timeout(200)
        e = await pg.evaluate(ESTADO); lay = await pg.evaluate("() => S.layout")
        chk(errs, e["mode"] == "lectura" and lay == "panorama" and not e["taller"], "T, R y C no hacen nada (Lectura, Panorama)")
        await pg.evaluate("() => select('galeria-patricia-ready', false)"); await pg.wait_for_timeout(900)
        f = await pg.evaluate("() => { const h = document.getElementById('insp').firstElementChild; return { titulo: (h.querySelector('.node-title') || {}).textContent, acciones: [...h.querySelectorAll('.ui-acciones button')].map(b => b.textContent), tallerActs: getComputedStyle(h.querySelector('.taller-acts')).display, unv: [...h.querySelectorAll('.ui-unv')].some(e => getComputedStyle(e).display !== 'none') }; }")
        chk(errs, f["titulo"] == "Galería Patricia Ready" and f["acciones"][:2] == ["Ver vecindario", "Ver su línea"] and f["tallerActs"] == "none" and not f["unv"], f"la ficha abre como la del visitante ({f['acciones']}; sin Taller ni «por validar»)")
        await pg.click("#i-focus"); await pg.wait_for_timeout(2400)
        v = await pg.evaluate("() => ({ foco: S.focus, n: V.nodes.length, year: S.year, k: +transform.k.toFixed(2) })"); chk(errs, v["foco"] == "galeria-patricia-ready" and v["n"] > 100, f"el vecindario se compone ({v})")
        await pg.screenshot(path=OUT + "/p_vecindario.png")
        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(1200); await pg.keyboard.press("Escape"); await pg.wait_for_timeout(1200)
        await pg.evaluate("() => uiGoYear(2016)"); await pg.wait_for_timeout(1800)
        t = await pg.evaluate("() => ({ year: S.year, banda: !timebar.hidden, n: V.nodes.length })"); chk(errs, t["year"] == 2016 and t["banda"] and t["n"] > 1000, f"el tiempo abre ({t})")
        await pg.click("#t-close"); await pg.wait_for_timeout(900)
        await pg.evaluate("() => uiHelp()"); await pg.wait_for_timeout(300)
        ay = await pg.evaluate("() => ({ verbos: [...mbox.querySelectorAll('.ui-verbos > b')].length, taller: getComputedStyle(mbox.querySelector('.ui-help .taller')).display })"); chk(errs, ay["verbos"] == 10 and ay["taller"] == "none", f"la ayuda del visitante: {ay['verbos']} verbos, sin la sección Taller")
        await pg.evaluate("() => closeModal()")
        # Lámina PNG: fuera del artefacto no hay capacidad de descargas: la lámina se muestra en un modal para guardarla con clic derecho
        await pg.click("#btn-png"); await pg.wait_for_timeout(2500)
        lam = await pg.evaluate("() => ({ modal: modal.style.display !== 'none', img: !!mbox.querySelector('img[src^=\"data:image/png\"]'), texto: (mbox.querySelector('p') || {}).textContent || '' })")
        chk(errs, lam["modal"] and lam["img"] and "clic derecho" in lam["texto"], "Lámina PNG muestra la imagen para guardarla (sin la capacidad de descargas del artefacto)")
        await pg.evaluate("() => closeModal()")
        print("ERRORES:", errs or "ninguno"); await b.close()
        # 3 · con un localStorage que trae «taller» y «dark» (como si fuera el navegador del editor): sigue naciendo visitante, en perla
        b, pg, errs2, fuera2 = await sesion(pw, 1440, 900, "localStorage.setItem('rizoma:mode', 'taller'); localStorage.setItem('rizoma:theme', 'dark'); localStorage.setItem('rizoma:ui', JSON.stringify({ layout: 'canva' }));")
        e = await pg.evaluate(ESTADO); lay = await pg.evaluate("() => S.layout"); print("3 con localStorage del editor", json.dumps({k: e[k] for k in ('noEdit', 'mode', 'theme', 'taller')}, ensure_ascii=False), "layout", lay)
        chk(errs2, e["noEdit"] is True and e["mode"] == "lectura" and e["theme"] == "perla" and not e["taller"] and lay == "panorama", "con «taller», «dark» y «canva» guardados, nace visitante en perla y Panorama igual")
        print("ERRORES (localStorage):", errs2 or "ninguno"); await b.close()
        # 4 · teléfono: abre sin errores
        b, pg, errs3, _ = await sesion(pw, 390, 844)
        e = await pg.evaluate(ESTADO); chk(errs3, e["noEdit"] is True and e["n"] > 1000, f"en teléfono abre como visitante ({e['n']} nodos)")
        print("ERRORES (teléfono):", errs3 or "ninguno", "· capturas en", OUT); await b.close()
        if errs or errs2 or errs3: raise SystemExit(1)
if __name__ == "__main__": asyncio.run(main())
