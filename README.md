# Pit Operations Support Monitor

A Linux-based pit operations support monitoring project designed to simulate field equipment monitoring for aggregate, quarry, or material handling operations.

This project combines PLC-style equipment logic concepts with Linux server-side monitoring, logging, alarm detection, and shift reporting.

## Overview

The system simulates operational support for a pit site with the following equipment:

- Primary Jaw Crusher
- Secondary Cone Crusher
- Main Transfer Conveyor
- Stacker Conveyor
- Dust Suppression Water Pump
- Diesel Generator
- Feed Hopper Level Monitoring
- Emergency Stop Circuit

The Linux server monitors equipment states, logs alarms, tracks downtime conditions, and generates shift support reports.

## Operational Scenario

This project is intended to reflect a field support workflow where operations or maintenance staff need to know:

- Is the primary crusher running?
- Is the transfer conveyor tripped?
- Did a motor overload occur?
- Is the dust suppression pump active?
- Is the hopper level too high?
- Did generator fuel drop below threshold?
- How many alarms occurred during the shift?

## Repository Structure

- `plc_logic/pit_operations_logic.md`  
  PLC-style control and alarm logic description

- `linux_server/pit_monitor.py`  
  Main monitoring script

- `linux_server/equipment_config.json`  
  Equipment definitions, thresholds, and tag names

- `linux_server/shift_report.sh`  
  Shift report generation script

- `linux_server/sample_equipment_status.log`  
  Example output log

- `docs/architecture.md`  
  System architecture and monitoring flow

## Equipment Monitored

### Primary Equipment
- Primary Jaw Crusher `CR-101`
- Secondary Cone Crusher `CR-201`
- Main Transfer Conveyor `CV-301`
- Radial Stacker Conveyor `CV-401`

### Support Equipment
- Dust Suppression Pump `PU-501`
- Site Diesel Generator `GEN-601`

### Process / Safety Signals
- Feed Hopper Level
- Conveyor Motor Current
- Crusher Bearing Temperature
- Emergency Stop
- Generator Fuel Level

## Example Alarm Conditions

- Jaw crusher bearing temperature above 95°C
- Transfer conveyor motor current above 110 A
- Hopper level above 90%
- Generator fuel below 25%
- Emergency stop active
- Crusher overload trip
- Conveyor stopped while plant is in production mode

## Technologies Used

- Python 3
- Bash
- Linux
- JSON configuration
- PLC / controls logic concepts
- Operational support reporting

## How to Run

### Start the monitor

```bash
cd linux_server
python3 pit_monitor.py
```

### Generate a shift report

```bash
chmod +x shift_report.sh
./shift_report.sh
```

## Example Use Cases

- Industrial IT support
- Operations support tooling
- Mining / pit equipment visibility
- Controls support simulation
- Linux monitoring projects for GitHub portfolio

## Skills Demonstrated

- Linux server scripting
- Python automation
- Bash reporting
- Equipment alarm monitoring
- Operational support tooling
- PLC-style control logic integration
- Shift event reporting

## Resume Bullet Example

Developed a Linux-based pit operations support monitoring solution simulating crusher, conveyor, pump, and generator equipment states with alarm logging, downtime visibility, and shift reporting using Python, Bash, and PLC-style logic concepts.

## Author

Sula Jayasekara
