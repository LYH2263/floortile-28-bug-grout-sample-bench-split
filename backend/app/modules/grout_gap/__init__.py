"""Grout gap module: effective tile edges after deducting grout width (mm)."""


def effective_edges(tile_l: float, tile_w: float, grout_mm: float) -> tuple[float, float]:
    """Effective tile edge lengths in meters: tile edge minus grout width.

    Raises ValueError when grout is negative or the effective edge is <= 0.
    """
    g = float(grout_mm) / 1000.0
    if g < 0:
        raise ValueError("grout_mm must be >= 0")
    eff_l = float(tile_l) - g
    eff_w = float(tile_w) - g
    if eff_l <= 0 or eff_w <= 0:
        raise ValueError("effective tile edge must be > 0 (grout too wide for tile)")
    return eff_l, eff_w


def effective_piece_area(tile_l: float, tile_w: float, grout_mm: float) -> float:
    """Effective single-tile area (m²) that feeds the area method."""
    eff_l, eff_w = effective_edges(tile_l, tile_w, grout_mm)
    return eff_l * eff_w
