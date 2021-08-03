"""Some maths using numpy."""

__all__ = ["triangularwave", "sigmoid"]

import numpy as np

def triangularwave(period, numpoints):
    """Triangular wave ranging from 0 to 1 with given period and given number of points.

    Examples:
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


def sigmoid(a, c, numpoints_or_x):
    """Calculates sigmoid signal given steepness(a), inflection point (c), and number of points.

    Example:
    >>> import a107
    >>> numpoints = 30
    >>> print(a107.asciichart(a107.sigmoid(-1, 22, 30)+a107.sigmoid(.5, 2, 30), cfg={"height": 10}))
        2.00  ┤
        1.91  ┤       ╭───────────╮
        1.82  ┤     ╭─╯           ╰╮
        1.73  ┤    ╭╯              │
        1.64  ┤   ╭╯               ╰╮
        1.54  ┤  ╭╯                 │
        1.45  ┤ ╭╯                  ╰╮
        1.36  ┤╭╯                    │
        1.27  ┼╯                     ╰╮
        1.18  ┤                       │
        1.09  ┤                       ╰─╮
        1.00  ┤                         ╰───
    """
    if np.isscalar(numpoints_or_x):
        x = np.linspace(0, numpoints_or_x-1, numpoints_or_x)
    else:
        x = numpoints_or_x

    return 1.0/(1.0+np.exp(-a*(x-c)))
