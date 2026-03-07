# Pit Operations PLC Logic Overview

This document describes the PLC-style operational logic used by the pit operations support monitor.

## Equipment List

| Equipment ID | Description | Type |
|---|---|---|
| CR-101 | Primary Jaw Crusher | Crusher |
| CR-201 | Secondary Cone Crusher | Crusher |
| CV-301 | Main Transfer Conveyor | Conveyor |
| CV-401 | Radial Stacker Conveyor | Conveyor |
| PU-501 | Dust Suppression Water Pump | Pump |
| GEN-601 | Site Diesel Generator | Generator |

## Main Operational Logic

## 1. Primary Crusher Run Permissive

Primary Jaw Crusher `CR-101` may run only when:

- Emergency stop is clear
- Crusher overload is clear
- Bearing temperature is below 95°C
- Feed hopper level is below 95%
- Generator available or utility power available

### Logic Concept

```text
IF E_STOP = 0
AND CR-101_OVERLOAD = 0
AND CR-101_BRG_TEMP < 95
AND HOPPER_LEVEL < 95
AND POWER_AVAILABLE = 1
THEN CR-101_RUN_PERMISSIVE = 1
```

---

## 2. Secondary Crusher Run Permissive

Secondary Cone Crusher `CR-201` may run only when:

- Primary crusher running
- Emergency stop clear
- Overload clear
- Bearing temperature below 100°C

```text
IF CR-101_RUN = 1
AND E_STOP = 0
AND CR-201_OVERLOAD = 0
AND CR-201_BRG_TEMP < 100
THEN CR-201_RUN_PERMISSIVE = 1
```

---

## 3. Transfer Conveyor Run Permissive

Main Transfer Conveyor `CV-301` may run only when:

- Primary crusher running
- Secondary crusher running
- No conveyor motor overload
- No emergency stop
- Belt misalignment not active

```text
IF CR-101_RUN = 1
AND CR-201_RUN = 1
AND CV-301_OVERLOAD = 0
AND CV-301_MISALIGN = 0
AND E_STOP = 0
THEN CV-301_RUN_PERMISSIVE = 1
```

---

## 4. Stacker Conveyor Run Permissive

Stacker conveyor runs only when transfer conveyor is running and no local faults exist.

```text
IF CV-301_RUN = 1
AND CV-401_OVERLOAD = 0
AND CV-401_MISALIGN = 0
AND E_STOP = 0
THEN CV-401_RUN_PERMISSIVE = 1
```

---

## 5. Dust Suppression Pump Logic

Dust suppression pump `PU-501` should run whenever either crusher is running.

```text
IF CR-101_RUN = 1
OR CR-201_RUN = 1
THEN PU-501_RUN_CMD = 1
```

Alarm if flow not detected within 10 seconds after pump start command.

---

## 6. Generator Low Fuel Alarm

Generator alarm occurs when fuel level falls below 25%.

```text
IF GEN-601_FUEL_LEVEL < 25
THEN GEN-601_LOW_FUEL_ALARM = 1
```

Critical alarm below 15%.

---

## 7. Emergency Stop Logic

Any active E-stop forces all run outputs off.

```text
IF E_STOP = 1
THEN
CR-101_RUN = 0
CR-201_RUN = 0
CV-301_RUN = 0
CV-401_RUN = 0
PU-501_RUN = 0
```

---

## 8. Downtime Tracking Rule

Downtime event begins when plant is in production mode and any critical equipment is unexpectedly stopped.

Critical equipment:
- CR-101
- CR-201
- CV-301

```text
IF PRODUCTION_MODE = 1
AND (CR-101_RUN = 0 OR CR-201_RUN = 0 OR CV-301_RUN = 0)
AND NO_PLANNED_STOP = 1
THEN DOWNTIME_ACTIVE = 1
```

## Key Thresholds

| Signal | Warning | Alarm |
|---|---|---|
| CR-101 Bearing Temp | 90°C | 95°C |
| CR-201 Bearing Temp | 95°C | 100°C |
| CV-301 Motor Current | 100 A | 110 A |
| CV-401 Motor Current | 75 A | 85 A |
| Hopper Level | 85% | 90% |
| Generator Fuel | 25% | 15% |

## Support Intent

This logic is intended to support:
- operations visibility
- maintenance troubleshooting
- shift reporting
- alarm logging
- Linux-side monitoring integration
