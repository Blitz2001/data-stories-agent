"""Data step: load the dataset, compute the story, verify every on-screen number.

Both renderers (2D matplotlib and 3D Blender) read the same verified story,
so the numbers in every version of the video are identical and traceable.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "owid-co2-data.csv"
SOURCE_URL = "https://github.com/owid/co2-data"
SOURCE_NAME = "Our World in Data (UN World Population Prospects)"

START, N_BARS, MIN_POP = 1990, 10, 1_000_000
SHORT_NAMES = {"Bosnia and Herzegovina": "Bosnia & Herz."}


@dataclass
class Claim:
    text: str          # sentence that appears on screen / in the script
    value: float       # the number behind it
    check: str         # how it was verified
    source: str = SOURCE_URL


def load_population(path: Path = DATA) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["country", "year", "iso_code", "population"])
    # Countries only: OWID aggregates (World, Europe, income groups) use OWID_ codes
    df = df[df.iso_code.notna() & ~df.iso_code.str.startswith("OWID", na=False)]
    return df.pivot(index="country", columns="year", values="population")


def build_story(pop: pd.DataFrame) -> dict:
    # latest year that most countries report (avoids a year with only a few early entries)
    end = int(max(c for c in pop.columns if pop[c].notna().mean() > 0.5))
    base = pop[START]
    eligible = pop.index[(base >= MIN_POP) & pop[end].notna()]
    change = (pop.loc[eligible].div(base[eligible], axis=0) - 1) * 100
    final = change[end].sort_values().head(N_BARS)
    countries = list(final.index)
    series = change.loc[countries, range(START, end + 1)]

    lead = countries[0]
    lead_chg = float(series.loc[lead, end])
    p0, p1 = float(pop.loc[lead, START]), float(pop.loc[lead, end])

    claims = [
        Claim(f"{lead}'s population fell {abs(lead_chg):.1f}% between {START} and {end}",
              lead_chg, "recomputed from raw population counts"),
        Claim(f"{lead}: {p0/1e6:.2f}M → {p1/1e6:.2f}M people", p1 - p0, "raw counts"),
        Claim(f"{lead} lost almost 1 in 3 people", lead_chg, "-33.4% < change < -28%"),
    ]
    story = {
        "title": "Shrinking countries",
        "subtitle": f"Population change, {START}–{end} · countries over 1M people",
        "start": START, "end": end, "lead": lead,
        "countries": countries,
        "labels": [SHORT_NAMES.get(c, c) for c in countries],
        "series": {c: [float(v) for v in series.loc[c]] for c in countries},
        "pop_start": p0, "pop_end": p1, "lead_change": lead_chg,
        "claims": [asdict(c) for c in claims],
        "source_name": SOURCE_NAME, "source_url": SOURCE_URL,
    }
    verify(story, pop)
    return story


def verify(story: dict, pop: pd.DataFrame) -> None:
    """Re-derive every on-screen number independently; raise if anything disagrees."""
    s, e, lead = story["start"], story["end"], story["lead"]
    recomputed = (pop.loc[lead, e] / pop.loc[lead, s] - 1) * 100
    assert abs(recomputed - story["lead_change"]) < 1e-9, "lead change mismatch"
    assert -100 / 3 < story["lead_change"] < -28, "'almost 1 in 3' no longer true"
    finals = [story["series"][c][-1] for c in story["countries"]]
    assert finals == sorted(finals), "bars not in rank order"
    assert all(v < 0 for v in finals), "a listed country did not shrink"
    for c in story["countries"]:
        assert pop.loc[c, s] >= MIN_POP, f"{c} below population threshold"


if __name__ == "__main__":
    story = build_story(load_population())
    out = ROOT / "out" / "story.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(story, indent=2, ensure_ascii=False))
    for c in story["claims"]:
        print("✓", c["text"])
