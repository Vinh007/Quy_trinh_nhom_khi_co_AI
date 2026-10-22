"""
Test endpoint GET /api/con-cho?ma_phien=...
Trả về số chỗ còn lại của một phiên (sức chứa 30 chỗ).
"""

import os
os.environ["DB_PATH"] = ":memory:"

import pytest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def so_trong():
    """Xoá bảng trước mỗi test."""
    main.db.execute("DELETE FROM dang_ky")
    main.db.commit()


def test_con_cho_phien_trong():
    res = client.get("/api/con-cho?ma_phien=P01")
    assert res.status_code == 200
    assert res.json() == {"con_cho": 30}


def test_con_cho_sau_khi_dang_ky():
    client.post("/api/dang-ky", json={"ma_sv": "SV001", "ma_phien": "P01"})
    client.post("/api/dang-ky", json={"ma_sv": "SV002", "ma_phien": "P01"})
    res = client.get("/api/con-cho?ma_phien=P01")
    assert res.status_code == 200
    assert res.json() == {"con_cho": 28}


def test_con_cho_khi_da_day():
    for i in range(30):
        client.post("/api/dang-ky", json={"ma_sv": f"SV{i:03}", "ma_phien": "P01"})
    res = client.get("/api/con-cho?ma_phien=P01")
    assert res.status_code == 200
    assert res.json() == {"con_cho": 0}


def test_con_cho_dem_rieng_tung_phien():
    client.post("/api/dang-ky", json={"ma_sv": "SV001", "ma_phien": "P01"})
    res_p1 = client.get("/api/con-cho?ma_phien=P01")
    res_p2 = client.get("/api/con-cho?ma_phien=P02")
    assert res_p1.json() == {"con_cho": 29}
    assert res_p2.json() == {"con_cho": 30}
