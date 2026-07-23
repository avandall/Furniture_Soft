import io
import os
import sys
import time
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("quick_quote_server"))
from main import app, init_db



init_db()
client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Quick-Quote AI" in response.text


def test_preset_pricing_api():
    response = client.post("/api/v1/workshops/ws_api_test/pricing/preset?template_key=pho_thong")
    assert response.status_code == 200
    data = response.json()
    assert data["config"]["workshop_id"] == "ws_api_test"
    assert len(data["config"]["categories"]) == 3

    # Test Get Pricing
    get_res = client.get("/api/v1/workshops/ws_api_test/pricing")
    assert get_res.status_code == 200
    assert get_res.json()["workshop_id"] == "ws_api_test"


def test_preset_pricing_api_invalid_template():
    response = client.post("/api/v1/workshops/ws_invalid/pricing/preset?template_key=invalid_template")
    assert response.status_code == 200
    data = response.json()
    assert data["config"]["workshop_id"] == "ws_invalid"
    assert len(data["config"]["categories"]) == 0


def test_async_quotation_upload_and_polling():
    # 1. Upload ảnh giả định với xưởng đã có bảng giá
    dummy_file = io.BytesIO(b"fake image bytes data")
    response = client.post(
        "/api/v1/quotations/upload",
        data={"workshop_id": "ws_api_test"},
        files={"file": ("test_draw.png", dummy_file, "image/png")},
    )

    # Đảm bảo phản hồi ngay 202 Accepted
    assert response.status_code == 202
    res_data = response.json()
    assert "job_id" in res_data
    assert res_data["status"] == "PENDING"

    job_id = res_data["job_id"]

    # 2. Polling chờ Background Task xử lý hoàn thành
    max_retries = 10
    completed_job = None
    for _ in range(max_retries):
        poll_res = client.get(f"/api/v1/quotations/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data["status"] in ("COMPLETED", "FAILED"):
            completed_job = poll_data
            break
        time.sleep(0.1)

    assert completed_job is not None
    assert completed_job["status"] == "COMPLETED"
    assert "result" in completed_job
    assert completed_job["result"]["total_amount"] > 0


def test_async_quotation_upload_unconfigured_workshop():
    # Upload ảnh cho xưởng chưa cài đặt bảng giá
    dummy_file = io.BytesIO(b"fake image bytes data unconfigured")
    response = client.post(
        "/api/v1/quotations/upload",
        data={"workshop_id": "ws_no_pricing_test"},
        files={"file": ("test_draw.png", dummy_file, "image/png")},
    )

    assert response.status_code == 202
    job_id = response.json()["job_id"]

    max_retries = 10
    completed_job = None
    for _ in range(max_retries):
        poll_res = client.get(f"/api/v1/quotations/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data["status"] in ("COMPLETED", "FAILED"):
            completed_job = poll_data
            break
        time.sleep(0.1)

    assert completed_job is not None
    assert completed_job["status"] == "COMPLETED"
    assert "result" in completed_job
    # Vì xưởng chưa cài bảng giá -> Tổng tiền = 0 VND và có cảnh báo thiếu giá
    assert completed_job["result"]["total_amount"] == 0
    assert completed_job["result"]["has_warnings"] is True

