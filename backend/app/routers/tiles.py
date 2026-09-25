from fastapi import APIRouter, HTTPException

from app.repositories import rooms as room_repo
from app.repositories import settings_repo
from app.repositories import tiles as tile_repo
from app.services.grout_sample import attach_sample_fields

router = APIRouter(tags=["tiles"])


def _default_room():
    items = room_repo.list_rooms()
    for r in items:
        if r.get("data_quality") != "dirty":
            return r
    return items[0] if items else None


@router.get("/tiles")
def list_tiles():
    grout = settings_repo.get_grout_mm()
    room = _default_room()
    items = [attach_sample_fields(t, room, grout) for t in tile_repo.list_tiles()]
    return {"items": items, "sample_room": room, "catalog_grout_mm": grout}


@router.get("/tiles/{tile_id}")
def get_tile(tile_id: int):
    row = tile_repo.get_tile(tile_id)
    if not row:
        raise HTTPException(404, "tile not found")
    grout = settings_repo.get_grout_mm()
    return attach_sample_fields(row, _default_room(), grout)
