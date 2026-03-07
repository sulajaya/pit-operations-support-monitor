#!/usr/bin/env bash

set -uo pipefail

LOG_FILE="equipment_status.log"
REPORT_DIR="./reports"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
REPORT_FILE="$REPORT_DIR/shift_report_$TIMESTAMP.txt"

mkdir -p "$REPORT_DIR"

if [ ! -f "$LOG_FILE" ]; then
    echo "ERROR: Log file not found: $LOG_FILE"
    exit 1
fi

{
    echo "Pit Operations Shift Report"
    echo "Generated: $(date)"
    echo "Site: North Ridge Aggregate Pit"
    echo "------------------------------------------------------------"
    echo
    echo "1. Alarm Summary"
    echo "------------------------------------------------------------"
    echo "Total WARNING events: $(grep -c 'WARNING:' "$LOG_FILE")"
    echo "Total ALARM events:   $(grep -c 'ALARM:' "$LOG_FILE")"
    echo "Total DOWNTIME events: $(grep -c 'DOWNTIME:' "$LOG_FILE")"
    echo "Emergency stop events: $(grep -c 'Emergency stop active' "$LOG_FILE")"
    echo
    echo "2. Equipment-Specific Events"
    echo "------------------------------------------------------------"
    echo "CR-101 events: $(grep -c 'CR-101' "$LOG_FILE")"
    echo "CR-201 events: $(grep -c 'CR-201' "$LOG_FILE")"
    echo "CV-301 events: $(grep -c 'CV-301' "$LOG_FILE")"
    echo "CV-401 events: $(grep -c 'CV-401' "$LOG_FILE")"
    echo "PU-501 events: $(grep -c 'PU-501' "$LOG_FILE")"
    echo "GEN-601 events: $(grep -c 'GEN-601' "$LOG_FILE")"
    echo
    echo "3. Most Recent Alarms"
    echo "------------------------------------------------------------"
    grep 'ALARM:' "$LOG_FILE" | tail -10
    echo
    echo "4. Most Recent Warnings"
    echo "------------------------------------------------------------"
    grep 'WARNING:' "$LOG_FILE" | tail -10
    echo
    echo "5. Most Recent Downtime Events"
    echo "------------------------------------------------------------"
    grep 'DOWNTIME:' "$LOG_FILE" | tail -10
    echo
    echo "6. Recent Status Snapshots"
    echo "------------------------------------------------------------"
    grep 'STATUS |' "$LOG_FILE" | tail -10
    echo
    echo "7. Support Notes"
    echo "------------------------------------------------------------"
    echo "- Review repeated overload events on CR-101 / CR-201."
    echo "- Check CV-301 and CV-401 belt tracking if misalignment alarms repeat."
    echo "- Verify dust suppression flow when PU-501 alarm occurs."
    echo "- Refuel GEN-601 if low fuel warnings become frequent."
    echo "- Review hopper loading practices if high-high hopper alarms repeat."
    echo
} > "$REPORT_FILE"

echo "Shift report created: $REPORT_FILE"
