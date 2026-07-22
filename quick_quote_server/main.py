from fastapi import FastAPI
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


@app.get("/")
def read_root():
    return {
        "system": "Quick-Quote AI P0 Backend",
        "status": "online",
        "docs_url": "/docs",
    }
