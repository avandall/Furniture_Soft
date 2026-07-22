import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.domain.models import WorkshopPricingConfig, CategoryPricing
from app.infrastructure.repositories.database import Base
from app.infrastructure.repositories.pricing_repository import WorkshopPricingRepository
from app.infrastructure.repositories.job_repository import QuotationJobRepository

# Database SQLite in-memory cho Unit Test
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_workshop_pricing_repository(db_session):
    repo = WorkshopPricingRepository(db_session)
    config = WorkshopPricingConfig(
        workshop_id="ws_repo_test",
        categories=[
            CategoryPricing(category="Tủ áo", unit="m2", prices={"mdf_melamine": 2200000})
        ],
    )

    # Test Save
    saved_config = repo.save_pricing(config)
    assert saved_config.workshop_id == "ws_repo_test"
    assert len(saved_config.categories) == 1

    # Test Get
    fetched_config = repo.get_pricing("ws_repo_test")
    assert fetched_config is not None
    assert fetched_config.workshop_id == "ws_repo_test"
    assert fetched_config.categories[0].category == "Tủ áo"


def test_quotation_job_repository(db_session):
    repo = QuotationJobRepository(db_session)

    # Test Create Job
    job = repo.create_job("job_123", "ws_test", "uploads/test.png")
    assert job.job_id == "job_123"
    assert job.status == "PENDING"

    # Test Update Status & Result
    updated_job = repo.update_job_status(
        job_id="job_123",
        status="COMPLETED",
        result={"total_amount": 15000000},
    )
    assert updated_job.status == "COMPLETED"
    assert updated_job.result["total_amount"] == 15000000

    # Test Get Job
    fetched_job = repo.get_job("job_123")
    assert fetched_job is not None
    assert fetched_job.job_id == "job_123"
