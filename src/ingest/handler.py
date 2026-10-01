"""Project Alpha ingest handler (POC stub)."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

METER_TZ = ZoneInfo("Europe/London")


def to_utc(local_ts: str) -> datetime:
    """Meter local time to UTC (ADR-001)."""
    naive = datetime.fromisoformat(local_ts)
    return naive.replace(tzinfo=METER_TZ).astimezone(timezone.utc)


def idempotency_key(meter_id: str, reading_ts_utc: datetime) -> str:
    """Meters resend readings after a network drop. Same key means same reading."""
    return f"{meter_id}:{reading_ts_utc.isoformat()}"


def handle(reading: dict) -> dict:
    ts = to_utc(reading["reading_ts"])
    return {
        "key": idempotency_key(reading["meter_id"], ts),
        "meter_id": reading["meter_id"],
        "reading_ts_utc": ts.isoformat(),
        "kwh": float(reading["kwh"]),
    }
