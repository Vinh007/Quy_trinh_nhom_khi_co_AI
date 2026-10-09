"""
Máy chủ FastAPI – Cổng đăng ký Ngày hội việc làm
Chạy: uvicorn main:app --reload
Tài liệu API: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os

# ──────────────────────────────────────────────
# Cấu hình cơ sở dữ liệu
# ──────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "ngayhoi.db")


def init_db() -> None:
    """Khởi tạo CSDL và bảng dang_ky nếu chưa tồn tại."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dang_ky (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_sv    TEXT    NOT NULL,
            ma_phien TEXT    NOT NULL,
            UNIQUE (ma_sv, ma_phien)
        )
        """
    )
    conn.commit()
    conn.close()


init_db()

# ──────────────────────────────────────────────
# Khởi tạo ứng dụng FastAPI
# ──────────────────────────────────────────────
app = FastAPI(
    title="Ngày hội việc làm",
    description="API đăng ký phiên tuyển dụng cho sinh viên",
    version="1.0.0",
)

# ──────────────────────────────────────────────
# Cấu hình CORS – chỉ cho phép giao diện frontend
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # Chỉ một địa chỉ, không dùng "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Schema dữ liệu – Pydantic tự kiểm tra, trả 422 nếu thiếu
# ──────────────────────────────────────────────
class DangKy(BaseModel):
    ma_sv: str      # Mã sinh viên, ví dụ: "22020001"
    ma_phien: str   # Mã phiên tuyển dụng, ví dụ: "P01"


# ──────────────────────────────────────────────
# Endpoint đăng ký
# ──────────────────────────────────────────────
@app.post(
    "/api/dang-ky",
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký phiên tuyển dụng",
    responses={
        201: {"description": "Đăng ký thành công"},
        409: {"description": "Sinh viên đã đăng ký phiên này"},
        422: {"description": "Dữ liệu không hợp lệ (thiếu trường)"},
    },
)
def dang_ky(body: DangKy):
    """
    Đăng ký sinh viên vào một phiên tuyển dụng.

    - **201 Created**: Ghi thành công.
    - **409 Conflict**: Cặp (ma_sv, ma_phien) đã tồn tại – ràng buộc UNIQUE.
    - **422 Unprocessable Entity**: FastAPI/Pydantic tự trả nếu thiếu trường.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dang_ky (ma_sv, ma_phien) VALUES (?, ?)",
            (body.ma_sv, body.ma_phien),
        )
        conn.commit()
        return {"ok": True}
    except sqlite3.IntegrityError:
        # Ràng buộc UNIQUE bị vi phạm → 409 Conflict
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="DA_DANG_KY",
        )
    finally:
        conn.close()  # Luôn đóng connection, tránh database locked
