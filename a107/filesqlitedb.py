import sqlite3, os, a107, io, numpy as np, pickle

__all__ = ["FileSQLite", "InvalidQuery", "NoData"]

class InvalidQuery(Exception): pass

class NoData(Exception): pass

def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


def adapt_object(object):
    return sqlite3.Binary(pickle.dumps(object))


def convert_object(bytes_):
    return pickle.loads(bytes_)


class FileSQLite:
    """This is one layer over a SQLite database.

    Args:
        path: full path to database file
        logger: used for logging important messages; defaults to a107.get_python_logger()
        master: used as alternative to access logger (master.logger) and other not yet specified operations

    I created this class because:
        1) (main reason) to configure the connection (row factory etc.) automatically
        2) Only opens connection on demand; like this one has the opportunity to check whether the database exists and
           initialize if instead of creating an empty file as SQLite does
    """

    @property
    def conn(self):
        if self.__conn is None:
            sqlite3.register_adapter(np.ndarray, adapt_array)  # Converts np.array to TEXT when inserting
            sqlite3.register_converter("array", convert_array) # Converts TEXT to np.array when selecting
            # sqlite3.register_adapter(object, adapt_object)
            # sqlite3.register_converter("object", convert_object)

            self.__conn = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES)
            self.__conn.row_factory = sqlite3.Row
        return self.__conn

    @property
    def logger(self):
        if self.__logger is None: self.__logger = a107.get_python_logger()
        return self.__logger

    def __init__(self, path, logger=None, master=None):
        self.path = path
        self.__logger = logger
        self.__conn = None
        self.master = master
        if master is not None and logger is None and hasattr(master, "logger"):
            self.__logger = master.logger

    def __del__(self):
        self.close()

    # OVERRIDABLE
    def _initialize(self):
        """Override this to create the database. Don't worry about commit()."""

    # INTERFACE

    def close(self):
        if self.__conn:
            self.__conn.close(); self.__conn = None

    def create_database(self, flag_overwrite=False):
        """Creates database if it does not exist or if forced overwriting."""
        exists = os.path.isfile(self.path)
        flag_delete = False
        try:
            if not exists or flag_overwrite:
                if exists:
                    self.logger.info(f"Deleting file '{self.path}'...")
                    self.close(); os.unlink(self.path)
                try:
                    self._initialize()
                except:
                    flag_delete = True
                    raise
                self.commit()
                self.logger.info(f"Created file '{self.path}'")
        except:
            if flag_delete:
                if os.path.isfile(self.path):
                    self.close(); os.unlink(self.path)
                    self.logger.info(f"Deleted file '{self.path}' because initialization failed.")
            raise

    def get_scalar(self, *args, **kwargs):
        """Executes statement that presumably fetches one row containing one column."""
        onerow = self.execute(*args, **kwargs).fetchone()
        if not onerow: raise NoData()
        if len(onerow) > 1: raise InvalidQuery("Statement has more than one column, why are you calling get_scalar()?")
        return onerow[0]

    def describe(self, tablename):
        """Making up for the lack of SQL "describe" command."""
        return self.conn.execute(f"pragma table_info({tablename})")

    def show_tables(self):
        """Making up for the lack of SQL "show tables" statement."""
        return self.conn.execute("select name from sqlite_master where type='table'")

    def get_singlecolumn(self, *args, **kwargs):
        """Executes statement that presumably fechers one column per row."""
        return [row[0] for row in self.execute(*args, **kwargs)]

    def execute(self, *args, **kwargs):
        return self.conn.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self.conn.executemany(*args, **kwargs)

    def commit(self, *args, **kwargs):
        return self.conn.commit(*args, **kwargs)

    def rollback(self, *args, **kwargs):
        return self.conn.rollback(*args, **kwargs)

    def interrupt(self, *args, **kwargs):
        return self.conn.interrupt(*args, **kwargs)

