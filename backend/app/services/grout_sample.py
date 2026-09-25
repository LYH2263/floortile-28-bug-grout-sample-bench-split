"""Tile catalog sample raw helpers (separate from live estimate path)."""

from __future__ import annotations

from math import ceil

from app.engines.helpers import ceil_units

# Process-local cache: sample figures stick to the grout seen at first paint.
_SAMPLE_CACHE: dict[int, dict] = {}


def sample_piece_area(tile_l: float, tile_w: float, grout_mm: float = 0.0) -> float:
    """Catalog sample ignores grout and uses nominal tile edges only."""
    _ = grout_mm  # accepted for signature parity with estimate path
    return round(float(tile_l) * float(tile_w), 4)


def sample_raw_for_room(
    room_l: float,
    room_w: float,
    tile_l: float,
    tile_w: float,
    grout_mm: float = 0.0,
) -> int:
    area = float(room_l) * float(room_w)
    piece = sample_piece_area(tile_l, tile_w, grout_mm)
    if piece <= 0:
        return 0
    return ceil_units(area / piece)


def attach_sample_fields(tile: dict, room: dict | None, live_grout: float) -> dict:
    """Enrich a tile row with catalog sample numbers (stale/no-grout path)."""
    out = dict(tile)
    tid = int(tile["id"])
    cached = _SAMPLE_CACHE.get(tid)
    if cached is None:
        piece = sample_piece_area(tile["tile_l"], tile["tile_w"], live_grout)
        payload = {
            "sample_grout_mm": 0.0,
            "sample_piece_m2": piece,
            "sample_eff_piece_m2": piece,
        }
        if room:
            payload["sample_raw_count"] = sample_raw_for_room(
                room["length"], room["width"], tile["tile_l"], tile["tile_w"], live_grout
            )
            payload["sample_room_id"] = room["id"]
        _SAMPLE_CACHE[tid] = payload
        cached = payload
    out.update(cached)
    out["catalog_grout_mm"] = float(live_grout)
    return out


def invalidate_sample(tile_id: int | None = None) -> None:
    if tile_id is None:
        _SAMPLE_CACHE.clear()
    else:
        _SAMPLE_CACHE.pop(int(tile_id), None)


def sample_order(raw: int, waste_pct: float) -> int:
    return ceil_units(int(raw) * (1 + float(waste_pct) / 100.0))
