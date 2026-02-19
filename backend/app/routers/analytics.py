"""Analytics router: model info, coverage stats, and employee performance."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CoverageStatsResponse,
    EmployeePerformanceResponse,
    ModelInfoResponse,
)
from app.services import analytics_service, ml_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    """Return ML model evaluation metrics and feature importances."""
    metrics = ml_service.get_metrics()
    return ModelInfoResponse(
        roc_auc=metrics["roc_auc"],
        accuracy=metrics["accuracy"],
        precision=metrics["precision"],
        recall=metrics["recall"],
        feature_importances=metrics["feature_importances"],
    )


@router.get("/coverage-stats", response_model=CoverageStatsResponse)
def coverage_stats(db: Session = Depends(get_db)):
    """Return call coverage statistics computed from incident and call log data."""
    stats = analytics_service.get_coverage_stats(db)
    return CoverageStatsResponse(**stats)


@router.get("/employee-performance", response_model=list[EmployeePerformanceResponse])
def employee_performance(db: Session = Depends(get_db)):
    """Return all employees sorted by call acceptance rate (descending)."""
    results = analytics_service.get_employee_performance(db)
    return [EmployeePerformanceResponse(**r) for r in results]
