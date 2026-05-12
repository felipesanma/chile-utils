# Datasets

Catálogo de datasets disponibles en `chile-utils`.

Los datasets se mantienen en carpetas de primer nivel para que las rutas raw sean cortas y estables.

```txt
https://raw.githubusercontent.com/felipesanma/chile-utils/main/<dataset>/<archivo>
```

---

# Territorio

Datasets de división político-administrativa de Chile: regiones, provincias y comunas.

Archivos:

```txt
territorio/regiones.json
territorio/provincias.json
territorio/comunas.json
territorio/comunas-con-coordenadas.json
territorio/README.md
```

Ejemplo:

```json
{
  "codigo": "13101",
  "nombre": "Santiago",
  "provincia_codigo": "131",
  "region_codigo": "13"
}
```

Documentación específica:

```txt
territorio/README.md
```

---

# Municipalidades

Datasets de municipalidades de Chile y sus sitios web institucionales, cruzados con la división político-administrativa del país.

Archivos:

```txt
municipalidades/municipalidades.json
municipalidades/sitios-web.json
municipalidades/metadata.json
municipalidades/README.md
```

Ejemplo:

```json
{
  "comuna_codigo": "13101",
  "comuna_nombre": "Santiago",
  "provincia_codigo": "131",
  "region_codigo": "13",
  "region_nombre": "Metropolitana de Santiago",
  "municipalidad": "Municipalidad de Santiago",
  "sitio_web": null,
  "fuente": "munichile.cl"
}
```

Documentación específica:

```txt
municipalidades/README.md
```

---

# Feriados

Datasets de feriados de Chile desde el año 2000 en adelante, generados desde feriados.io y normalizados en JSON.

Archivos:

```txt
feriados/feriados.json
feriados/feriados-2000.json
feriados/feriados-YYYY.json
feriados/metadata.json
feriados/README.md
```

Ejemplo:

```json
{
  "fecha": "2026-01-01",
  "nombre": "Año Nuevo",
  "tipo": "Civil",
  "irrenunciable": true,
  "ambito": "nacional",
  "pais": "CL",
  "anio": 2026,
  "fuente": "feriados.io"
}
```

Documentación específica:

```txt
feriados/README.md
```

---

# PJUD

Datasets relacionados con tribunales, cortes, competencias y tipos de tribunal del Poder Judicial de Chile.

Archivos:

```txt
pjud/cortes-apelaciones.json
pjud/tribunales.json
pjud/competencias.json
pjud/tipos-tribunal.json
```

Ejemplo:

```json
{
  "id": 992,
  "nombre": "Juzgado de Garantía de Arica",
  "competencia": "penal",
  "corte_id": 10,
  "corte_nombre": "C.A. de Arica"
}
```

---

# SUPERIR / Boletín Concursal

Dataset obtenido desde el Boletín Concursal público de Chile.

Archivos:

```txt
superir/publicaciones.json.gz
superir/metadata.json
```

`publicaciones.json.gz` está comprimido con gzip porque el JSON original supera el tamaño recomendado para Git normal.

Ejemplo Python:

```python
import gzip
import json
import urllib.request

url = "https://raw.githubusercontent.com/felipesanma/chile-utils/main/superir/publicaciones.json.gz"

with urllib.request.urlopen(url) as response:
    with gzip.GzipFile(fileobj=response) as gz:
        publicaciones = json.load(gz)
```
