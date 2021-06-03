import a107, datetime

ts = a107.dt2ts(datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc))
print(ts)