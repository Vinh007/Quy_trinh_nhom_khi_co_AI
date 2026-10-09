import { useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8000/api/dang-ky";

// ─── Các phiên tuyển dụng mẫu ────────────────────────────────────────────────
const PHIEN_LIST = [
  { ma: "P01", ten: "P01 – Công nghệ thông tin" },
  { ma: "P02", ten: "P02 – Kinh tế & Quản trị" },
  { ma: "P03", ten: "P03 – Kỹ thuật & Chế tạo" },
  { ma: "P04", ten: "P04 – Truyền thông & Marketing" },
];

export default function App() {
  const [maSv, setMaSv] = useState("");
  const [maPhien, setMaPhien] = useState("P01");
  // state: "idle" | "loading" | "success" | "conflict" | "error"
  const [uiState, setUiState] = useState("idle");
  const [errMsg, setErrMsg] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!maSv.trim()) return;

    setUiState("loading");

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ma_sv: maSv.trim(), ma_phien: maPhien }),
      });

      if (res.status === 201) {
        setUiState("success");
      } else if (res.status === 409) {
        setUiState("conflict");
      } else {
        const data = await res.json();
        setErrMsg(JSON.stringify(data.detail));
        setUiState("error");
      }
    } catch (err) {
      setErrMsg("Không kết nối được máy chủ. Kiểm tra backend đã chạy chưa.");
      setUiState("error");
    }
  }

  function handleReset() {
    setUiState("idle");
    setMaSv("");
    setMaPhien("P01");
    setErrMsg("");
  }

  return (
    <div className="page">
      {/* ── Header ───────────────────────────────────────────────── */}
      <header className="header">
        <div className="header-badge">🎯 Sự kiện</div>
        <h1 className="header-title">Ngày hội việc làm 2025</h1>
        <p className="header-sub">
          Đăng ký phiên tuyển dụng – Trường Đại học Công nghệ
        </p>
      </header>

      {/* ── Card ─────────────────────────────────────────────────── */}
      <main className="card-wrapper">
        <div className={`card ${uiState !== "idle" && uiState !== "loading" ? "card--result" : ""}`}>

          {/* ── TRẠNG THÁI 1: Form (idle / loading) ──────────────── */}
          {(uiState === "idle" || uiState === "loading") && (
            <form className="form" onSubmit={handleSubmit}>
              <div className="form-icon">📋</div>
              <h2 className="form-title">Đăng ký tham gia</h2>
              <p className="form-desc">
                Điền thông tin bên dưới để đăng ký vào phiên tuyển dụng phù hợp
                với bạn.
              </p>

              <div className="field">
                <label htmlFor="ma_sv" className="label">
                  Mã sinh viên <span className="required">*</span>
                </label>
                <input
                  id="ma_sv"
                  type="text"
                  className="input"
                  placeholder="Ví dụ: 22020001"
                  value={maSv}
                  onChange={(e) => setMaSv(e.target.value)}
                  required
                  disabled={uiState === "loading"}
                />
              </div>

              <div className="field">
                <label htmlFor="ma_phien" className="label">
                  Phiên tuyển dụng <span className="required">*</span>
                </label>
                <select
                  id="ma_phien"
                  className="select"
                  value={maPhien}
                  onChange={(e) => setMaPhien(e.target.value)}
                  disabled={uiState === "loading"}
                >
                  {PHIEN_LIST.map((p) => (
                    <option key={p.ma} value={p.ma}>
                      {p.ten}
                    </option>
                  ))}
                </select>
              </div>

              <button
                id="btn-submit"
                type="submit"
                className={`btn btn--primary ${uiState === "loading" ? "btn--loading" : ""}`}
                disabled={uiState === "loading"}
              >
                {uiState === "loading" ? (
                  <>
                    <span className="spinner" />
                    Đang gửi…
                  </>
                ) : (
                  "✔ Đăng ký ngay"
                )}
              </button>
            </form>
          )}

          {/* ── TRẠNG THÁI 2: Thành công (201) ───────────────────── */}
          {uiState === "success" && (
            <div className="result result--success" id="state-success">
              <div className="result-icon">🎉</div>
              <h2 className="result-title">Đăng ký thành công!</h2>
              <p className="result-msg">
                Chúc mừng bạn đã đăng ký phiên{" "}
                <strong>{maPhien}</strong> với mã sinh viên{" "}
                <strong>{maSv}</strong>.
              </p>
              <div className="result-badge result-badge--green">
                HTTP 201 Created
              </div>
              <button className="btn btn--secondary" onClick={handleReset}>
                ← Đăng ký thêm
              </button>
            </div>
          )}

          {/* ── TRẠNG THÁI 3: Đã đăng ký (409 Conflict) ─────────── */}
          {uiState === "conflict" && (
            <div className="result result--conflict" id="state-conflict">
              <div className="result-icon">⚠️</div>
              <h2 className="result-title">Đã đăng ký trước đó</h2>
              <p className="result-msg">
                Mã sinh viên <strong>{maSv}</strong> đã đăng ký phiên{" "}
                <strong>{maPhien}</strong> rồi. Mỗi sinh viên chỉ được đăng ký
                một lần cho mỗi phiên.
              </p>
              <div className="result-badge result-badge--orange">
                HTTP 409 Conflict – DA_DANG_KY
              </div>
              <button className="btn btn--secondary" onClick={handleReset}>
                ← Thử lại
              </button>
            </div>
          )}

          {/* ── Lỗi khác (422, network…) ─────────────────────────── */}
          {uiState === "error" && (
            <div className="result result--error" id="state-error">
              <div className="result-icon">❌</div>
              <h2 className="result-title">Có lỗi xảy ra</h2>
              <p className="result-msg">{errMsg}</p>
              <button className="btn btn--secondary" onClick={handleReset}>
                ← Quay lại
              </button>
            </div>
          )}
        </div>

        {/* ── Info strip ───────────────────────────────────────── */}
        <div className="info-strip">
          <div className="info-item">
            <span className="info-icon">📅</span>
            <span>15 – 16 / 11 / 2025</span>
          </div>
          <div className="info-item">
            <span className="info-icon">📍</span>
            <span>Hội trường A – Cơ sở Cầu Giấy</span>
          </div>
          <div className="info-item">
            <span className="info-icon">🏢</span>
            <span>50+ doanh nghiệp tham gia</span>
          </div>
        </div>
      </main>
    </div>
  );
}
