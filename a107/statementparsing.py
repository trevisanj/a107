"""Statement parser for my consoles."""
from dataclasses import dataclass
from colored import fg, attr
__all__ = ["str2args", "StatementError"]


class StatementError(Exception):
    def __init__(self, statement, position, text):
        super().__init__(text)
        self.statement = statement
        self.position = position

    def explain(self):
        return f"{self.statement}\n{' '*self.position}^\n{str(self)}"


@dataclass
class _Flags:
    # This class exists so that I can set values from sub-method
    inside: bool = False  # inside argument
    kwarg: bool = False # parsing a key-value pair
    backslash: bool = False # found a backslash


def str2args(sargs):
    QUOTES = ('"', "'")
    args, kwargs = [], {}

    def new_arg():
        QBERT = "!)@(#*$&"
        part = sargs[bp+(1 if quoting else 0):i]
        # Removes single backslashes and replaces double backslashes with single backslashes (temporary operation required)
        part = part.replace("\\\\", QBERT).replace("\\", "").replace(QBERT, "\\")
        if flags.kwarg:
            kwargs[args.pop()] = part
            flags.kwarg = False
        else: args.append(part)
        flags.inside = False

    def error(text):
        return StatementError(sargs, i, text)

    def errorpart():
        return f"Error in position {i}, character '{ch}'"

    n = len(sargs)
    i = 0
    quote = None  # opening quotation mark: ' or "
    quoting = False
    expecting_space = False
    flags = _Flags()
    bp = None  # break point
    while True:
        if i == n:
            if quoting: raise error("Unclosed quotation")
            if flags.inside: new_arg()
            break
        ch = sargs[i]
        if expecting_space and ch != " ": raise error(f"{errorpart()}: expecting space")
        else: expecting_space = False

        if not quoting:
            if ch == " ":
                if flags.inside: new_arg()
            elif ch == "=":
                if flags.kwarg: raise error(f"{errorpart()}: repeated equal sign")
                if flags.inside: new_arg()
                flags.kwarg = True
            elif ch == "\\": raise error(f"{errorpart()}: backslash not allowed outside quotation marks")
            else:
                if not flags.inside:
                    flags.inside, bp = True, i
                    quoting = ch in QUOTES
                    if quoting: quote = ch
                else:
                    if ch in QUOTES: raise error(f"{errorpart()}: unexpected quotation mark")
        else:
            if flags.backslash:
                # just ignores next character
                flags.backslash = False
            else:
                if ch == quote:
                    new_arg()
                    flags.inside, quoting, expecting_space = False, False, True
                elif ch == "\\":
                    flags.backslash = True
        i += 1
    print(f"{fg('purple_4a')+attr('bold')}str2args() is still in probation phase; therefore we'll print its results:\n<<{sargs}>>\nargs={args}\nkwargs={kwargs}{attr('reset')}\n")
    return args, kwargs
