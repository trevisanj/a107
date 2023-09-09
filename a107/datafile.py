"""
Ancestor class for all classes that represent a file type with load/save/init features.

20230907 Based on f311, then f312, then I decided to incorporate this into a107
"""
__all__ = ["DataFile"]

import os, a107, shutil, sys

class DataFile(a107.AttrsPart):
    """
    Class representing a file in disk

    **Attention** For subclasses, filetype check is **strongly advised**. Two ways of doing this:
                      (a) inherit _test_magic() (recommended);
                      (b) if there are no testable magic characters, test for absurd
                          within _do_load(). Try to crash early.
    """
    # Descendants shoulds set this
    default_filename = None
    # Whether it is a text file format (otherwise binary)
    flag_txt = True
    # Whether or not to be considered by load_any_file()
    flag_collect = True
    # List of script names that can edit this file type
    editors = None


    @a107.classproperty
    def description(cls):
        return a107.get_obj_doc0(cls)

    def __init__(self):
        a107.AttrsPart.__init__(self)
        # File name is set by load()
        self.__flag_loaded = False
        self.filename = None

    # # Methods to be implemented by subclasses
    #   =======================================

    def _do_save_as(self, filename):
        raise NotImplementedError()

    def _do_load(self, filename):
        raise NotImplementedError("Forgot to implement _do_load() for class '{}'".
                                  format(self.classname))

    def _test_magic(self, filename):
        """
        Opens file just to verify whether it is what it is expected to be (**raise if not**)

        Implement this if you want to implement file type verification separate from _do_load()

        """
        pass

    # # Interface
    #   =========

    def save_as(self, filename=None):
        """
        Dumps object contents into file on disk.

        Args:
          filename (optional): defaults to self.filename. If passed, self.filename
            will be updated to filename.
        """
        if filename is None:
            filename = self.filename
        if filename is None:
            filename = self.default_filename
        if filename is None:
            raise RuntimeError("Class '{}' has no default filename".format(self.__class__.__name__))
        self._do_save_as(filename)
        self.filename = filename

    def load(self, filename=None):
        """Loads file and registers filename as attribute."""
        assert not self.__flag_loaded, "File can be loaded only once"
        if filename is None:
            filename = self.default_filename
        assert filename is not None, \
            "{0!s} class has no default filename".format(self.__class__.__name__)

        # Convention: trying to open empty file is an error,
        # because it could be of (almost) any type.

        size = os.path.getsize(filename)
        if size == 0:
            raise RuntimeError("Empty file: '{0!s}'".format(filename))

        self._test_magic(filename)
        self._do_load(filename)
        self.filename = filename
        self.__flag_loaded = True

    def init_default(self):
        """
        Initializes object with its default values

        Tries to load self.default_filename from default
        data directory. For safety, filename is reset to None so that it doesn't point to the
        original file.
        """
        if self.default_filename is None:
            raise RuntimeError("Class '{}' has no default filename".format(self.__class__.__name__))
        fullpath = _get_default_data_path(self.default_filename, class_=self.__class__)
        self.load(fullpath)
        self.filename = None

    def validate(self):
        pass


def _get_default_data_path(*args, class_=None):
    """
    Returns path to default data directory

    Arguments 'module' and 'class' give the chance to return path relative to package other than
    f312.filetypes

    Args:
        module: Python module object. It is expected that this module has a sub-subdirectory
                named 'data/default'
        class_: Python class object to extract path information from. If this argument is used,
                it will be expected that the class "root" package will have a sub-subdirectory
                named 'data/default'. Argument 'class_' **has precedence over argument 'module'**
        flag_raise: raises error if file is not found. This can be turned off for whichever purpose
    """

    pkgname =  class_.__module__
    mseq = pkgname.split(".")
    if len(mseq) < 2 or mseq[1] != "filetypes":
        raise ValueError("Invalid module name for class '{}': '{}' "
                         "(must be '(...).filetypes[.(...)]')".format(class_.__name__, pkgname))
    # gets "root" module object
    # For example, if pkgname is "pyfant.filetypes.filemain", module below will be
    # the "pyfant" module object
    module = sys.modules[mseq[0]]

    module_path = os.path.split(module.__file__)[0]
    p = os.path.abspath(os.path.join(module_path, "data", "default", *args))

    if not os.path.isfile(p):
        raise RuntimeError("Path not found '{}'".format(p))

    return p


def _copy_default_data_file(filename, module):
    """Copies file from default data directory to local directory."""
    fullpath = _get_default_data_path(filename, module=module)
    shutil.copy(fullpath, ".")

