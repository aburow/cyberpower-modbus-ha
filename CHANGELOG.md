# Changelog

## 1.1.1-dev.2
- Add shared `sensor_availability_unified.py` template for dependency-free, cross-project default availability behavior.
- Keep full block polling unchanged while setting non-core entities to disabled-by-default in the Entity Registry.
- Default-enable a minimal CyberPower core set (runtime, battery state of charge, input/output voltage, output load, online and on-battery state).

## 1.1.1-dev.1
- Replace local icon mappings with the shared `icons_unified.py` canonical module used across UPS projects.
- Keep deterministic `mdi:` icon resolution through shared `resolve_sensor_icon` and `resolve_binary_sensor_icon`.

## 1.1.0
- Add deterministic `mdi:` icon mapping for sensor and binary sensor entities.
- Apply explicit icon assignment at entity construction to avoid frontend fallback icon heuristics.
- Add local pre-commit lint hooks for `ruff`, `semgrep`, and `grain`.

## 1.0.0
Promote to 1.0.0 release.

## 0.4.0
- Serialize Modbus I/O per device endpoint with a shared lock.
- Connect and close per update cycle; rebuild client on socket errors.
- Add backoff on repeated failures and pacing delays for slower devices.
- Move SNMP metadata/type detection off the event loop.
- Improve logging context, timings, and debug visibility.
- Add architecture diagram and debug log guidance in README.

## 0.1.1
- Split single-phase Modbus block reads to stay within device limits.
- Refined binary sensor classes for clearer UI text.
- Clarified holding-register-only support in docs.

## 0.1.0
- Initial CyberPower UPS Modbus integration based on the APC Modbus codebase.
- Single-phase Modbus register mapping validated against a live device.
- Three-phase mapping included but untested/experimental.
