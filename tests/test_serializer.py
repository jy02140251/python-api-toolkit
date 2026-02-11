"""Tests for serialization utilities."""

import pytest
from datetime import datetime
from decimal import Decimal
from enum import Enum

from api_toolkit.serializer import (
    serialize, to_json, from_json, to_camel_case,
    to_snake_case, transform_keys, JSONEncoder
)


class Color(Enum):
    RED = "red"
    BLUE = "blue"


class TestSerialize:
    def test_serialize_dict(self):
        data = {"name": "test", "count": 42}
        result = serialize(data)
        assert result == data

    def test_serialize_datetime(self):
        dt = datetime(2025, 1, 15, 12, 0, 0)
        result = serialize(dt)
        assert result == "2025-01-15T12:00:00"

    def test_serialize_decimal(self):
        result = serialize(Decimal("19.99"))
        assert result == 19.99

    def test_serialize_enum(self):
        result = serialize(Color.RED)
        assert result == "red"

    def test_serialize_with_exclude(self):
        data = {"name": "test", "password": "secret", "email": "test@test.com"}
        result = serialize(data, exclude=["password"])
        assert "password" not in result
        assert "name" in result


class TestCaseConverters:
    def test_to_camel_case(self):
        assert to_camel_case("hello_world") == "helloWorld"
        assert to_camel_case("user_id") == "userId"
        assert to_camel_case("simple") == "simple"

    def test_to_snake_case(self):
        assert to_snake_case("helloWorld") == "hello_world"
        assert to_snake_case("userId") == "user_id"
        assert to_snake_case("simple") == "simple"

    def test_transform_keys(self):
        data = {"user_name": "test", "user_email": "t@t.com"}
        result = transform_keys(data, to_camel_case)
        assert "userName" in result
        assert "userEmail" in result


class TestJsonEncoder:
    def test_encode_datetime(self):
        result = to_json({"ts": datetime(2025, 6, 1)})
        assert "2025-06-01" in result

    def test_encode_pretty(self):
        result = to_json({"a": 1}, pretty=True)
        assert "\n" in result

    def test_roundtrip(self):
        original = {"key": "value", "num": 42}
        json_str = to_json(original)
        restored = from_json(json_str)
        assert restored == original