import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="floortile-test-")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services.grout_sample import sample_raw_for_room  # noqa: E402


def _tile(items, tile_id):
    return next(t for t in items if t["id"] == tile_id)


def test_sample_matches_bench_for_same_room_tile_grout():
    with TestClient(app) as client:
        bench = client.get(
            "/api/estimate",
            params={"room_id": 1, "tile_id": 1, "grout_mm": 2},
        ).json()
        client.post("/api/settings", json={"grout_mm": 2})
        tile = _tile(client.get("/api/tiles").json()["items"], 1)
        assert tile["sample_room_id"] == 1
        assert tile["sample_grout_mm"] == 2.0
        assert tile["sample_eff_piece_m2"] == bench["eff_piece_m2"] == 0.3576
        assert tile["sample_raw_count"] == bench["raw_count"] == 76


def test_sample_tracks_grout_changes_and_realigns_at_zero():
    with TestClient(app) as client:
        client.post("/api/settings", json={"grout_mm": 0})
        tile = _tile(client.get("/api/tiles").json()["items"], 1)
        assert tile["sample_grout_mm"] == 0.0
        assert tile["sample_eff_piece_m2"] == tile["sample_piece_m2"] == 0.36
        assert tile["sample_raw_count"] == 75

        # change grout only, tile edges untouched -> sample must move immediately
        client.post("/api/settings", json={"grout_mm": 2})
        tile = _tile(client.get("/api/tiles").json()["items"], 1)
        assert tile["sample_eff_piece_m2"] == 0.3576
        assert tile["sample_raw_count"] == 76

        # back to zero -> same no-grout basis as before any grout was set
        client.post("/api/settings", json={"grout_mm": 0})
        tile = _tile(client.get("/api/tiles").json()["items"], 1)
        assert tile["sample_eff_piece_m2"] == 0.36
        assert tile["sample_raw_count"] == 75


def test_invalid_edge_tile_or_grout_does_not_break_catalog():
    with TestClient(app) as client:
        # dirty tile 3 has a zero edge: listed, but flagged instead of numbered
        client.post("/api/settings", json={"grout_mm": 0})
        items = client.get("/api/tiles").json()["items"]
        bad_tile = _tile(items, 3)
        assert bad_tile["sample_valid"] is False
        assert bad_tile["sample_eff_piece_m2"] is None
        assert "sample_raw_count" not in bad_tile
        assert _tile(items, 1)["sample_valid"] is True
        # bench still rejects the same tile
        assert client.get(
            "/api/estimate", params={"room_id": 1, "tile_id": 3}
        ).status_code == 422

        # grout wider than a 600 tile flags that tile but the 800 tile still
        # samples; the catalog never 500s and the bench rejects the bad pair
        client.post("/api/settings", json={"grout_mm": 700})
        items = client.get("/api/tiles").json()["items"]
        assert _tile(items, 1)["sample_valid"] is False  # 0.6 - 0.7 < 0
        assert _tile(items, 2)["sample_valid"] is True  # 0.8 - 0.7 = 0.1
        assert client.get(
            "/api/estimate", params={"room_id": 1, "tile_id": 1, "grout_mm": 700}
        ).status_code == 422
        client.post("/api/settings", json={"grout_mm": 0})


def test_sample_helper_rejects_non_positive_effective_edge():
    assert sample_raw_for_room(6.0, 4.5, 0.6, 0.6, 0.0) == 75
    assert sample_raw_for_room(6.0, 4.5, 0.6, 0.6, 2.0) == 76
    with pytest.raises(ValueError):
        sample_raw_for_room(6.0, 4.5, 0.6, 0.6, -1.0)
    with pytest.raises(ValueError):
        sample_raw_for_room(6.0, 4.5, 0.6, 0.6, 600.0)
