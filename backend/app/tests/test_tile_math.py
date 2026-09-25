import pytest

from app.engines.tile_math import layout_preview, tile_count


def test_guest_room_600_waste8():
    r = tile_count(6.0, 4.5, 0.6, 0.6, 8.0)
    assert r["area_m2"] == 27.0
    assert r["raw_count"] == 75
    assert r["order_count"] == 81
    assert r["layout"]["cols"] == 10
    assert r["layout"]["rows"] == 8
    assert r["layout"]["grid_count"] == 80


def test_layout_preview_small_room():
    lp = layout_preview(2.5, 2.0, 0.6, 0.6)
    assert lp["cols"] == 5
    assert lp["rows"] == 4
    assert lp["grid_count"] == 20


def test_zero_waste():
    r = tile_count(3.0, 3.0, 1.0, 1.0, 0.0)
    assert r["raw_count"] == 9
    assert r["order_count"] == 9


def test_grout_zero_matches_legacy():
    legacy = tile_count(6.0, 4.5, 0.6, 0.6, 8.0)
    same = tile_count(6.0, 4.5, 0.6, 0.6, 8.0, grout_mm=0.0)
    assert same == legacy
    assert same["grout_mm"] == 0.0
    assert same["eff_piece_m2"] == same["piece_m2"]


def test_grout_shrinks_effective_piece():
    # 0.6m tile with 2mm grout -> 0.598m effective edge, 0.357604 m² effective piece
    r = tile_count(6.0, 4.5, 0.6, 0.6, 8.0, grout_mm=2.0)
    assert r["grout_mm"] == 2.0
    assert r["eff_piece_m2"] == 0.3576
    assert r["piece_m2"] == 0.36  # nominal piece unchanged
    assert r["raw_count"] == 76  # ceil(27 / 0.357604)
    assert r["order_count"] == 83  # ceil(76 * 1.08)
    assert r["layout"]["cols"] == 11  # ceil(6 / 0.598)
    assert r["layout"]["rows"] == 8  # ceil(4.5 / 0.598)
    assert r["layout"]["grid_count"] == 88


def test_grout_zero_tile_still_fails():
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.0, 0.6, 8.0)


def test_negative_grout_fails():
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.6, 0.6, 8.0, grout_mm=-1.0)


def test_grout_wider_than_tile_fails():
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.6, 0.6, 8.0, grout_mm=600.0)  # edge -> 0
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.6, 0.6, 8.0, grout_mm=700.0)  # edge -> negative
