# Territorio

Datasets de división político-administrativa de Chile: regiones, provincias y comunas.

La información se normaliza desde la API pública de División Político Administrativa de Gobierno Digital:

```txt
https://apis.digital.gob.cl/dpa/
```

Este proyecto es independiente y no pertenece a Gobierno Digital ni a ninguna institución pública. Los datos provienen de fuentes públicas y se publican con fines de interoperabilidad, transparencia y reutilización tecnológica.

---

# Archivos

## regiones.json

Listado de regiones.

Estructura:

```json
{
  "codigo": "13",
  "nombre": "Metropolitana de Santiago",
  "lat": -33.4417,
  "lng": -70.6541,
  "url": ""
}
```

## provincias.json

Listado de provincias con referencia a su región.

Estructura:

```json
{
  "codigo": "131",
  "nombre": "Santiago",
  "region_codigo": "13",
  "lat": -33.5548,
  "lng": -70.7329,
  "url": ""
}
```

## comunas.json

Listado liviano de comunas con referencia a provincia y región.

Estructura:

```json
{
  "codigo": "13101",
  "nombre": "Santiago",
  "provincia_codigo": "131",
  "region_codigo": "13"
}
```

## comunas-con-coordenadas.json

Listado de comunas con coordenadas y URL de la fuente.

Estructura:

```json
{
  "codigo": "13101",
  "nombre": "Santiago",
  "provincia_codigo": "131",
  "region_codigo": "13",
  "lat": -33.4378,
  "lng": -70.6505,
  "url": ""
}
```

---

# Consumo

Ejemplo usando la URL raw de GitHub:

```javascript
const response = await fetch(
  "https://raw.githubusercontent.com/felipesanma/chile-utils/main/territorio/comunas.json"
);

const comunas = await response.json();

console.log(comunas);
```

---

# Regenerar

Desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
```

```bash
python scripts/build_territorio.py
```

El script descarga la información desde la fuente pública, normaliza los campos, valida relaciones y escribe los JSON formateados con 2 espacios.

Si la fuente oficial presenta problemas temporales de certificado TLS, se puede regenerar de forma explícita con:

```bash
DPA_ALLOW_INSECURE_TLS=1 python scripts/build_territorio.py
```
