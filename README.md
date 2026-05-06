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

# Futuras categorías

El objetivo es ir agregando más datasets reutilizables relacionados con Chile.

Posibles futuras categorías:

```txt
municipalidades/
regiones/
comunas/
```

---

# Posibles datasets futuros

* Comunas y regiones
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

