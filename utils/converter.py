from typing import Any

def is_int(obj: Any) -> bool:
    try:
        int(obj)
        return True
    except ValueError:
        return False