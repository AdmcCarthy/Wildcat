"""The Relief base maps: built from Relief's layers, in lon/lat, ordered for painting, covering every well they sit under."""

import json
from pathlib import Path

import pytest
from shapely.geometry import Point, shape

D = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope="module", params=["relief_shelf.json", "relief_ns.json"])
def base(request):
    return json.loads((D / request.param).read_text(encoding="utf-8"))


def test_features_are_lonlat_and_painted_in_order(base):
    assert base["crs"] == "EPSG:4326"
    kinds = [f["properties"]["kind"] for f in base["features"]]
    assert set(kinds) == {"land", "sea"} and kinds == sorted(kinds, key=lambda k: k != "sea")
    for kind in ("sea", "land"):
        mids = [f["properties"]["mid"] for f in base["features"] if f["properties"]["kind"] == kind]
        assert mids == sorted(mids) and mids[0] > 0
    lon0, lat0, lon1, lat1 = shape(base["coverage"]).bounds
    assert -50 < lon0 < lon1 < 65 and 45 < lat0 < lat1 < 82


def test_attribution_names_the_sources(base):
    assert "Copernicus" in base["attribution"] and "EMODnet" in base["attribution"] and "Relief" in base["attribution"]


def test_shelf_base_credits_gebco_where_it_fills_the_frame():
    shelf = json.loads((D / "relief_shelf.json").read_text(encoding="utf-8"))
    assert "GEBCO" in shelf["attribution"] and "not for navigation" in shelf["attribution"]


def test_shelf_base_covers_every_recent_well():
    cover = shape(json.loads((D / "relief_shelf.json").read_text(encoding="utf-8"))["coverage"])
    wells = json.loads((D / "wells_recent.geojson").read_text(encoding="utf-8"))["features"]
    outside = [f["properties"]["well"] for f in wells if not cover.contains(Point(f["geometry"]["coordinates"]))]
    assert not outside, outside


def test_north_sea_base_covers_the_drilled_frame():
    cover = shape(json.loads((D / "relief_ns.json").read_text(encoding="utf-8"))["coverage"])
    assert cover.contains(shape({"type": "Polygon", "coordinates": [[[1.7, 56.25], [7.0, 56.25], [7.0, 61.9], [1.7, 61.9], [1.7, 56.25]]]}))
