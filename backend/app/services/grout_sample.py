"""Tile catalog sample raw helpers.

Sample figures use the SAME effective-edge basis as the live estimate path
(app.modules.grout_gap), so the catalog example stays aligned with the bench:
grout 0 -> seamless numbers; positive grout -> tile edge minus grout. Figures
are computed on every request from the live default grout, never cached.
"""

from __future__ import annotations

from app.engines.helpers import ceil_units
from app.modules.grout_gap import effective_edges


def sample_piece_area(tile_l: float, tile_w: float, grout_mm: float = 0.0) -> float:
    """Effective single-tile area (m²) at the given grout width."""
    eff_l, eff_w = effective_edges(tile_l, tile_w, grout_mm)
    return round(eff_l * eff_w, 4)


def sample_raw_for_room(
    room_l: float,
    room_w: float,
    tile_l: float,
    tile_w: float,
    grout_mm: float = 0.0,
) -> int:
    eff_l, eff_w = effective_edges(tile_l, tile_w, grout_mm)
    piece = eff_l * eff_w
    area = float(room_l) * float(room_w)
    return ceil_units(area / piece)


def attach_sample_fields(tile: dict, room: dict | None, live_grout: float) -> dict:
    """Enrich a tile row with catalog sample numbers on the live grout basis."""
    out = dict(tile)
    nominal = round(float(tile["tile_l"]) * float(tile["tile_w"]), 4)
    payload = {
        "sample_grout_mm": float(live_grout),
        "sample_piece_m2": nominal,
    }
    try:
        payload["sample_eff_piece_m2"] = sample_piece_area(
            tile["tile_l"], tile["tile_w"], live_grout
        )
        if room:
            payload["sample_raw_count"] = sample_raw_for_room(
                room["length"], room["width"],
                tile["tile_l"], tile["tile_w"], live_grout,
            )
            payload["sample_room_id"] = room["id"]
    except ValueError as exc:
        # Grout too wide for this tile (or zero-edge dirty tile): no example.
        payload["sample_eff_piece_m2"] = None
        payload["sample_raw_count"] = None
        payload["sample_error"] = str(exc)
    out.update(payload)
    out["catalog_grout_mm"] = float(live_grout)
    return out


def sample_order(raw: int, waste_pct: float) -> int:
    return ceil_units(int(raw) * (1 + float(waste_pct) / 100.0))
