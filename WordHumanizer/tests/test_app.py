import time

import pytest
from fastapi.testclient import TestClient

from config import Settings
from core.pipeline import DocumentProcessor
from tests.conftest import FakeLanguageTool


@pytest.fixture
def client(tmp_path):
    from app import create_app
    settings = Settings()
    settings.temp_dir = tmp_path / "temp"
    settings.log_dir = tmp_path / "logs"
    settings.max_upload_mb = 1

    def factory(options, progress, cancelled):
        return DocumentProcessor(FakeLanguageTool(), None, options, 18000, progress, cancelled)

    return TestClient(create_app(settings, factory))


def wait(client, job_id):
    for _ in range(100):
        data = client.get(f"/api/jobs/{job_id}").json()
        if data["status"] in ("done", "failed"):
            return data
        time.sleep(0.05)
    raise AssertionError("job did not finish")


def test_home_and_config(client):
    assert "Word Humanizer" in client.get("/").text
    config = client.get("/api/config").json()
    assert "en-US" in config["languages"] and "academic" in config["rewrite_styles"]


def test_upload_process_download(client, sample_docx):
    with open(sample_docx, "rb") as handle:
        res = client.post("/api/jobs", files={"file": ("My Research.docx", handle)},
                          data={"options": '{"spelling": true, "protected_terms": "Zarqa"}'})
    assert res.status_code == 200, res.text
    job = wait(client, res.json()["id"])
    assert job["status"] == "done", job
    assert job["report"]["corrections"] > 0
    assert job["output_filename"] == "My Research_processed.docx"

    download = client.get(f"/api/jobs/{job['id']}/download")
    assert download.status_code == 200 and download.content[:2] == b"PK"
    report = client.get(f"/api/jobs/{job['id']}/report?format=txt")
    assert "Processing Report" in report.text
    assert client.delete(f"/api/jobs/{job['id']}").status_code == 200
    assert client.get(f"/api/jobs/{job['id']}").status_code == 404


def test_rejects_non_word_files(client, tmp_path):
    res = client.post("/api/jobs", files={"file": ("virus.exe", b"MZ....")})
    assert res.status_code == 400
    res = client.post("/api/jobs", files={"file": ("renamed.docx", b"MZ not a zip")})
    assert res.status_code == 400 and "ZIP" in res.json()["detail"]


def test_rejects_oversized_upload(client):
    res = client.post("/api/jobs", files={"file": ("big.docx", b"PK\x03\x04" + b"0" * (2 * 1024 * 1024))})
    assert res.status_code == 400 and "limit" in res.json()["detail"]


def test_bad_options(client, sample_docx):
    with open(sample_docx, "rb") as handle:
        res = client.post("/api/jobs", files={"file": ("a.docx", handle)}, data={"options": "{not json"})
    assert res.status_code == 400


def test_unknown_job(client):
    assert client.get("/api/jobs/nope").status_code == 404
