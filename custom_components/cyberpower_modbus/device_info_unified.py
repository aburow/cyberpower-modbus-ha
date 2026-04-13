# SPDX-FileCopyrightText: 2026 github.com/aburow
# SPDX-License-Identifier: GPL-3.0-only

"""Unified device info resolver for bridge compatibility (dependency-free)."""

from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "1.0"

CANONICAL_KEYS = {
    "manufacturer",
    "model",
    "sw_version",
    "hw_version",
    "serial_number",
    "configuration_url",
}


def _clean(value: Any) -> str | None:
    """Return a normalized string value or None for unknown/empty values."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower() == "unknown":
        return None
    return text


def _first(values: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    """Return first normalized non-empty value for key aliases."""
    for key in keys:
        if key in values:
            normalized = _clean(values.get(key))
            if normalized is not None:
                return normalized
    return None


def _clean_url(value: Any) -> str | None:
    """Return normalized URL only when explicitly full http(s) URL."""
    text = _clean(value)
    if text is None:
        return None
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return None


def resolve_device_info(
    values: dict[str, Any], source: str
) -> dict[str, str | None]:
    """Return canonical device info fields for MQTT discovery device block."""
    try:
        if not isinstance(values, dict):
            return {}

        # Current CyberPower sources provide equivalent metadata keys.
        # Keep behavior deterministic by only normalizing known aliases.
        _ = source  # source accepted by contract; mapping is source-agnostic for now.

        resolved: dict[str, str | None] = {}

        manufacturer = _first(values, ("manufacturer", "mfr", "vendor", "brand"))
        if manufacturer is not None:
            resolved["manufacturer"] = manufacturer

        model = _first(values, ("model", "hw_model", "device_model", "ups_model"))
        if model is not None:
            resolved["model"] = model

        sw_version = _first(
            values,
            (
                "sw_version",
                "firmware_version",
                "fw_version",
                "firmware",
                "software_version",
            ),
        )
        if sw_version is not None:
            resolved["sw_version"] = sw_version

        hw_version = _first(values, ("hw_version", "hardware_version", "card_model"))
        if hw_version is not None:
            resolved["hw_version"] = hw_version

        serial_number = _first(values, ("serial_number", "serial", "serial_no"))
        if serial_number is not None:
            resolved["serial_number"] = serial_number

        configuration_url = _clean_url(
            _first(
                values,
                ("configuration_url", "config_url", "web_url", "device_url", "url"),
            )
        )
        if configuration_url is not None:
            resolved["configuration_url"] = configuration_url

        # Hard guard: return canonical keys only, non-empty strings only.
        return {
            key: value
            for key, value in resolved.items()
            if key in CANONICAL_KEYS and isinstance(value, str) and value.strip()
        }
    except (AttributeError, KeyError, TypeError, ValueError):
        return {}
