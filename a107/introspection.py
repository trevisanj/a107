"""Routines that somehow look into the package itself"""


import os
import glob
# import imp
import importlib
import inspect
import a99
import time


__all__ = ["import_module", "collect_doc",
           "get_classes_in_module", "get_obj_doc0", "get_subpackages_names"]


def import_module(filename):
    """
    Returns module object

    Source: https://www.blog.pythonlibrary.org/2016/05/27/python-201-an-intro-to-importlib/
    """
    module_name = "xyz"

    module_spec = importlib.util.spec_from_file_location(module_name, filename)

    if module_spec is None:
        raise RuntimeError("Python cannot import file '{}'".format(filename))

    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    # print(dir(module))
    #
    # msg = 'The {module_name} module has the following methods:' \
    #       ' {methods}'
    # print(msg.format(module_name=module_name,
    #                  methods=dir(module)))

    return module


def collect_doc(module, base_class=None, prefix="", flag_exclude_prefix=False):
    """
    Collects class names and docstrings in module for classes starting with prefix

    Arguments:
        module -- Python module
        prefix -- argument for str.startswith(); if not passed, does not filter
        base_class -- filters only descendants of this class
        flag_exclude_prefix -- whether or not to exclude prefix from class name in result

    Returns: [(classname0, signature, docstring0), ...]
    """

    ret = []
    for attrname in module.__all__:
        if prefix and not attrname.startswith(prefix):
            continue

        attr = module.__getattribute__(attrname)

        if base_class is not None and not issubclass(attr, base_class):
            continue

        spec = inspect.signature(attr)

        ret.append((attrname if not flag_exclude_prefix else attrname[len(prefix):], spec, attr.__doc__))

    return ret


def get_classes_in_module(module, superclass=object):
    """
    Returns a list with all classes in module that descend from parent

    Args:
        module: builtins.module
        superclass: a class

    Returns: list
    """

    ret = []
    for classname in dir(module):
        attr = module.__getattribute__(classname)
        try:
            if issubclass(attr, superclass) and (attr != superclass):
                ret.append(attr)
        except TypeError:
            # "issubclass() arg 1 must be a class"
            pass
        except RuntimeError:
            # a99.get_python_logger().exception("Failed probing attribute '{}'".format(classname))
            # raise
            pass
    return ret


def get_obj_doc0(obj, alt="(no doc)"):
    """Returns first line of cls.__doc__, or alternative text"""
    ret = obj.__doc__.strip().split("\n")[0] if obj.__doc__ is not None else alt
    return ret


def get_subpackages_names(dir_):
    """Figures out the names of the subpackages of a package

    Args:
        dir_: (str) path to package directory

    Source: http://stackoverflow.com/questions/832004/python-finding-all-packages-inside-a-package
    """

    def is_package(d):
        d = os.path.join(dir_, d)
        return os.path.isdir(d) and glob.glob(os.path.join(d, '__init__.py*'))

    ret = list(filter(is_package, os.listdir(dir_)))
    ret.sort()
    return ret

