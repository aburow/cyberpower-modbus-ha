# Live APC UPS Polling Notes

- The `scripts/read_apc_registers.py` helper uses `pymodbus` (inside `.venv`) to read the key registers listed in `apc_modbus_registers.py` from `192.168.100.8:502` with Modbus unit ID `1`.
- Run it with `PYTHONPATH=. ./.venv/bin/python scripts/read_apc_registers.py` after activating the `.venv` created for `pymodbus`.

## Observed behavior (2024-XX-XX)

| Register | Result |
| --- | --- |
| `ups_status`, `ups_status_change`, `general_error`, `power_system_error`, `battery_system_error` | Successful read; values all `0` (no faults, standard status). |
| Remaining registers (runtime, SOC, battery volts/temps, output frequency/voltage) | Modbus `ExceptionResponse`: function code `131`, exception code `2` (illegal data address). |
| Identification registers (firmware/model/SKU/serial/battery install date/name) | Same `ExceptionResponse` (function code `131`, exception code `2`); the UPS currently blocks reads beyond the core status bits. |

> The UPS only allows the first few registers without additional configuration. The downstream integration must handle these responses gracefully (log and skip) and consider using alternative function codes or addresses when they become available.
