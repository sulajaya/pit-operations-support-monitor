#!/usr/bin/env python3

import json
import os
import random
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "equipment_config.json")
LOG_FILE = os.path.join(BASE_DIR, "equipment_status.log")
POLL_INTERVAL_SECONDS = 5


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def log_event(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def random_variation(base, spread, min_value=None, max_value=None):
    value = base + random.uniform(-spread, spread)
    if min_value is not None:
        value = max(min_value, value)
    if max_value is not None:
        value = min(max_value, value)
    return round(value, 1)


def simulate_site_state(config):
    production_mode = config["site"]["production_mode"]
    emergency_stop = random.choices([0, 1], weights=[98, 2], k=1)[0]
    utility_power_available = random.choices([1, 0], weights=[97, 3], k=1)[0]

    generator_running = 0 if utility_power_available == 1 else 1
    generator_fuel = random_variation(42, 18, 8, 80)
    hopper_level = random_variation(72, 20, 20, 98)

    cr101_bearing_temp = random_variation(88, 10, 65, 104)
    cr201_bearing_temp = random_variation(92, 10, 70, 108)
    cr101_overload = random.choices([0, 1], weights=[94, 6], k=1)[0]
    cr201_overload = random.choices([0, 1], weights=[95, 5], k=1)[0]

    power_available = 1 if (utility_power_available == 1 or generator_running == 1) else 0

    cr101_run = 1
    if (
        emergency_stop == 1
        or cr101_overload == 1
        or cr101_bearing_temp >= 95
        or hopper_level >= 95
        or power_available == 0
    ):
        cr101_run = 0

    cr201_run = 1
    if (
        cr101_run == 0
        or emergency_stop == 1
        or cr201_overload == 1
        or cr201_bearing_temp >= 100
    ):
        cr201_run = 0

    cv301_motor_current = random_variation(96, 20, 40, 125)
    cv401_motor_current = random_variation(68, 18, 20, 95)
    cv301_overload = 1 if cv301_motor_current >= 110 else 0
    cv401_overload = 1 if cv401_motor_current >= 85 else 0
    cv301_misalignment = random.choices([0, 1], weights=[97, 3], k=1)[0]
    cv401_misalignment = random.choices([0, 1], weights=[98, 2], k=1)[0]

    cv301_run = 1
    if (
        cr101_run == 0
        or cr201_run == 0
        or emergency_stop == 1
        or cv301_overload == 1
        or cv301_misalignment == 1
    ):
        cv301_run = 0

    cv401_run = 1
    if (
        cv301_run == 0
        or emergency_stop == 1
        or cv401_overload == 1
        or cv401_misalignment == 1
    ):
        cv401_run = 0

    pu501_run_command = 1 if (cr101_run == 1 or cr201_run == 1) else 0
    pu501_flow_ok = random.choices([1, 0], weights=[95, 5], k=1)[0] if pu501_run_command == 1 else 0
    pu501_run = 1 if (pu501_run_command == 1 and pu501_flow_ok == 1) else 0

    return {
        "production_mode": production_mode,
        "emergency_stop": emergency_stop,
        "utility_power_available": utility_power_available,
        "power_available": power_available,
        "generator_running": generator_running,
        "generator_fuel_percent": generator_fuel,
        "hopper_level_percent": hopper_level,
        "CR-101": {
            "run": cr101_run,
            "overload": cr101_overload,
            "bearing_temp_c": cr101_bearing_temp,
        },
        "CR-201": {
            "run": cr201_run,
            "overload": cr201_overload,
            "bearing_temp_c": cr201_bearing_temp,
        },
        "CV-301": {
            "run": cv301_run,
            "motor_current_a": cv301_motor_current,
            "overload": cv301_overload,
            "misalignment": cv301_misalignment,
        },
        "CV-401": {
            "run": cv401_run,
            "motor_current_a": cv401_motor_current,
            "overload": cv401_overload,
            "misalignment": cv401_misalignment,
        },
        "PU-501": {
            "run_command": pu501_run_command,
            "run": pu501_run,
            "flow_ok": pu501_flow_ok,
        },
    }


def evaluate_alarms(config, state):
    alarms = []
    process_limits = config["process_tags"]
    hopper_warn = process_limits["hopper_high_warning_percent"]
    hopper_alarm = process_limits["hopper_high_alarm_percent"]

    if state["emergency_stop"] == 1:
        alarms.append("CRITICAL: Emergency stop active")

    hopper_level = state["hopper_level_percent"]
    if hopper_level >= hopper_alarm:
        alarms.append(f"ALARM: Feed hopper high-high level at {hopper_level}%")
    elif hopper_level >= hopper_warn:
        alarms.append(f"WARNING: Feed hopper high level at {hopper_level}%")

    for eq in config["equipment"]:
        eq_id = eq["id"]

        if eq_id == "CR-101":
            temp = state["CR-101"]["bearing_temp_c"]
            if temp >= eq["bearing_temp_alarm_c"]:
                alarms.append(f"ALARM: {eq_id} {eq['name']} bearing temperature high at {temp}C")
            elif temp >= eq["bearing_temp_warning_c"]:
                alarms.append(f"WARNING: {eq_id} {eq['name']} bearing temperature elevated at {temp}C")
            if state["CR-101"]["overload"] == 1:
                alarms.append(f"ALARM: {eq_id} {eq['name']} overload trip active")

        elif eq_id == "CR-201":
            temp = state["CR-201"]["bearing_temp_c"]
            if temp >= eq["bearing_temp_alarm_c"]:
                alarms.append(f"ALARM: {eq_id} {eq['name']} bearing temperature high at {temp}C")
            elif temp >= eq["bearing_temp_warning_c"]:
                alarms.append(f"WARNING: {eq_id} {eq['name']} bearing temperature elevated at {temp}C")
            if state["CR-201"]["overload"] == 1:
                alarms.append(f"ALARM: {eq_id} {eq['name']} overload trip active")

        elif eq_id == "CV-301":
            amps = state["CV-301"]["motor_current_a"]
            if amps >= eq["motor_current_alarm_a"]:
                alarms.append(f"ALARM: {eq_id} {eq['name']} motor current high at {amps} A")
            elif amps >= eq["motor_current_warning_a"]:
                alarms.append(f"WARNING: {eq_id} {eq['name']} motor current elevated at {amps} A")
            if state["CV-301"]["misalignment"] == 1:
                alarms.append(f"ALARM: {eq_id} {eq['name']} belt misalignment detected")

        elif eq_id == "CV-401":
            amps = state["CV-401"]["motor_current_a"]
            if amps >= eq["motor_current_alarm_a"]:
                alarms.append(f"ALARM: {eq_id} {eq['name']} motor current high at {amps} A")
            elif amps >= eq["motor_current_warning_a"]:
                alarms.append(f"WARNING: {eq_id} {eq['name']} motor current elevated at {amps} A")
            if state["CV-401"]["misalignment"] == 1:
                alarms.append(f"ALARM: {eq_id} {eq['name']} belt misalignment detected")

        elif eq_id == "GEN-601":
            fuel = state["generator_fuel_percent"]
            if fuel < eq["fuel_alarm_percent"]:
                alarms.append(f"ALARM: {eq_id} {eq['name']} fuel critically low at {fuel}%")
            elif fuel < eq["fuel_warning_percent"]:
                alarms.append(f"WARNING: {eq_id} {eq['name']} fuel low at {fuel}%")

    if state["PU-501"]["run_command"] == 1 and state["PU-501"]["flow_ok"] == 0:
        alarms.append("ALARM: PU-501 Dust Suppression Water Pump command active but no flow detected")

    if state["production_mode"]:
        if state["CR-101"]["run"] == 0:
            alarms.append("DOWNTIME: CR-101 Primary Jaw Crusher unavailable during production mode")
        if state["CR-201"]["run"] == 0:
            alarms.append("DOWNTIME: CR-201 Secondary Cone Crusher unavailable during production mode")
        if state["CV-301"]["run"] == 0:
            alarms.append("DOWNTIME: CV-301 Main Transfer Conveyor unavailable during production mode")

    return alarms


def build_status_line(state):
    return (
        f"STATUS | "
        f"EStop={state['emergency_stop']} | "
        f"PowerAvail={state['power_available']} | "
        f"Hopper={state['hopper_level_percent']}% | "
        f"CR-101 Run={state['CR-101']['run']} Temp={state['CR-101']['bearing_temp_c']}C O/L={state['CR-101']['overload']} | "
        f"CR-201 Run={state['CR-201']['run']} Temp={state['CR-201']['bearing_temp_c']}C O/L={state['CR-201']['overload']} | "
        f"CV-301 Run={state['CV-301']['run']} Current={state['CV-301']['motor_current_a']}A Misalign={state['CV-301']['misalignment']} | "
        f"CV-401 Run={state['CV-401']['run']} Current={state['CV-401']['motor_current_a']}A Misalign={state['CV-401']['misalignment']} | "
        f"PU-501 Run={state['PU-501']['run']} FlowOK={state['PU-501']['flow_ok']} | "
        f"GEN-601 Run={state['generator_running']} Fuel={state['generator_fuel_percent']}%"
    )


def main():
    config = load_config()
    log_event("============================================================")
    log_event(f"Pit operations monitor started for site: {config['site']['name']}")
    log_event(f"Shift: {config['site']['shift_name']}")
    log_event("Monitoring equipment: CR-101, CR-201, CV-301, CV-401, PU-501, GEN-601")
    log_event("============================================================")
    while True:
        state = simulate_site_state(config)
        log_event(build_status_line(state))
        for alarm in evaluate_alarms(config, state):
            log_event(alarm)
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
