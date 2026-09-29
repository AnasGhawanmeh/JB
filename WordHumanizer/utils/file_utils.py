"""File validation and naming helpers."""

import re
import shutil
import subprocess
import zipfile
from pathlib import Path

MAX_UNCOMPRESSED_BYTES = 1024 * 1024 * 1024  # 1 GB, zip-bomb guard
MAX_COMPRESSION_RATIO = 200


class InvalidDocumentError(ValueError):
    pass


def safe_filename(name, default="document.docx"):
    name = Path(name or "").name
    name = re.sub(r"[^\w.\- ]+", "_", name).strip(" .")
    return name or default


def output_name(input_name, suffix="processed"):
    path = Path(safe_filename(input_name))
    return f"{path.stem}_{suffix}.docx"


def validate_docx(path, max_bytes=None):
    """Check that ``path`` really is a Word .docx package.

    Checks extension, size, ZIP signature, required parts, macros and a
    zip-bomb heuristic. Raises InvalidDocumentError on failure.
    """
    path = Path(path)
    if path.suffix.lower() != ".docx":
        raise InvalidDocumentError("Only .docx files are supported (convert .doc files first).")
    size = path.stat().st_size
    if size == 0:
        raise InvalidDocumentError("The file is empty.")
    if max_bytes and size > max_bytes:
        raise InvalidDocumentError(
            f"The file is too large ({size / 1e6:.1f} MB; limit {max_bytes / 1e6:.0f} MB).")
    with open(path, "rb") as handle:
        if handle.read(4) != b"PK\x03\x04":
            raise InvalidDocumentError("The file is not a valid .docx (ZIP) package.")
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise InvalidDocumentError("The ZIP package is not a Word document.")
            if any(n.lower().endswith("vbaproject.bin") for n in names):
                raise InvalidDocumentError("Macro-enabled documents are not accepted.")
            total = sum(info.file_size for info in archive.infolist())
            if total > MAX_UNCOMPRESSED_BYTES or total > size * MAX_COMPRESSION_RATIO + 10_000_000:
                raise InvalidDocumentError("The document expands to a suspicious size.")
    except zipfile.BadZipFile as error:
        raise InvalidDocumentError("The file is corrupted or not a .docx package.") from error
    return True


def convert_doc_to_docx(path, out_dir):
    """Convert a legacy .doc file with LibreOffice (if installed)."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise InvalidDocumentError(
            ".doc files need LibreOffice for conversion; install it or save the file as .docx in Word.")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "docx", "--outdir", str(out_dir),
             str(Path(path).resolve())],
            check=True, capture_output=True, timeout=300,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as error:
        raise InvalidDocumentError(f"LibreOffice could not convert the .doc file ({error}).") from error
    converted = out_dir / (Path(path).stem + ".docx")
    if not converted.exists():
        raise InvalidDocumentError("LibreOffice could not convert the .doc file.")
    return converted
