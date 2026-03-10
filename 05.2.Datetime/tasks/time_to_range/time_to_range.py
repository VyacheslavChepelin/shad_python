import datetime
import enum
import typing as tp  # noqa


class GranularityEnum(enum.Enum):
    """
    Enum for describing granularity
    """
    DAY = datetime.timedelta(days=1)
    TWELVE_HOURS = datetime.timedelta(hours=12)
    HOUR = datetime.timedelta(hours=1)
    THIRTY_MIN = datetime.timedelta(minutes=30)
    FIVE_MIN = datetime.timedelta(minutes=5)


def truncate_to_granularity(dt: datetime.datetime, gtd: GranularityEnum) -> datetime.datetime:
    """
    :param dt: datetime to truncate
    :param gtd: granularity
    :return: resulted datetime
    """
    if gtd == GranularityEnum.DAY:
        return dt.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    elif gtd == GranularityEnum.TWELVE_HOURS:
        return dt.replace(hour = (12 if dt.hour >= 12 else 0), minute = 0, second = 0, microsecond = 0)
    elif gtd == GranularityEnum.HOUR:
        return dt.replace(minute = 0, second = 0, microsecond = 0)
    elif gtd == GranularityEnum.THIRTY_MIN:
        return dt.replace(minute = (30 if dt.minute >= 30 else 0), second = 0, microsecond = 0)
    elif gtd == GranularityEnum.FIVE_MIN:
        return dt.replace(minute = (dt.minute // 5) * 5, second = 0, microsecond = 0)
    return dt

class DtRange:
    def __init__(
            self,
            before: int,
            after: int,
            shift: int,
            gtd: GranularityEnum
    ) -> None:
        """
        :param before: number of datetimes should take before `given datetime`
        :param after: number of datetimes should take after `given datetime`
        :param shift: shift of `given datetime`
        :param gtd: granularity
        """
        self.__before = before
        self.__after = after
        self.__shift = shift
        self.__gtd = gtd

    def __call__(self, dt: datetime.datetime) -> list[datetime.datetime]:
        """
        :param dt: given datetime
        :return: list of datetimes in range
        """
        new_dt = truncate_to_granularity(dt, self.__gtd) + self.__shift * self.__gtd.value
        return [new_dt + add * self.__gtd.value for add in range(-self.__before, self.__after + 1)]



def get_interval(
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        gtd: GranularityEnum
) -> list[datetime.datetime]:
    """
    :param start_time: start of interval
    :param end_time: end of interval
    :param gtd: granularity
    :return: list of datetimes according to granularity
    """
    start_time_gtd = truncate_to_granularity(start_time, gtd)
    end_time_gtd = truncate_to_granularity(end_time, gtd)
    interval = []
    while start_time_gtd <= end_time_gtd:
        if start_time <= start_time_gtd <= end_time:
            interval.append(start_time_gtd)
        start_time_gtd += gtd.value
    return interval
