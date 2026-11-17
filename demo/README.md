# Demo pública del Radar de quejas

Página estática (HTML, CSS y JS, sin build ni servidor) que muestra **informes ya generados** por el agente real.
No llama a OpenAI, ni a una API, ni a Redis: por eso es gratis, estable y rápida.

```
demo/
  index.html        la página (6 pantallas)
  styles.css        diseño: modo claro, colores de Google, tipografías propias
  app.js            filtros cruzados, gráficos SVG, informes, citas y panel de evidencia
  flow.js           el recorrido animado «cómo funciona»
  fonts/            Bricolage Grotesque e Instrument Sans (licencia OFL), para que funcione sin internet
  data/
    reports.json    datos de los informes (legible)
    reports.js      la misma información, para que la página abra con doble clic
```

## Verla en local

Doble clic en `demo/index.html`. Funciona sin servidor porque los datos se cargan desde `data/reports.js`.

## Regenerar los informes

Solo este paso gasta OpenAI (unos centavos: 4 informes con `gpt-4o-mini`).

```powershell
# 1. Datos de entrada (una vez): data/quejas.csv
uv run python scripts/prepare_data.py

# 2. Índice de búsqueda (una vez, o si cambias las quejas)
uv run indexar.py

# 3. Respuestas correctas de la evaluación (opcional, aparecen en la página)
uv run python -m scripts.eval_truth

# 4. Ver qué haría, sin gastar nada
uv run python -m scripts.export_demo --dry

# 5. Generar los informes (llama a OpenAI)
uv run python -m scripts.export_demo

# Solo refrescar las 200 quejas y la evaluación, conservando los informes ya generados (NO llama a OpenAI)
uv run python -m scripts.export_demo --solo-datos
```

## Qué hace la página

Seis pantallas, cada una ocupa toda la altura de la ventana (en móvil crecen para que nada se corte). Navegación con la
barra superior, los puntos laterales o el scroll:

1. **Producto:** qué es, para quién y qué garantiza, con una afirmación real del informe y su cita.
2. **Cómo funciona:** recorrido animado de 10 pasos (pregunta → supervisor → investigador → analista → redactor →
   revisión humana → informe). Usa los datos reales del informe elegido (decisiones del supervisor, quejas consultadas,
   cifras calculadas por código). Se puede reproducir, pausar, avanzar y probar «Pedir cambios».
3. **Datos:** cifras, quejas por año, temas y empresas, con filtros cruzados: pulsa un tema, una empresa o un año y todo
   se recalcula.
4. **Informes:** los 4 informes del agente. Cada cita `[queja N]` abre al lado el texto original, con su empresa, tema y
   fecha, y desde ahí se puede filtrar por ellos.
5. **Quejas:** las 200, con buscador que resalta coincidencias y la queja completa al lado.
6. **Método:** cómo se garantiza la fiabilidad y la evaluación.

Detalles:

- **Diseño:** modo claro, blanco y gris con los cuatro colores de Google. Los colores de las series (azul y rojo) están
  validados para daltonismo; el amarillo se usa solo como decoración porque es demasiado claro para marcas o texto.
- **Accesibilidad:** todo se maneja con teclado (en el gráfico por año, flechas e Intro), cada gráfico tiene una tabla
  equivalente («Ver tabla») y se respeta `prefers-reduced-motion` (sin animaciones ni reproducción automática).
- **Enlaces compartibles:** el informe, los filtros y la queja abierta viven en la URL (por ejemplo
  `index.html#informe=fraude&anio=2022`).
- El gráfico «Quejas por año» muestra una **muestra** de 200 quejas repartidas entre 2017 y 2024, no el total: no
  representa una tendencia real, y la página lo dice.

El script ejecuta el agente real con la revisión humana aprobada automáticamente, y para cada informe guarda el
borrador, las quejas citadas con su texto completo (empresa, tema, fecha) y los conteos por tema.
Si el agente cita un ID de queja que **no existe** en `data/quejas.csv`, el script lo avisa por pantalla y la página
lo muestra marcado con ✗ en lugar de ocultarlo.

Después de regenerar, comprueba a mano 2 o 3 citas: abre `data/quejas.csv`, busca el `complaint_id` y confirma que
la queja dice lo que el informe afirma.

## Publicar en GitHub Pages

GitHub Pages solo deja elegir la raíz del repositorio o la carpeta `/docs`, no `demo/`. La forma más limpia es
publicar con una GitHub Action que sube solo la carpeta `demo/`.

1. Crea el archivo `.github/workflows/pages.yml`:

   ```yaml
   name: Publicar demo
   on:
     push:
       branches: [main]
       paths: ["demo/**"]
     workflow_dispatch:
   permissions:
     contents: read
     pages: write
     id-token: write
   concurrency:
     group: pages
     cancel-in-progress: true
   jobs:
     deploy:
       runs-on: ubuntu-latest
       environment:
         name: github-pages
         url: ${{ steps.deployment.outputs.page_url }}
       steps:
         - uses: actions/checkout@v4
         - uses: actions/configure-pages@v5
         - uses: actions/upload-pages-artifact@v3
           with:
             path: demo
         - id: deployment
           uses: actions/deploy-pages@v4
   ```

2. En GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Haz commit y push a `main`. La URL será `https://<tu-usuario>.github.io/agentic-research/`.

## Qué se publica (y qué no)

- Se publica únicamente la carpeta `demo/`: la página y `data/reports.*`.
- `.env`, `data/quejas.csv` y el índice de Chroma **no** están en `demo/` y no se publican.
- Los textos de las quejas citadas sí van en `reports.json`: son quejas públicas de la CFPB con los datos personales
  ya anonimizados (`XXXX`).
- Los datos vienen de una copia pública del dataset de la CFPB (hasta febrero de 2024), no de la web actual de la CFPB.
