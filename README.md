# Rizoma 2.0 — copia pública

**Quién se relaciona con quién en las artes visuales chilenas, 1991–hoy.** Un levantamiento de Benjamín Wilson, en borrador y creciendo.

Se lee en **[benjawilson.com/rizoma](https://benjawilson.com/rizoma)** (y a pantalla completa en la dirección de GitHub Pages de este repositorio).

Esto es la **copia pública** del mapa, generada automáticamente: una sola página (`index.html`, ~12,5 MB; viaja comprimida) con sus datos
adentro, D3 al lado (`d3.v7.9.0.min.js`) y una imagen para compartir (`og.png`). El taller donde se edita es otro sitio; aquí **no se edita
nada a mano**: cada versión se vuelve a generar con `tools/publicar.sh` y se sube entera. La última línea de `index.html` dice qué versión
está servida (`<!-- rizoma-publico:ui.N · datos v2.x.y -->`).

Cada hecho del mapa cita su fuente (documental, autodeclarada, declarada o calculada). El mapa no afirma verdades: afirma proveniencias.
Correcciones y hechos nuevos: por ahora, a su autor.

## Cómo se republica

La copia es una foto de la página del taller: cuando el taller publica una versión nueva (datos, interfaz o ediciones), hay que volver a
generarla. Desde cualquier sesión con este repositorio clonado y la página publicada a mano:

    sh tools/publicar.sh <pagina.html>

donde `<pagina.html>` es la página viva del taller bajada tal cual (o el `rizoma-2.html` recién construido: es la misma página). El script
genera `index.html` con el modo visitante fijo (`tools/publico.py`), la imagen para compartir (`tools/og.py`), corre la prueba
(`tools/tandap.py`: tiene que terminar en «ERRORES: ninguno»; si falla, no publica) y hace commit («ui.N · datos v2.x.y») y push. GitHub
Pages sirve la versión nueva alrededor de un minuto después; si la copia ya era esa versión, no hace nada. Las herramientas de `tools/` vienen
copiadas del taller (su `tools/publicar.sh` las copia y corre este); `tools/squarespace-rizoma.html` es el bloque de código de la página de
Squarespace que incrusta la copia.
