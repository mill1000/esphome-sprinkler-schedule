# esphome-sprinkler-schedule

An external ESPHome component that adds scheduling capabilities to the existing [sprinkler controller](https://esphome.io/components/sprinkler.html) component. Supports defining one or more schedules with independent start times, cycle frequency, and cycle repetitions. Each schedule can be configured to run specific valves with per-vavle run durations. Each schedule exposes a suite of control buttons, status sensors and has a configurable conflict-resolution method.

## Features

- Supports one or more schedules for a sprinkler controller component.
- Each schedule has independent:
  - Schedule start time as a Home Assistant time entity
  - Schedule frequency (days between runs) and cycle repetitions (cycles per run)
  - Conflict resolution method
  - Sensors
    - Last run timestamp
    - Next run timestamp
    - Estimated duration
  - Valve configuration
      - Enable switch
      - Run duration
  - Control buttons:
    - Run Now - Run the schedule immediately and recalculate the next scheduled run
    - Manual Cycle - Run the schedule immediately without updating the next scheduled run
    - Run Tomorrow - Run the schedule tomorrow
    - Delay - Delay the scheduled run by 1 day
    - Reset - Reset and recalculate the next scheduled run
---

## Prerequisites

* The component must added to your node.
  ```yaml
  external_components:
    - source: github://mill1000/esphome-sprinkler-schedule@main
      components: [sprinkler_schedule]
  ```
* A [time component](https://esphome.io/components/#time-components) must be configured.

## Schedule Configuration

**Note:**

All buttons, numbers, sensors, switches and time entities are standard ESPHome components. They can de defined as simple names, or full configurations can be provided.

e.g.
```yaml
enable_switch: Schedule A
# OR
enable_switch:
  name: Schedule A
  id: schedule_a_enable_switch
```

### Top-Level Configuration

| Key                   | Type                              | Required | Default | Description
| --------------------- | --------------------------------- | -------- | ------- | ---------------------------
| `id`                  | string                            | Y        | N/A     | Unique ID of the schedule instance.
| `controller_id`       | id                                | Y        | N/A     | The ID of the sprinkler controller component to run the schedule on.
| `time_id`             | id                                | N        | Auto    | The ID of the time entity. Automatically set to the ID of a time component if only a single one is defined.
| `start_time`          | string or time object             | Y        | N/A     | Schedule start time of day.
| `conflict_resolution` | string: either `skip` or `queue`  | N        | `skip`  | Conflict resolution method when the controller is busy. `skip` ignores the run, and reschedules the next run. `queue` reschedules the run after the controller's current operation completes.
| `frequency_number`    | string or number object           | Y        | N/A     | Days between scheduled runs.
| `repetitions_number`  | string or number object           | N        | 1       | Number of cycle repetitions per run.
| `valves`              | list of valve objects             | Y        | N/A     | Valve configurations for the schedule.

#### Sensors
All sensors are optional.

| Key                         | Type                    | Description
| --------------------------- | ----------------------- | ---------------------------
| `last_run_sensor`           | string or sensor object | Timestamp of the last scheduled run.
| `next_run_sensor`           | string or sensor object | Timestamp of the next scheduled run.
| `estimated_duration_sensor` | string or sensor object | Total estimated duration for the run.

#### Buttons
All buttons are optional.

| Key                   | Type                    | Description
| --------------------- | ----------------------- | ---------------------------
| `run_now_button`      | string or button object | Immediately start a run and recalculate next run.
| `manual_run_button`   | string or button object | Immediately start a run without recalculating next run.
| `run_tomorrow_button` | string or button object | Schedule run for tomorrow.
| `delay_button`        | string or button object | Delay next run by 1 day.
| `reset_button`        | string or button object | Reset and recalculate next run.

### Valves

Configures valves for each schedule. The number and order of the valves must match the controller’s `valves` list.

| Key                    | Type                    | Required | Description
| ---------------------- | ----------------------- | -------- | ---------------------------
| `enable_switch`        | string or switch object | N        | Enable this valve in the schedule.
| `run_duration_number`  | string or number object | Y        | The valves run duration.


## Example Configuration

A minimal sample is given below. See this [example](example.yaml) for a more complete configuration.

```yaml
external_components:
  - source: github://mill1000/esphome-sprinkler-schedule@main
    components: [sprinkler_schedule]

time:
  - platform: homeassistant
    id: homeassistant_time
    timezone: America/Denver

# Sprinkler controller
sprinkler:
  - id: sprinkler_controller
    main_switch:
      name: Sprinklers
      id: sprinklers_main_switch
      internal: true
    auto_advance_switch:
      name: Zone Auto Advance
    standby_switch:
      name: Standby
    repeat_number:
      name: Cycle Repeat
      id: sprinkler_repeat
      internal: true
    valve_overlap: 2s
    valves:
      - valve_switch_id: relay_0
        enable_switch:
          name: Zone 1 Enable
        run_duration_number:
          name: Zone 1 Duration
          unit_of_measurement: min
          min_value: 0
          max_value: 30
          initial_value: 20
      - valve_switch_id: relay_1
        enable_switch:
          name: Zone 2 Enable
        run_duration_number:
          name: Zone 2 Duration
          unit_of_measurement: min
          min_value: 0
          max_value: 30
          initial_value: 20
      - valve_switch_id: relay_2
        enable_switch:
          name: Zone 3 Enable
        run_duration_number:
          name: Zone 3 Duration
          unit_of_measurement: min
          min_value: 0
          max_value: 30
          initial_value: 20

# Configure a single schedule
sprinkler_schedule:
  - id: schedule_a
    controller_id: sprinkler_controller
    time_id: homeassistant_time
    start_time:
      name: Schedule A Start
      initial_value: "06:00:00"

    enable_switch: Schedule A Enable
    frequency_number: Schedule A Frequency
    repetitions_number: Schedule A Repetitions

    last_run_sensor: Schedule A Last Run
    next_run_sensor: Schedule A Next Run
    estimated_duration_sensor: Schedule A Duration

    run_now_button: Schedule A Run Now
    manual_run_button: Schedule A Manual Cycle
    run_tomorrow_button: Schedule A Tomorrow
    delay_button: Schedule A Delay
    reset_button: Schedule A Reset

    valves:
      - enable_switch: Schedule A Zone 1 Enable
        run_duration_number:
          name: Schedule A Zone 1 Duration
          unit_of_measurement: min
          initial_value: 20
      - enable_switch: Schedule A Zone 2 Enable
        run_duration_number:
          name: Schedule A Zone 2 Duration
          unit_of_measurement: min
          initial_value: 20
      - enable_switch: Schedule A Zone 3 Enable
        run_duration_number:
          name: Schedule A Zone 3 Duration
          unit_of_measurement: min
          initial_value: 20
```