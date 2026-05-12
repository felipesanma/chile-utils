# Municipalidades

Datasets de municipalidades de Chile y sus sitios web institucionales, cruzados con la división político-administrativa del país.

Fuente principal:

```txt
https://www.munichile.cl/
```

La base territorial se cruza con:

```txt
territorio/comunas.json
territorio/regiones.json
```

Este dataset se centra en la institución municipal. No incluye alcaldes, concejales, funcionarios, correos personales ni teléfonos personales.

---

# Archivos

```txt
municipalidades/
  municipalidades.json
  sitios-web.json
  metadata.json
  README.md
```

## municipalidades.json

Directorio normalizado de municipalidades.

Estructura:

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

## sitios-web.json

Vista liviana para sitios web institucionales.

Estructura:

```json
{
  "comuna_codigo": "13101",
  "comuna_nombre": "Santiago",
  "municipalidad": "Municipalidad de Santiago",
  "sitio_web": null
}
```

`sitio_web` puede ser `null` cuando no existe o no pudo confirmarse desde una fuente institucional confiable.

## metadata.json

Metadata de generación.

---

# Consumo

Directorio completo:

```txt
https://raw.githubusercontent.com/felipesanma/chile-utils/main/municipalidades/municipalidades.json
```

Sitios web:

```txt
https://raw.githubusercontent.com/felipesanma/chile-utils/main/municipalidades/sitios-web.json
```

Ejemplo JavaScript:

```javascript
const response = await fetch(
  "https://raw.githubusercontent.com/felipesanma/chile-utils/main/municipalidades/municipalidades.json"
);

const municipalidades = await response.json();

console.log(municipalidades);
```

---

# Generación Manual

Desde la raíz del repositorio:

```bash
python scripts/build_municipalidades.py
```

El script lee los datasets territoriales, cruza cada municipalidad con su comuna, valida duplicados y genera JSON formateado con 2 espacios.

---

# Descargo

Este proyecto es independiente y no pertenece a MUNICHILE, SUBDERE ni a ninguna institución pública chilena.

Los datos provienen de fuentes públicas y se publican con fines de interoperabilidad, análisis y reutilización tecnológica.
