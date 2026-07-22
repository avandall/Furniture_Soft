from typing import Optional
from sqlalchemy.orm import Session
from app.infrastructure.repositories.models_orm import QuotationJobORM


class QuotationJobRepository:
    """
    Repository quản lý vòng đời Job bất đồng bộ (Async Job Lifecycle).
    """

    def __init__(self, db: Session):
        self.db = db

    def create_job(
        self, job_id: str, workshop_id: str, image_url: Optional[str] = None
    ) -> QuotationJobORM:
        """
        Tạo Job mới với trạng thái PENDING.
        """
        job = QuotationJobORM(
            job_id=job_id,
            workshop_id=workshop_id,
            image_url=image_url,
            status="PENDING",
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[dict] = None,
        error_message: Optional[str] = None,
    ) -> Optional[QuotationJobORM]:
        """
        Cập nhật trạng thái Job (PROCESSING, COMPLETED, FAILED) và lưu kết quả.
        """
        job = (
            self.db.query(QuotationJobORM)
            .filter(QuotationJobORM.job_id == job_id)
            .first()
        )
        if not job:
            return None

        job.status = status
        if result is not None:
            job.result = result
        if error_message is not None:
            job.error_message = error_message

        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job(self, job_id: str) -> Optional[QuotationJobORM]:
        """
        Lấy thông tin Job theo job_id cho API Polling.
        """
        return (
            self.db.query(QuotationJobORM)
            .filter(QuotationJobORM.job_id == job_id)
            .first()
        )
