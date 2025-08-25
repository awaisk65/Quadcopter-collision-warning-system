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
- pymavlink

## Install Dependencies

- `pip install pymavlink`


## Usage

### Default Mode

If you want to run with default settings:

`python proximity_warning.py`

- This Uses:

  - Drone 1: `udp:127.0.0.1:14540`

  - Drone 2: `udp:127.0.0.1:14541`

  - Horizontal threshold: 15 m

  - Vertical threshold: 5 m

## Custom Mode

Manually provide connection strings and thresholds via CLI arguments:

`python proximity_warning.py --conn1 <conn1_str> --conn2 <conn2_str> --hthresh <meters> --vthresh <meters>`

## Example:

`python proximity_warning.py --conn1 udp:127.0.0.1:14540 --conn2 udp:127.0.0.1:14541 --hthresh 20 --vthresh 10`

## Mode Change Behavior

When both drones are within thresholds:

- A `[WARNING]` message is printed.

- The script sends a set_mode_send() command to switch drones into Loiter/Hold mode:

  - PX4: Loiter (5)

  - ArduPilot: Loiter (5)

- This causes both drones to stop and hold their positions at the point of warning.

## Proximity Warning Diagram

![Drone Proximity Warning](images/diagram.png)


## Example Output

## Safe Case:
`[INFO] Safe. H: 22.45 m, V: 7.12 m` <br>

## Close but safe vertically:
`[INFO] Drone 1 and Drone 2 close (H: 16.50 m), vertical separation safe` <br>

## Warning Case (action triggered):
`[WARNING] Drone 1 and Drone 2 too close! H: 12.34 m, V: 3.21 m` <br>
`[ACTION] Requested Drone 1 to switch to hold mode.` <br>
`[ACTION] Requested Drone 2 to switch to hold mode.` <br>

## Notes

- Mode numbers may differ between PX4 and ArduPilot. Adjust `5` in `_set_mode_hold()` if HOLD mode does not map correctly on your autopilot.

- Ensure both drones are streaming MAVLink data over UDP/TCP before running the script.

- Use in simulation first (e.g., SITL + Gazebo) before deploying on real hardware.

## License

This project is released under the MIT License. Free to use, modify, and distribute with attribution.

