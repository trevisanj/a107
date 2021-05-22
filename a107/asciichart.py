import asciichartpy
__all__ = ["asciichart"]

def asciichart(series, cfg=None, maxlines=100):
    """Wraps asciichart.plot() to fix y-axis numbers alignment and warn of too great a height."""

    def fix_asciichart(lines):
        dotidx = max([line.index(".") for line in lines if "." in line])
        lines_ = []
        for line in lines:
            try:
                idx = line.index(".")
                lines_.append(" "*(dotidx-idx)+line)
            except ValueError:
                lines_.append(line)
        return "\n".join(lines_)

    text = asciichartpy.plot(series, cfg)
    lines = text.split("\n")
    if len(lines) > maxlines:
        raise ValueError(f"Your chart has more than {maxlines} of text; maybe you would like to specify cfg['height']?")
    text = fix_asciichart(lines)
    return text