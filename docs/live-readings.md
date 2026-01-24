# Live APC UPS Polling Notes

The helper script `scripts/read_apc_registers.py` polls registers defined in `apc_modbus_registers.py` using the **990-5702A-EN** register map (Smart-UPS excluding SMT/SMX/SURTD/SRT). Strings are one character per register.

## Usage

```
PYTHONPATH=. ./.venv/bin/python scripts/read_apc_registers.py <host> --function holding
```

## Observed behavior (AP9631, unit 1)

| Device | Result |
| --- | --- |
| `192.168.100.7` (Smart-UPS RT 2000 RM XL) | Status words read as `0`; all other registers return `ExceptionResponse` (function code `131`, exception code `2`). |
| `192.168.100.8` (Smart-UPS 700) | Same behavior as above: status words read, remaining registers return illegal data address. |

These devices currently allow reads for the first status registers only. The integration should handle the rest as unsupported for now.
