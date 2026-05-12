# Feriados

Datasets de feriados de Chile desde el año 2000 en adelante, generados desde feriados.io y normalizados en JSON.

Fuente de datos:

```txt
https://feriados.io/docs
```

Endpoint usado:

```txt
https://api.feriados.io/v1/CL/holidays/{year}
```

Este proyecto es independiente y no pertenece a feriados.io ni a ninguna institución pública chilena. Los datos se publican con fines de interoperabilidad, análisis y reutilización tecnológica.

---

# Archivos

```txt
feriados/
  feriados.json
  feriados-2000.json
  feriados-2001.json
  ...
  feriados-YYYY.json
  metadata.json
  README.md
```

`feriados.json` contiene el consolidado ordenado por fecha ascendente. Los archivos `feriados-YYYY.json` contienen solo los feriados de ese año.

---

# Formato

Cada registro tiene esta estructura:

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

Notas de normalización:

* `fecha` usa formato ISO `YYYY-MM-DD`.
* `tipo` queda en `null` si la API no lo entrega.
* `irrenunciable` se normaliza a boolean o `null`.
* `ambito` usa el valor de la API si existe; si no existe, usa `"nacional"`.
* `pais` siempre es `"CL"`.
* `fuente` siempre es `"feriados.io"`.

---

# Consumo

Consolidado:

```txt
https://raw.githubusercontent.com/felipesanma/chile-utils/main/feriados/feriados.json
```

Archivo anual:

```txt
https://raw.githubusercontent.com/felipesanma/chile-utils/main/feriados/feriados-2026.json
```

Ejemplo JavaScript:

```javascript
const response = await fetch(
  "https://raw.githubusercontent.com/felipesanma/chile-utils/main/feriados/feriados.json"
);

const feriados = await response.json();

console.log(feriados);
```

---

# Generación Manual

Instala dependencias desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
```

Ejecuta el generador:

```bash
cp .env.example .env
```

Edita `.env` con tu API key real y carga las variables antes de ejecutar:

```bash
set -a
source .env
set +a
python scripts/build_feriados.py
```

Ejemplo con año final:

```bash
set -a
source .env
set +a
FERIADOS_END_YEAR=2030 python scripts/build_feriados.py
```

También puedes exportar la variable directamente si no quieres usar `.env`:

```bash
export FERIADOS_IO_API_KEY="frd_tu_api_key"
python scripts/build_feriados.py
```

La API key se lee desde `FERIADOS_IO_API_KEY`. El archivo `.env` está ignorado por Git y no debe commitearse en el repositorio.
