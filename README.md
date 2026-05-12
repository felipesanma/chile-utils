# chile-utils

Datasets públicos, simples y versionados sobre Chile, pensados para desarrolladores, investigadores, civic tech, periodistas, legaltechs y proyectos de análisis o visualización.

El objetivo del repositorio es transformar datos públicos dispersos en archivos JSON fáciles de consumir, documentados y estables en el tiempo.

---

# Datasets

```txt
pjud/
  cortes-apelaciones.json
  tribunales.json
  competencias.json
  tipos-tribunal.json

territorio/
  regiones.json
  provincias.json
  comunas.json
  comunas-con-coordenadas.json

municipalidades/
  municipalidades.json
  sitios-web.json
  metadata.json

feriados/
  feriados.json
  feriados-2000.json
  feriados-YYYY.json
  metadata.json

superir/
  publicaciones.json.gz
  metadata.json
```

La estructura se mantiene plana por dataset para que las URLs raw sean estables y fáciles de recordar. Cada carpeta de datos puede tener su propio `README.md` cuando necesita reglas de uso, generación o normalización.

Guía completa de datasets:

```txt
docs/datasets.md
```

Fuentes y criterios de origen:

```txt
docs/fuentes.md
```

Cómo contribuir o regenerar datos:

```txt
docs/contribuciones.md
```

---

# Uso Rápido

Todos los archivos versionados pueden consumirse desde GitHub raw:

```txt
https://raw.githubusercontent.com/felipesanma/chile-utils/main/<ruta-del-archivo>
```

Ejemplo JavaScript:

```javascript
const response = await fetch(
  "https://raw.githubusercontent.com/felipesanma/chile-utils/main/territorio/comunas.json"
);

const comunas = await response.json();

console.log(comunas);
```

Ejemplo Python con JSON comprimido:

```python
import gzip
import json
import urllib.request

url = "https://raw.githubusercontent.com/felipesanma/chile-utils/main/superir/publicaciones.json.gz"

with urllib.request.urlopen(url) as response:
    with gzip.GzipFile(fileobj=response) as gz:
        publicaciones = json.load(gz)

print(len(publicaciones))
```

---

# Regeneración

Instala dependencias:

```bash
python -m pip install -r requirements.txt
```

Scripts disponibles:

```txt
scripts/build_territorio.py
scripts/build_municipalidades.py
scripts/build_feriados.py
scripts/download_boletin_json.py
```

Algunos datasets requieren variables de entorno o acceso a fuentes externas. Revisa `docs/contribuciones.md` y el README específico de cada carpeta antes de regenerar.

---

# Estructura

```txt
docs/
  datasets.md
  fuentes.md
  contribuciones.md

scripts/
  build_*.py
  download_*.py

<dataset>/
  *.json
  metadata.json
  README.md
```

Los datasets quedan en la raíz para priorizar consumo directo. La documentación transversal vive en `docs/`, y los scripts reproducibles viven en `scripts/`.

---

# Principios

* JSON simple y portable.
* Códigos oficiales como string.
* Campos en `snake_case`.
* Archivos formateados con 2 espacios.
* Datos públicos e institucionales.
* Sin datos personales innecesarios.
* Fuentes documentadas.
* Scripts de generación claros y repetibles.

---

# Licencia

MIT

---

# Descargo

Este proyecto es independiente y no pertenece a ninguna institución pública chilena ni a las fuentes de datos utilizadas.

Los datos provienen de fuentes públicas y se publican únicamente con fines de interoperabilidad, transparencia, análisis y reutilización tecnológica.
