from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlparse


SOURCE = "https://www.munichile.cl/"
SOURCE_NAME = "munichile.cl"
COUNTRY = "CL"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "municipalidades"
TERRITORIO_DIR = Path(__file__).resolve().parents[1] / "territorio"
EXCLUDED_COMUNA_CODES = {
    # MUNICHILE referencia 345 municipios. La comuna Antártica no tiene
    # municipalidad propia y se administra desde Cabo de Hornos.
    "12202",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_url(value: Any) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        value = str(value)

    value = re.sub(r"\s+", "", value).strip()
    if not value:
        return None

    if not value.startswith(("https://", "http://")):
        value = f"https://{value}"

    value = value.rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeError(f"URL inválida: {value}")

    return value


def make_municipality_name(comuna_nombre: str) -> str:
    return f"Municipalidad de {comuna_nombre}"


def validate_unique_comuna_codes(records: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for record in records:
        comuna_codigo = record["comuna_codigo"]
        if comuna_codigo in seen:
            raise RuntimeError(f"comuna_codigo duplicado: {comuna_codigo}")
        seen.add(comuna_codigo)


def validate_record(record: dict[str, Any], valid_comuna_codes: set[str]) -> None:
    required_fields = (
        "comuna_codigo",
        "comuna_nombre",
        "region_codigo",
        "municipalidad",
    )
    for field in required_fields:
        if not record.get(field):
            raise RuntimeError(
                f"Registro sin {field}: {record.get('comuna_codigo')}"
            )

    if record["comuna_codigo"] not in valid_comuna_codes:
        raise RuntimeError(
            f"comuna_codigo inexistente en territorio/comunas.json: "
            f"{record['comuna_codigo']}"
        )

    sitio_web = record.get("sitio_web")
    if sitio_web is not None:
        normalize_url(sitio_web)


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def main() -> None:
    comunas = read_json(TERRITORIO_DIR / "comunas.json")
    regiones = read_json(TERRITORIO_DIR / "regiones.json")

    if not isinstance(comunas, list):
        raise RuntimeError("territorio/comunas.json debe contener una lista.")
    if not isinstance(regiones, list):
        raise RuntimeError("territorio/regiones.json debe contener una lista.")

    valid_comuna_codes = {comuna["codigo"] for comuna in comunas}
    region_names = {region["codigo"]: region["nombre"] for region in regiones}
    missing_websites: list[str] = []
    invalid_websites: list[str] = []
    unmatched: list[str] = []
    records: list[dict[str, Any]] = []

    for comuna in comunas:
        comuna_codigo = comuna["codigo"]
        if comuna_codigo in EXCLUDED_COMUNA_CODES:
            print(
                "Comuna fuera del dataset municipal por no tener municipalidad "
                f"propia: {comuna_codigo} {comuna['nombre']}"
            )
            continue

        region_codigo = comuna["region_codigo"]
        region_nombre = region_names.get(region_codigo)
        if not region_nombre:
            unmatched.append(f"{comuna_codigo} {comuna['nombre']}")
            continue

        sitio_web = normalize_url(None)
        if sitio_web is None:
            missing_websites.append(f"{comuna_codigo} {comuna['nombre']}")

        record = {
            "comuna_codigo": comuna_codigo,
            "comuna_nombre": comuna["nombre"],
            "provincia_codigo": comuna["provincia_codigo"],
            "region_codigo": region_codigo,
            "region_nombre": region_nombre,
            "municipalidad": make_municipality_name(comuna["nombre"]),
            "sitio_web": sitio_web,
            "fuente": SOURCE_NAME,
        }
        records.append(record)

    records.sort(key=lambda item: (item["region_codigo"], item["comuna_nombre"]))
    validate_unique_comuna_codes(records)

    for record in records:
        try:
            validate_record(record, valid_comuna_codes)
        except RuntimeError as exc:
            if "URL inválida" in str(exc):
                invalid_websites.append(
                    f"{record['comuna_codigo']} {record['comuna_nombre']}"
                )
            else:
                raise

    if len(records) < 300:
        raise RuntimeError(
            f"Se generaron menos de 300 municipalidades: {len(records)}"
        )

    sitios_web = [
        {
            "comuna_codigo": record["comuna_codigo"],
            "comuna_nombre": record["comuna_nombre"],
            "municipalidad": record["municipalidad"],
            "sitio_web": record["sitio_web"],
        }
        for record in records
    ]
    metadata = {
        "source": SOURCE,
        "description": (
            "Directorio normalizado de municipalidades y sitios web "
            "institucionales de Chile."
        ),
        "country": COUNTRY,
        "records_count": len(records),
        "generated_at": utc_now_iso(),
        "files": [
            "municipalidades.json",
            "sitios-web.json",
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "municipalidades.json", records)
    write_json(OUTPUT_DIR / "sitios-web.json", sitios_web)
    write_json(OUTPUT_DIR / "metadata.json", metadata)

    print(f"Total de comunas procesadas: {len(comunas)}")
    print(f"Total de municipalidades generadas: {len(records)}")
    print(f"Comunas sin sitio web encontrado: {len(missing_websites)}")
    print(f"Sitios web que no pudieron validarse: {len(invalid_websites)}")
    if unmatched:
        print("Comunas que no pudieron cruzarse con región:")
        for item in unmatched:
            print(f"- {item}")
    if missing_websites:
        print("Advertencia: hay municipalidades sin sitio web confirmado.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
