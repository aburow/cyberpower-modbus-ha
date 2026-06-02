# Changelog

## 1.1.1-dev.9
- Fix single-phase output load scaling so whole-percent Modbus readings are no longer divided by 10.
- Add CyberPower enterprise SNMP telemetry for single-phase output power (`W`) and output energy (`kWh`) on the normal coordinator poll cycle.
- Keep SNMP telemetry best-effort with short per-cycle polling (`timeout=1`, `retries=1`) so SNMP failures do not affect Modbus refresh success.
- Add Home Assistant-compatible power and energy sensor metadata using current unit enums and sensor device/state classes.

## 1.1.1-dev.8
- Add `sensor_catalog_unified.py` as an import-free, static, exhaustive per-profile sensor catalog for downstream selector/picklist consumers.
- Preserve existing unified contract/profile exposure semantics by keeping catalog completeness separate from default-enabled/source-key contract curation.

## 1.1.1-dev.7
- Add info-level coordinator update cycle boundary logs (`Starting update cycle`, `Update cycle complete in ...s`).
- Add info-level poll timing breakdown logs (`total`, `lock_wait`, `modbus`, `connect`, `block_reads`, `individual_reads`, `close`, `reconnects`) for runtime hotspot isolation.
- Update README troubleshooting guidance with the new timing instrumentation log lines.

## 1.1.1-dev.6
- Add `capability_profile_unified.py` with `contract_version`/`CONTRACT_VERSION` set to `2.0.0` and modbus v2 capability profiles (poll groups + block optimization hints).
- Align unified interface contracts for bridge runtime loading (`icons_unified.py`, `sensor_availability_unified.py`, `device_info_unified.py`) with never-raise behavior.
- Add interop contract tests for plain-Python imports, runtime interface safety, canonical device-info output constraints, and capability profile validation rules.

## 1.1.1-dev.5
- Add `device_info_unified.py` with `resolve_device_info(values, source)` for ups-docker-ha bridge compatibility.
- Add `CONTRACT_VERSION = "1.0"` and canonical-key-only normalization behavior for bridge-consumable device metadata.
- Add acceptance tests for import safety, key/value constraints, malformed input handling, and deterministic mapping behavior.

## 1.1.1-dev.4
- Add a `Set or Reset Monitors` button entity to apply monitoring defaults in bulk per UPS entry.
- Button action enables core/default entities and disables non-core entities through the HA Entity Registry.
- Keep full block polling and device detection logic unchanged.

## 1.1.1-dev.3
- Add `entity_enabled_default(local_entity_key: str) -> bool` to `sensor_availability_unified.py` for ups-docker-ha compatibility.
- Keep module import-safe outside Home Assistant and preserve existing in-integration availability behavior.

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
