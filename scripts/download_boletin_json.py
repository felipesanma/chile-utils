from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import re

import requests


SOURCE_PAGE = "https://www.boletinconcursal.cl/boletin/procedimientos"
SOURCE_ENDPOINT = (
    "https://www.boletinconcursal.cl/boletin/getRegistroDiarioPublicacionJson"
)
DATA_DIR = Path(__file__).resolve().parents[1] / "superir"
PUBLICACIONES_PATH = DATA_DIR / "publicaciones.json.gz"
LEGACY_PUBLICACIONES_PATH = DATA_DIR / "publicaciones.json"
METADATA_PATH = DATA_DIR / "metadata.json"


def extract_csrf_token(html: str) -> str:
    match = re.search(
        r'<meta\s+[^>]*name=["\']_csrf["\'][^>]*content=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    if not match:
        match = re.search(
            r'<meta\s+[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']_csrf["\']',
            html,
            re.IGNORECASE,
        )

    if not match:
        raise RuntimeError("No se encontró el token CSRF en el HTML inicial.")

    return match.group(1)


def ensure_success(response: requests.Response, context: str) -> None:
    if not response.ok:
        raise RuntimeError(
            f"{context} falló con HTTP {response.status_code}: {response.text[:500]}"
        )


def main() -> None:
    session = requests.Session()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; chile-utils/1.0; "
            "+https://github.com/felipesanma/chile-utils)"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
    }

    print(f"Descargando página inicial: {SOURCE_PAGE}")
    initial_response = session.get(SOURCE_PAGE, headers=headers, timeout=30)
    ensure_success(initial_response, "La descarga de la página inicial")

    csrf_token = extract_csrf_token(initial_response.text)
    print("Token CSRF encontrado.")

    post_headers = {
        "User-Agent": headers["User-Agent"],
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": headers["Accept-Language"],
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.boletinconcursal.cl",
        "Referer": SOURCE_PAGE,
    }

    print(f"Descargando JSON desde endpoint: {SOURCE_ENDPOINT}")
    json_response = session.post(
        SOURCE_ENDPOINT,
        data={"_csrf": csrf_token},
        headers=post_headers,
        timeout=30,
    )
    ensure_success(json_response, "La descarga del JSON")

    try:
        records = json.loads(json_response.text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("La respuesta del endpoint no es JSON válido.") from exc

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LEGACY_PUBLICACIONES_PATH.unlink(missing_ok=True)

    json_payload = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    with gzip.open(PUBLICACIONES_PATH, "wt", encoding="utf-8") as output_file:
        output_file.write(json_payload)

    metadata = {
        "source_page": SOURCE_PAGE,
        "source_endpoint": SOURCE_ENDPOINT,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "records_type": type(records).__name__,
        "compression": "gzip",
        "output_file": str(PUBLICACIONES_PATH.relative_to(DATA_DIR.parent)),
    }
    if isinstance(records, list):
        metadata["records_count"] = len(records)

    METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"JSON guardado en {PUBLICACIONES_PATH}")
    print(f"Metadata guardada en {METADATA_PATH}")
    if isinstance(records, list):
        print(f"Registros descargados: {len(records)}")
    print("Descarga completada correctamente.")


if __name__ == "__main__":
    main()
