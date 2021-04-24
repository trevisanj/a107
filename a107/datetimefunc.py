"""Date/time utilities, mostly all sorts of conversions"""

import math
import time
import datetime
import dateutil.parser
import numpy as np

__all__ = ["now_str", "date2datetime", "dt2ts", "ts2dt", "dt2str", "str2dt", "ts2str",
           "time2seconds", "seconds2time", "to_datetime", "str2ts", "iso8601_to_float",
           "float_to_iso8601", "dt2stamp", "v_ts2dt", "to_timestamp"]


_FMT = "%Y-%m-%d %H:%M"  # Date & time format
_FMTS = "%Y-%m-%d %H:%M:%S"  # Date & time format with seconds
_FMT0 = "%Y-%m-%d"  # Date format only
_FMT1 = "%Y%m%d" # Date format, compacted
_FMTSTAMP = "%Y.%m.%d.%H.%M.%S"  # Format for dates and times that will be parts of filenames

def now_str():
    return datetime.datetime.strftime(datetime.datetime.now(), _FMTS)


def date2datetime(date):
    return datetime.datetime.combine(date, datetime.datetime.min.time())


def dt2ts(dt):
    """Converts to float representing number of seconds since 1970-01-01 GMT."""
    # Note: no assertion to really keep this fast
    assert isinstance(dt, (datetime.datetime, datetime.date))
    ret = time.mktime(dt.timetuple())
    if isinstance(dt, datetime.datetime):
        ret += 1e-6 * dt.microsecond
    return ret
    # except ValueError:
    #   return 0

def ts2dt(ts, flag_microseconds=True):
    """Converts timestamp to a datetime, with option of dropping the microseconds."""
    if not flag_microseconds:
        ts = int(ts)
    return datetime.datetime.fromtimestamp(ts)

v_ts2dt = np.vectorize(ts2dt)
v_ts2dt.__doc__ = """Vectorized version of ts2dt()"""

def dt2str(dt, flagSeconds=True):
    """Converts datetime object to str if not yet an str."""
    if isinstance(dt, str):
        return dt
    return dt.strftime((_FMTS if flagSeconds else _FMT) if isinstance(dt, datetime.datetime) else _FMT0)


def dt2stamp(dt):
    """Converts datetime to a 'stamp' str to embed in filenames, for example."""
    return dt.strftime(_FMTSTAMP if isinstance(dt, datetime.datetime) else _FMT1)

def str2dt(s):
    """Works with time with/without seconds."""
    return datetime.datetime.strptime(s, _FMT1 if len(s) == 8 else
        _FMTS if s.count(":") == 2 else _FMT if s.count(":") == 1 else _FMT0)


def ts2str(s, flagSeconds=True):
    """Shortcut to dt2str(ts2dt(s))."""
    return dt2str(ts2dt(s), flagSeconds) if s > 0 else ""


def str2ts(s):
    """Converts str to timestamp."""
    return dt2ts(str2dt(s))

def time2seconds(t):
    """Returns seconds since 0h00."""
    return t.hour * 3600 + t.minute * 60 + t.second + float(t.microsecond) / 1e6


def seconds2time(s):
    """Inverse of time2seconds()."""
    hour, temp = divmod(s, 3600)
    minute, temp = divmod(temp, 60)
    temp, second = math.modf(temp)
    return datetime.time(hour=int(hour), minute=int(minute), second=int(second),
                         microsecond=int(round(temp * 1e6)))

def to_datetime(arg):
    """Tries to convert any type of argument to datetime

    Args:
        arg: datetime, date, or str. If "?", will be converted to 1970-1-1.
             if 0 or "now", will be converted to datetime.datetime.now()
    """


    if isinstance(arg, datetime.datetime):
        return arg
    elif arg == 0:
        return datetime.datetime.now()
    elif isinstance(arg, str):
        if arg == "now":
            arg = datetime.datetime.now()
        elif arg == "?":
            arg = datetime.datetime(1970, 1, 1)
        else:
            arg = str2dt(arg)
    elif isinstance(arg, datetime.date):
        arg = date2datetime(arg)
    elif isinstance(arg, (int, float)):
        # Suppose it is a timestamp
        arg = ts2dt(arg)
    else:
        raise TypeError("Wrong type for argument 'arg': {}".format(arg.__class__.__name__))

    return arg


def to_timestamp(arg):
    """Tries to convert anything into a timestamp."""
    if isinstance(arg, float):
        return arg
    return dt2ts(to_datetime(arg))


def iso8601_to_float(s):
    return dateutil.parser.parse(s).timestamp()


def float_to_iso8601(w):
    return datetime.datetime.utcfromtimestamp(w).isoformat()
