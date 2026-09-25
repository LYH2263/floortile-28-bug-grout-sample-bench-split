from pydantic import BaseModel


class EstimateRequest(BaseModel):
    room_id: int
    tile_id: int
    waste_pct: float | None = None
    grout_mm: float | None = None
    save: bool = False
    note: str = ""


class EstimateResponse(BaseModel):
    room_id: int
    tile_id: int
    room_name: str
    tile_name: str
    area_m2: float
    piece_m2: float
    grout_mm: float
    eff_piece_m2: float
    raw_count: int
    waste_pct: float
    order_count: int
    layout: dict
    run_id: int | None = None
