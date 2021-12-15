"""Text interface routines - input/output for the terminal."""

import textwrap, sys, random, os, argparse, numpy as np
from colored import fg, bg, attr
from .loggingaux import SmartFormatter

__all__ = ["format_h1", "format_h2", "format_h3", "format_h4",
           "format_error", "format_warning", "format_debug", "print_error", "menu", "format_progress", "markdown_table",
           "format_box", "yesno", "rest_table", "expand_multirow_data",
           "question", "format_slug", "print_file", "aargh", "format_yoda", "format_madyoda", "print_cfg",
           "format_color", "print_girafales", "fancilyquoted", "format_h", "print_polluted", "kebab"]


NIND = 2  # Number of spaces per indentation level
COLORED_ERROR = fg("salmon_1")
COLORED_WARNING = fg("yellow")
COLORED_DEBUG = fg("deep_pink_1a")


########################################################################################################################
# Methods that return list or str

def format_slug(s, eye=None, fmt="list"):
    """
    Encloses string inside the guts of an ASCII-art [1] slug.
    
    Args:
        s: str
        eye: 0, 1, 2, or None. If None, will be random.
        fmt: format of result. For possible values for this argument, see _validate_fmt()

    Returns:
        list, str etc., depending on fmt

    References:
        [1] http://ascii.co.uk/art/snail
    """

    _validate_fmt(fmt)

    n = len(s)
    a, b, c, d = (x*n for x in '  _"')
    s_ = s  # .replace(" ", "-")

    if eye is None:
        eye = random.randint(0, 2)

    z = "." if eye == 0 else "o" if eye == 1 else "O"
    k = " "
    ret = [
    f'    {a}{z}  {z}',
    f'     {b}\\/ ',
    f'   _{c}_/|',
    f' /´{k}{s_}{k}´/ ',
    f'/+""{d}"´  ',
    ]
    return _list_or_str(ret, fmt)


def format_underline(s, char="=", indents=0, fmt="list"):
    """
    Traces a dashed line below string

    Args:
        s: string
        char:
        indents: number of leading intenting spaces
        fmt: format of result. For possible values for this argument, see _validate_fmt()

    Returns:
        list, str etc., depending on fmt

    >>> print("\\n".join(format_underline("Life of João da Silva", "^", 2)))
      Life of João da Silva
      ^^^^^^^^^^^^^^^^^^^^^
    """

    _validate_fmt(fmt)

    n = len(s)
    ind = " " * indents
    ret = ["{}{}".format(ind, s), "{}{}".format(ind, char*n)]
    return _list_or_str(ret, fmt)


def format_h(i, s, format="text", indents=0, fmt="list"):
    return {1: format_h1, 2: format_h2, 3: format_h3, 4: format_h4, 4: format_h5}[i](s, format, indents, fmt)


def format_h1(s, format="text", indents=0, fmt="list"):
    """
    Encloses string in format text

    Args:
        s: string
        format: "text"/"markdown"/"rest"/"html"
        indents: number of leading intenting spaces
        fmt: format of result. For possible values for this argument, see _validate_fmt()

    Returns:
        list, str etc., depending on fmt

    >>> print("\\n".join(format_h2("Header 1", indents=10)))
              Header 1
              --------

    >>> print("\\n".join(format_h2("Header 1", "markdown", 0)))
    ## Header 1
    """

    _validate_fmt(fmt)

    _CHAR = "="
    return _format_h_aux(s, format, indents, fmt, _CHAR, 1)


def format_h2(s, format="text", indents=0, fmt="list"):
    """format_h ~1~ 2"""
    _validate_fmt(fmt)
    _CHAR = "-"
    return _format_h_aux(s, format, indents, fmt, _CHAR, 2)


def format_h3(s, format="text", indents=0, fmt="list"):
    """format_h ~1~ 3"""
    _validate_fmt(fmt)
    _CHAR = "~"
    return _format_h_aux(s, format, indents, fmt, _CHAR, 3)


def format_h4(s, format="text", indents=0, fmt="list"):
    """format_h ~1~ 4"""
    _validate_fmt(fmt)
    _CHAR = "^"
    return _format_h_aux(s, format, indents, fmt, _CHAR, 4)


def format_h5(s, format="text", indents=0, fmt="list"):
    """format_h ~1~ 5"""
    _validate_fmt(fmt)
    _CHAR = "5"
    return _format_h_aux(s, format, indents, fmt, _CHAR, 5)


