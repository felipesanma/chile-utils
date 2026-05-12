import json
import locale
import os
from pathlib import Path
import re
import sys
from typing import Any

import requests


SOURCE_BASE_URL = "https://apis.digital.gob.cl/dpa"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "territorio"
ALLOW_INSECURE_TLS = os.environ.get("DPA_ALLOW_INSECURE_TLS") == "1"


if ALLOW_INSECURE_TLS:
    requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]


def fetch_json(path: str) -> list[dict[str, Any]]:
    url = f"{SOURCE_BASE_URL}{path}"
    response = requests.get(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "chile-utils territorio dataset builder",
        },
        timeout=30,
        verify=not ALLOW_INSECURE_TLS,
    )

    if not response.ok:
        raise RuntimeError(f"GET {url} falló con HTTP {response.status_code}")

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"GET {url} no retornó JSON válido") from exc

    if not isinstance(data, list):
        raise RuntimeError(f"GET {url} no retornó una lista JSON")

    return data


def normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    return re.sub(r"\s+", " ", value).strip()


def normalize_code(value: Any, field_name: str) -> str:
    code = normalize_text(value)
    if not code:
        raise RuntimeError(f"Código faltante en campo {field_name}")

    return code


def normalize_coordinate(value: Any) -> float | None:
    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sort_by_name(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        locale.setlocale(locale.LC_COLLATE, "es_CL.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_COLLATE, "es_ES.UTF-8")
        except locale.Error:
            pass

    return sorted(items, key=lambda item: locale.strxfrm(item["nombre"]))


def assert_unique_codes(items: list[dict[str, Any]], dataset_name: str) -> None:
    seen: set[str] = set()
    for item in items:
        code = item["codigo"]
        if code in seen:
            raise RuntimeError(f"Código duplicado en {dataset_name}: {code}")
        seen.add(code)


def normalize_region(sector: dict[str, Any]) -> dict[str, Any]:
    return {
        "codigo": normalize_code(sector.get("codigo"), "codigo"),
        "nombre": normalize_text(sector.get("nombre")),
        "lat": normalize_coordinate(sector.get("lat")),
        "lng": normalize_coordinate(sector.get("lng")),
        "url": normalize_text(sector.get("url")),
    }


def normalize_provincia(sector: dict[str, Any]) -> dict[str, Any]:
    return {
        "codigo": normalize_code(sector.get("codigo"), "codigo"),
        "nombre": normalize_text(sector.get("nombre")),
        "region_codigo": normalize_code(sector.get("codigo_padre"), "codigo_padre"),
        "lat": normalize_coordinate(sector.get("lat")),
        "lng": normalize_coordinate(sector.get("lng")),
        "url": normalize_text(sector.get("url")),
    }


def normalize_comuna(
    sector: dict[str, Any],
    provincia_region_by_codigo: dict[str, str],
) -> dict[str, Any]:
    provincia_codigo = normalize_code(sector.get("codigo_padre"), "codigo_padre")
    region_codigo = provincia_region_by_codigo.get(provincia_codigo)

    if not region_codigo:
        raise RuntimeError(
            "No se encontró región para la provincia "
            f"{provincia_codigo} de la comuna {sector.get('codigo')}"
        )

    return {
        "codigo": normalize_code(sector.get("codigo"), "codigo"),
        "nombre": normalize_text(sector.get("nombre")),
        "provincia_codigo": provincia_codigo,
        "region_codigo": region_codigo,
        "lat": normalize_coordinate(sector.get("lat")),
        "lng": normalize_coordinate(sector.get("lng")),
        "url": normalize_text(sector.get("url")),
    }


def validate_relations(
    provincias: list[dict[str, Any]],
    comunas: list[dict[str, Any]],
    regiones_by_codigo: dict[str, dict[str, Any]],
    provincias_by_codigo: dict[str, dict[str, Any]],
) -> None:
    for provincia in provincias:
        region_codigo = provincia.get("region_codigo")
        if not region_codigo:
            raise RuntimeError(f"Provincia sin region_codigo: {provincia['codigo']}")

        if region_codigo not in regiones_by_codigo:
            raise RuntimeError(
                f"Provincia {provincia['codigo']} referencia región inexistente: "
                f"{region_codigo}"
            )

    for comuna in comunas:
        provincia_codigo = comuna.get("provincia_codigo")
        if not provincia_codigo:
            raise RuntimeError(f"Comuna sin provincia_codigo: {comuna['codigo']}")

        if provincia_codigo not in provincias_by_codigo:
            raise RuntimeError(
                f"Comuna {comuna['codigo']} referencia provincia inexistente: "
                f"{provincia_codigo}"
            )


def write_json(file_name: str, data: list[dict[str, Any]]) -> None:
    path = OUTPUT_DIR / file_name
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if ALLOW_INSECURE_TLS:
        print("DPA_ALLOW_INSECURE_TLS=1 activo: se omitirá validación TLS.")

    raw_regiones = fetch_json("/regiones?limit=1000")
    raw_provincias = fetch_json("/provincias?limit=1000")
    raw_comunas = fetch_json("/comunas?limit=1000")

    regiones = sort_by_name([normalize_region(region) for region in raw_regiones])
    provincias = sort_by_name(
        [normalize_provincia(provincia) for provincia in raw_provincias]
    )
    provincia_region_by_codigo = {
        provincia["codigo"]: provincia["region_codigo"] for provincia in provincias
    }
    comunas_con_coordenadas = sort_by_name(
        [
            normalize_comuna(comuna, provincia_region_by_codigo)
            for comuna in raw_comunas
        ]
    )
    comunas = [
        {
            "codigo": comuna["codigo"],
            "nombre": comuna["nombre"],
            "provincia_codigo": comuna["provincia_codigo"],
            "region_codigo": comuna["region_codigo"],
        }
        for comuna in comunas_con_coordenadas
    ]

    assert_unique_codes(regiones, "regiones")
    assert_unique_codes(provincias, "provincias")
    assert_unique_codes(comunas, "comunas")

    regiones_by_codigo = {region["codigo"]: region for region in regiones}
    provincias_by_codigo = {
        provincia["codigo"]: provincia for provincia in provincias
    }
    validate_relations(
        provincias,
        comunas,
        regiones_by_codigo,
        provincias_by_codigo,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json("regiones.json", regiones)
    write_json("provincias.json", provincias)
    write_json("comunas.json", comunas)
    write_json("comunas-con-coordenadas.json", comunas_con_coordenadas)

    print(f"Regiones: {len(regiones)}")
    print(f"Provincias: {len(provincias)}")
    print(f"Comunas: {len(comunas)}")
    print("Datasets territoriales generados correctamente.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
