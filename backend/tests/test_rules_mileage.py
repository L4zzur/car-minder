import pytest

from rules.mileage import validate_new_mileage_log_odometer, validate_new_odometer
from services.exceptions import OdometerNotAdvancedError, OdometerRollbackError


def test_validate_new_odometer_valid():
    """Higher or equal odometer reading should pass validation."""
    validate_new_odometer(current_odometer_km=10000, new_odometer_km=10500)
    validate_new_odometer(current_odometer_km=10000, new_odometer_km=10000)


def test_validate_new_odometer_rollback_raises_error():
    """Lower odometer reading must raise OdometerRollbackError."""
    with pytest.raises(OdometerRollbackError) as exc_info:
        validate_new_odometer(current_odometer_km=10000, new_odometer_km=9999)

    exc = exc_info.value
    assert exc.status_code == 422
    assert exc.code == "odometer_rollback"
    assert exc.details["current_odometer"] == 10000
    assert exc.details["new_odometer"] == 9999


def test_validate_new_mileage_log_odometer_valid():
    """Strictly higher odometer reading for a new log should pass validation."""
    validate_new_mileage_log_odometer(current_odometer_km=50000, new_odometer_km=50100)


def test_validate_new_mileage_log_odometer_equal_raises_error():
    """Same odometer reading for a new log must raise OdometerNotAdvancedError."""
    with pytest.raises(OdometerNotAdvancedError) as exc_info:
        validate_new_mileage_log_odometer(
            current_odometer_km=50000, new_odometer_km=50000
        )

    exc = exc_info.value
    assert exc.status_code == 422
    assert exc.code == "odometer_not_advanced"
    assert exc.details["current_odometer"] == 50000
    assert exc.details["new_odometer"] == 50000


def test_validate_new_mileage_log_odometer_rollback_raises_error():
    """Lower odometer reading for a new log must raise OdometerRollbackError."""
    with pytest.raises(OdometerRollbackError) as exc_info:
        validate_new_mileage_log_odometer(
            current_odometer_km=50000, new_odometer_km=49999
        )

    exc = exc_info.value
    assert exc.status_code == 422
    assert exc.code == "odometer_rollback"
    assert exc.details["current_odometer"] == 50000
    assert exc.details["new_odometer"] == 49999
