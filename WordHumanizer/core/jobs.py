"""Background job manager used by the web application."""

import shutil
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from core.pipeline import ProcessingCancelled
from utils.logger import get_logger

log = get_logger("jobs")


@dataclass
class Job:
    id: str
    filename: str
    work_dir: Path
    input_path: Path
    output_path: Path
    options: object
    status: str = "queued"        # queued | running | done | failed | cancelled
    progress: float = 0.0
    message: str = "Waiting in queue"
    error: str = ""
    report: object = None
    created: float = field(default_factory=time.time)
    finished: float = 0.0
    cancel_requested: bool = False

    def public(self):
        data = {
            "id": self.id,
            "filename": self.filename,
            "status": self.status,
            "progress": round(self.progress, 3),
            "message": self.message,
            "error": self.error,
            "output_filename": self.output_path.name,
        }
        if self.report is not None:
            data["report"] = self.report.to_dict()
        return data


class JobManager:

    def __init__(self, processor_factory, temp_dir, max_workers=1, ttl_seconds=7200):
        self.processor_factory = processor_factory
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds
        self.jobs = {}
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max(1, max_workers), thread_name_prefix="job")

    def new_work_dir(self):
        job_id = uuid.uuid4().hex
        work_dir = self.temp_dir / job_id
        work_dir.mkdir(parents=True)
        return job_id, work_dir

    def submit(self, job_id, work_dir, filename, input_path, output_path, options):
        job = Job(job_id, filename, work_dir, Path(input_path), Path(output_path), options)
        with self.lock:
            self.jobs[job_id] = job
        self.executor.submit(self._run, job)
        return job

    def get(self, job_id):
        self.cleanup()
        with self.lock:
            return self.jobs.get(job_id)

    def cancel(self, job_id):
        job = self.get(job_id)
        if job is None:
            return False
        job.cancel_requested = True
        if job.status in ("done", "failed", "cancelled", "queued"):
            self._remove(job_id)
        return True

    def cleanup(self):
        now = time.time()
        with self.lock:
            expired = [j.id for j in self.jobs.values()
                       if j.finished and now - j.finished > self.ttl]
        for job_id in expired:
            self._remove(job_id)

    def _remove(self, job_id):
        with self.lock:
            job = self.jobs.pop(job_id, None)
        if job is not None:
            job.cancel_requested = True
            shutil.rmtree(job.work_dir, ignore_errors=True)

    def _run(self, job):
        if job.cancel_requested:
            return
        job.status = "running"

        def progress(fraction, message):
            job.progress = fraction
            job.message = message

        try:
            processor = self.processor_factory(job.options, progress, lambda: job.cancel_requested)
            job.report = processor.process(job.input_path, job.output_path)
            job.status = "done"
            job.message = "Finished"
        except ProcessingCancelled:
            job.status = "cancelled"
            job.message = "Cancelled"
        except Exception as error:  # noqa: BLE001
            log.exception("Job %s failed", job.id)
            job.status = "failed"
            job.error = str(error) or error.__class__.__name__
            job.message = "Failed"
        finally:
            job.finished = time.time()
            # The uploaded original is not kept once processing is over.
            try:
                job.input_path.unlink(missing_ok=True)
            except OSError:
                pass
            if job.status == "cancelled":
                self._remove(job.id)