def markdown_table(data, headers, fmt="list"):
    """
    Creates MarkDown table. Returns list of strings

    Args:
        data: [(cell00, cell01, ...), (cell10, cell11, ...), ...]
        headers: sequence of strings: (header0, header1, ...)
        fmt: format of result. For possible values for this argument, see _validate_fmt()

    Returns:
        list, str etc., depending on fmt
    """

    _validate_fmt(fmt)

    maxx = [max([len(x) for x in column]) for column in zip(*data)]
    maxx = [max(ll) for ll in zip(maxx, [len(x) for x in headers])]
    mask = " | ".join(["%-{0:d}s".format(n) for n in maxx])

    ret = [mask%tuple(headers)]

    ret.append(" | ".join(["-"*n for n in maxx]))
    for line in data:
        ret.append(mask%tuple(line))
    return _list_or_str(ret, fmt)


def rest_table(data, headers, fmt="list"):
    """
    Creates reStructuredText table (grid format), allowing for multiline cells

    Arguments:
        data:  [((cell000, cell001, ...), (cell010, cell011, ...), ...), ...]
        headers: sequence of strings: (header0, header1, ...)
        fmt: format of result. For possible values for this argument, see _validate_fmt()

    Returns:
        list, str etc., depending on fmt

    **Note** Tolerant to non-strings

    **Note** Cells may or may not be multiline

    >>> rest_table([["Eric", "Idle"], ["Graham", "Chapman"], ["Terry", "Gilliam"]], ["Name", "Surname"])
    """

    _validate_fmt(fmt)

    num_cols = len(headers)
    new_data, row_heights = expand_multirow_data(data)
    new_data = [[str(x) for x in row] for row in new_data]
    col_widths = [max([len(x) for x in col]) for col in zip(*new_data)]
    col_widths = [max(cw, len(s)) for cw, s in zip(col_widths, headers)]

    if any([x == 0 for x in col_widths]):
        raise RuntimeError("Column widths ({}) has at least one zero".format(col_widths))

    num_lines = sum(row_heights)  # line != row (rows are multiline)

    # horizontal lines
    hl0 = "+"+"+".join(["-"*(n+2) for n in col_widths])+"+"
    hl1 = "+"+"+".join(["="*(n+2) for n in col_widths])+"+"

    frmtd = ["{0:{1}}".format(x, width) for x, width in zip(headers, col_widths)]
    ret = [hl0, "| "+" | ".join(frmtd)+" |", hl1]

    i0 = 0
    for i, row_height in enumerate(row_heights):
        if i > 0:
            ret.append(hl0)
        for incr in range(row_height):
            frmtd = ["{0:{1}}".format(x, width) for x, width in zip(new_data[i0+incr], col_widths)]
            ret.append("| "+" | ".join(frmtd)+" |")
        i0 += row_height

    ret.append(hl0)
    return _list_or_str(ret, fmt)


########################################################################################################################
# Other stuff

def format_color(s, fg_=None, bg_=None, attrs=None):
    """Wraps over colored for convenience"""
    aa = []
    if fg_: aa.append(fg(fg_))
    if bg_: aa.append(bg(bg_))
    if attrs:
        if isinstance(attrs, str):
            attrs = [attrs]
        aa.extend([attr(attr_) for attr_ in attrs])
    return "".join(aa)+s+attr("reset")


def format_yoda(s, happy=True):
    """The classic Yoda formatting."""
    return "{4}{2}{0}|o_o|{0} -- {1}{3}".format("^" if happy else "v", s, fg("dark_olive_green_3a"), attr("reset"), attr("bold"))


def format_madyoda(s, happy=True):
    """Randomize the words Yoda will. Messed it is I know, but care do I?"""
    words = s.split(" ")
    random.shuffle(words)
    s2 = " ".join(words)
    return format_yoda(s, happy)

def format_error(s):
    """Standardized embellishment. Adds formatting to error message."""
    return _format_genericlog(s, "Error", COLORED_ERROR)

def format_warning(s):
    """Standardized embellishment. Adds formatting to warning message."""
    return _format_genericlog(s, "Warning", COLORED_WARNING)

def format_debug(s):
    """Standardized embellishment. Adds formatting to warning message."""
    return _format_genericlog(s, "Debug", COLORED_DEBUG)

def print_error(s):
    """Prints string as error message."""
    print((format_error(s)))


def question(question, options, default=None):
    """Ask a question with case-insensitive options of answers

    Args:
        question: string **without** the question mark and without the options.
            Example: 'Commit changes'
        options: string or sequence of strings. If string, options will be single-lettered.
            Examples: 'YNC', ['yes', 'no', 'cancel']. options are case-insensitive
        default: default option. If passed, default option will be shown in uppercase.

    Answers are case-insensitive, but options will be shown in lowercase, except for the default
    option.

    Returns:
        str: chosen option. Although the answer is case-insensitive, the result will be as informed
             in the 'options' argument.
    """

    # Make sure options is a list
    options_ = [x for x in options]

    if default is not None and default not in options_:
        raise ValueError("Default option '{}' is not in options {}.".format(default, options))

    oto = "/".join([x.upper() if x == default else x.lower() for x in options_])  # to show
    ocomp = [x.lower() for x in options_]  # to be used in comparison

    while True:
        ans = input("{} ({})? ".format(question, oto)).lower()
        if ans == "" and default is not None:
            ret = default
            break
        elif ans in ocomp:
            ret = options_[ocomp.index(ans)]
            break
    return ret


