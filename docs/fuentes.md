# Fuentes

Este documento resume las fuentes públicas usadas por los datasets del repositorio y los criterios básicos de normalización.

---

# Criterios Generales

* Mantener nombres en español.
* Usar `snake_case`.
* Mantener códigos oficiales como string.
* Convertir coordenadas a number cuando existan.
* No inventar datos faltantes.
* No incluir datos personales si no son necesarios para el dataset.
* Documentar la fuente y el método de generación.

---

# Territorio

Fuente:

```txt
https://apis.digital.gob.cl/dpa/
```

Uso:

* Regiones.
* Provincias.
* Comunas.
* Coordenadas cuando la fuente las entrega.

Script:

```txt
scripts/build_territorio.py
```

---

# Municipalidades

Fuente principal:

```txt
https://www.munichile.cl/
```

Fuentes complementarias:

```txt
territorio/comunas.json
territorio/regiones.json
```

Uso:

* Cruce institucional por comuna.
* Nombres de municipalidades.
* Sitios web institucionales solo cuando puedan confirmarse desde una fuente confiable.

No se incluyen:

* Alcaldes.
* Concejales.
* Funcionarios.
* Correos personales.
* Teléfonos personales.

Script:

```txt
scripts/build_municipalidades.py
```

---

# Feriados

Fuente:

```txt
https://feriados.io/docs
```

API:

```txt
https://api.feriados.io/v1/CL/holidays/{year}
```

Requiere:

```txt
FERIADOS_IO_API_KEY
```

Script:

```txt
scripts/build_feriados.py
```

---

# SUPERIR / Boletín Concursal

Fuente:

```txt
https://www.boletinconcursal.cl/boletin/procedimientos
```

Endpoint:

```txt
https://www.boletinconcursal.cl/boletin/getRegistroDiarioPublicacionJson
```

Script:

```txt
scripts/download_boletin_json.py
```

Notas:

* El script obtiene cookie de sesión con `requests.Session()`.
* El token CSRF se extrae desde el HTML inicial.
* El archivo generado se guarda comprimido como `superir/publicaciones.json.gz`.

---

# PJUD

Los datasets PJUD existentes corresponden a catálogos normalizados de tribunales, cortes, competencias y tipos de tribunal.

Antes de modificar estos archivos, revisar consistencia de IDs, nombres y relaciones entre cortes, competencias y tribunales.
