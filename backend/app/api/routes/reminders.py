from uuid import UUID

from fastapi import APIRouter, Depends

from api.deps import get_reminder_service
from core.schemas import (
    ReminderCreate,
    ReminderRead,
    ReminderUpdate,
)
from services import ReminderService
from services.exceptions import ReminderNotFoundError

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("", response_model=ReminderRead, status_code=201)
async def add_reminder(
    create_schema: ReminderCreate,
    service: ReminderService = Depends(get_reminder_service),
) -> ReminderRead:
    return await service.add_reminder(create_schema)


@router.get(
    "/service-item/{service_item_id}",
    response_model=list[ReminderRead],
    status_code=200,
)
async def list_by_service_item(
    service_item_id: UUID,
    service: ReminderService = Depends(get_reminder_service),
) -> list[ReminderRead]:
    return await service.list_by_service_item(service_item_id)


@router.get(
    "/service-item/{service_item_id}/active",
    response_model=list[ReminderRead],
    status_code=200,
)
async def list_active_by_service_item(
    service_item_id: UUID,
    service: ReminderService = Depends(get_reminder_service),
) -> list[ReminderRead]:
    return await service.list_active_by_service_item(service_item_id)


@router.get("/{reminder_id}", response_model=ReminderRead, status_code=200)
async def get_reminder(
    reminder_id: UUID,
    service: ReminderService = Depends(get_reminder_service),
) -> ReminderRead:
    reminder = await service.get_reminder(reminder_id)
    if reminder is None:
        raise ReminderNotFoundError(reminder_id)
    return reminder


@router.patch("/{reminder_id}", response_model=ReminderRead, status_code=200)
async def update_reminder(
    reminder_id: UUID,
    update_schema: ReminderUpdate,
    service: ReminderService = Depends(get_reminder_service),
) -> ReminderRead:
    return await service.update_reminder(reminder_id, update_schema)


@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(
    reminder_id: UUID,
    service: ReminderService = Depends(get_reminder_service),
) -> None:
    await service.delete_reminder(reminder_id)
