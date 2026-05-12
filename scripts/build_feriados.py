from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

import requests


COUNTRY = "CL"
SOURCE = "https://feriados.io/docs"
SOURCE_API = "https://api.feriados.io/v1/CL/holidays/{year}"
START_YEAR = 2000
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "feriados"
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def get_api_key() -> str:
    api_key = os.environ.get("FERIADOS_IO_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Falta FERIADOS_IO_API_KEY. Exporta la variable antes de ejecutar "
            "el script."
        )

    return api_key


def get_end_year() -> int:
    raw_end_year = os.environ.get("FERIADOS_END_YEAR", "").strip()
    if not raw_end_year:
        return datetime.now().year

    try:
        end_year = int(raw_end_year)
    except ValueError as exc:
        raise RuntimeError("FERIADOS_END_YEAR debe ser un año numérico.") from exc

    if end_year < START_YEAR:
        raise RuntimeError(
            f"FERIADOS_END_YEAR debe ser mayor o igual a {START_YEAR}."
        )

    return end_year


def parse_api_error(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "Respuesta de error sin cuerpo JSON estructurado."

    error = payload.get("error")
    if not isinstance(error, dict):
        return "Respuesta de error sin detalle."

    code = error.get("code", "UNKNOWN_ERROR")
    message = error.get("message", "Sin mensaje.")
    status = error.get("status")
    if status is None:
        return f"{code}: {message}"

    return f"{code} ({status}): {message}"


def fetch_year(year: int, api_key: str) -> list[dict[str, Any]]:
    url = SOURCE_API.format(year=year)
    response = requests.get(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "chile-utils feriados dataset builder",
        },
        timeout=30,
    )

    try:
        payload = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Año {year}: la API no respondió JSON válido.") from exc

    if response.status_code in (401, 403):
        raise RuntimeError(
            f"Año {year}: HTTP {response.status_code}. Revisa FERIADOS_IO_API_KEY."
        )

    if not response.ok:
        raise RuntimeError(
            f"Año {year}: HTTP {response.status_code}. {parse_api_error(payload)}"
        )

    if not isinstance(payload, dict):
        raise RuntimeError(f"Año {year}: respuesta JSON inesperada.")

    if payload.get("success") is False:
        raise RuntimeError(f"Año {year}: {parse_api_error(payload)}")

    data = payload.get("data")
    if not isinstance(data, list):
        raise RuntimeError(f"Año {year}: el campo data no es una lista.")

    return data


def first_present(item: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in item:
            return item[key]

    return None


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        value = str(value)

    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def normalize_boolean(value: Any) -> bool | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        if value == 0:
            return False
        if value == 1:
            return True
        raise RuntimeError(f"Valor irrenunciable numérico inválido: {value}")

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "si", "sí", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n"}:
            return False
        raise RuntimeError(f"Valor irrenunciable string inválido: {value}")

    raise RuntimeError(f"Valor irrenunciable inválido: {value}")


def normalize_holiday(item: dict[str, Any], year: int) -> dict[str, Any]:
    fecha = normalize_text(first_present(item, ("date", "fecha")))
    nombre = normalize_text(first_present(item, ("name", "nombre")))
    tipo = normalize_text(first_present(item, ("type", "tipo")))
    ambito = normalize_text(first_present(item, ("scope", "ambito", "region")))

    if not fecha:
        raise RuntimeError(f"Año {year}: feriado sin fecha.")
    if not nombre:
        raise RuntimeError(f"Año {year}: feriado sin nombre para fecha {fecha}.")

    irrenunciable = normalize_boolean(
        first_present(item, ("irrenunciable", "is_irrenunciable"))
    )

    return {
        "fecha": fecha,
        "nombre": nombre,
        "tipo": tipo,
        "irrenunciable": irrenunciable,
        "ambito": ambito or "nacional",
        "pais": COUNTRY,
        "anio": year,
        "fuente": "feriados.io",
    }


def validate_holiday(holiday: dict[str, Any], expected_year: int) -> None:
    fecha = holiday["fecha"]
    nombre = holiday["nombre"]
    anio = holiday["anio"]

    if not DATE_PATTERN.match(fecha):
        raise RuntimeError(f"Fecha con formato inválido: {fecha}")

    date_year = int(fecha[:4])
    if anio != date_year:
        raise RuntimeError(
            f"El año {anio} no coincide con la fecha {fecha}."
        )

    if date_year != expected_year:
        raise RuntimeError(
            f"Archivo anual {expected_year} contiene feriado de {date_year}: "
            f"{fecha} {nombre}"
        )

    if not nombre:
        raise RuntimeError(f"Feriado sin nombre: {fecha}")

    if holiday["irrenunciable"] is not None and not isinstance(
        holiday["irrenunciable"], bool
    ):
        raise RuntimeError(
            f"irrenunciable debe ser boolean o null: {fecha} {nombre}"
        )


def validate_no_duplicates(holidays: list[dict[str, Any]], context: str) -> None:
    seen: set[tuple[str, str]] = set()
    for holiday in holidays:
        key = (holiday["fecha"], holiday["nombre"])
        if key in seen:
            raise RuntimeError(
                f"Duplicado en {context}: {holiday['fecha']} {holiday['nombre']}"
            )
        seen.add(key)


def write_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def main() -> None:
    api_key = get_api_key()
    end_year = get_end_year()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_holidays: list[dict[str, Any]] = []
    files = ["feriados.json"]

    for year in range(START_YEAR, end_year + 1):
        print(f"Descargando feriados de Chile para {year}...")
        raw_holidays = fetch_year(year, api_key)
        holidays = [normalize_holiday(item, year) for item in raw_holidays]
        holidays.sort(key=lambda holiday: holiday["fecha"])

        for holiday in holidays:
            validate_holiday(holiday, year)

        validate_no_duplicates(holidays, f"feriados-{year}.json")

        file_name = f"feriados-{year}.json"
        files.append(file_name)
        write_json(OUTPUT_DIR / file_name, holidays)
        all_holidays.extend(holidays)

    all_holidays.sort(key=lambda holiday: holiday["fecha"])
    validate_no_duplicates(all_holidays, "feriados.json")

    metadata = {
        "source": SOURCE,
        "source_api": SOURCE_API,
        "country": COUNTRY,
        "from_year": START_YEAR,
        "to_year": end_year,
        "generated_at": utc_now_iso(),
        "records_count": len(all_holidays),
        "files": files,
    }

    write_json(OUTPUT_DIR / "feriados.json", all_holidays)
    write_json(OUTPUT_DIR / "metadata.json", metadata)

    print(f"Feriados descargados: {len(all_holidays)}")
    print(f"Archivos generados en {OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
