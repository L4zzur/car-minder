from services.exceptions import OdometerRollbackError


def validate_new_odometer(
    current_odometer_km: int,
    new_odometer_km: int,
) -> None:
    if new_odometer_km < current_odometer_km:
        raise OdometerRollbackError(
            current_odometer=current_odometer_km,
            new_odometer=new_odometer_km,
        )