def yesno(question, default=None):
    """Asks a yes/no question

    Args:
        question: string **without** the question mark and without the options.
            Example: 'Create links'
        default: default option. Accepted values are True, False, 'Y', 'YES', 'N', 'NO'
            or lowercase versions of these values (this argument is case-insensitive)

    Returns:
        bool: True if user answered Yes, False otherwise
    """

    if default is not None:
        if isinstance(default, bool):
            pass
        elif isinstance(default, int):
            default = bool(default)
        else:
            default_ = default.upper()
            if default_ not in ('Y', 'YES', 'N', 'NO'):
                raise RuntimeError("Invalid default value: '{}'".format(default))
            default = default_ in ('Y', 'YES')

    while True:
        ans = input("{} ({}/{})? ".format(question, "Y" if default == True else "y",
                                         "N" if default == False else "n")).upper()
        if ans == "" and default is not None:
            ret = default
            break
        elif ans in ("N", "NO"):
            ret = False
            break
        elif ans in ("Y", "YES"):
            ret = True
            break
    return ret


def menu(title, options, cancel_label="Cancel", flag_allow_empty=False, flag_cancel=True, ch='.'):
  """Text menu.

  Arguments:
    title -- menu title, to appear at the top
    options -- sequence of strings
    cancel_label='Cancel' -- label to show at last "zero" option
    flag_allow_empty=0 -- Whether to allow empty option
    flag_cancel=True -- whether there is a "0 - Cancel" option
    ch="." -- character to use to draw frame around title

  Returns:
    option -- an integer: None; 0-Back/Cancel/etc; 1, 2, ...

  Adapted from irootlab menu.m"""

  num_options, flag_ok = len(options), 0
  option = None  # result
  min_allowed = 0 if flag_cancel else 1  # minimum option value allowed (if option not empty)

  while True:
    print("")
    for line in format_box(title, ch):
        print("  "+line)
    for i, s in enumerate(options):
      print(("  {0:d} - {1!s}".format(i+1, s)))
    if flag_cancel: print(("  0 - << (*{0!s}*)".format(cancel_label)))
    try:
        s_option = input('? ')
    except KeyboardInterrupt:
        raise
    except:
        print("")

    n_try = 0
    while True:
      if n_try >= 10:
        print('You are messing up!')
        break

      if len(s_option) == 0 and flag_allow_empty:
        flag_ok = True
        break

      try:
        option = int(s_option)
        if min_allowed <= option <= num_options:
          flag_ok = True
          break
      except ValueError:
        print("Invalid integer value!")

      print(("Invalid option, range is [{0:d}, {1:d}]!".format(0 if flag_cancel else 1, num_options)))

      n_try += 1
      s_option = input("? ")

    if flag_ok:
      break
  return option


class Roller:
    """Class to roll same string over and over."""
    def __init__(self, s):
        self.arr = np.fromiter(s, (str, 1))
        self.n = len(s)

    def get(self, size, start=0):
        indexes = np.mod(np.arange(start, start+size), self.n)
        return "".join(self.arr[indexes])


def format_box(title, ch="*", fmt="list"):
    """
    Encloses title in a box.

    Args:
        title:
        ch:
        fmt: "list"/"str"

    Returns:
        list or str, depending on fmt

    >>> for line in format_box("Today's T.O.D.O. list"):
    ...     print(line)
    *****************************
    *** Today's T.O.D.O. list ***
    *****************************
    """

    _validate_fmt(fmt)
    r = Roller(ch)
    lt = len(title)
    s0 = r.get(lt+8)
    ret = [s0,
           (r.get(3) + " " + title + " " + r.get(3, lt+5)),
           s0,
          ]
    return _list_or_str(ret, fmt)


def format_progress(i, n):
    """Returns string containing a progress bar, a percentage, etc."""
    if n == 0:
        fraction = 0
    else:
        fraction = float(i)/n
    LEN_BAR = 25
    num_plus = int(round(fraction*LEN_BAR))
    s_plus = '+'*num_plus
    s_point = '.'*(LEN_BAR-num_plus)
    return '[{0!s}{1!s}] {2:d}/{3:d} - {4:.1f}%'.format(s_plus, s_point, i, n, fraction*100)


# ######################################################################################################################
# Text table functions


