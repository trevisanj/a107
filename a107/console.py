"""
Console class adapted from cliserv client+server.
"""

import os
import atexit
import sys
import signal
import readline
from colored import fg, bg, attr
import re
import csv
import random
import inspect
import textwrap
import a107

__all__ = ["ConsoleCommands", "Console", "ConsoleError", "console_bool", "embed_ipython"]

COLOR_OKGREEN = fg("green")
COLOR_FAIL = fg("red")
COLOR_EXCEPTION = fg("light_red")
COLOR_HAPPY = fg("light_green")
COLOR_SAD = fg("blue")
COLOR_INPUT = fg("orange_1")


def console_bool(s):
    """Translates str console arguments to bool"""
    if isinstance(s, str) and s.upper() == "FALSE":
        return False
    return bool(s)

class ConsoleCommands(object):
    """
    Class that implements all server-side "commands".

    Subclass this to implement new commands. All arguments come as strings. Do not use keyword
    arguments, as the Server is not capable of parsing them.
    """

    def __init__(self):
        self.console = None

    # ┌─┐┬  ┬┌─┐┬─┐┬─┐┬┌┬┐┌─┐  ┌┬┐┌─┐
    # │ │└┐┌┘├┤ ├┬┘├┬┘│ ││├┤   │││├┤
    # └─┘ └┘ └─┘┴└─┴└─┴─┴┘└─┘  ┴ ┴└─┘

    def _get_welcome0(self):
        return f"Welcome to {self.console.slug}"

    # ┌┐ ┌─┐┌─┐┬┌─┐  ┌─┐┌─┐┌┬┐┌┬┐┌─┐┌┐┌┌┬┐┌─┐
    # ├┴┐├─┤└─┐││    │  │ │││││││├─┤│││ ││└─┐
    # └─┘┴ ┴└─┘┴└─┘  └─┘└─┘┴ ┴┴ ┴┴ ┴┘└┘─┴┘└─┘

    def help(self, what=None):
        """Prints help text or provides help for specific command.

        '?' is an alias for 'help'.
        """
        if what is None:
            mm = [x for x in inspect.getmembers(self, predicate=inspect.ismethod) if not x[0].startswith("_")]

            lines = [self.console.slug, "=" * len(self.console.slug), ""]

            if self.console.description:
                lines += [self.console.description, ""]

            maxlen = max([len(x[0]) for x in mm])
            lines += ["{}{:>{}}{} -- {}".format(attr("bold"), name, maxlen, attr("reset"), a107.get_obj_doc0(method))
                     for name, method in mm]

            return "\n".join(lines)

        else:
            if what not in self.__get_command_names():
                raise InvalidMethodError("Invalid method: '{}'. Type 'help' to list methods.".format(what))

            method = self.__getattribute__(what)
            sig = str(inspect.signature(method)).replace("(", "").replace(")", "").replace(",", "")
            return "{}{} {}{}\n\n{}".format(attr("bold"), what, sig, attr("reset"), method.__doc__)

    def ping(self):
        """Returns "pong"."""
        return "pong"

    def slug(self):
        """Returns the console slug."""
        return self.console.slug

    def exit(self):
        """Exits the console."""
        return self.console.exit()

    # ┬  ┌─┐┌─┐┬  ┬┌─┐  ┌┬┐┌─┐  ┌─┐┬  ┌─┐┌┐┌┌─┐
    # │  ├┤ ├─┤└┐┌┘├┤   │││├┤   ├─┤│  │ ││││├┤
    # ┴─┘└─┘┴ ┴ └┘ └─┘  ┴ ┴└─┘  ┴ ┴┴─┘└─┘┘└┘└─┘

    def _get_welcome(self):
        return "\n".join(a107.format_slug(self._get_welcome0(), random.randint(0, 2)))

    def __get_command_names(self):
        """Return the names of the commands the the console can execute."""

        return [x[0] for x in inspect.getmembers(self, predicate=inspect.ismethod) if
              not x[0].startswith("_")]


