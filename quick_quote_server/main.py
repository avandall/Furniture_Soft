import os
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

# Mount thư mục static phục vụ giao diện Web App Frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def read_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "system": "Quick-Quote AI P0 Backend",
        "status": "online",
        "docs_url": "/docs",
    }
