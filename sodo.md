# Sơ đồ kiến trúc – Cổng đăng ký Ngày hội việc làm

## 1. Tổng quan hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                          NGƯỜI DÙNG                             │
│                    (Trình duyệt – Sinh viên)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP Request
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│             FRONTEND  –  http://localhost:5173                  │
│                  Vite + React  (ui/)                            │
│                                                                 │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────────────┐    │
│  │  Form    │──▶│  fetch()     │──▶│  Hiển thị kết quả    │    │
│  │  (idle)  │   │  POST /api/  │   │  201 / 409 / error   │    │
│  └──────────┘   │  dang-ky     │   └──────────────────────┘    │
│                 └──────┬───────┘                                │
└────────────────────────┼────────────────────────────────────────┘
                         │ CORS – chỉ cho phép localhost:5173
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND  –  http://localhost:8000                  │
│                   FastAPI + Uvicorn  (backend/)                 │
│                                                                 │
│  POST /api/dang-ky                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Pydantic Model DangKy { ma_sv, ma_phien }              │    │
│  │    ├─ Thiếu trường → 422 Unprocessable Entity           │    │
│  │    └─ Hợp lệ → INSERT INTO dang_ky ...                  │    │
│  │         ├─ Thành công  → 201 {"ok": true}               │    │
│  │         └─ IntegrityError (UNIQUE) → 409 DA_DANG_KY     │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            │ sqlite3 (built-in Python)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE  –  backend/ngayhoi.db  (SQLite)          │
│                                                                 │
│  TABLE dang_ky                                                  │
│  ┌────┬──────────┬──────────┐                                   │
│  │ id │  ma_sv   │ ma_phien │  ← UNIQUE(ma_sv, ma_phien)        │
│  ├────┼──────────┼──────────┤                                   │
│  │  1 │ 22020001 │   P01    │                                   │
│  │  2 │ 22020002 │   P01    │                                   │
│  └────┴──────────┴──────────┘                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Luồng xử lý đăng ký

```
Sinh viên nhập                FastAPI                  SQLite
ma_sv + ma_phien                                      ngayhoi.db
      │
      │  POST /api/dang-ky
      │  { ma_sv, ma_phien }
      ├─────────────────────────▶ Pydantic validate
      │                               │
      │                   ┌───────────┴────────────┐
      │                   │ Thiếu trường?           │
      │                   │    → 422 Unprocessable  │
      │                   └───────────┬────────────┘
      │                               │ Hợp lệ
      │                               │ INSERT INTO dang_ky
      │                               ├──────────────────▶ OK
      │                               │                    → 201 {"ok":true}
      │                               │
      │                               ├──────────────────▶ UNIQUE Error
      │                               │                    → 409 DA_DANG_KY
      │
      ◀─────────────────────────── Response
      │
      ▼
  Giao diện cập nhật
  (3 trạng thái: form / thành công / lỗi trùng)
```

---

## 3. Cấu trúc thư mục

```
week3/
├── backend/
│   ├── .venv/            ← Môi trường ảo Python
│   ├── main.py           ← FastAPI server
│   └── ngayhoi.db        ← SQLite (tự tạo khi chạy)
├── ui/
│   ├── src/
│   │   ├── App.jsx       ← Component chính (3 trạng thái UI)
│   │   ├── App.css       ← Giao diện
│   │   └── main.jsx      ← Entry point React
│   ├── index.html
│   └── package.json
├── sodo.md               ← File này
└── Report.md             ← Báo cáo
```

---

## 4. Cấu hình CORS

| Thuộc tính       | Giá trị                     |
|------------------|-----------------------------|
| allow_origins    | `["http://localhost:5173"]` |
| allow_methods    | `["*"]`                     |
| allow_headers    | `["*"]`                     |
| allow_credentials| `True`                      |

> ⚠️ **Không dùng `"*"` cho allow_origins** – chỉ khai báo đúng địa chỉ frontend.

---

## 5. Mã HTTP và ý nghĩa

| Mã  | Tên                   | Khi nào xảy ra                        |
|-----|-----------------------|---------------------------------------|
| 201 | Created               | Đăng ký thành công, ghi vào DB        |
| 409 | Conflict              | Cặp (ma_sv, ma_phien) đã tồn tại      |
| 422 | Unprocessable Entity  | Thiếu trường (Pydantic tự kiểm tra)   |