class Console(object):
    """
    Console

    Args:
        slug: be kind and give me a slug
        cmd: Commands or descendant thereof instance
        datadir: data directory. This is the place where it read and write file "{slug}.history"
        description:
        flag_cfg: whether to try to use config file
    """

    @property
    def configpagh(self):
        return os.path.join(self.datadir, self.slug + ".cfg")

    @property
    def historypath(self):
        return os.path.join(self.datadir, f"{self.slug}.history")

    def __init__(self, slug, cmd, datadir=".", description="", flag_cfg=False):
        self.slug = slug
        self.datadir = datadir
        self.description = description
        self.cmd = cmd
        self.flag_cfg = flag_cfg
        cmd.console = self

        # pre-startup
        if self.datadir:
            os.makedirs(self.datadir, exist_ok=True)

        self.cfg = None
        if flag_cfg:
            cfg = self.cfg = a107.AAConfigObj(self.configpagh)

        self.running = False

    # USE ME

    def execute(self, _st):
        """
        Send statement to server, receive reply, unpickle and return.

        Args:
            _st: string, e.g., 'help("ping")', or 'ping?'
        """

        st = self.__make_statement(_st)
        ret = self.__process_statement(st)

        return ret

    def exit(self):
        self.running = False

    def run(self):
        """Will run console and automatically exit the program.

        Exits because it registers handlers to intercept Ctrl+C and Ctrl+Z.
        """

        # This one gets called at Ctrl+C, but ...
        def _atexit():
            readline.write_history_file(self.historypath)

        # ... we need this to handle the Ctrl+Z.
        def _ctrl_z_handler(signum, frame):
            # this will trigger _atexit()
            sys.exit()

        atexit.register(_atexit)
        signal.signal(signal.SIGTSTP, _ctrl_z_handler)

        try:
            readline.read_history_file(self.historypath)
            # default history len is -1 (infinite), which may grow unruly
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass

        print(self.execute("_get_welcome"))

        try:
            self.running = True
            while self.running:
                st = input("{}{}{}>".format(COLOR_INPUT, attr("bold"), self.slug))
                print(attr("reset"), end="")

                if not st:
                    pass
                elif st.lower().startswith("what should i do"):
                    _yoda("Use the force.")
                else:
                    try:
                        import tabulate
                        ret = self.execute(st)
                        _yoda("Happy I am.", True)
                        prdef = False
                        if ret is None:
                            pass
                        elif isinstance(ret, str):
                            print(ret)
                        # Tries to detect "tabulate-like" (rows, headers) arguments
                        elif isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[0], list) and isinstance(ret[1], list):
                            print(tabulate.tabulate(*ret))
                        else:
                            prdef = True

                        if prdef:
                            _myprint(ret)
                    except Exception as e:
                        _yoda("That work did not.", False)
                        _my_print_exception(e)
        except KeyboardInterrupt:
            pass
        finally:
            pass

    # OVERRIDE ME

    def _process_invalid_method(self, parts):
        name = parts[0]
        raise InvalidMethodError(f"Invalid method: '{name}'")

    # LEAVE ME ALONE

    def __make_statement(self, _st):
        """
        Performs some interpretation at _st.

        Implemented translations:
            '?' --> 'help'
            'methodname?' --> 'help "methodname"'
        """

        if _st == "?":
            st = "help"
        else:
            gg = re.match("(\w+)\?$", _st)
            if gg is not None:
                st = 'help "{}"'.format(gg[1])
            else:
                st = _st
        return st

    def __process_statement(self, st):
        """Parses statement and makes method call.

        Args:
            st: bytes
        """
        try:
            reader = csv.reader([st], delimiter=" ", skipinitialspace=True)
            parts = [[x.strip() for x in row] for row in reader][0]
            name = parts[0]

            try:
                method = self.cmd.__getattribute__(name)
            except AttributeError:
                ret = self._process_invalid_method(parts)
            else:
                # Some basic conversion
                parts_ = [None if x == "None" else x for x in parts]
                ret = method(*parts_[1:])

        except ConsoleError as e:
            raise
        except Exception as e:
            a107.get_python_logger().exception("Error processing statement")
            raise

        return ret

def _yoda(s, happy=True):
    print(attr("bold")+(COLOR_HAPPY if happy else COLOR_SAD), end="")
    print("{0}|o_o|{0} -- {1}".format("^" if happy else "v", s), end="")
    print(attr("reset")*2)


def _my_print_exception(e):
    print("{}{}({}){}{} {}{}".format(COLOR_EXCEPTION, attr("bold"), e.__class__.__name__,
                                      attr("reset"), COLOR_EXCEPTION, str(e), attr("reset")))

def _myprint(x):
    """Used to print results from client statements.

    Using textwrap seems to be way better than a107.make_code_readable(), pprint, pprintpp or
    autopep8."""

    if not isinstance(x, str):
        x = repr(x)
    x = x.replace("\n", "")
    x = re.sub(r'\s+', ' ', x)
    print("\n".join(textwrap.wrap(x, 80)))


class ConsoleError(Exception):
    """Base class for all exceptions that are raised by Console.

    You can raise this if you don't want your error to print the traceback."""
    pass

class InvalidMethodError(ConsoleError):
    """Raised at invalid method call."""
    pass


# "compatibility"
def publish_in_pythonconsole(*args, **kwargs):
    raise RuntimeError("This never worked well; use embed_ipython() instead")


def embed_ipython(commands, globalsdict, colors="linux"):
    """
    Extracts commands to globalsdict and Embeds Ipython
    Args:
        commands: Commands instance
        globalsdict: dictionary obtained (probably in main module) using globals()
        colors: embed() suppresses colors by default, so I implemented this control with a default value

    Actions performed:

        - modifies globalsdict to have all commands + a "print_help()" method
        - supresses Ctrl+Z. **You will have to type "exit"**. Don't worry, Yoda will tell you
    """

    from IPython import embed

    def print_help(command=None):
        "Prints help"
        print(commands.help(command))
    # globalsdict["print_help"] = print_help

    mm = [x for x in inspect.getmembers(commands, predicate=inspect.ismethod) if not x[0].startswith("_")]
    for name, method in mm:
        globalsdict[name] = method
    # del Commands, method, mm  # , console

    def _ctrl_z_handler(signum, frame):
        # this will trigger _atexit()
        print(a107.format_yoda('Press Ctrl+Z do not, type "exit" you must'))

        # atexit.register(on_exit)  # _atexit)
    signal.signal(signal.SIGTSTP, _ctrl_z_handler)

    del mm, name, method
    locals().update(globalsdict)
    embed(header="\n".join(a107.format_slug(commands.slug())), colors=colors)



# TODO why did I have this here? Guess it was some test if __name__ == "__main__":
#     import a107
#     commands = a107.ConsoleCommands()
#     console = a107.Console(cmd=commands)