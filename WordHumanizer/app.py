"""Word Humanizer web application.

Run:  uvicorn app:app --port 8000     (then open http://localhost:8000)
"""

import json
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from config import BASE_DIR, get_settings
from core.jobs import JobManager
from core.language_tool_client import LanguageToolClient
from core.options import REWRITE_STYLES, ProcessingOptions
from core.pipeline import DocumentProcessor
from core.rewriting_engine import create_rewriting_engine
from utils.file_utils import (InvalidDocumentError, convert_doc_to_docx,
                              output_name, safe_filename, validate_docx)
from utils.logger import setup_logger

LANGUAGES = {
    "en-US": "English (US)", "en-GB": "English (UK)", "en-AU": "English (Australia)",
    "en-CA": "English (Canada)", "de-DE": "German", "fr": "French", "es": "Spanish",
    "it": "Italian", "pt-PT": "Portuguese (Portugal)", "pt-BR": "Portuguese (Brazil)",
    "nl": "Dutch", "pl-PL": "Polish", "ru-RU": "Russian", "uk-UA": "Ukrainian", "ar": "Arabic",
}


def default_processor_factory(settings):
    rewriter_holder = {}

    def factory(options, progress, cancelled):
        lt = LanguageToolClient.from_settings(settings, language=options.language, picky=options.picky)
        rewriter = None
        if options.rewrite:
            if "engine" not in rewriter_holder:
                rewriter_holder["engine"] = create_rewriting_engine(settings)
            rewriter = rewriter_holder["engine"]
        return DocumentProcessor(lt, rewriter, options, settings.max_chars, progress, cancelled)

    return factory


def create_app(settings=None, processor_factory=None):
    settings = settings or get_settings()
    setup_logger(settings.log_dir)
    manager = JobManager(
        processor_factory or default_processor_factory(settings),
        settings.temp_dir,
        max_workers=settings.max_concurrent_jobs,
        ttl_seconds=settings.job_ttl_minutes * 60,
    )
    max_bytes = settings.max_upload_mb * 1024 * 1024

    app = FastAPI(title="Word Humanizer", version="1.0.0")
    app.state.jobs = manager
    app.state.settings = settings
    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    def home():
        return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")

    @app.get("/api/health")
    def health():
        return {
            "application": "Word Humanizer",
            "status": "running",
            "languagetool_url": settings.languagetool_url,
            "rewrite_provider": settings.rewrite_provider,
            "max_upload_mb": settings.max_upload_mb,
        }

    @app.get("/api/config")
    def ui_config():
        return {
            "languages": LANGUAGES,
            "default_language": settings.language,
            "rewrite_styles": list(REWRITE_STYLES),
            "rewrite_available": settings.rewrite_provider not in ("", "none"),
            "defaults": ProcessingOptions(language=settings.language).to_dict(),
            "max_upload_mb": settings.max_upload_mb,
        }

    @app.post("/api/jobs")
    async def create_job(file: UploadFile = File(...), options: str = Form("{}")):
        try:
            opts = ProcessingOptions.from_dict(json.loads(options or "{}"))
        except (ValueError, TypeError) as error:
            raise HTTPException(400, f"Invalid options: {error}") from error

        filename = safe_filename(file.filename)
        suffix = Path(filename).suffix.lower()
        if suffix not in (".docx", ".doc"):
            raise HTTPException(400, "Please upload a Word document (.docx or .doc).")

        job_id, work_dir = manager.new_work_dir()
        upload_path = work_dir / f"source{suffix}"
        size = 0
        try:
            with open(upload_path, "wb") as handle:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > max_bytes:
                        raise InvalidDocumentError(
                            f"The file is larger than the {settings.max_upload_mb} MB limit.")
                    handle.write(chunk)
            if suffix == ".doc":
                upload_path = convert_doc_to_docx(upload_path, work_dir / "converted")
            validate_docx(upload_path, max_bytes)
        except InvalidDocumentError as error:
            _rm(work_dir)
            raise HTTPException(400, str(error)) from error
        except Exception as error:  # noqa: BLE001
            _rm(work_dir)
            raise HTTPException(400, f"Could not read the upload: {error}") from error

        output_path = work_dir / output_name(filename)
        job = manager.submit(job_id, work_dir, filename, upload_path, output_path, opts)
        return job.public()

    @app.get("/api/jobs/{job_id}")
    def job_status(job_id: str):
        return _job(manager, job_id).public()

    @app.get("/api/jobs/{job_id}/download")
    def download(job_id: str):
        job = _job(manager, job_id)
        if job.status != "done" or not job.output_path.exists():
            raise HTTPException(409, "The document is not ready yet.")
        return FileResponse(
            job.output_path, filename=job.output_path.name,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    @app.get("/api/jobs/{job_id}/report")
    def report(job_id: str, format: str = "json"):
        job = _job(manager, job_id)
        if job.report is None:
            raise HTTPException(409, "The report is not ready yet.")
        if format == "txt":
            return PlainTextResponse(
                job.report.to_text(),
                headers={"Content-Disposition": f'attachment; filename="{Path(job.filename).stem}_report.txt"'},
            )
        return job.report.to_dict()

    @app.delete("/api/jobs/{job_id}")
    def delete(job_id: str):
        if not manager.cancel(job_id):
            raise HTTPException(404, "Unknown job.")
        return {"deleted": job_id}

    return app


def _job(manager, job_id):
    job = manager.get(job_id)
    if job is None:
        raise HTTPException(404, "Unknown or expired job.")
    return job


def _rm(path):
    import shutil
    shutil.rmtree(path, ignore_errors=True)


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
