import collections
import os.path
import re
import shutil
from threading import Lock
import sys
import a107
import logging
import glob


__all__ = [
    "rename_to_temp", "is_text_file", "add_bits_to_path", "add_parts_to_path", "crunch_dir",
    "slugify", "write_lf", "get_path", "new_filename", "temp_filename", "sequential_filename", "create_symlink", "which",
    "ensure_path", "open_html", "sequential_filename_with_dateslug"
]


# # Filename or pathname-related string manipulations

def slugify(string):
    """
    Removes non-alpha characters, and converts spaces to hyphens. Useful for making file names.


    Source: http://stackoverflow.com/questions/5574042/string-slugification-in-python
    """
    string = re.sub('[^\w .-]', '', string)
    string = string.replace(" ", "-")
    return string


def crunch_dir(name, n=50):
    """Puts "..." in the middle of a directory name if lengh > n."""
    if len(name) > n + 3:
        name = "..." + name[-n:]
    return name


def add_parts_to_path(path_, filename_prefix=None, extension=None):
    """
    Adds prefix/suffix to filename

    Arguments:
        path_ -- path to file
        filename_prefix -- prefix to be added to file name
        extension -- extension to be added to file name. The dot is automatically added, such as
            "ext" and ".ext" will have the same effect

    Examples:
        > add_bits_to_path("/home/user/file", "prefix-")
        /home/user/prefix-file

        > add_bits_to_path("/home/user/file", None, ".ext")
        /home/user/file.ext

        > add_bits_to_path("/home/user/file", None, "ext")  # dot in extension is optional
        /home/user/file.ext

        > add_bits_to_path("/home/user/", None, ".ext")
        /home/user/.ext
    """

    dir_, basename = os.path.split(path_)

    if filename_prefix:
        basename = filename_prefix+basename
    if extension:
        if not extension.startswith("."):
            extension = "."+extension
        basename = basename+extension

    return os.path.join(dir_, basename)

# Compatibility
def add_bits_to_path(*args, **kwargs):
    raise RuntimeError("This error is not your fault. Just the creator of this method realized that its name is misleading, please correct your code to use add_parts_to_path() instead.")

# # Probe, write, rename etc.

def new_filename(prefix, extension=None, flag_minimal=True):
    """returns a file name that does not exist yet, e.g. prefix-0001.extension

    Args:
        prefix:
        extension: examples: "dat", ".dat" (leading dot will be detected, does not repeat dot in name)
        flag_minimal:

          - True: will try to be as "clean" as possible
          - False: will generate filenames in a simple, same-length pattern

    Example: ``new_filename("molecules-", "dat", True)``

    In the example above, the first attempt will be "molecules.dat", then "molecules-0000.dat".
    If flag_minimal were True, it would skip the first attempt.
    """

    if extension is None:
        extension = ""

    if len(extension) > 0 and extension[0] == '.':
        extension = extension[1:]

    # extension-sensitive format for filename
    fmt = '{0!s}-{1:04d}.{2!s}' if extension else '{0!s}-{1:04d}'

    # Removes tailing dash because it would look funny (but will be re-added in format string)
    prefix_ = prefix[:-1] if prefix.endswith("-") else prefix

    i = -1
    ret = None
    while True:
        if i == -1:
            if flag_minimal:
                ret = "{}.{}".format(prefix_, extension) if extension else prefix_
            else:
                i += 1
                continue
        else:
            ret = fmt.format(prefix_, i, extension)

        if not os.path.exists(ret):
            break
        i += 1
        if i > 9999:
            raise RuntimeError("Could not make a new file name for (prefix='{0!s}', extension='{1!s}')".format(prefix, extension))
    return ret


def temp_dir():
    """Returns path to temporary directory ~/tmp. If directory does not exist, creates it

    Firefox in my Ubuntu is installed through Snap and cannot see the /tmp directory, so a directory inside home
    is guaranteed
    """
    ret = os.path.expanduser("~/tmp")
    ensure_path(ret)
    return ret

def temp_filename(prefix, extension=None):
    """Wrapper for new_filename that filename without path nor extension from prefix and prepends '/tmp/  to it."""
    return a107.new_filename(os.path.join(temp_dir(), os.path.splitext(os.path.split(prefix)[1])[0]), extension,
                             flag_minimal=False)


