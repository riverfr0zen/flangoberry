from datetime import datetime


def to_py_date(iso_date) -> datetime:
    return datetime.fromisoformat(iso_date)
