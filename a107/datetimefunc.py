"""Date/time utilities, mostly all sorts of conversions.

In 20210528, I added ts and tzinfo options to all methods that convert to datetime, where applicable (see tzinfo_tz()).


"""
import math, datetime, dateutil.parser, numpy as np

__all__ = ["now_str", "date2datetime", "dt2ts", "ts2dt", "dt2str", "str2dt", "ts2str",
           "time2seconds", "seconds2time", "to_datetime", "str2ts", "iso8601_to_float",
           "float_to_iso8601", "dt2slug", "v_ts2dt", "to_timestamp", "tzinfo_tz", "utc",
           "now_ts"]

utc = datetime.timezone.utc

_FMT = "%Y-%m-%d %H:%M"  # Date & time format
_FMTS = "%Y-%m-%d %H:%M:%S"  # Date & time format with seconds
_FMT0 = "%Y-%m-%d"  # Date format only
_FMT1 = "%Y%m%d" # Date format, compacted
_FMTSTAMP = "%Y.%m.%d.%H.%M.%S"  # Format for dates and times that will be parts of filenames


def now_str(tz=None):
    return datetime.datetime.strftime(datetime.datetime.now(tz), _FMTS)

def now_ts():
    return dt2ts(datetime.datetime.now())


def tzinfo_tz(dt, tzinfo=None, tz=None):
    """Adds/replaces (tzinfo) and/or shifts (tz) timezone of date.

    Args:
        dt: datetime.datetime
        tzinfo: adds/replaces timezone information to newly generated datetime
        tz: shifts the timezone as if you were teleported instantaneously to other place in the world

    Returns: new datetime.datetime

    tzinfo and tz can be combined (the former takes effect before the latter)."""
    if tzinfo is not None: dt = dt.replace(tzinfo=tzinfo)
    if tz is not None: dt = dt.astimezone(tz)
    return dt


def date2datetime(date, tzinfo=None):
    ret = datetime.datetime.combine(date, datetime.datetime.min.time())
    if tzinfo is not None: ret = ret.replace(tzinfo=tzinfo)
    return ret


def dt2ts(dt):
    """Converts to float representing number of seconds since 1970-01-01 GMT. This method is timezone-aware.

    This method is timezone-aware, so that the same datetime specification at different timezones will give different
    timestamps:

        >>> a107.dt2ts(datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc))
        0.0
        >>> a107.dt2ts(datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone(datetime.timedelta(hours=-3))))
        10800.0  # It was already 3 am in the UK when the day of 1970-01-01 started in Brazil
        >>> a107.dt2ts(datetime.datetime(1970, 1, 1))
        10800.0  # This is the result I get in Brazil (timezone-naïve cas works as if local)

    """
    if dt.__class__ == datetime.date: dt = date2datetime(dt)
    else: assert isinstance(dt, datetime.datetime)
    ret = dt.timestamp()
    return ret


def ts2dt(ts, tz=None):
    """Converts timestamp to datetime.

    My timezone is GMT-3, so it gives me my time when UK was seeing the "epoch":

        >>> a107.ts2dt(0)
        datetime.datetime(1969, 12, 31, 21, 0)

    Now if I shift the timezone to UTC, we see the "epoch" being printed

        >>> a107.ts2dt(0).astimezone(datetime.timezone.utc)
        datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)

    The above is equivalent to:

        >>> a107.ts2dt(0, datetime.timezone.utc)
        datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    """
    ret = datetime.datetime.fromtimestamp(ts)
    if tz is not None: ret = ret.astimezone(tz)
    return ret


v_ts2dt = np.vectorize(ts2dt)
v_ts2dt.__doc__ = """Vectorized version of ts2dt()"""


def dt2str(dt, flagSeconds=True):
    """Converts datetime object to str if not yet an str."""
    if isinstance(dt, str):
        return dt
    return dt.strftime((_FMTS if flagSeconds else _FMT) if isinstance(dt, datetime.datetime) else _FMT0)


def dt2slug(dt):
    """Converts datetime to a 'slug' str to embed in filenames, for example."""
    return dt.strftime(_FMTSTAMP if isinstance(dt, datetime.datetime) else _FMT1)


def str2dt(s, tzinfo=None):
    """Converts str to datetime."""
    fmt = _FMT1 if len(s) == 8 \
          else _FMTS if s.count(":") == 2 else _FMT if s.count(":") == 1 \
          else _FMT0
    ret = datetime.datetime.strptime(s, fmt)
    if tzinfo is not None: ret = ret.replace(tzinfo=tzinfo)
    return ret


def ts2str(s, flagSeconds:bool = True, tz=None):
    """Shortcut to dt2str(ts2dt(s))."""
    assert isinstance(flagSeconds, bool)
    return dt2str(ts2dt(s, tz=tz), flagSeconds)


def str2ts(s, tzinfo=None):
    """Converts str (expressed in local time) to timestamp."""
    return dt2ts(str2dt(s, tzinfo=tzinfo))


def to_datetime(arg):
    """Tries to convert any type of argument to datetime.

    Special values:
        "?": will be converted to 1970-1-1
    """
    if isinstance(arg, datetime.datetime):
        return arg
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
    """Tries to convert anything into a timestamp. This method is timezone-aware (as it eventually uses dt2ts())."""
    if isinstance(arg, float): return arg
    dt = to_datetime(arg)
    ret = dt2ts(dt)
    return ret


def iso8601_to_float(s):
    return dateutil.parser.parse(s).timestamp()


def float_to_iso8601(w):
    return datetime.datetime.utcfromtimestamp(w).isoformat()


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
