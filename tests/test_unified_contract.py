"""Contract validation tests for UPS Unified interop."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOMAIN_PATH = ROOT / "custom_components" / "cyberpower_modbus"


def _load_module(file_name: str):
    spec = importlib.util.spec_from_file_location(file_name, DOMAIN_PATH / file_name)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_interface_modules_import_in_plain_python() -> None:
    _load_module("icons_unified.py")
    _load_module("sensor_availability_unified.py")
    _load_module("device_info_unified.py")


def test_runtime_interface_functions_never_raise() -> None:
    icons = _load_module("icons_unified.py")
    availability = _load_module("sensor_availability_unified.py")
    device_info = _load_module("device_info_unified.py")

    assert icons.resolve_sensor_icon("battery_capacity")
    assert availability.entity_enabled_default("battery_capacity") in (True, False)
    assert isinstance(device_info.resolve_device_info({}, "cyberpower_modbus"), dict)

    # malformed inputs should still not raise
    assert availability.entity_enabled_default(None) is True  # type: ignore[arg-type]
    assert device_info.resolve_device_info(None, "bad_source") == {}  # type: ignore[arg-type]


def test_device_info_returns_only_non_empty_canonical_values() -> None:
    device_info = _load_module("device_info_unified.py")
    resolved = device_info.resolve_device_info(
        {
            "manufacturer": "CyberPower",
            "model": "PR3000",
            "firmware_version": "1.2.3",
            "serial_number": "ABC123",
            "configuration_url": "https://ups.local",
            "extra": "ignored",
        },
        "cyberpower_modbus",
    )

    allowed = {
        "manufacturer",
        "model",
        "sw_version",
        "hw_version",
        "serial_number",
        "configuration_url",
    }
    assert set(resolved).issubset(allowed)
    assert all(v is not None and str(v).strip() != "" for v in resolved.values())


def test_entity_enabled_default_is_deterministic() -> None:
    availability = _load_module("sensor_availability_unified.py")
    key = "runtime_remaining"
    assert availability.entity_enabled_default(key) == availability.entity_enabled_default(
        key
    )


def test_capability_profiles_contract_rules() -> None:
    profiles_module = _load_module("capability_profile_unified.py")
    profiles = profiles_module.CAPABILITY_PROFILES
    assert profiles

    for profile in profiles:
        assert isinstance(profile.get("profile_id"), str) and profile["profile_id"]
        assert profile.get("protocol") in {"modbus", "snmp", "hybrid"}

        poll_groups = profile.get("poll_groups", {})
        assert "slow" in poll_groups

        protocol = profile["protocol"]
        if protocol == "modbus":
            registers = profile.get("registers", [])
            keys = [register["key"] for register in registers]
            assert len(keys) == len(set(keys))

            for register in registers:
                poll_group = register.get("poll_group", "slow")
                assert poll_group in poll_groups

            for block in profile.get("register_blocks", []):
                poll_group = block.get("poll_group", "slow")
                assert poll_group in poll_groups

        if protocol == "snmp":
            oids = profile.get("oids", {})
            for metric in oids.values():
                assert "oid" in metric or "oids" in metric
                poll_group = metric.get("poll_group", "slow")
                assert poll_group in poll_groups

            for block in profile.get("snmp_blocks", []):
                poll_group = block.get("poll_group", "slow")
                assert poll_group in poll_groups
                for metric_key in block.get("metrics", []):
                    assert metric_key in oids

        if protocol == "hybrid":
            modbus = profile.get("modbus", {})
            snmp = profile.get("snmp", {})
            modbus_keys = {register["key"] for register in modbus.get("registers", [])}
            snmp_keys = set(snmp.get("oids", {}).keys())
            key_precedence = profile.get("key_precedence", {})
            collisions = modbus_keys & snmp_keys
            unresolved = collisions - set(key_precedence.keys())
            assert not unresolved
