"""Some maths using numpy."""

__all__ = ["triangularwave", "sigmoid", "make_impulseresponse"]

import numpy as np, scipy.interpolate

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


def make_impulseresponse(H, size, flag_add_zero=True):
    """Interpolates to create "H-like" curve with size points.

    Args:
        H: "seed" points. If you want it to go down smoothly, it is important to end it with a zero (this is done
           automatically by default).
        size: number of points of output

    Return:
        numpy 1-D array

    Example:
    >>> import a107
    >>> H = [20, 20, 20, 20, 0]
    >>> print(a107.asciichart([H, 2*a107.make_impulseresponse(H, 20), 3*a107.make_impulseresponse(H, 40)], cfg={"height": 20}))
       60.00  ┼─────────────────────────────╮
       57.00  ┤                             │
       54.00  ┤                             ╰╮
       51.00  ┤                              │
       48.00  ┤                              ╰╮
       45.00  ┤                               │
       42.00  ┤                               ╰╮
       39.00  ┤──────────────╮                 │
       36.00  ┤              │                 ╰╮
       33.00  ┤              ╰╮                 │
       30.00  ┤               │                 ╰╮
       27.00  ┤               │                  │
       24.00  ┤               ╰╮                 ╰╮
       21.00  ┼───╮            │                  │
       18.00  ┤   │            ╰╮                 ╰╮
       15.00  ┤   │             │                  │
       12.00  ┤   │             │                  ╰╮
        9.00  ┤   │             ╰╮                  │
        6.00  ┤   │              │                  ╰╮
        3.00  ┤   │              │                   │
        0.00  ┤   ╰              ╰                   ╰
    """
    if flag_add_zero and H[-1] != 0: H = np.concatenate((H, [0.]))
    x = range(len(H))
    interpolator = scipy.interpolate.interp1d(x, H)
    ret = interpolator(np.linspace(0, len(H)-1, size))
    return ret
