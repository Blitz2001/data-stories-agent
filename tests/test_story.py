"""Tests for the data + verification step: wrong numbers must never reach a video."""
import copy

import numpy as np
import pandas as pd
import pytest

import story as S

YEARS = list(range(1990, 2025))


def make_pop(changes: dict[str, float], base: float = 5_000_000) -> pd.DataFrame:
    """Countries whose population moves linearly from `base` to base*(1+change%)."""
    rows = {}
    for name, pct in changes.items():
        rows[name] = np.linspace(base, base * (1 + pct / 100), len(YEARS))
    return pd.DataFrame.from_dict(rows, orient="index", columns=YEARS)


@pytest.fixture
def pop():
    changes = {f"Country{i:02d}": -2.0 * i for i in range(1, 13)}  # -2% … -24%
    changes["Leader"] = -31.0
    changes["Growing"] = 25.0
    return make_pop(changes)


def test_picks_largest_decline_first(pop):
    story = S.build_story(pop)
    assert story["lead"] == "Leader"
    assert story["countries"][0] == "Leader"
    assert len(story["countries"]) == S.N_BARS


def test_lead_change_matches_raw_counts(pop):
    story = S.build_story(pop)
    expected = (pop.loc["Leader", 2024] / pop.loc["Leader", 1990] - 1) * 100
    assert story["lead_change"] == pytest.approx(expected)
    assert story["lead_change"] == pytest.approx(-31.0)


def test_growing_countries_never_listed(pop):
    assert "Growing" not in S.build_story(pop)["countries"]


def test_small_countries_excluded(pop):
    pop.loc["Tiny"] = np.linspace(500_000, 100_000, len(YEARS))  # -80% but under 1M
    assert "Tiny" not in S.build_story(pop)["countries"]


def test_every_claim_has_a_source(pop):
    for claim in S.build_story(pop)["claims"]:
        assert claim["source"].startswith("https://")
        assert claim["check"]


def test_verify_rejects_tampered_number(pop):
    story = S.build_story(pop)
    bad = copy.deepcopy(story)
    bad["lead_change"] -= 0.5
    with pytest.raises(AssertionError, match="lead change"):
        S.verify(bad, pop)


def test_verify_rejects_claim_that_is_no_longer_true():
    # "almost 1 in 3" must fail if the leader only lost 20%
    pop = make_pop({f"C{i}": -1.0 * i for i in range(1, 12)} | {"Leader": -20.0})
    with pytest.raises(AssertionError, match="1 in 3"):
        S.build_story(pop)


def test_verify_rejects_wrong_order(pop):
    story = S.build_story(pop)
    bad = copy.deepcopy(story)
    bad["countries"][0], bad["countries"][1] = bad["countries"][1], bad["countries"][0]
    with pytest.raises(AssertionError, match="rank order"):
        S.verify(bad, pop)


def test_aggregates_are_dropped(tmp_path):
    csv = tmp_path / "pop.csv"
    pd.DataFrame({
        "country": ["Realland", "World", "Europe"],
        "year": [1990, 1990, 1990],
        "iso_code": ["RLD", "OWID_WRL", None],
        "population": [1e6, 5e9, 7e8],
    }).to_csv(csv, index=False)
    assert list(S.load_population(csv).index) == ["Realland"]
