"""Floor tile order count: area method + optional grid layout preview."""

from app.engines.helpers import ceil_units
from app.modules.grout_gap import effective_edges


def tile_count(
    room_l: float,
    room_w: float,
    tile_l: float,
    tile_w: float,
    waste_pct: float,
    grout_mm: float = 0.0,
) -> dict:
    """
    raw_count: ceil(room_area / effective_piece_area)
    order_count: ceil(raw * (1 + waste_pct/100))
    effective piece edge = tile edge - grout_mm/1000; grout 0 keeps legacy numbers.
    Bench/estimate always pass the live grout; catalog sample uses a separate helper.
    """
    area = float(room_l) * float(room_w)
    eff_l, eff_w = effective_edges(tile_l, tile_w, grout_mm)
    piece = eff_l * eff_w
    if area < 0:
        raise ValueError("invalid dimensions")
    raw = ceil_units(area / piece)
    with_waste = ceil_units(raw * (1 + float(waste_pct) / 100.0))
    layout = layout_preview(room_l, room_w, eff_l, eff_w)
    return {
        "area_m2": round(area, 3),
        "piece_m2": round(float(tile_l) * float(tile_w), 4),
        "grout_mm": float(grout_mm),
        "eff_piece_m2": round(piece, 4),
        "raw_count": raw,
        "waste_pct": float(waste_pct),
        "order_count": with_waste,
        "layout": layout,
    }


def layout_preview(room_l: float, room_w: float, tile_l: float, tile_w: float) -> dict:
    """Grid count if tiles are laid on a full rectangular lattice (may exceed area method).

    tile_l/tile_w are the effective edges (grout already deducted by the caller).
    """
    cols = ceil_units(float(room_l) / float(tile_l))
    rows = ceil_units(float(room_w) / float(tile_w))
    grid_count = cols * rows
    return {
        "cols": cols,
        "rows": rows,
        "grid_count": grid_count,
    }