def expand_multirow_data(data):
    """
    Converts multirow cells to a list of lists and informs the number of lines of each row.

    Returns:
         tuple: new_data, row_heights
    """

    num_cols = len(data[0]) # number of columns

    # calculates row heights
    row_heights = []
    for mlrow in data:
        row_height = 0
        for j, cell in enumerate(mlrow):
            row_height = max(row_height, 1 if not isinstance(cell, (list, tuple)) else len(cell))
        row_heights.append(row_height)
    num_lines = sum(row_heights) # line != row (rows are multiline)

    # rebuilds table data
    new_data = [[""]*num_cols for i in range(num_lines)]
    i0 = 0
    for row_height, mlrow in zip(row_heights, data):
        for j, cell in enumerate(mlrow):
            if not isinstance(cell, (list, tuple)):
                cell = [cell]

            for incr, x in enumerate(cell):
                new_data[i0+incr][j] = x

        i0 += row_height

    return new_data, row_heights


def print_file(path_, width=80):
    """Prints File.

    Args:
        path_: path to file
        width:

    """
    printb = lambda s: print("{}{}{}".format(fg("blue"), s.strip(), attr("reset")))
    printbb = lambda s: print("{}{}{}{}".format(fg("blue"), attr("bold"), s.strip(), attr("reset")))
    bname = os.path.basename(path_)
    n = len(bname)
    printbb(f"--|{bname}|" + "-" * (width - n - 4))
    with open(path_, "r") as f:
        for line in f:
            printb(line)
    printbb("-" * width)


def aargh(doc, main):
    """
    Command-line interface with argument parser without parameters.

    Arguments:

    """
    parser = argparse.ArgumentParser(description=doc, formatter_class=SmartFormatter)
    args = parser.parse_args()
    main()


def print_cfg(cfg):
    """Use this to print argparse's parsed args (which I now calls cfg, not args)."""
    for attrname in dir(cfg):
        if not attrname.startswith("_"):
            print(f"{attrname}={repr(getattr(cfg, attrname))}")


def print_girafales(s):
    """Formats tabulate.tabulate()-generated output in table style. I don't know why this method has this name."""
    lines = s.split("\n"); n = len(lines)
    sepindex = [line.startswith("-") for line in lines].index(True)
    maxwidth = max(len(x) for x in lines if not x.endswith("-"))
    for i, line in enumerate(lines):
        line = f"{line[:maxwidth]:<{maxwidth}}"
        a0 = ""
        if i < sepindex-1:
            a0 = attr("bold")+fg("light_yellow")
        elif i <= sepindex:
            a0 = fg("black")+bg("white")+attr("bold")
        elif i == n-1 and len(line) > 0 and line[0] == "*":
            a0 = attr("bold")
        elif i/2 != int(i/2):
            a0 = bg("dark_blue")
        print(f"{a0}{line}{attr('reset')}")


def fancilyquoted(s):
    return f"❝{s}❞"


def print_polluted(msg, numcols=100):
    """Use this with a nasty short message when I am angry with code that doesn't work properly."""
    for ch in msg:
        if ch == " ": print()
        else: print(ch*numcols)


def kebab(s, width):
    """Reformats paragraph(s) for given width.

    Single newlines are converted to spaces, then text wrap is applied. Double newlines are kept.

    This method does not tidy up extra spaces or newlines.
    """
    paragraphs = [paragraph.replace("\n", " ") for paragraph in s.split("\n\n")]
    ret = "\n\n".join(["\n".join(textwrap.wrap(paragraph, width)) for paragraph in paragraphs])
    return ret


# ######################################################################################################################
# Auxiliary internal functions

# The following functions are (or should be used) by all the functions in this API that return list or str

def _validate_fmt(fmt):
    validfmts = ["list", "str", "tuple", str, list, tuple]
    if fmt not in validfmts:
        raise ValueError(f"Invalid argument for value 'fmt': \"{fmt}\" (must be within {validfmts})")


def _list_or_str(ret, fmt):
    if fmt in ("str", str):
        return "\n".join(ret)
    elif fmt in ("tuple", tuple):
        return tuple(ret)
    return ret


# Other stuff

def _format_genericlog(message, type, color):
    return "{}{}{}:{} {}{}{}".format(color, attr("bold"), type, attr("reset"), color, message, attr("reset"))


def _format_h_aux(s, format, indents, fmt, char, i):
    if format.startswith("text"):
        return format_underline(s, char, indents, fmt)
    elif format.startswith("markdown"):
        ret = ["# {}".format(s)]
        return _list_or_str(ret, fmt)
    elif format.startswith("rest"):
        return format_underline(s, char, 0, fmt)
    elif format == "html":
        return f"<h{i}>{s}</h{i}>"
    else:
        validformats = ["text", "markdown", "rest", "html"]
        raise ValueError(f"Invalid value for argument 'format': \"{format}\" (must be within {validformats})")
