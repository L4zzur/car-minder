from collections.abc import Mapping
from uuid import UUID


class ServiceError(Exception):
    status_code = 500
    code = "service_error"
    message = "Service error"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: Mapping[str, object] | None = None,
    ) -> None:
        self.message = message or self.message
        self.details = dict(details) if details is not None else {}
        super().__init__(self.message)


class NotFoundServiceError(ServiceError):
    """Object not found exception"""

    status_code = 404


class ConflictServiceError(ServiceError):
    """Object conflict exception"""

    status_code = 409


class BusinessRuleServiceError(ServiceError):
    """Business rule exception"""

    status_code = 422


# User
class UserNotFoundError(NotFoundServiceError):
    code = "user_not_found"
    message = "User not found"

    def __init__(self, user_id: UUID | None = None) -> None:
        details = {"user_id": str(user_id)} if user_id is not None else None
        super().__init__(details=details)


class UsernameAlreadyTakenError(ConflictServiceError):
    code = "username_already_taken"
    message = "Username is already taken"

    def __init__(self, username: str | None = None) -> None:
        details = {"username": str(username)} if username is not None else None
        super().__init__(details=details)


# Car
class CarNotFoundError(NotFoundServiceError):
    code = "car_not_found"
    message = "Car not found"

    def __init__(self, car_id: UUID | None = None) -> None:
        details = {"car_id": str(car_id)} if car_id is not None else None
        super().__init__(details=details)


# Odometer
class MileageLogNotFoundError(NotFoundServiceError):
    code = "mileage_log_not_found"
    message = "Mileage log not found"

    def __init__(self, mileage_log_id: UUID | None = None) -> None:
        details = (
            {"mileage_log_id": str(mileage_log_id)}
            if mileage_log_id is not None
            else None
        )
        super().__init__(details=details)


class OdometerRollbackError(BusinessRuleServiceError):
    code = "odometer_rollback"
    message = "Odometer reading cannot be lower than current known odometer"

    def __init__(self, current_odometer: int, new_odometer: int) -> None:
        details = {
            "current_odometer": current_odometer,
            "new_odometer": new_odometer,
        }
        super().__init__(details=details)


class OdometerNotAdvancedError(BusinessRuleServiceError):
    code = "odometer_not_advanced"
    message = "Odometer reading must be greater than current known odometer"

    def __init__(self, current_odometer: int, new_odometer: int) -> None:
        details = {
            "current_odometer": current_odometer,
            "new_odometer": new_odometer,
        }
        super().__init__(details=details)


# Service item
class ServiceItemNotFoundError(NotFoundServiceError):
    code = "service_item_not_found"
    message = "Service item not found"

    def __init__(self, service_item_id: UUID | None = None) -> None:
        details = (
            {"service_item_id": str(service_item_id)}
            if service_item_id is not None
            else None
        )
        super().__init__(details=details)


class ServiceItemNameAlreadyExistsError(ConflictServiceError):
    code = "service_item_name_already_exists"
    message = "Service item with the same name already exists"

    def __init__(self, service_item_name: str | None = None) -> None:
        details = (
            {"service_item_name": str(service_item_name)}
            if service_item_name is not None
            else None
        )
        super().__init__(details=details)


# Reminder
class ReminderNotFoundError(NotFoundServiceError):
    code = "reminder_not_found"
    message = "Reminder not found"

    def __init__(self, reminder_id: UUID | None = None) -> None:
        details = {"reminder_id": str(reminder_id)} if reminder_id is not None else None
        super().__init__(details=details)


class ReminderIntervalError(BusinessRuleServiceError):
    code = "reminder_interval_invalid"
    message = "Reminder interval configuration is invalid"

    def __init__(
        self,
        *,
        interval_km: int | None = None,
        interval_days: int | None = None,
        notify_before_km: int | None = None,
        notify_before_days: int | None = None,
        reason: str | None = None,
    ) -> None:
        details: dict[str, object] = {
            "interval_km": interval_km,
            "interval_days": interval_days,
            "notify_before_km": notify_before_km,
            "notify_before_days": notify_before_days,
        }
        if reason is not None:
            details["reason"] = reason
        super().__init__(details=details)
