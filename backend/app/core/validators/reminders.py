from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReminderIntervalData:
    interval_km: int | None = None
    interval_days: int | None = None
    notify_before_km: int | None = None
    notify_before_days: int | None = None


def validate_reminder_intervals(data: ReminderIntervalData) -> None:
    if data.interval_km is None and data.interval_days is None:
        raise ValueError(
            "At least one of 'interval_km' or 'interval_days' must be provided"
        )

    if data.notify_before_km is not None:
        if data.interval_km is None:
            raise ValueError(
                "If 'notify_before_km' is set, 'interval_km' must be provided"
            )
        if data.notify_before_km > data.interval_km:
            raise ValueError(
                "'notify_before_km' "
                f"({data.notify_before_km}) "
                "cannot be greater than 'interval_km' "
                f"({data.interval_km})"
            )

    if data.notify_before_days is not None:
        if data.interval_days is None:
            raise ValueError(
                "If 'notify_before_days' is set, 'interval_days' must be provided"
            )
        if data.notify_before_days > data.interval_days:
            raise ValueError(
                "'notify_before_days' "
                f"({data.notify_before_days}) "
                "cannot be greater than 'interval_days' "
                f"({data.interval_days})"
            )
