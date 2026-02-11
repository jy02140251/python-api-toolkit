"""
Request Validator Module.

Provides declarative request payload validation with
custom rules and detailed error messages.
"""

import re
from typing import Any, Dict, List, Optional, Callable


class ValidationError(Exception):
    """Raised when request validation fails."""

    def __init__(self, errors: List[Dict[str, str]]):
        self.errors = errors
        super().__init__(f"Validation failed: {len(errors)} error(s)")


class RequestValidator:
    """
    Declarative request payload validator.

    Define validation rules and validate request data
    with detailed error reporting.

    Example:
        >>> validator = RequestValidator()
        >>> validator.add_rule("email", required=True, pattern=r"^[^@]+@[^@]+$")
        >>> validator.add_rule("age", required=True, min_value=0, max_value=150)
        >>> errors = validator.validate({"email": "test@example.com", "age": 25})
    """

    def __init__(self):
        self._rules: Dict[str, Dict[str, Any]] = {}

    def add_rule(
        self,
        field: str,
        required: bool = False,
        field_type: Optional[type] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        pattern: Optional[str] = None,
        choices: Optional[list] = None,
        custom: Optional[Callable[[Any], Optional[str]]] = None,
    ) -> "RequestValidator":
        """
        Add a validation rule for a field.

        Returns self for method chaining.
        """
        self._rules[field] = {
            "required": required,
            "type": field_type,
            "min_length": min_length,
            "max_length": max_length,
            "min_value": min_value,
            "max_value": max_value,
            "pattern": pattern,
            "choices": choices,
            "custom": custom,
        }
        return self

    def validate(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Validate data against all defined rules.

        Args:
            data: Dictionary of field values to validate.

        Returns:
            List of error dictionaries. Empty list if valid.
        """
        errors: List[Dict[str, str]] = []

        for field, rules in self._rules.items():
            value = data.get(field)

            # Required check
            if rules["required"] and (value is None or value == ""):
                errors.append({"field": field, "message": f"{field} is required"})
                continue

            if value is None:
                continue

            # Type check
            if rules["type"] and not isinstance(value, rules["type"]):
                errors.append({
                    "field": field,
                    "message": f"{field} must be of type {rules['type'].__name__}",
                })
                continue

            # String validations
            if isinstance(value, str):
                if rules["min_length"] and len(value) < rules["min_length"]:
                    errors.append({
                        "field": field,
                        "message": f"{field} must be at least {rules['min_length']} characters",
                    })
                if rules["max_length"] and len(value) > rules["max_length"]:
                    errors.append({
                        "field": field,
                        "message": f"{field} must be at most {rules['max_length']} characters",
                    })
                if rules["pattern"] and not re.match(rules["pattern"], value):
                    errors.append({
                        "field": field,
                        "message": f"{field} format is invalid",
                    })

            # Numeric validations
            if isinstance(value, (int, float)):
                if rules["min_value"] is not None and value < rules["min_value"]:
                    errors.append({
                        "field": field,
                        "message": f"{field} must be >= {rules['min_value']}",
                    })
                if rules["max_value"] is not None and value > rules["max_value"]:
                    errors.append({
                        "field": field,
                        "message": f"{field} must be <= {rules['max_value']}",
                    })

            # Choices validation
            if rules["choices"] and value not in rules["choices"]:
                errors.append({
                    "field": field,
                    "message": f"{field} must be one of: {rules['choices']}",
                })

            # Custom validation
            if rules["custom"]:
                custom_error = rules["custom"](value)
                if custom_error:
                    errors.append({"field": field, "message": custom_error})

        return errors

    def validate_or_raise(self, data: Dict[str, Any]) -> None:
        """Validate and raise ValidationError if invalid."""
        errors = self.validate(data)
        if errors:
            raise ValidationError(errors)