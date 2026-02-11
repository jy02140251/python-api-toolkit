"""Data serialization and deserialization utilities."""

from typing import Any, Dict, List, Optional, Type, TypeVar, get_type_hints
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import json

T = TypeVar("T")


class JSONEncoder(json.JSONEncoder):
    """Extended JSON encoder with support for common Python types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        return super().default(obj)


def serialize(data: Any, exclude: Optional[List[str]] = None) -> Any:
    """Serialize Python objects to JSON-compatible format."""
    exclude = set(exclude or [])
    if isinstance(data, dict):
        return {k: serialize(v) for k, v in data.items() if k not in exclude}
    if isinstance(data, (list, tuple)):
        return [serialize(item) for item in data]
    if isinstance(data, datetime):
        return data.isoformat()
    if isinstance(data, Decimal):
        return float(data)
    if isinstance(data, Enum):
        return data.value
    if hasattr(data, "to_dict"):
        result = data.to_dict()
        return {k: v for k, v in result.items() if k not in exclude}
    return data


def to_json(data: Any, pretty: bool = False, **kwargs) -> str:
    """Convert data to JSON string."""
    indent = 2 if pretty else None
    return json.dumps(data, cls=JSONEncoder, indent=indent, **kwargs)


def from_json(json_str: str) -> Any:
    """Parse JSON string to Python object."""
    return json.loads(json_str)


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_snake_case(camel_str: str) -> str:
    """Convert camelCase to snake_case."""
    result = []
    for i, char in enumerate(camel_str):
        if char.isupper() and i > 0:
            result.append("_")
        result.append(char.lower())
    return "".join(result)


def transform_keys(data: Dict, transformer) -> Dict:
    """Transform dictionary keys using a function."""
    if isinstance(data, dict):
        return {transformer(k): transform_keys(v, transformer) for k, v in data.items()}
    if isinstance(data, list):
        return [transform_keys(item, transformer) for item in data]
    return data