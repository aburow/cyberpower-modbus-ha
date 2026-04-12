"""Acceptance tests for unified bridge device info contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "cyberpower_modbus"
    / "device_info_unified.py"
)
SPEC = importlib.util.spec_from_file_location("device_info_unified", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CANONICAL_KEYS = MODULE.CANONICAL_KEYS
CONTRACT_VERSION = MODULE.CONTRACT_VERSION
resolve_device_info = MODULE.resolve_device_info


def test_import_safe_and_contract_version() -> None:
    """Import works without Home Assistant and contract version is present."""
    assert CONTRACT_VERSION == "1.0"


def test_resolve_device_info_representative_payload() -> None:
    """Representative payload resolves canonical values."""
    values = {
        "manufacturer": "  CyberPower  ",
        "model": "PR3000ERTXL2U",
        "firmware_version": "50.11.I",
        "card_model": "RMCARD205",
        "serial_number": "GS1234567890",
        "configuration_url": "https://ups.local/config",
        "extra_field": "ignored",
    }

    resolved = resolve_device_info(values, "cyberpower_modbus")
    assert resolved == {
        "manufacturer": "CyberPower",
        "model": "PR3000ERTXL2U",
        "sw_version": "50.11.I",
        "hw_version": "RMCARD205",
        "serial_number": "GS1234567890",
        "configuration_url": "https://ups.local/config",
    }


def test_empty_or_unknown_values_return_subset_or_empty() -> None:
    """Unknown/blank values are omitted."""
    values = {
        "manufacturer": "unknown",
        "model": " ",
        "sw_version": "",
        "serial_number": None,
        "configuration_url": "ups.local",
    }

    assert resolve_device_info(values, "cyberpower_modbus") == {}


def test_returned_keys_subset_of_canonical_only() -> None:
    """Returned keys are canonical only."""
    resolved = resolve_device_info(
        {
            "vendor": "CyberPower",
            "device_model": "OL3000RTXL2U",
            "firmware": "1.2.3",
            "serial": "ABC123",
        },
        "some_source",
    )
    assert set(resolved).issubset(CANONICAL_KEYS)


def test_no_null_or_blank_values_returned() -> None:
    """Output never includes blank values."""
    resolved = resolve_device_info(
        {
            "manufacturer": "CyberPower",
            "configuration_url": "   ",
            "serial_number": "  XYZ  ",
        },
        "cyberpower_modbus",
    )
    assert all(isinstance(v, str) and v.strip() for v in resolved.values())
    assert resolved["serial_number"] == "XYZ"


def test_malformed_input_never_raises() -> None:
    """Malformed input safely returns empty dict."""
    assert resolve_device_info(None, "cyberpower_modbus") == {}  # type: ignore[arg-type]
