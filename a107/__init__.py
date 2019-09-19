
# ## Constants affecting logging
#    ---------------------------
#
# If the following need change, this should be done before calling get_python_logger() for the
# first time
#
# Set this to make the python logger to log to the console. Note: will have no
# effect if changed after the first call to get_python_logger()
flag_log_console = True
# Set this to make the python logger to log to a file named "<fn_log>".
# Note: will have no effect if changed after the first call to get_python_logger()
flag_log_file = False
# log filename
fn_log = "a107.log"
# Logging level for the python logger
import logging
logging_level = logging.INFO

from .config import *
from .datetimefunc import *
from .conversion import *
from .parts import *
from .loggingaux import *
from .search import *
from .textinterface import *
from .introspection import *
from .misc import *
from .console import *
from .fileio import *
del logging