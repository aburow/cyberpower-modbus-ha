# Bug #1: Output load scaling mismatch

## Summary
The CyberPower Modbus integration had a load percentage scaling mismatch that caused the reported output load to be under-counted on some device families.

## Root cause
- Single-phase devices exposed `output_load_percent` at register `0x3027` as a whole percent value.
- Three-phase devices exposed `load_percent_phase_a/b/c` at registers `0x002E-0x0030` as `0.1%` values.
- The integration initially treated both families as if they should be scaled the same way, which made the single-phase load read `10x` too low.

## Documentation evidence
- Single-phase manual: `3027` is labeled `Output load percent` with no fractional scale shown.
- Three-phase manual: `Load percent Phase A/B/C` is explicitly labeled `0.1%`.

## Fix applied
- Single-phase `output_load_percent` now uses `scale: 1`.
- Three-phase `load_percent_phase_a/b/c` remain `scale: 10`.

## Validation
- Added a regression test that asserts the split scale behavior directly from the register definitions.
- Verified with `./.venv/bin/pytest -q tests/test_unified_contract.py`.

## Why this matters
This bug is easy to reintroduce if future refactors normalize load-related registers without preserving the per-device documentation split. It also affects downstream projects that consume these entities and assume the load value is already correctly scaled.
