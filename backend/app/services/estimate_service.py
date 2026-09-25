from fastapi import HTTPException

from app.engines.tile_math import tile_count
from app.repositories import history, rooms, settings_repo, tiles


def run_estimate(
    room_id: int,
    tile_id: int,
    waste_pct: float | None,
    grout_mm: float | None,
    save: bool,
    note: str,
):
    room = rooms.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    tile = tiles.get_tile(tile_id)
    if not tile:
        raise HTTPException(404, "tile not found")
    if room.get("data_quality") == "dirty":
        raise HTTPException(422, "room marked dirty; fix dimensions before estimate")

    waste = float(waste_pct) if waste_pct is not None else settings_repo.get_waste_pct()
    grout = float(grout_mm) if grout_mm is not None else settings_repo.get_grout_mm()
    try:
        calc = tile_count(
            room["length"], room["width"], tile["tile_l"], tile["tile_w"], waste, grout
        )
    except ValueError as exc:
        # Invalid grout/dimensions: fail the estimate; nothing is persisted.
        raise HTTPException(422, str(exc))

    run_id = None
    if save:
        payload = {**calc, "room_id": room_id, "tile_id": tile_id}
        run_id = history.insert_run(room_id, tile_id, waste, payload, note, grout_mm=grout)

    return {
        "room_id": room_id,
        "tile_id": tile_id,
        "room": room,
        "tile": tile,
        "run_id": run_id,
        **calc,
    }
