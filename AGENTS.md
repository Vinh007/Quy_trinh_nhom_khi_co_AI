# Quy tắc cho agent trong kho ngayhoi

## Được làm
- Sửa mã trong backend/ và ui/src/.
- Thêm test mới trong backend/tests/.

## Không được làm
- Sửa hoặc xóa test có sẵn trong backend/tests/.
- Sửa .github/workflows/, AGENTS.md, spec.md.
- Thêm thư viện mới khi chưa ghi lý do trong mô tả PR.
- Đổi allow_origins sang "*".

## Trước khi mở PR
1. cd backend && python -m pytest -q → mọi test xanh.
2. git diff --stat → chỉ có tệp trong phạm vi được làm.
3. Điền đủ pull_request_template.md, gồm dòng AI-assisted.
