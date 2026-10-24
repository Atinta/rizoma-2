"""La copia pública de la página (tanda P): una página publicada → <destino>/index.html, lista para servirse fuera de claude.ai.

    python3 -I publico.py <pagina.html> <carpeta destino>
      <pagina.html>     la página viva del artefacto bajada tal cual (en una sesión de Claude: Artifact → read con path "index.html")
                        o el rizoma-2.html recién construido por build2 → ui.py: son la misma página
      <carpeta destino> la copia local del repositorio Atinta/rizoma-2 (escribe index.html y, si faltan, d3.v7.9.0.min.js y .nojekyll)

Vive en tools/ui/ del taller y viaja copiado a tools/ del repositorio (lo copia tools/publicar.sh), así que no depende de dónde está ni de
ui.py: cualquier sesión con el repositorio y la página viva puede republicar (`sh tools/publicar.sh <pagina.html>` dentro del repositorio).

La página publicada en el artefacto es el taller de Benjamín: dentro de claude.ai pregunta al entorno quién la abre y al dueño le da el
Taller. Fuera del artefacto esa pregunta no existe y la página abriría en modo editor para cualquiera. La copia pública es la misma página
(misma versión de datos y de interfaz) con cuatro diferencias, todas comprobadas por tandap.py:
  1. modo visitante fijo: S.noEdit desde el primer cuadro, la app con la clase `noedit`, siempre en Lectura y Panorama (sin Taller, sin
     «Publicar cambios», sin exportar, en perla y con portada);
  2. cabecera propia (lang, título, descripción, etiquetas para compartir, icono) en vez de la del servicio de artefactos, con un esqueleto
     propio y fijo que conserva la regla `[hidden]{display:none!important}` de la que la página depende (el del servicio cambia de vez en
     cuando; con el fijo, la copia sale igual desde la página viva y desde rizoma-2.html);
  3. D3 servido desde el mismo sitio (d3.v7.9.0.min.js junto a index.html) en vez de cdnjs;
  4. una marca `<!-- rizoma-publico:ui.N · datos v2.x.y -->` al final, para saber qué versión está servida.
No toca datos ni interfaz: si algo de esto tiene que cambiar, cambia aquí (tools/ui/publico.py del taller), nunca en index.html a mano.
"""
import json, os, re, shutil, sys

URL = "https://benjawilson.com/rizoma"            # la dirección pública (la página de Squarespace que incrusta la copia)
SITIO = "https://atinta.github.io/rizoma-2/"       # donde se sirve la copia (GitHub Pages)
TITULO = "Rizoma 2.0 · Quién se relaciona con quién en las artes visuales chilenas, 1991–hoy"
DESCR = ("Mapa interactivo del ecosistema cultural chileno desde 1991: galerías, museos, fondos públicos, ferias, artistas y la gente a cargo, "
         "con cada hecho citando su fuente. Un levantamiento de Benjamín Wilson, en borrador y creciendo.")
ICONO = ("data:image/svg+xml," + "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='13' fill='none' "
         "stroke='%23b2452f' stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='4.5' fill='%23b2452f'/%3E%3C/svg%3E")
# el esqueleto que el servicio de artefactos pone alrededor de la página, fijado aquí (la página cuenta con la regla [hidden] y el margen 0)
ESQUELETO = (":root{color-scheme:light}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#faf9f5;color:#141413}"
             "img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}")
D3 = "d3.v7.9.0.min.js"


def version_datos(html):
    """La última versión de datos («v2.x.y — …») del historial de la página, o ''."""
    try:
        ed = json.loads(re.search(r'<script id="edits-data" type="application/json">(.*?)</script>', html, re.S).group(1))
        vs = sorted((h.get("fecha", ""), h.get("nota", "")) for h in ed.get("historial", []) if re.match(r"v\d", h.get("nota", "")))
        return re.match(r"v\d+\.\d+\.\d+", vs[-1][1]).group(0) if vs else ""
    except Exception:
        return ""


