"""Some maths using numpy."""

__all__ = ["triangularwave"]

import numpy as np

def triangularwave(period, numpoints):
    """Triangular wave ranging from 0 to 1 with given period and given number of points.

    >>> import a107
    >>> print(a107.asciichart(a107.triangularwave(20, 101)))
    1.00  ┼     ╭────────╮          ╭────────╮          ╭────────╮          ╭────────╮          ╭────────╮
    0.00  ┼─────╯        ╰──────────╯        ╰──────────╯        ╰──────────╯        ╰──────────╯        ╰────

    >>> import a107
    >>> print(a107.asciichart(a107.triangularwave(20, 101), cfg={"height": 5}))
    1.00  ┼         ╭╮                  ╭╮                  ╭╮                  ╭╮                  ╭╮
    0.80  ┤      ╭──╯╰──╮            ╭──╯╰──╮            ╭──╯╰──╮            ╭──╯╰──╮            ╭──╯╰──╮
    0.60  ┤     ╭╯      ╰╮          ╭╯      ╰╮          ╭╯      ╰╮          ╭╯      ╰╮          ╭╯      ╰╮
    0.40  ┤  ╭──╯        ╰──╮    ╭──╯        ╰──╮    ╭──╯        ╰──╮    ╭──╯        ╰──╮    ╭──╯        ╰──╮
    0.20  ┤ ╭╯              ╰╮  ╭╯              ╰╮  ╭╯              ╰╮  ╭╯              ╰╮  ╭╯              ╰╮
    0.00  ┼─╯                ╰──╯                ╰──╯                ╰──╯                ╰──╯                ╰─
    """
    i = np.arange(numpoints)
    halfperiod = period/2
    ret = (halfperiod-np.abs(i % period - halfperiod))/halfperiod
    return ret
