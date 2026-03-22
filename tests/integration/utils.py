from datetime import datetime
from uuid import UUID


def is_valid_uuid(subject: str) -> bool:
    """
    Checks if a string is a valid UUID
    """

    try:
        UUID(subject)
    except ValueError:
        return False

    return True


def is_valid_time_string(date_string):
    """
    Checks if a string is a valid ISO 8601 date or datetime.
    """
    try:
        datetime.fromisoformat(date_string)
    except ValueError:
        return False

    return True
