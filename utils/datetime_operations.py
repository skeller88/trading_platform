import datetime
from datetime import timezone

strftime_milliseconds = "%Y-%m-%dT%H:%M:%S%z"
strftime_seconds = "%Y-%m-%dT%H:%M:%S"
strftime_minutes = "%Y-%m-%dT%H:%M"
seconds_per_minute = 60
seconds_per_hour = 3600
seconds_per_day = seconds_per_hour * 24


def datetime_now_with_utc_offset():
    """
    https://stackoverflow.com/questions/8777753/converting-datetime-date-to-utc-timestamp-in-python
    need to make the datetime instance offset-aware, and round to nearest second for easier processing
    :param datetime:
    :return:
    """
    return datetime.datetime.utcnow().replace(tzinfo=timezone.utc)


def datetime_to_timestamp(datetime_instance):
    """
    https://stackoverflow.com/questions/8777753/converting-datetime-date-to-utc-timestamp-in-python/8778548

    This method is stripping the microseconds from datetime, and I can't figure out why.
    :param datetime_instance:
    :return:
    """
    return datetime_instance.replace(tzinfo=timezone.utc).timestamp()


def microsecond_timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(microsecond_timestamp_to_second_timestamp(timestamp), timezone.utc)


def microsecond_timestamp_to_second_timestamp(timestamp):
    return int(timestamp / 1000)


def timestamp_to_datetime(timestamp):
    """
    https://stackoverflow.com/questions/9744775/how-to-convert-integer-timestamp-to-python-datetime
    :param timestamp:
    :return:
    """
    return datetime.datetime.fromtimestamp(int(timestamp), timezone.utc)


def utc_timestamp():
    return datetime.datetime.utcnow().timestamp()