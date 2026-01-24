# APC Smart-UPS Modbus Reference (990-5702A-EN)

This reference summarizes the Modbus register map for Smart-UPS models **excluding** SMT/SMX/SURTD/SRT (e.g., Smart-UPS 700 and RT 2000 RM XL) as documented in `990-5702A-EN.pdf`. Registers are 16-bit, big-endian, and addressed from `0` on the wire (Modicon `40001`). Strings use **one ASCII character per register** in this map.

## Status Words
| Register | Field | Notes |
| --- | --- | --- |
| `40001` (`0x0000`) | `Status Word 0` | Bypass/turn-on state bits. |
| `40002` (`0x0001`) | `Status Word 1` | Shutdown/relay fault/charger fault/over-temp bits. |
| `40003` (`0x0002`) | `Status Word 2` | Inverter/relay fault bits. |
| `40004` (`0x0003`) | `Status Word 3` | On line/on battery/overload/low battery/replace battery bits. |

## Core Measurements
| Register | Field | Units |
| --- | --- | --- |
| `40006` (`0x0005`) | `% Battery State of Charge` | % |
| `40007` (`0x0006`) | `Runtime Remaining` | minutes |
| `40008` (`0x0007`) | `Battery Voltage` | V |
| `40010` (`0x0009`) | `Amps Drawn by Load` | A |
| `40014` (`0x000D`) | `Nominal Output Voltage` | V |
| `40015` (`0x000E`) | `Actual Output Voltage` | V |
| `40016` (`0x000F`) | `Maximum Input Voltage Since Last Reading` | V |
| `40017` (`0x0010`) | `Minimum Input Voltage Since Last Reading` | V |
| `40018` (`0x0011`) | `Input Voltage` | V |
| `40019` (`0x0012`) | `Input Frequency` | Hz |
| `40027` (`0x001A`) | `Minimum Return Battery Capacity` | % |
| `40030` (`0x001D`) | `Nominal Output Voltage (setting)` | V |
| `40032` (`0x001F`) | `Low Battery Duration` | minutes |
| `40078` (`0x004D`) | `Battery Current` | A (signed) |

## Identification
| Register | Field | Notes |
| --- | --- | --- |
| `40035–40042` (`0x0022–0x0029`) | `UPS ID Character #1–#8` | 8 registers, one ASCII character each; concatenate for the UPS ID string. |

## Using This Map
- Reads beyond supported registers return an **illegal data address** exception; the integration should log and skip unsupported registers.
- If you add more fields (e.g., phase A/B/C measurements), list them in `apc_modbus_registers.py` and surface them in the HA sensor list.
