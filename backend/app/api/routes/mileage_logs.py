from uuid import UUID

from fastapi import APIRouter, Depends

from api.deps import get_current_user, get_mileage_log_service
from core.models import User
from core.schemas import MileageLogCreate, MileageLogRead
from services import MileageLogService

router = APIRouter(prefix="/mileage-logs", tags=["mileage-logs"])


@router.post("", response_model=MileageLogRead, status_code=201)
async def add_mileage_log(
    create_schema: MileageLogCreate,
    current_user: User = Depends(get_current_user),
    service: MileageLogService = Depends(get_mileage_log_service),
) -> MileageLogRead:
    return await service.add_mileage(create_schema, current_user.id)


@router.get("/car/{car_id}", response_model=list[MileageLogRead], status_code=200)
async def list_by_car(
    car_id: UUID,
    current_user: User = Depends(get_current_user),
    service: MileageLogService = Depends(get_mileage_log_service),
) -> list[MileageLogRead]:
    return await service.list_by_car(car_id, current_user.id)


@router.delete("/{mileage_log_id}", status_code=204)
async def delete_mileage_log(
    mileage_log_id: UUID,
    current_user: User = Depends(get_current_user),
    service: MileageLogService = Depends(get_mileage_log_service),
) -> None:
    await service.delete_mileage(mileage_log_id, current_user.id)
