"""Generic conversion routines.

Note: date- and time- related conversion routines are in the datetimefunc module instead.
"""


__all__ = [
"str2bool", "to_bool", "bool2str", "chunk_string", "ordinal_suffix", "seconds2str",
"module2dict", "unicode2greek",
"greek2unicode", "make_code_readable", "int2superscript", "color2hex", "hex2color",
"rowsheader2dictlist", "ffmt", "smartfloat"]


import math
import re


def rowsheader2dictlist(rows, header):
    """Converts data such as used in tabulate.tabulate() to the heavily "fieldname"-redundant list of dicts.

    >>> a107.rowsheader2dictlist(((1, "John"), (2, "Terry"), (3, "Eric"), (4, "Graham"), (5, "Michael")), ("Id", "Name"))
    [{'Id': 1, 'Name': 'John'},
     {'Id': 2, 'Name': 'Terry'},
     {'Id': 3, 'Name': 'Eric'},
     {'Id': 4, 'Name': 'Graham'},
     {'Id': 5, 'Name': 'Michael'}]
    """
    ret = []
    for row in rows:
        ret.append({key: value for key, value in zip(header, row)})
    return ret


def color2hex(color, flag_lowercase=True):
    """Transforms a sequence (R, G, B[, A]) (R,G,B,A in [0, 255]) into a string of a 2-digit hexadecimal for each color.

    Args:
        color: sequence of values. If values are instance of float and <= 1, multiplies by 255 and converts to integer
        flag_lowercase: whether to return something like "abc10e" or "ABC10E"

    Returns:
        string of concatenated 2-digit hexadecimal numbers, e.g., "FE0102", which corresponds to (254, 01, 02)

    Adapted from https://stackoverflow.com/questions/3380726/converting-a-rgb-color-tuple-to-a-six-digit-code-in-python
    """

    to_int_and_clamp = lambda x: max(0, min(int(x*255 if isinstance(x, float) and x <= 1 else x), 255))

    ret = ("".join([f"{to_int_and_clamp(x):02x}" for x in color]))
    if not flag_lowercase:
        ret = ret.upper()
    return ret


def hex2color(hhhhhh):
    """Transform every 2 digits of hhhhhh into an integer in [0, 255] and returns a tuple with these integers."""
    if hhhhhh[0] == "#":
        hhhhhh = hhhhhh[1:]
    return tuple([int(hhhhhh[i:i+2], 16) for i in range(0, len(hhhhhh), 2)])


def str2bool(s):
    """Understands "T"/"F" only (case-sensitive). To be used for file parsing.

    **Note** This routine is limited on purpose for speed.
    """
    if s == "T":
        return True
    elif s == "F":
        return False
    raise ValueError("I don't understand '{0!s}' as a logical value".format(s))


def to_bool(s):
    """More clever and slower. Understands T, TRUE, ON, F, FALSE, OFF. Case insensitive."""
    if isinstance(s, bool):
        return s
    if isinstance(s, (int, float)):
        return s != 0
    s = s.upper()
    if s in ("T", "TRUE", "ON", "1"):
        return True
    elif s in ("F", "FALSE", "OFF", "0"):
        return False
    raise ValueError("I don't understand '{0!s}' as a logical value".format(s))


def bool2str(x):
    """Converts bool variable to either "T" or "F".

    **Note** This routine is limited on purpose for speed.
    """
    assert isinstance(x, bool)
    return "T" if x else "F"


def make_code_readable(s):
    """Add newlines at strategic places in code string for printing.

    Args:
        s: str, piece of code. If not str, will attempt to convert to str.

    Returns:
        str
    """

    s = s if isinstance(s, str) else str(s)

    MAP = {",": ",\n", "{": "{\n ", "}": "\n}"}

    ll = []

    state = "open"
    flag_single = False
    flag_double = False
    flag_backslash = False
    for ch in s:
        if flag_backslash:
            flag_backslash = False
            continue

        if ch == "\\":
            flag_backslash = True
            continue

        if flag_single:
            if ch == "'":
                flag_single = False
        elif not flag_double and ch == "'":
            flag_single = True

        if flag_double:
            if ch == '"':
                flag_double = False
        elif not flag_single and ch == '"':
            flag_double = True

        if flag_single or flag_double:
            ll.append(ch)
        else:
            ll.append(MAP.get(ch, ch))

    return "".join(ll)


def chunk_string(string, length):
    """
    Splits a string into fixed-length chunks.

    This function returns a generator, using a generator comprehension. The
    generator returns the string sliced, from 0 + a multiple of the length
    of the chunks, to the length of the chunks + a multiple of the length
    of the chunks.

    Reference: http://stackoverflow.com/questions/18854620
    """
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def ordinal_suffix(i):
    """Returns 'st', 'nd', or 'rd'."""
    v = str(i)
    return "st" if v.endswith("1") \
            else "nd" if v.endswith("2") else "rd" if v.endswith("3") else "th"


def seconds2str(seconds):
    """Returns string such as 1h 05m 55s."""

    if seconds < 0:
        return "{0:.3g}s".format(seconds)
    elif math.isnan(seconds):
        return "NaN"
    elif math.isinf(seconds):
        return "Inf"

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h >= 1:
        return "{0:g}h {1:02g}m {2:.3g}s".format(h, m, s)
    elif m >= 1:
        return "{0:02g}m {1:.3g}s".format(m, s)
    else:
        return "{0:.3g}s".format(s)


