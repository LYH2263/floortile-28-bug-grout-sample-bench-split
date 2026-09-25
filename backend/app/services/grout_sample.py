"""Tile catalog sample raw helpers (separate from live estimate path).

The catalog sample uses the same effective-piece basis as the bench: the
grout width is deducted from every tile edge before dividing the room area.
Figures are always recomputed from the live catalog grout, so changing the
grout moves the sample immediately and grout 0 realigns it with the
no-grout numbers.
"""

from __future__ import annotations

from app.engines.helpers import ceil_units
from app.modules.grout_gap import effective_edges, effective_piece_area


def sample_piece_area(tile_l: float, tile_w: float, grout_mm: float = 0.0) -> float:
    """Effective single-piece area (m²) at the given grout, same basis as the bench.

    Raises ValueError when grout is negative or leaves a non-positive edge.
    """
    return effective_piece_area(tile_l, tile_w, grout_mm)


def sample_raw_for_room(
    room_l: float,
    room_w: float,
    tile_l: float,
    tile_w: float,
    grout_mm: float = 0.0,
) -> int:
    area = float(room_l) * float(room_w)
    # Use the unrounded effective piece so ceil matches tile_count exactly.
    eff_l, eff_w = effective_edges(tile_l, tile_w, grout_mm)
    return ceil_units(area / (eff_l * eff_w))


def attach_sample_fields(tile: dict, room: dict | None, live_grout: float) -> dict:
    """Enrich a tile row with catalog sample numbers computed at live_grout.

    Tiles whose effective edge is non-positive (dirty zero-edge tiles, or a
    grout wider than the tile) carry sample_valid=False and no numbers, so one
    bad tile never hides the rest of the catalog; the bench still rejects the
    same tile/grout pair with 422.
    """
    out = dict(tile)
    grout = float(live_grout)
    nominal = round(float(tile["tile_l"]) * float(tile["tile_w"]), 4)
    out["sample_grout_mm"] = grout
    out["catalog_grout_mm"] = grout
    out["sample_piece_m2"] = nominal
    try:
        piece = sample_piece_area(tile["tile_l"], tile["tile_w"], grout)
    except ValueError:
        out["sample_eff_piece_m2"] = None
        out["sample_valid"] = False
        return out
    out["sample_eff_piece_m2"] = round(piece, 4)
    out["sample_valid"] = True
    if room:
        out["sample_raw_count"] = sample_raw_for_room(
            room["length"], room["width"], tile["tile_l"], tile["tile_w"], grout
        )
        out["sample_room_id"] = room["id"]
    return out


def invalidate_sample(tile_id: int | None = None) -> None:
    """Kept for callers; samples are recomputed live, so there is nothing to flush."""
    _ = tile_id


def sample_order(raw: int, waste_pct: float) -> int:
    return ceil_units(int(raw) * (1 + float(waste_pct) / 100.0))
