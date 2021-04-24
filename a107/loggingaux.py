"""Logging routines"""
import logging, sys, traceback
from argparse import *
from .parts import *
__all__ = ["get_python_logger", "add_file_handler", "reset_logger", "LogTwo", "SmartFormatter", "str_exc", "get_new_logger",
           "log_exception_as_info"]


def reset_logger():
    global _python_logger
    _python_logger = None

_python_logger = None
_fmtr = logging.Formatter('[%(levelname)-8s] %(message)s')
def get_python_logger():
    """Returns logger to receive Python messages.

    At first call, _python_logger is created. At subsequent calls, _python_logger is returned. 
    Therefore, if you want to change `a107.flag_log_file` or `a107.flag_log_console`, do so
    before calling get_python_logger(), otherwise these changes will be ineffective.
    """
    import a107
    global _python_logger
    if _python_logger is None:
        _python_logger = get_new_logger()

    return _python_logger


def get_new_logger(level=None, flag_log_console=None, flag_log_file=None, fn_log=None):
    """Creates new logger"""
    import a107
    if level is None:
        level = a107.logging_level
    if  flag_log_console is None:
        flag_log_console = a107.flag_log_console
    if  flag_log_file is None:
        flag_log_file = a107.flag_log_file
    if  fn_log is None:
        fn_log = a107.fn_log
    logger = logging.Logger("a107", level=level)
    if flag_log_file:
        add_file_handler(logger, fn_log)
    if flag_log_console:
        ch = logging.StreamHandler()
        ch.setFormatter(_fmtr)
        logger.addHandler(ch)
    return logger


def add_file_handler(logger, logFilename=None):
    """Adds file handler to logger.

    File is opened in "a" mode (append)
    """
    assert isinstance(logger, logging.Logger)
    ch = logging.FileHandler(logFilename, "a")
    # ch.setFormatter(logging._defaultFormatter) # todo may change to have same formatter as last handler of logger
    ch.setFormatter(_fmtr)
    logger.addHandler(ch)


@froze_it
class LogTwo(object):
    """Logs messages to both stdout and file."""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def close(self):
        self.log.close()


class SmartFormatter(RawDescriptionHelpFormatter):
    """
    Help formatter that will show default option values and also respect
    newlines in description. Neither are done by the default help formatter.
    """

    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not SUPPRESS:
                defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += ' (default: %(default)s)'
        return help


        # # this is the RawTextHelpFormatter._split_lines
        # if text.startswith('R|'):
        #     return text[2:].splitlines()
        # return argparse.ArgumentDefaultsHelpFormatter._split_lines(self, text, width)


def str_exc(E):
    """Generates a string from an Exception"""
    return "{0!s}: {1!s}".format(E.__class__.__name__, str(E))


def log_exception_as_info(logger, e, title):
    """Logs exception as info. Should be called inside an 'except' clause

    I found out that apparently the console is always polluted if we call logger.exception(), so I am calling
    ...info() instead."""
    logger.info(title+": "+str_exc(e)+"\n"+traceback.format_exc())