def module2dict(module):
    """Creates a dictionary whose keys are module.__all__

    Returns: {"(attribute name)": attribute, ...}
    """

    lot = [(key, module.__getattribute__(key)) for key in module.__all__]
    ret = dict(lot)
    return ret

# **        ****                ******        ****                ******        ****
#   **    **    ******    ******      **    **    ******    ******      **    **    ******    ******
#     ****            ****              ****            ****              ****            ****
#
# Greek alphabet-related routines.
# These routines were created for my Convmol project, but I thought they are kindda cool. Who knows

# Source:
#     "A Python dictionary mapping the Unicode codes of the greek alphabet to their names"
#     https://gist.github.com/beniwohli/765262
#
_UNICODE_GREEK = (
('\u0391', 'Alpha'),
('\u0392', 'Beta'),
('\u0393', 'Gamma'),
('\u0394', 'Delta'),
('\u0395', 'Epsilon'),
('\u0396', 'Zeta'),
('\u0397', 'Eta'),
('\u0398', 'Theta'),
('\u0399', 'Iota'),
('\u039A', 'Kappa'),
('\u039B', 'Lamda'),
('\u039C', 'Mu'),
('\u039D', 'Nu'),
('\u039E', 'Xi'),
('\u039F', 'Omicron'),
('\u03A0', 'Pi'),
('\u03A1', 'Rho'),
('\u03A3', 'Sigma'),
('\u03A4', 'Tau'),
('\u03A5', 'Upsilon'),
('\u03A6', 'Phi'),
('\u03A7', 'Chi'),
('\u03A8', 'Psi'),
('\u03A9', 'Omega'),
('\u03B1', 'alpha'),
('\u03B2', 'beta'),
('\u03B3', 'gamma'),
('\u03B4', 'delta'),
('\u03B5', 'epsilon'),
('\u03B6', 'zeta'),
('\u03B7', 'eta'),
('\u03B8', 'theta'),
('\u03B9', 'iota'),
('\u03BA', 'kappa'),
('\u03BB', 'lamda'),
('\u03BC', 'mu'),
('\u03BD', 'nu'),
('\u03BE', 'xi'),
('\u03BF', 'omicron'),
('\u03C0', 'pi'),
('\u03C1', 'rho'),
('\u03C3', 'sigma'),
('\u03C4', 'tau'),
('\u03C5', 'upsilon'),
('\u03C6', 'phi'),
('\u03C7', 'chi'),
('\u03C8', 'psi'),
('\u03C9', 'omega'),
)

_UNICODE2GREEK = dict(_UNICODE_GREEK)
_GREEK2UNICODE = dict([(x[1], x[0]) for x in _UNICODE_GREEK])

def unicode2greek(s):
    """Converts unicode single code, e.g., '\u03A3' to Greek letter name, e.g. 'Sigma'"""

    # "?" is the "zero-element"
    if s == "?":
        return s

    return _UNICODE2GREEK[s]

def greek2unicode(s):
    """Converts Greek letter name, e.g., 'Sigma', to unicode character, e.g. '\u03A3' """

    # "?" is the "zero-element"
    if s == "?":
        return s

    return _GREEK2UNICODE[s]


# superscript numbers
_INT_TO_SUPERSCRIPT = {
 0: "\u2070",
 1: "\u2071",
 2: "\u00b2",
 3: "\u00b3",
 4: "\u2074",
 5: "\u2075",
 6: "\u2076",
 7: "\u2077",
 8: "\u2078",
 9: "\u2079",
}

def int2superscript(i):
    """int2superscript(i) --> str"""

    return "".join((_INT_TO_SUPERSCRIPT[int(ch)] for ch in str(i)))


#-----------------------------------------------------------------------------------------------------------------------
# The floating-point formatting solution

def smartfloat(f, maxsig=6, maxdec=10):
    """Float version of ffmt() (useful e.g. in order to let tabulate.tabulate() align floats)."""
    return float(ffmt(f, maxsig, maxdec))


def ffmt(f, maxsig=6, maxdec=10):
    """Formats float number in float format with maximum number of significant digits.
    Args:
        f: float number to be formatted
        maxsig: maximum number of significant digits
        maxdec: maximum number of decimals (after which f will be rounded in any case)

    Returns: str

    >>> ffmt(0.000000079)
    '0.000000079'
    >>> ffmt(0.00000007999)
    '0.00000008'
    >>> ffmt(12345678.123457)
    '12345700.'
    """
    flag_neg = f < 0
    f = abs(f)
    s = f"{f:.{maxdec}f}"
    dotpos = s.index(".")
    s = s.replace(".", "")
    s = s.rstrip("0")
    n = len(s)
    s = s.lstrip("0")
    numleadingzeros = n-len(s)
    n = len(s)
    if n > maxsig:
        s = str(round(int(s)/10**(n-maxsig)))
    s = "0"*numleadingzeros+s
    n = len(s)
    if n < dotpos:
        s += "0"*(dotpos-n)
    s = (s[:dotpos]+"."+s[dotpos:])
    if flag_neg:
        s = "-"+s
    return s
