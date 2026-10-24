"""La imagen para compartir de la copia pública (og.png, 1200×630): el Panorama en frío, como lo ve el visitante.

    python3 -I og.py <carpeta destino>      # lee <destino>/index.html y deja <destino>/og.png

Viaja copiado a tools/ del repositorio junto con publico.py (lo copia tools/publicar.sh del taller).
"""
import asyncio, os, sys
from playwright.async_api import async_playwright
if len(sys.argv) < 2: sys.exit(__doc__)
DEST = os.path.abspath(sys.argv[1])
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        await pg.goto("file://" + os.path.join(DEST, "index.html")); await pg.wait_for_function("() => typeof G !== 'undefined' && typeof V !== 'undefined'"); await pg.wait_for_timeout(2500)
        if await pg.query_selector("#ui-p-mapa"): await pg.click("#ui-p-mapa"); await pg.wait_for_timeout(600)
        await pg.evaluate("() => fit(false)"); await pg.wait_for_timeout(1200)
        await pg.screenshot(path=os.path.join(DEST, "og.png"))
        await b.close(); print("og.png listo:", os.path.join(DEST, "og.png"))
asyncio.run(main())
