from app.config import DEFAULT_GROUT_MM, DEFAULT_WASTE_PCT
from app.db import connect


def get_all() -> dict:
    conn = connect()
    try:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        out = {r["key"]: r["value"] for r in rows}
        if "waste_pct" not in out:
            out["waste_pct"] = str(DEFAULT_WASTE_PCT)
        if "grout_mm" not in out:
            out["grout_mm"] = str(DEFAULT_GROUT_MM)
        return out
    finally:
        conn.close()


def get_waste_pct() -> float:
    raw = get_all().get("waste_pct", str(DEFAULT_WASTE_PCT))
    return float(raw)


def get_grout_mm() -> float:
    raw = get_all().get("grout_mm", str(DEFAULT_GROUT_MM))
    return float(raw)


def set_value(key: str, value) -> None:
    conn = connect()
    try:
        conn.execute(
            """
            INSERT INTO settings(key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, str(value)),
        )
        conn.commit()
    finally:
        conn.close()
