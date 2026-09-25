import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="floortile-test-")

from fastapi.testclient import TestClient  # noqa: E402

from app.db import connect  # noqa: E402
from app.main import app  # noqa: E402


def _runs_count() -> int:
    conn = connect()
    try:
        return conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    finally:
        conn.close()


def test_estimate_dry_run_with_grout():
    with TestClient(app) as client:
        r = client.get(
            "/api/estimate",
            params={"room_id": 1, "tile_id": 1, "grout_mm": 2},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["grout_mm"] == 2.0
        assert body["eff_piece_m2"] == 0.3576
        assert body["raw_count"] == 76
        assert body["order_count"] == 83
        assert body["layout"]["cols"] == 11
        assert body["run_id"] is None
        # dry run writes no history
        assert _runs_count() == 0


def test_estimate_persist_pins_grout_and_counts():
    with TestClient(app) as client:
        r = client.post(
            "/api/estimate",
            json={"room_id": 1, "tile_id": 1, "grout_mm": 2, "save": True, "note": "t"},
        )
        assert r.status_code == 200
        run_id = r.json()["run_id"]
        assert run_id is not None
        got = client.get(f"/api/runs/{run_id}").json()
        assert got["grout_mm"] == 2.0
        assert got["result"]["grout_mm"] == 2.0
        assert got["result"]["eff_piece_m2"] == 0.3576
        assert got["result"]["raw_count"] == 76
        assert got["result"]["order_count"] == 83


def test_catalog_sample_tracks_live_grout_and_matches_bench():
    with TestClient(app) as client:
        # grout 0: sample uses seamless edges, same raw as the bench
        r = client.get("/api/tiles")
        assert r.status_code == 200
        tile = next(t for t in r.json()["items"] if t["id"] == 1)
        assert tile["sample_grout_mm"] == 0.0
        assert tile["sample_piece_m2"] == 0.36
        assert tile["sample_eff_piece_m2"] == 0.36
        assert tile["sample_raw_count"] == 75
        bench0 = client.get("/api/estimate", params={"room_id": 1, "tile_id": 1}).json()
        assert tile["sample_raw_count"] == bench0["raw_count"]

        # only the grout changes: sample recomputes on the next request
        assert client.post("/api/settings", json={"grout_mm": 2}).status_code == 200
        tile = next(t for t in client.get("/api/tiles").json()["items"] if t["id"] == 1)
        assert tile["sample_grout_mm"] == 2.0
        assert tile["sample_piece_m2"] == 0.36  # nominal edges untouched
        assert tile["sample_eff_piece_m2"] == 0.3576
        assert tile["sample_raw_count"] == 76
        bench2 = client.get(
            "/api/estimate", params={"room_id": 1, "tile_id": 1, "grout_mm": 2}
        ).json()
        assert tile["sample_eff_piece_m2"] == bench2["eff_piece_m2"]
        assert tile["sample_raw_count"] == bench2["raw_count"]

        # back to zero: sample and bench realign on the seamless basis
        assert client.post("/api/settings", json={"grout_mm": 0}).status_code == 200
        tile = next(t for t in client.get("/api/tiles").json()["items"] if t["id"] == 1)
        assert tile["sample_grout_mm"] == 0.0
        assert tile["sample_eff_piece_m2"] == 0.36
        assert tile["sample_raw_count"] == 75
        bench0b = client.get("/api/estimate", params={"room_id": 1, "tile_id": 1}).json()
        assert tile["sample_raw_count"] == bench0b["raw_count"]


def test_catalog_sample_with_wide_grout_marks_tile_instead_of_error():
    with TestClient(app) as client:
        assert client.post("/api/settings", json={"grout_mm": 600}).status_code == 200
        r = client.get("/api/tiles")
        assert r.status_code == 200
        tile = next(t for t in r.json()["items"] if t["id"] == 1)
        assert tile["sample_eff_piece_m2"] is None
        assert tile["sample_raw_count"] is None
        assert tile["sample_error"]
        # dirty zero-edge tile must also list without a 500
        dirty = next(t for t in r.json()["items"] if t["data_quality"] == "dirty")
        assert dirty["sample_raw_count"] is None
        client.post("/api/settings", json={"grout_mm": 0})


def test_invalid_grout_fails_and_writes_no_history():
    with TestClient(app) as client:
        before = _runs_count()
        for bad in (-1.0, 600.0, 700.0):
            r = client.post(
                "/api/estimate",
                json={"room_id": 1, "tile_id": 1, "grout_mm": bad, "save": True},
            )
            assert r.status_code == 422, bad
        assert _runs_count() == before


def test_default_grout_from_settings_and_old_runs_untouched():
    with TestClient(app) as client:
        # default grout is 0 -> legacy numbers
        r = client.get("/api/estimate", params={"room_id": 1, "tile_id": 1})
        assert r.status_code == 200
        assert r.json()["grout_mm"] == 0.0
        assert r.json()["raw_count"] == 75

        # change default -> only new estimates use it
        r = client.post("/api/settings", json={"grout_mm": 3})
        assert r.status_code == 200
        assert float(r.json()["grout_mm"]) == 3.0
        r = client.get("/api/estimate", params={"room_id": 1, "tile_id": 1})
        assert r.json()["grout_mm"] == 3.0

        # save with the new default, then change default again
        run_id = client.post(
            "/api/estimate", json={"room_id": 1, "tile_id": 1, "save": True}
        ).json()["run_id"]
        assert client.post("/api/settings", json={"grout_mm": 5}).status_code == 200
        got = client.get(f"/api/runs/{run_id}").json()
        assert got["grout_mm"] == 3.0
        assert got["result"]["grout_mm"] == 3.0
        assert got["result"]["order_count"] > 0

        # negative default grout is rejected
        assert client.post("/api/settings", json={"grout_mm": -2}).status_code == 422
