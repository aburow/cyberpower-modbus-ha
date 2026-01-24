# APC Smart-UPS Modbus Reference

This reference distills the register groups from `990-9840B-EN.pdf` into a quick lookup for the Home Assistant HACS 2026 integration. The absolute register numbers (column “Register Number”) follow Modicon conventions: `40001` corresponds to address `0` on the wire, the data is big-endian, and multi-register values must be combined before scaling. If a value lists a “Scale (Divide Reading By)”, divide the raw register output by that value to get the real unit.

## Status & Fault Overview
| Register | Modicon | Description | Notes |
| --- | --- | --- | --- |
| `40001` (`0x0000`, `UPSStatus_BF`, 2 registers) | State bits for Online, OnBattery, Bypass, OutputOff, Fault, InputBad, PendingOutputOff/On, Commanded, high-efficiency and maintenance modes, etc. | Treat it as a bitmask device state that drives most HA binary sensors. |
| `40003` (`0x0002`, `UPSStatusChangeCause_EN`) | Enumerated reason codes (0 = SystemInitialization … 30 = FailureBypassExpired). | Only trust it when `UPSStatus_BF` changes; otherwise ignore spurious transitions. |
| `40020` | `GeneralError_BF` faults not covered elsewhere (EEPROM, UI button, network warning). | Sticky bits—clear via `UPSCommand_BF` fault clear. |
| `40021` | `PowerSystemError_BF` (output overload, short, relay faults, etc.). | Useful for alert binary sensors on HA device page. |
| `40023` | `BatterySystemError_BF` (voltage sensing, charger, fan faults). | Maps directly to battery alarm indicators. |

## Sensor & Runtime Measurements
| Register | Modicon | Field | Unit/Scale | Description |
| --- | --- | --- | --- | --- |
| `40129` | `0x0080` | `RunTimeRemaining` (UINT32) | seconds | Max 65 535; compare relative to HA shutdown thresholds. |
| `40131` | `0x0082` | `StateOfCharge_Pct` | `%` (divide by 512) | Direct battery charge percent. |
| `40132` / `40133` | `0x0083` / `0x0084` | `Battery.Positive/Negative.VoltageDC` (INT16) | Volts (divide by 32) | Battery bus voltage channels (watch +/− separately). |
| `40136` | `0x0087` | `Battery.Temperature` (INT16) | °C (divide by 128) | Use for thermal sensor binary sensor/alert. |
| `40138–40140` | `0x0089–0x008B` | Output real/apparent power % | `%` (divide by 256) | Phase 1/2 output loading. |
| `40141–40144` | `0x008C–0x008F` | Output current/voltage | Amps (divide by 32) / Volts (divide by 64) | Hook into HA sensors for mains reporting. |
| `40145` | `0x0090` | `Output.Frequency` | Hz (divide by 128) | For power quality dashboards. |
| `40146` | `0x0091` | `Output.Energy` | Wh (scale 1) | Cumulative output energy. |

## Input & Bypass Measurements
| Register | Field | Notes |
| --- | --- | --- |
| `40148` | `Bypass.InputStatus_BF` | Same bit layout as `Input.InputStatus_BF`, includes Acceptable, VoltageTooLow/High, Distorted, Boost/Trim, FrequencyTooLow/High, Phase/Neutral alarms, and “PoweringLoad”. |
| `40149–40154` | `Bypass.VoltageAC`, `Bypass.Frequency`, `Input.InputStatus_BF`, `Input[0–2].VoltageAC` | Voltage values divide by 64, frequency by 128, status bits function like the bypass mirror but point to the main supply. |
| `40155` | `Efficiency_EN` | ENUM for efficiency percentage (divide by 128) plus special flags (InBypass, OnBattery, LoadTooLow, etc.). |
| `40156` | `MOG.TurnOffCountdown_EN` | Seconds remaining before the main outlet group shuts down (−1 = inactive, 0 = expired). |

## Outlet Status & Load-Shed
`MOG.OutletStatus_BF` (`40004` / `0x0003`, 2 registers) exposes mutually exclusive state bits (On, Off, Reboot, Shutdown, Sleep, Pending load shed, Off/On delays). Each `SOG[x].OutletStatus_BF` (`40007`, `0006`; `40010`, `0009`; `40013`, `000C`) mirrors the same bit layout. Combine these with `SOG[x].TurnOff/TurnOn/StayOff` timers (`41035–41047`) and `LoadShed` configuration registers (`41065–41074`) to expose detailed outlet automation states.

## Command and Control Registers
| Register | Description | Typical use |
| --- | --- | --- |
| `41537` (`UPSCommand_BF`) | Commands for factory reset, bypass control, fault clear, log reset. | Expose as HA services that write booleans to this bitfield. |
| `41539` (`OutletCommand_BF`) | Targeted cancel/on/off/shutdown/reboot commands plus modifiers (`UseOnDelay`, `ColdBootAllowed`) and source selectors (USB, RJ45, SmartSlot, InternalNetwork). | Trigger outlet automation sequences or emergency shutdowns. |
| `41541` | `SimpleSignalingCommand_BF` | Remote shutdown/on toggles from the simple signaling port. |
| `41542–41544` | `ReplaceBatteryTestCommand_BF`, `RunTimeCalibrationCommand_BF`, `UserInterfaceCommand_BF` | Control battery/test workflows and UI beeper/mute actions. |

## Strings & Diagnostics
| Register | Notes |
| --- | --- |
| `42049` (`ModbusMapID`) | Always `"12345678"`. Useful to verify you are talking to the expected map. |
| `42051` (`TestString`) / `42055–42062` | Fixed ASCII/number values that prove byte order; use when building regression tests for Modbus responses. |

## Identification Strings
| Register | Notes |
| --- | --- |
| `40517` (`0x0204`, `FWVersion_STR`, 8 registers) | UPS firmware version string (16 ASCII characters). Read-only. |
| `40533` (`0x0214`, `Model_STR`, 16 registers) | UPS model name (32 ASCII characters). |
| `40549` (`0x0224`, `SKU_STR`, 16 registers) | UPS SKU identifier. |
| `40565` (`0x0234`, `SerialNumber_STR`, 8 registers) | UPS serial number (16 ASCII characters). |
| `40596` (`0x0253`, `Battery.DateSetting`, 1 register) | Battery installation date (days since January 1, 2000). Read-write. |
| `40597` (`0x0254`, `Name_STR`, 8 registers) | User-assigned UPS name (16 ASCII characters). Read-write. |

## Using the Reference
- Always combine multiple registers before scaling. The PDF layout provides all 32-bit fields (e.g., `RunTimeRemaining`, `Output.Energy`) and enumerations.
- Read-only registers should not be written to unless explicitly marked (e.g., `MOG/SOG settings` and command registers).
- Document any additional addresses you add to Home Assistant in `docs/registers.md` or similar so the table stays up to date with the real hardware usage.

This document is a living summary. Update it when new data fields are discovered, and keep `990-9840B-EN.pdf` as the canonical backup reference.
