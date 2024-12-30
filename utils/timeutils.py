from datetime import datetime, timezone

def tz_now() -> datetime:
    return datetime.now(tz=timezone.utc)