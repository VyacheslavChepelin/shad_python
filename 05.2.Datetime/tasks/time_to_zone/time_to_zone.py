from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_TZ_NAME = "Europe/Moscow"


def now() -> datetime:
    """Return now in default timezone"""
    return datetime.now(tz = ZoneInfo(DEFAULT_TZ_NAME))

def strftime(dt: datetime, fmt: str) -> str:
    """Return dt converted to string according to format in default timezone"""
    dt = (
        dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME))
        if dt.tzinfo is not None
        else dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    )
    return dt.strftime(fmt)


def strptime(dt_str: str, fmt: str) -> datetime:
    """Return dt parsed from string according to format in default timezone"""
    dt = datetime.strptime(dt_str, fmt)
    if dt.tzinfo is None:
        return dt.replace(tzinfo = ZoneInfo(DEFAULT_TZ_NAME))
    else:
        return dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME))


def diff(first_dt: datetime, second_dt: datetime) -> int:
    """Return seconds between two datetimes rounded down to closest int"""
    second_dt = (
        second_dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME))
        if second_dt.tzinfo is not None
        else second_dt.replace(tzinfo = ZoneInfo(DEFAULT_TZ_NAME)))
    first_dt = (
        first_dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME))
        if first_dt.tzinfo is not None
        else first_dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    )
    return int((second_dt - first_dt).total_seconds())

def timestamp(dt: datetime) -> int:
    """Return timestamp for given datetime rounded down to closest int"""
    dt = (
        dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME))
        if dt.tzinfo is not None
        else dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    )
    return int(dt.timestamp())


def from_timestamp(ts: float) -> datetime:
    """Return datetime from given timestamp"""
    return datetime.fromtimestamp(ts, tz=ZoneInfo(DEFAULT_TZ_NAME))
