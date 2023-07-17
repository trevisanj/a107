class AutoClass:
    """Generic data class: attributes are figured out from **kwargs."""

    def __init__(self, **kwargs):
        self.__aa = []
        for k, v in kwargs.items():
            setattr(self, k, v)
            if k not in self.__aa: self.__aa.append(k)
        self.__post_init__()

    def __post_init__(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}("+", ".join([x+"="+repr(getattr(self, x)) for x in self.__aa])+")"

    def set(self, attrname, value):
        if attrname not in self.__aa: self.__aa.append(attrname)
        self.__dict__[attrname] = value

    def to_dict(self):
        ret = {}; mydict = self.__dict__
        for key in self.__aa: ret[key] = mydict.get(key)
        return ret