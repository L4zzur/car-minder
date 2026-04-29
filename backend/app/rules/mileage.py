from services.exceptions import OdometerNotAdvancedError, OdometerRollbackError


def validate_new_odometer(
    current_odometer_km: int,
    new_odometer_km: int,
) -> None:
    if new_odometer_km < current_odometer_km:
        raise OdometerRollbackError(
            current_odometer=current_odometer_km,
            new_odometer=new_odometer_km,
        )


def validate_new_mileage_log_odometer(
    current_odometer_km: int,
    new_odometer_km: int,
) -> None:
    validate_new_odometer(
        current_odometer_km=current_odometer_km,
        new_odometer_km=new_odometer_km,
    )
    if new_odometer_km == current_odometer_km:
        raise OdometerNotAdvancedError(
            current_odometer=current_odometer_km,
            new_odometer=new_odometer_km,
        )