def sequential_filename(prefix, extension=None, num_digits=4):
    """
    Returns a file name that does not exist yet and continues numbering from last existing.

    Args:
        prefix:
        extension: examples: "dat", ".dat" (leading dot will be detected, does not repeat dot in name)
        num_digits:

    This was created to continue a sequence of files even is some of them have been deleted.
    """

    # Note: the way extension is handled is different from new_filename(). For glob's sake, I decided to include the dot
    # in extension, not in fmt

    assert not isinstance(num_digits, bool)

    if extension is None:
        extension = ""
    if len(extension) > 0 and extension[0] != ".":
        extension = "."+extension
    # extension-sensitive format for filename
    fmt = '{0!s}-{1:0'+str(num_digits)+'d}{2!s}' if extension else '{0!s}-{1:0'+str(num_digits)+'d}'

    # Removes tailing dash because it would look funny (but will be re-added in format string)
    prefix = prefix[:-1] if prefix.endswith("-") else prefix

    ff = glob.glob(f"{prefix}-*{extension}")
    ff.sort()
    try:
        _, filename = os.path.split(ff[-1])
        curr = int(re.match(f"{prefix}-(\d+)", ff[-1]).groups()[0])
    except (IndexError, TypeError):
        curr = -1


    curr += 1
    ret = fmt.format(prefix, curr, extension)
    return ret

def sequential_filename_with_dateslug(prefix, extension):
    """Convenience function to generate filenames.

    Args:
        prefix:
        extension:

    Return:
        nice filename

    Uses a combination of dt2slug() and sequential_filename() to make a new filename.
    """
    return sequential_filename(f"{prefix}.{a107.dt2slug()}", extension)




_rename_to_temp_lock = Lock()


def rename_to_temp(filename):
    """*Thread-safe* renames file to temporary filename. Returns new name"""
    with _rename_to_temp_lock:
        root, ext = os.path.splitext(filename)
        if len(ext) > 0:
            ext = ext[1:]  # the dot (".") is originally included
        new_name = new_filename(root, ext)
        os.rename(filename, new_name)
        return new_name


def write_lf(h, s):
  """Adds lf to end of string and writes it to file."""
  h.write(s+"\n")


def create_symlink(source, link_name):
    """
    Creates symbolic link for either operating system.

    http://stackoverflow.com/questions/6260149/os-symlink-support-in-windows
    """
    os_symlink = getattr(os, "symlink", None)
    if isinstance(os_symlink, collections.Callable):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()



# ## http://eli.thegreenplace.net/2011/10/19/perls-guess-if-file-is-text-or-binary-lemented-in-python
_PY3 = sys.version_info[0] == 3

# A function that takes an integer in the 8-bit range and returns
# a single-character byte object in py3 / a single-character string
# in py2.
#
_int2byte = (lambda x: bytes((x,))) if _PY3 else chr

_text_characters = (
        b''.join(_int2byte(i) for i in range(32, 127)) +
        b'\n\r\t\f\b')

def is_text_file(filepath, blocksize=2**14):
    """ Uses heuristics to guess whether the given file is text or binary,
        by reading a single block of bytes from the file.
        If more than some abound of the chars in the block are non-text, or there
        are NUL ('\x00') bytes in the block, assume this is a binary file.
    """
    with open(filepath, "rb") as fileobj:
        block = fileobj.read(blocksize)
        if b'\x00' in block:
            # Files with null bytes are binary
            return False
        elif not block:
            # an empty file is considered a valid text file
            return True

        # Use translate's 'deletechars' argument to efficiently remove all
        # occurrences of _text_characters from the block
        nontext = block.translate(None, _text_characters)
        return float(len(nontext)) / len(block) <= 0.30


def which(program):
    """
    Mimics UNIX 'which' command: return full path to executable file.

    http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def get_path(*args, module=a107):
    """Returns full path to specified module.

    Args:
      *args: are added at the end of module path with os.path.join()
      module: Python module, defaults to a107

    Returns: path string
    """

    p = os.path.abspath(os.path.join(os.path.split(module.__file__)[0], *args))
    return p


def ensure_path(path):
    """
    Iteratively calls mkdir until full path exists.

    Args:
        path: absolute or relative path ("~" character is allowed)

    Returns:
        whether any directory was created
    """
    ret = False
    path = os.path.abspath(os.path.expanduser(path))
    dd = [x for x in path.split(os.path.sep) if x]
    sofar = ""
    for d in dd:
        sofar += os.path.sep+d
        if not os.path.isdir(sofar):
            os.mkdir(sofar)
            ret = True

    return ret


def open_html(html, prefix="a107temphtml"):
    """Saves HTML as a temporary file and opens it on the web browser.

    Args:
        html: str containing HTML content
        prefix: prefix for temp_filename()
    """
    import webbrowser
    filename = temp_filename(prefix, "html")
    with open(filename, "w") as h:
        h.write(html)
    webbrowser.open(filename)
