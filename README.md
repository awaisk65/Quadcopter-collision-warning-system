# Drone Proximity Warning and Auto-Hold

This project provides a proximity monitoring system for two drones using MAVLink (via pymavlink).  
It continuously reads GPS and altitude data from both drones, computes horizontal and vertical distances, and raises warnings when thresholds are breached.

If both the horizontal distance (H) and vertical distance (V) fall below defined thresholds, the system automatically requests both drones to switch to Hold/Loiter mode, preventing further approach.

## Features

- Connects to two MAVLink-enabled drones via UDP or serial.
- Reads:
  - Global GPS position (`GPS_RAW_INT`)
  - Local position and altitude (`LOCAL_POSITION_NED`)
- Computes:
  - Horizontal distance using haversine formula
  - Vertical distance from local NED altitude
- Triggers proximity warnings:
  - **H ≤ Hthresh and V ≤ Vthresh → WARNING**
- On WARNING:
  - Requests both drones to switch to Hold/Loiter mode
- Adjustable thresholds and connection strings via CLI arguments.

## Requirements

- Python 3.7+
- `pymavlink`

## Install Dependencies

- pip install pymavlink


## Usage

## Default Mode

- Runs with built-in defaults:

- Drone 1: udp:127.0.0.1:14540

- Drone 2: udp:127.0.0.1:14541

- Horizontal threshold: 15 m

- Vertical threshold: 5 m

python proximity_warning.py

## Custom Mode

Manually provide MAVLink connection strings and thresholds:

python proximity_warning.py --conn1 <conn1_str> --conn2 <conn2_str> --hthresh <meters> --vthresh <meters>

## Example:

python proximity_warning.py \
  --conn1 udp:127.0.0.1:14540 \
  --conn2 udp:127.0.0.1:14541 \
  --hthresh 20 \
  --vthresh 10

## Mode Change Behavior

When both drones are within thresholds:

- A [WARNING] message is printed.

- The script sends a set_mode_send() command to switch drones into Loiter/Hold mode:

  - PX4: Loiter (5)

  - ArduPilot: Loiter (5)

- This causes both drones to stop and hold their positions at the point of warning.

## Example Output
[INFO] Drone 1 and Drone 2 close (H: 16.50 m), vertical separation safe
[WARNING] Drone 1 and Drone 2 too close! H: 12.34 m, V: 3.21 m
[ACTION] Requested Drone 1 to switch to hold mode.
[ACTION] Requested Drone 2 to switch to hold mode.
[INFO] Safe. H: 22.45 m, V: 7.12 m

## License

This project is released under the MIT License.
Free to use, modify, and distribute with attribution.