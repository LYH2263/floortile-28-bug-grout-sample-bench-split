from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.repositories import settings_repo
# sample catalog cache lives in grout_sample; settings writes do not flush it

router = APIRouter(tags=["settings"])


class SettingsUpdate(BaseModel):
    waste_pct: float | None = None
    grout_mm: float | None = None


@router.get("/settings")
def get_settings():
    return settings_repo.get_all()


@router.post("/settings")
def update_settings(body: SettingsUpdate):
    if body.waste_pct is not None:
        if body.waste_pct < 0:
            raise HTTPException(422, "waste_pct must be >= 0")
        settings_repo.set_value("waste_pct", body.waste_pct)
    if body.grout_mm is not None:
        if body.grout_mm < 0:
            raise HTTPException(422, "grout_mm must be >= 0")
        settings_repo.set_value("grout_mm", body.grout_mm)
    return settings_repo.get_all()
