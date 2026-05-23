from datetime import datetime, timezone
import gzip
import json
import os
from pathlib import Path
import re
import sys

import requests


SOURCE_PAGE = "https://www.boletinconcursal.cl/boletin/procedimientos"
SOURCE_ENDPOINT = "https://www.boletinconcursal.cl/boletin/getRegistroDiarioPublicacionCsv"
DATA_DIR = Path(__file__).resolve().parents[1] / "superir"
PUBLICACIONES_PATH = DATA_DIR / "publicaciones.csv.gz"
METADATA_PATH = DATA_DIR / "metadata.json"
LEGACY_PUBLICACIONES_PATHS = (
    DATA_DIR / "publicaciones.json",
    DATA_DIR / "publicaciones.json.gz",
    DATA_DIR / "publicaciones.csv",
)
ALLOW_INSECURE_TLS = os.environ.get("SUPERIR_ALLOW_INSECURE_TLS") == "1"


if ALLOW_INSECURE_TLS:
    requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]


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


def request_with_tls_context(method: str, session: requests.Session, url: str, **kwargs):
    try:
        return session.request(
            method,
            url,
            verify=not ALLOW_INSECURE_TLS,
            **kwargs,
        )
    except requests.exceptions.SSLError as exc:
        raise RuntimeError(
            "Falló la validación TLS al conectar con el Boletín Concursal. "
            "Si la fuente presenta un problema temporal de certificado, ejecuta "
            "con SUPERIR_ALLOW_INSECURE_TLS=1."
        ) from exc


def count_csv_records(csv_text: str) -> int | None:
    lines = [line for line in csv_text.splitlines() if line.strip()]
    if len(lines) < 2:
        return None

    return len(lines) - 1


def main() -> None:
    if ALLOW_INSECURE_TLS:
        print("SUPERIR_ALLOW_INSECURE_TLS=1 activo: se omitirá validación TLS.")

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
    initial_response = request_with_tls_context(
        "GET",
        session,
        SOURCE_PAGE,
        headers=headers,
        timeout=30,
    )
    ensure_success(initial_response, "La descarga de la página inicial")

    csrf_token = extract_csrf_token(initial_response.text)
    print("Token CSRF encontrado.")

    post_headers = {
        "User-Agent": headers["User-Agent"],
        "Accept": "text/csv, text/plain, */*; q=0.01",
        "Accept-Language": headers["Accept-Language"],
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.boletinconcursal.cl",
        "Referer": SOURCE_PAGE,
    }

    print(f"Descargando CSV desde endpoint: {SOURCE_ENDPOINT}")
    csv_response = request_with_tls_context(
        "POST",
        session,
        SOURCE_ENDPOINT,
        data={"_csrf": csrf_token},
        headers=post_headers,
        timeout=30,
    )
    ensure_success(csv_response, "La descarga del CSV")

    csv_text = csv_response.text
    if not csv_text.strip():
        raise RuntimeError("La respuesta del endpoint CSV está vacía.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for legacy_path in LEGACY_PUBLICACIONES_PATHS:
        legacy_path.unlink(missing_ok=True)

    with gzip.open(PUBLICACIONES_PATH, "wt", encoding="utf-8") as output_file:
        output_file.write(csv_text)

    metadata = {
        "source_page": SOURCE_PAGE,
        "source_endpoint": SOURCE_ENDPOINT,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "records_type": "csv",
        "compression": "gzip",
        "output_file": str(PUBLICACIONES_PATH.relative_to(DATA_DIR.parent)),
    }
    records_count = count_csv_records(csv_text)
    if records_count is not None:
        metadata["records_count"] = records_count

    METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"CSV guardado en {PUBLICACIONES_PATH}")
    print(f"Metadata guardada en {METADATA_PATH}")
    if records_count is not None:
        print(f"Registros aproximados descargados: {records_count}")
    print("Descarga completada correctamente.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
