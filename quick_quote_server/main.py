from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.infrastructure.repositories.database import init_db
from app.interfaces.api.routes import router

# Khởi tạo bảng Database khi startup
init_db()

app = FastAPI(
    title="Quick-Quote AI (P0) Backend Server",
    description="Hệ thống báo giá nhanh mộc nội thất AI-assisted, Human-approved",
    version="0.1.0",
)

# Đăng ký các router API
app.include_router(router)

# Phục vụ giao diện Web App Frontend (index.html, styles.css, app.js)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def read_root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "system": "Quick-Quote AI P0 Backend",
        "status": "online",
        "docs_url": "/docs",
    }
