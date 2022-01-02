"""Very poor HTML generation."""
__all__ = ["rows2html", "tabulate_html", "row2html",]

import tabulate

def rows2html(rows, header=None, aligns=None, formats=None, flags_colorsign=None, tableclass=""):
    """Converts list of dicts to HTML table."""
    buffer = [f"<table class={tableclass}>"]
    nc = len(rows[0])
    s_aligns = [""]*nc if not aligns else [f" align={align}" if align is not None else "" for align in aligns]

    for i, row in enumerate(rows):
        if i == 0:
            if not header: header = list(row.keys())
            buffer.extend(["<tr>",
                           "\n".join([f"<th{s_align}>{caption}</th>" for caption, s_align in zip(header, s_aligns)]),
                           "</tr>"])
        buffer.append("<tr>")
        for j, value in enumerate(row.values()):
            class_ = "" if not flags_colorsign or not flags_colorsign[j] \
                else (" class="+("positive" if value > 0 else "negative" if value < 0 else "zero"))
            s_value = str(value) if not formats or formats[j] is None else f"{value:{formats[j]}}"
            buffer.append(f"<td{s_aligns[j]}{class_}>{s_value}</td>")
        buffer.append("</tr>")
    buffer.append("</table>")
    return "\n".join(buffer)


def tabulate_html(rows, header, tableclass=""):
    """Uses tabulate to generate HTML and assigns class 'saccat' to <table> tag."""
    _ret = tabulate.tabulate(rows, header, tablefmt="html", floatfmt="f")
    ret = _ret.replace("<table>", f"<table class='{tableclass}'>")
    return ret


def row2html(rows, header=None, tableclass=""):
    """Converts single-element list of dicts to 2-column HTML table."""
    if isinstance(rows, dict):
        rows = [rows]
    buffer = [f"<table class={tableclass}>"]
    if not header: header = list(rows[0].keys())
    for i, row in enumerate(rows):
        for caption, value in zip(header, row.values()):
            buffer.extend(["<tr>", f"<td class='header'>{caption.replace('<br>', ' ')}</td>", f"<td>{value}</td>", "</tr>"])
    buffer.append("</table>")
    return "\n".join(buffer)
