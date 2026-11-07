"""Data checks against Sodir's own series, and every number the story quotes."""

import json
from pathlib import Path

import pandas as pd
import pytest
from subscout.build import build

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data"


@pytest.fixture(scope="module")
def y():
    return pd.read_csv(D / "yearly.csv").set_index("year")


@pytest.fixture(scope="module")
def w():
    return pd.read_csv(D / "wildcats.csv")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    rep = build(ROOT, out)
    ledger = {r["name"]: float(r["value"].replace(",", "")) for r in json.loads((out / "build-report.json").read_text())["ledger"]}
    return rep, ledger, out


def test_wildcat_counts_match_sodir_series(y):
    # Sodir's completed-wildcat series (norskpetroleum.no), 1990-2025: within two wells every year
    s = y.loc[1990:2025]
    assert (s.wildcats - s.sodir_wildcats).abs().max() <= 2
    assert abs(s.wildcats.sum() - s.sodir_wildcats.sum()) / s.sodir_wildcats.sum() < 0.01


def test_success_definitions_are_consistent(w):
    assert (w.new_discovery <= w.technical + 1e-9).mean() > 0.998  # a discovery well proved hydrocarbons
    assert (w.commercial <= w.new_discovery).all()
    assert w.lead_years.dropna().ge(0).all()


def test_builds_cleanly(built):
    rep, _, out = built
    assert rep.errors == [] and rep.warnings == []
    page = (out / "index.html").read_text()
    assert "NaN" not in page.split('id="ss-payload"')[1]


def test_quoted_rates(built, y, w):
    _, L, _ = built
    s = y.loc[2016:2025]
    assert L["tech_last"] == pytest.approx(s.technical.sum() / s.wildcats.sum(), rel=1e-5)
    assert L["n_last"] == s.wildcats.sum()
    assert L["disc_last"] == s.discoveries.sum()
    v90 = y.loc[1990:1999]
    assert L["vol_disc_1990s"] == pytest.approx(v90.volume_msm3.sum() / v90.discoveries.sum() * 1e6, rel=1e-5)
    assert 0.5 < L["vol_disc_fall"] < 0.95  # 'each find is smaller' is a large fall, not noise


def test_year_claims_in_prose(y):
    # 2010 stands out (Johan Sverdrup) in volume per discovery since 2000; the hit rate holds near half
    assert y.loc[2000:2025, "volume_per_discovery"].idxmax() == 2010
    assert abs(y.loc[2006:2025].technical.sum() / y.loc[2006:2025].wildcats.sum() - 0.5) < 0.06


def test_platform_wells_produce_fast(w):
    p = w[w.from_platform & w.commercial]
    assert len(p) >= 3 and p.lead_years.median() < 1