def publico(html, datos=""):
    def once(old, new, label):
        nonlocal html
        n = html.count(old)
        assert n == 1, f"[publico] {label}: el anclaje aparece {n} veces"
        html = html.replace(old, new)

    mark = re.search(r"<!-- rizoma-ui:(ui\.\d+) -->", html)
    assert mark, "[publico] la página no lleva la marca de la capa de interfaz (¿es la página publicada, con ui.py corrido?)"
    ui = mark.group(1)

    # 2 · la cabecera: lo que el servicio de artefactos pone antes del <body> se reemplaza por una cabecera propia;
    #     el título, la descripción y las hojas de estilo que la página trae al principio del cuerpo pasan a <head>
    i = html.find("<body>")
    assert 0 < i < 2000, "[publico] no encuentro el <body> de la cabecera del servicio al principio de la página"
    cuerpo = html[i + len("<body>"):]
    j = cuerpo.find('<div class="app">')
    assert 0 < j < 80000, "[publico] no encuentro el principio de la app"
    cabeza = cuerpo[:j]   # <title>, <meta description>, <link>s y la hoja principal
    cabeza = re.sub(r"<title>.*?</title>\s*", "", cabeza, count=1, flags=re.S)
    cabeza = re.sub(r'<meta name="description"[^>]*>\s*', "", cabeza, count=1)
    head = ("<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
            f"<title>{TITULO}</title>\n<meta name=\"description\" content=\"{DESCR}\">\n"
            f"<link rel=\"canonical\" href=\"{URL}\">\n<link rel=\"icon\" href=\"{ICONO}\">\n"
            f"<meta property=\"og:type\" content=\"website\">\n<meta property=\"og:title\" content=\"{TITULO}\">\n<meta property=\"og:description\" content=\"{DESCR}\">\n"
            f"<meta property=\"og:url\" content=\"{URL}\">\n<meta property=\"og:image\" content=\"{SITIO}og.png\">\n<meta property=\"og:locale\" content=\"es_CL\">\n"
            "<meta name=\"twitter:card\" content=\"summary_large_image\">\n"
            f"<style>{ESQUELETO}</style>\n" + cabeza.strip() + "\n</head>\n<body>\n")
    html = head + cuerpo[j:]

    # 1 · modo visitante fijo
    once('<div class="app">', '<div class="app noedit">', "la app nace como visitante")
    once("layout: 'panorama', focus: null, foci: [], depth: 1,", "noEdit: true, layout: 'panorama', focus: null, foci: [], depth: 1,", "S.noEdit desde el principio")
    once("S.mode = (() => { try { return localStorage.getItem('rizoma:mode') || 'lectura'; } catch (e) { return 'lectura'; } })();",
         "S.mode = 'lectura';   /* copia pública: siempre Lectura */", "siempre Lectura")
    once("if (s.layout) S.layout = s.layout;  if (s.glifo) S.glifo = s.glifo;", "if (s.glifo) S.glifo = s.glifo;   /* copia pública: siempre Panorama */", "siempre Panorama")

    # 3 · D3 desde el mismo sitio
    once('<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"', f'<script src="{D3}"', "D3 local")

    # 4 · la marca
    k = html.rindex("</body></html>")
    html = html[:k] + f"<!-- rizoma-publico:{ui}{(' · datos ' + datos) if datos else ''} -->\n" + html[k:]
    return html, ui


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dest = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(dest, exist_ok=True)
    html = open(src, encoding="utf-8").read()
    datos = version_datos(html)
    out, ui = publico(html, datos)
    open(os.path.join(dest, "index.html"), "w", encoding="utf-8").write(out)
    if not os.path.exists(os.path.join(dest, D3)):   # el repositorio ya lo trae; en una carpeta nueva se copia desde el taller
        aqui = os.path.dirname(os.path.abspath(__file__))
        fuentes = [os.path.join(aqui, "..", "vendor", D3), os.path.join(aqui, "vendor", D3)]
        d3 = next((f for f in fuentes if os.path.exists(f)), None)
        assert d3, f"[publico] falta {D3} en {dest} y no está en tools/vendor/: cópialo del taller"
        shutil.copy(d3, os.path.join(dest, D3))
    nj = os.path.join(dest, ".nojekyll")
    if not os.path.exists(nj): open(nj, "w").close()
    print(f"publico: {ui}{' · datos ' + datos if datos else ''} → {os.path.join(dest, 'index.html')} ({len(out) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
