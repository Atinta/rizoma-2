#!/bin/sh
# tools/publicar.sh del repositorio Atinta/rizoma-2 (la copia pública del mapa, servida por GitHub Pages e incrustada en benjawilson.com/rizoma).
# Vuelve a generar la copia desde una página publicada y la sube. Sirve desde cualquier sesión que tenga el repositorio y la página:
#
#   sh tools/publicar.sh <pagina.html>
#     <pagina.html>  la página viva del artefacto bajada tal cual (en una sesión de Claude: Artifact → read con path "index.html"),
#                    o rizoma-2.html recién construido en el taller (build2 → ui.py): son la misma página
#
# Hace: tools/publico.py (→ index.html, modo visitante fijo), tools/og.py (→ og.png), tools/tandap.py (la prueba: tiene que terminar en
# «ERRORES: ninguno»), commit «ui.N · datos v2.x.y» y push. Si la página servida ya es esa versión, no hace nada. Nada del repositorio se
# edita a mano: index.html y og.png salen de aquí; tools/ viene copiado del taller (tools/ui/ de la carpeta de trabajo) por su publicar.sh.
# Variable opcional COAUTOR: líneas que se agregan al final del mensaje del commit (p. ej. «Co-Authored-By: …»).
set -e
REPO=$(cd "$(dirname "$0")/.." && pwd)
PAG=${1:?uso: sh tools/publicar.sh <pagina.html>}
[ -f "$PAG" ] || { echo "no existe la página: $PAG"; exit 1; }
[ -d "$REPO/.git" ] || { echo "no es un repositorio: $REPO"; exit 1; }
python3 -I "$REPO/tools/publico.py" "$PAG" "$REPO"
cd "$REPO"
VERSION=$(grep -o 'rizoma-publico:[^ ]*\( · datos v[0-9.]*\)\?' index.html | head -1 | sed 's/rizoma-publico://')
if git diff --quiet -- index.html && [ -z "$(git ls-files --others --exclude-standard -- index.html)" ]; then
  # la página servida ya es esta versión; sólo puede haber cambiado tools/ o el README
  if [ -z "$(git status --porcelain)" ]; then echo "nada que publicar: la copia ya es $VERSION"; exit 0; fi
  MSG="herramientas de publicación (tools/) · la copia sigue en $VERSION"
else
  python3 -I "$REPO/tools/og.py" "$REPO"
  LOG=$(mktemp)
  if python3 -I "$REPO/tools/tandap.py" "$REPO" > "$LOG" 2>&1; then tail -4 "$LOG"; else
    tail -15 "$LOG"; echo "la prueba tandap falló: no se publica (index.html y og.png vuelven a lo servido)"; git checkout -- index.html og.png 2>/dev/null || true; exit 1; fi
  MSG=$VERSION
  [ -z "$(git status --porcelain -- tools README.md 2>/dev/null)" ] || MSG="$MSG · herramientas"
fi
git config user.name >/dev/null 2>&1 || git config user.name "Benjamín Wilson"
git config user.email >/dev/null 2>&1 || git config user.email "benjamin@stickersatinta.com"
git add -A
git commit -q -m "$MSG${COAUTOR:+

$COAUTOR}"
git push -q
echo "publicado: $MSG → https://atinta.github.io/rizoma-2/ (GitHub Pages tarda alrededor de un minuto)"
