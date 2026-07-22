from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from app.infrastructure.repositories.database import Base


class WorkshopPricingORM(Base):
    """
    Bảng lưu trữ cấu hình bảng giá của xưởng mộc trong DB (dưới dạng JSONB / JSON).
    """
    __tablename__ = "workshop_pricing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workshop_id = Column(String(50), unique=True, index=True, nullable=False)
    pricing_config = Column(JSON, nullable=False)  # Tự động map JSONB trên Postgres hoặc JSON trên SQLite
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QuotationJobORM(Base):
    """
    Bảng lưu trữ Job bất đồng bộ cho luồng xử lý báo giá ngầm (Async Background Processing).
    """
    __tablename__ = "quotation_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(50), unique=True, index=True, nullable=False)
    workshop_id = Column(String(50), index=True, nullable=False)
    image_url = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    result = Column(JSON, nullable=True)  # Lưu QuotationResult dạng JSON
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
