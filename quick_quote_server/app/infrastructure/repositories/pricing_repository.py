from typing import Optional
from sqlalchemy.orm import Session
from app.domain.models import WorkshopPricingConfig
from app.infrastructure.repositories.models_orm import WorkshopPricingORM


class WorkshopPricingRepository:
    """
    Repository truy vấn & lưu trữ bảng giá xưởng gỗ vào Database.
    """

    def __init__(self, db: Session):
        self.db = db

    def save_pricing(self, config: WorkshopPricingConfig) -> WorkshopPricingConfig:
        """
        Lưu hoặc cập nhật cấu hình bảng giá xưởng.
        """
        orm_item = (
            self.db.query(WorkshopPricingORM)
            .filter(WorkshopPricingORM.workshop_id == config.workshop_id)
            .first()
        )

        config_dict = config.model_dump()

        if orm_item:
            orm_item.pricing_config = config_dict
        else:
            orm_item = WorkshopPricingORM(
                workshop_id=config.workshop_id,
                pricing_config=config_dict,
            )
            self.db.add(orm_item)

        self.db.commit()
        self.db.refresh(orm_item)
        return WorkshopPricingConfig.model_validate(orm_item.pricing_config)

    def get_pricing(self, workshop_id: str) -> Optional[WorkshopPricingConfig]:
        """
        Lấy cấu hình bảng giá của xưởng theo workshop_id.
        """
        orm_item = (
            self.db.query(WorkshopPricingORM)
            .filter(WorkshopPricingORM.workshop_id == workshop_id)
            .first()
        )
        if not orm_item:
            return None
        return WorkshopPricingConfig.model_validate(orm_item.pricing_config)
