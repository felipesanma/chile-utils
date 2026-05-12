# Contribuciones

Guía para mantener y extender `chile-utils` sin romper la experiencia de consumo de otros desarrolladores.

---

# Instalación

```bash
python -m pip install -r requirements.txt
```

Si necesitas variables locales, copia el ejemplo:

```bash
cp .env.example .env
```

`.env` está ignorado por Git. No commitees claves ni secretos.

---

# Regenerar Datasets

## Territorio

```bash
python scripts/build_territorio.py
```

Si la fuente DPA presenta problemas temporales de certificado TLS:

```bash
DPA_ALLOW_INSECURE_TLS=1 python scripts/build_territorio.py
```

## Municipalidades

```bash
python scripts/build_municipalidades.py
```

## Feriados

```bash
set -a
source .env
set +a
python scripts/build_feriados.py
```

Con año final:

```bash
FERIADOS_END_YEAR=2030 python scripts/build_feriados.py
```

## SUPERIR / Boletín Concursal

```bash
python scripts/download_boletin_json.py
```

---

# Validaciones Recomendadas

```bash
python -m py_compile scripts/*.py
```

```bash
python - <<'PY'
import json
from pathlib import Path

for path in Path(".").glob("**/*.json"):
    json.loads(path.read_text(encoding="utf-8"))
    print(f"OK {path}")
PY
```

```bash
git diff --check
```

---

# Convenciones

* JSON formateado con 2 espacios.
* Claves en `snake_case`.
* Códigos oficiales como string.
* Fechas en ISO `YYYY-MM-DD`.
* Timestamps en UTC.
* Archivos grandes comprimidos con gzip cuando sea necesario.
* README específico dentro de cada carpeta de dataset cuando el dataset tenga reglas propias.

---

# Privacidad

No agregar datos personales salvo que sean estrictamente necesarios y exista una justificación clara.

Evitar:

* Nombres de autoridades o funcionarios.
* Correos personales.
* Teléfonos personales.
* RUT u otros identificadores personales.

Preferir siempre información institucional pública y estable.

---

# Nuevos Datasets

Al agregar un dataset nuevo:

1. Crear carpeta propia.
2. Agregar JSON normalizado.
3. Agregar `metadata.json` cuando aplique.
4. Agregar README específico.
5. Agregar script reproducible en `scripts/` si el dataset se genera desde una fuente externa.
6. Actualizar `README.md`.
7. Actualizar `docs/datasets.md`.
8. Actualizar `docs/fuentes.md`.

Mantén los archivos del dataset en una carpeta de primer nivel. Evita mover datasets existentes salvo que sea imprescindible, porque eso rompe URLs raw usadas por terceros.
