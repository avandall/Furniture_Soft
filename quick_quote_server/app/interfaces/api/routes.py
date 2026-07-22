import uuid
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.domain.models import WorkshopPricingConfig, QuotationResult
from app.infrastructure.repositories.database import get_db
from app.infrastructure.repositories.pricing_repository import WorkshopPricingRepository
from app.infrastructure.repositories.job_repository import QuotationJobRepository
from app.infrastructure.storage.file_storage import LocalStorageService
from app.infrastructure.ai_services.vision_service import MockVisionService
from app.use_cases.manage_pricing import ManagePricingUseCase
from app.use_cases.process_quotation import ProcessQuotationUseCase

router = APIRouter(prefix="/api/v1", tags=["Quick Quote AI"])
storage_service = LocalStorageService()


def run_background_quotation_job(
    job_id: str,
    file_path: str,
    config: WorkshopPricingConfig,
    custom_profit_margin: Optional[float] = None,
    custom_labor_cost: Optional[int] = None,
    db_session_factory=get_db,
):
    """
    Background Task chạy xử lý ngầm bóc tách ảnh & tính giá mộc.
    Cập nhật trạng thái Job: PENDING -> PROCESSING -> COMPLETED (hoặc FAILED).
    """
    # Lấy DB Session riêng cho background task
    db = next(get_db())
    job_repo = QuotationJobRepository(db)

    try:
        job_repo.update_job_status(job_id, "PROCESSING")

        # Đọc dữ liệu file
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        # Thực thi Use Case báo giá
        # Tự động dùng MockVisionService nếu chưa cấu hình GEMINI_API_KEY
        use_case = ProcessQuotationUseCase(vision_service=MockVisionService())
        quotation_result: QuotationResult = use_case.execute(
            image_data=image_bytes,
            config=config,
            custom_profit_margin=custom_profit_margin,
            custom_labor_cost=custom_labor_cost,
        )

        # Cập nhật kết quả hoàn thành
        job_repo.update_job_status(
            job_id=job_id,
            status="COMPLETED",
            result=quotation_result.model_dump(),
        )

    except Exception as e:
        job_repo.update_job_status(
            job_id=job_id,
            status="FAILED",
            error_message=str(e),
        )
    finally:
        db.close()


# --- WORKSHOP PRICING ENDPOINTS ---

@router.post("/workshops/{workshop_id}/pricing/preset", status_code=status.HTTP_200_OK)
def create_preset_pricing(
    workshop_id: str,
    template_key: str = "pho_thong",
    db: Session = Depends(get_db),
):
    """
    Khởi tạo bảng giá xưởng từ Mẫu Preset (binh_dan, pho_thong, cao_cap).
    """
    pricing_repo = WorkshopPricingRepository(db)
    use_case = ManagePricingUseCase(pricing_repo)
    config = use_case.create_preset_pricing(workshop_id, template_key)
    return {"message": "Bảng giá preset đã được áp dụng", "config": config}


@router.post("/workshops/{workshop_id}/pricing", status_code=status.HTTP_200_OK)
def save_custom_pricing(
    workshop_id: str,
    config: WorkshopPricingConfig,
    db: Session = Depends(get_db),
):
    """
    Lưu hoặc cập nhật bảng giá tự chỉnh sửa của xưởng.
    """
    if config.workshop_id != workshop_id:
        config.workshop_id = workshop_id

    pricing_repo = WorkshopPricingRepository(db)
    use_case = ManagePricingUseCase(pricing_repo)
    saved_config = use_case.save_custom_pricing(config)
    return {"message": "Lưu bảng giá thành công", "config": saved_config}


@router.get("/workshops/{workshop_id}/pricing", status_code=status.HTTP_200_OK)
def get_workshop_pricing(workshop_id: str, db: Session = Depends(get_db)):
    """
    Lấy cấu hình bảng giá hiện tại của xưởng.
    """
    pricing_repo = WorkshopPricingRepository(db)
    use_case = ManagePricingUseCase(pricing_repo)
    config = use_case.get_pricing(workshop_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chưa tìm thấy bảng giá cho xưởng '{workshop_id}'",
        )
    return config


# --- ASYNC QUOTATION JOBS & POLLING ENDPOINTS ---

@router.post("/quotations/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_quotation_image(
    background_tasks: BackgroundTasks,
    workshop_id: str = Form(...),
    custom_profit_margin: Optional[float] = Form(None),
    custom_labor_cost: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Endpoint tiếp nhận file ảnh/PDF -> Lưu file & Tạo Job ngầm bất đồng bộ.
    Phản hồi lập tức 202 Accepted + job_id trong 200ms (Tránh HTTP Timeout & nghẽn I/O).
    """
    pricing_repo = WorkshopPricingRepository(db)
    job_repo = QuotationJobRepository(db)

    # Lấy bảng giá xưởng (Nội suy preset pho_thong nếu xưởng chưa tạo)
    pricing_use_case = ManagePricingUseCase(pricing_repo)
    config = pricing_use_case.get_pricing(workshop_id)
    if not config:
        config = pricing_use_case.create_preset_pricing(workshop_id, "pho_thong")

    # 1. Lưu file upload lên storage
    file_bytes = await file.read()
    saved_file_path = storage_service.save_file(file_bytes, file.filename)

    # 2. Tạo bản ghi Job mới trong DB
    job_id = uuid.uuid4().hex
    job_repo.create_job(job_id=job_id, workshop_id=workshop_id, image_url=saved_file_path)

    # 3. Đẩy tác vụ chạy ngầm vào BackgroundTasks
    background_tasks.add_task(
        run_background_quotation_job,
        job_id=job_id,
        file_path=saved_file_path,
        config=config,
        custom_profit_margin=custom_profit_margin,
        custom_labor_cost=custom_labor_cost,
    )

    return {
        "job_id": job_id,
        "status": "PENDING",
        "message": "File accepted for background AI quotation processing",
    }


@router.get("/quotations/jobs/{job_id}", status_code=status.HTTP_200_OK)
def get_quotation_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Polling Endpoint cho Frontend kiểm tra trạng thái Job (PENDING -> PROCESSING -> COMPLETED/FAILED)
    và nhận về kết quả báo giá QuotationResult khi Job hoàn thành.
    """
    job_repo = QuotationJobRepository(db)
    job = job_repo.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy Job có mã '{job_id}'",
        )

    return {
        "job_id": job.job_id,
        "workshop_id": job.workshop_id,
        "status": job.status,
        "result": job.result,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }
