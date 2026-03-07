# System Architecture

## Overview

The pit operations support monitor simulates a PLC-controlled material handling site and a Linux server used for support monitoring.

## Architecture

```text
Field Equipment / PLC Tags
        |
        | simulated equipment states
        v
Linux Monitoring Server
        |
        +--> event logging
        +--> alarm detection
        +--> status snapshots
        +--> shift reports
```

## Equipment Flow

1. Primary jaw crusher runs
2. Secondary cone crusher runs if upstream equipment healthy
3. Transfer conveyor runs if crushers are active
4. Stacker runs if transfer conveyor active
5. Dust suppression pump runs when crushing is active
6. Generator status monitored for fuel and power availability

## Linux Server Functions

- polls simulated equipment values
- evaluates thresholds
- logs status lines
- logs alarms
- tracks equipment state changes
- creates support-oriented shift reports

## Operational Focus

This project is designed around:
- field support visibility
- equipment fault awareness
- basic production support reporting
- Linux automation in industrial support environments
