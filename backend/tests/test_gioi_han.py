"""
Test giới hạn chỗ mỗi phiên – dựa trên spec.md (dòng 1-5).
Sức chứa: 30 sinh viên / phiên. Đếm riêng từng phiên.

Chạy:  pytest tests/test_gioi_han.py -v
"""

import os
os.environ["DB_PATH"] = ":memory:"  # CSDL tạm, không đụng dữ liệu thật

import pytest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def so_trong():
    """Xoá bảng trước mỗi test."""
    main.db.execute("DELETE FROM dang_ky")
    main.db.commit()


def lap_day(ma_phien, n):
    """Đăng ký n sinh viên vào phiên qua API."""
    for i in range(n):
        client.post("/api/dang-ky",
                     json={"ma_sv": f"SV{i:03}", "ma_phien": ma_phien})


# ===================================================================
# Dòng 1 | P01 trống | SV001 đăng ký P01 → 201
# ===================================================================
def test_1_phien_trong_dang_ky_thanh_cong():
    res = client.post("/api/dang-ky", json={"ma_sv": "SV001", "ma_phien": "P01"})
    assert res.status_code == 201
    assert res.json() == {"ok": True}


# ===================================================================
# Dòng 2 | P01 có 29 | SV mới đăng ký P01 → 201
# ===================================================================
def test_2_phien_co_29_dang_ky_thanh_cong():
    lap_day("P01", 29)
    res = client.post("/api/dang-ky", json={"ma_sv": "SV029", "ma_phien": "P01"})
    assert res.status_code == 201


# ===================================================================
# Dòng 3 | P01 có 30 | SV mới đăng ký P01 → 409 HET_CHO
# ===================================================================
def test_3_phien_co_30_tu_choi_het_cho():
    lap_day("P01", 30)
    res = client.post("/api/dang-ky", json={"ma_sv": "SV031", "ma_phien": "P01"})
    assert res.status_code == 409
    assert res.json()["detail"] == "HET_CHO"


# ===================================================================
# Dòng 4 | P01 có 30, gồm SV000 | SV000 đăng ký lại P01 → 409 DA_DANG_KY
# ===================================================================
def test_4_dang_ky_trung_tra_da_dang_ky():
    lap_day("P01", 30)                     # SV000..SV029 đã đăng ký
    res = client.post("/api/dang-ky", json={"ma_sv": "SV000", "ma_phien": "P01"})
    assert res.status_code == 409
    assert res.json()["detail"] == "DA_DANG_KY"


# ===================================================================
# Dòng 5 | P01 có 30 | SV031 đăng ký P02 → 201 (đếm riêng phiên)
# ===================================================================
def test_5_phien_khac_van_dang_ky_duoc():
    lap_day("P01", 30)                     # P01 đầy, nhưng P02 vẫn trống
    res = client.post("/api/dang-ky", json={"ma_sv": "SV031", "ma_phien": "P02"})
    assert res.status_code == 201
    assert res.json() == {"ok": True}
