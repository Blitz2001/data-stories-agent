"""Brand + timeline settings shared by the 2D and 3D renderers."""
W, H, FPS, SECONDS = 1080, 1920, 30, 10
HOOK_END, RACE_END = 2.0, 7.5

SURFACE = "#1a1a19"
TEXT = "#f0efec"
TEXT_2 = "#c3c2b7"
MUTED = "#8a8980"
GRID = "#383835"
BAR = "#3987e5"
ACCENT = "#e66767"   # reserved for the headline number / highlighted bar
CHANNEL = "DATA STORIES"


def ease(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def year_at(t: float, start: int, end: int) -> float:
    return start + ease((t - HOOK_END) / (RACE_END - HOOK_END)) * (end - start)


def values_at(series: dict, year: float, start: int) -> dict:
    """Linearly interpolate each country's % change at a fractional year."""
    i0 = int(year) - start
    frac = year - int(year)
    out = {}
    for c, vals in series.items():
        i1 = min(i0 + 1, len(vals) - 1)
        out[c] = vals[i0] * (1 - frac) + vals[i1] * frac
    return out


def captions(story: dict):
    return [
        (0.0, HOOK_END, "Some countries have fewer people\ntoday than in 1990"),
        (HOOK_END, RACE_END, "Change in population since 1990"),
        (RACE_END, SECONDS + 1, f"{story['lead']} lost almost 1 in 3 people"),
    ]
