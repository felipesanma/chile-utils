# chile-utils

Repositorio abierto con datasets, catálogos y utilidades reutilizables relacionados con Chile.

La idea de este proyecto es centralizar datos estructurados, simples de consumir y versionados públicamente para desarrolladores, investigadores, civic tech, periodistas, legaltechs y proyectos de análisis o visualización.

---

# Objetivo

Muchos datos públicos en Chile existen:

* dispersos,
* poco normalizados,
* difíciles de consumir,
* o directamente encerrados en PDFs.

Este repositorio busca transformar esos datos en formatos reutilizables y amigables para desarrolladores.

---

# Contenido actual

```txt
pjud/
  cortes.json
  tribunales.json
  competencias.json
  tipos-tribunal.json
superir/
  publicaciones.json.gz
  metadata.json
territorio/
  regiones.json
  provincias.json
  comunas.json
  comunas-con-coordenadas.json
feriados/
  feriados.json
  feriados-2000.json
  feriados-YYYY.json
  metadata.json
  README.md
municipalidades/
  municipalidades.json
  sitios-web.json
  metadata.json
  README.md
```

---

# Datasets actuales

## Poder Judicial (PJUD)

Datasets relacionados con tribunales y cortes del Poder Judicial de Chile.

### cortes.json

Listado oficial de Cortes de Apelaciones.

Ejemplo:

```json
{
  "id": 90,
  "nombre": "C.A. de Santiago"
}
```

---

### tribunales.json

Listado normalizado de tribunales.

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

### competencias.json

Competencias judiciales.

Ejemplo:

```json
{
  "id": "penal",
  "nombre": "Penal"
}
```

---

### tipos-tribunal.json

Clasificación estructurada de tribunales.

Ejemplo:

```json
{
  "id": "juzgado_garantia",
  "nombre": "Juzgado de Garantía",
  "competencias": [
    "penal"
  ]
}
```

---

## SUPERIR / Boletín Concursal

Dataset diario obtenido desde el Boletín Concursal público de Chile.

### publicaciones.json.gz

Archivo JSON comprimido con gzip que contiene las publicaciones disponibles desde el endpoint público del Boletín Concursal.

Ruta:

```txt
superir/publicaciones.json.gz
```

URL raw:

```txt
https://raw.githubusercontent.com/felipesanma/chile-utils/main/superir/publicaciones.json.gz
```

El archivo se actualiza diariamente mediante GitHub Actions y reemplaza la versión anterior cuando hay cambios.

### metadata.json

Metadata de la descarga diaria.

Incluye:

```json
{
  "source_page": "https://www.boletinconcursal.cl/boletin/procedimientos",
  "source_endpoint": "https://www.boletinconcursal.cl/boletin/getRegistroDiarioPublicacionJson",
  "downloaded_at": "2026-05-08T00:00:00+00:00",
  "records_type": "list",
  "compression": "gzip",
  "output_file": "superir/publicaciones.json.gz",
  "records_count": 123
}
```

---

## Territorio

Datasets de división político-administrativa de Chile: regiones, provincias y comunas.

Archivos disponibles:

```txt
territorio/regiones.json
territorio/provincias.json
territorio/comunas.json
territorio/comunas-con-coordenadas.json
```

Fuente:

```txt
https://apis.digital.gob.cl/dpa/
```

Ver documentación específica en:

```txt
territorio/README.md
```

---

## Feriados

Datasets de feriados de Chile desde el año 2000 en adelante, generados desde feriados.io y normalizados en JSON.

Archivos disponibles:

```txt
feriados/feriados.json
feriados/feriados-2000.json
feriados/feriados-YYYY.json
feriados/metadata.json
```

Fuente:

```txt
https://feriados.io/docs
```

La generación se ejecuta manualmente con `scripts/build_feriados.py` usando la variable de entorno `FERIADOS_IO_API_KEY`. Puedes cargarla desde un archivo `.env` local, que está ignorado por Git.

Ver documentación específica en:

```txt
feriados/README.md
```

---

## Municipalidades

Datasets de municipalidades de Chile y sus sitios web institucionales, cruzados con la división político-administrativa del país.

Archivos disponibles:

```txt
municipalidades/municipalidades.json
municipalidades/sitios-web.json
municipalidades/metadata.json
```

Fuente:

```txt
https://www.munichile.cl/
```

Ver documentación específica en:

```txt
municipalidades/README.md
```

---

# Uso

## Consumir desde GitHub

```txt
https://raw.githubusercontent.com/felipesanma/chile-utils/main/pjud/cortes.json
```

---

## Ejemplo JavaScript

```javascript
const response = await fetch(
  "https://raw.githubusercontent.com/felipesanma/chile-utils/main/pjud/tribunales.json"
);

const tribunales = await response.json();

console.log(tribunales);
```

---

## Ejemplo Python con publicaciones comprimidas

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

# Futuras categorías

El objetivo es ir agregando más datasets reutilizables relacionados con Chile.

Posibles futuras categorías:

```txt
municipalidades/
```

---

# Posibles datasets futuros

* Códigos postales
* APIs públicas chilenas
* Datasets judiciales
* Datos regulatorios
* Indicadores públicos
* Leyes y normativa estructurada
* Catálogos gubernamentales
* Datos geográficos

---

# Filosofía

Los datasets de este repositorio buscan ser:

* simples,
* abiertos,
* versionables,
* documentados,
* reutilizables,
* y fáciles de consumir desde cualquier lenguaje.

---

# Licencia

MIT

---

# Descargo

Este proyecto es independiente y no pertenece a ninguna institución pública chilena.

Los datos provienen de fuentes públicas y se publican únicamente con fines de interoperabilidad, transparencia y reutilización tecnológica.
