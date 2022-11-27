def besides(a: str, b: str) -> str:
    split_a = a.splitlines()
    split_b = b.splitlines()

    width_a = len(split_a[0])
    width_b = len(split_b[0])

    lines_a = len(split_a)
    lines_b = len(split_b)

    lines = max(lines_a, lines_b)

    if lines > lines_a:
        for _ in range(lines - lines_a):
            split_a.append(" " * width_a)
    if lines > lines_b:
        for _ in range(lines - lines_b):
            split_b.append(" " * width_b)

    return "\n".join("".join(line_segments) for line_segments in zip(split_a, split_b))


# https://stackoverflow.com/a/20757491
def bordered(text: str) -> str:
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    res = ["┌" + "─" * width + "┐"]
    for s in lines:
        res.append("│" + (s + " " * width)[:width] + "│")
    res.append("└" + "─" * width + "┘")
    return "\n".join(res)
