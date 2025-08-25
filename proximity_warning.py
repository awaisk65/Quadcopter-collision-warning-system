#!/usr/bin/env python3

"""
Drone Proximity Warning Script
==============================

This script connects to two MAVLink endpoints using pymavlink,
reads GPS and local position data, computes both horizontal
and vertical distances, and prints warnings if drones are closer
than user-defined thresholds.

Dependencies
------------
    pip install pymavlink

Usage
-----
Default mode (uses built-in connection strings and thresholds):
    python proximity_warning.py

Custom mode (provide connection strings and thresholds):
    python proximity_warning.py --conn1 <conn1_str> --conn2 <conn2_str> --hthresh <meters> --vthresh <meters>

Examples
--------
    python proximity_warning.py --conn1 udp:127.0.0.1:14540 --conn2 udp:127.0.0.1:14541 --hthresh 20 --vthresh 10
"""

import math
import time
import argparse
from pymavlink import mavutil


class DroneProximityMonitor:
    """
    Monitor the proximity between two drones using MAVLink GPS and local position data.
    """

    def __init__(self, conn_str1: str, conn_str2: str, h_threshold: float = 15.0, v_threshold: float = 5.0):
        """
        Initialize the proximity monitor.

        Parameters
        ----------
        conn_str1 : str
            MAVLink connection string for drone 1 (e.g., 'udp:127.0.0.1:14540')
        conn_str2 : str
            MAVLink connection string for drone 2 (e.g., 'udp:127.0.0.1:14541')
        h_threshold : float, optional
            Horizontal distance threshold in meters for warnings (default: 15.0)
        v_threshold : float, optional
            Vertical distance threshold in meters for warnings (default: 5.0)
        """

        self.conn1 = mavutil.mavlink_connection(conn_str1)
        self.conn2 = mavutil.mavlink_connection(conn_str2)
        self.h_threshold = h_threshold
        self.v_threshold = v_threshold

        self.latlon1, self.latlon2 = None, None
        self.altitude1, self.altitude2 = None, None
        self.sysid1, self.sysid2 = None, None

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Compute haversine distance between two GPS coordinates.

        Returns
        -------
        float
            Distance in meters
        """
        R = 6371000.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _read_gps(self, conn) -> tuple:
        """
        Read GPS data from MAVLink.

        Returns
        -------
        tuple or None
            (latitude, longitude) in degrees or None
        """
        msg = conn.recv_match(type="GPS_RAW_INT", blocking=True, timeout=1)
        if msg:
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            return lat, lon
        return None

    def _read_altitude(self, conn) -> float:
        """
        Read altitude data from MAVLink.

        Returns
        -------
        float or None
            Altitude in meters or None
        """
        msg = conn.recv_match(type="LOCAL_POSITION_NED", blocking=True, timeout=1)
        if msg:
            return msg.get_srcSystem(), -msg.z  # NED frame → z is negative up
        return None

    def _set_mode_hold(self, drone_id: int, conn):
        """
        Request mode change to HOLD/POSHOLD to stop drone movement.

        Parameters
        ----------
        drone_id : int
            Drone system ID
        conn : mavutil.mavfile
            MAVLink connection object
        """
        # try:
        # Switch mode to LOITER
        conn.mav.set_mode_send(
            conn.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            5  # LOITER mode number (for PX4/ArduPilot)
        )
        print(f"[ACTION] Requested Drone {drone_id} to switch to hold mode.")
        # except Exception as e:
        #     print(f"[ERROR] Failed to change mode for Drone {drone_id}: {e}")

    def monitor(self):
        """
        Start monitoring the two drones for proximity.
        """
        while True:
            gps1, gps2 = self._read_gps(self.conn1), self._read_gps(self.conn2)
            pos1, pos2 = self._read_altitude(self.conn1), self._read_altitude(self.conn2)


            if gps1:
                self.latlon1 = gps1
            if gps2:
                self.latlon2 = gps2
            if pos1:
                self.sysid1, self.altitude1 = pos1
            if pos2:
                self.sysid2, self.altitude2 = pos2

            if self.latlon1 and self.latlon2:
                distance = self._haversine(
                    self.latlon1[0], self.latlon1[1],
                    self.latlon2[0], self.latlon2[1]
                )

                vert_distance = None
                if self.altitude1 is not None and self.altitude2 is not None:
                    vert_distance = abs(self.altitude1 - self.altitude2)

                # ✅ Horizontal threshold check first
                if distance < self.h_threshold:
                    if vert_distance is not None and vert_distance < self.v_threshold:
                        print(
                            f"[WARNING] Drone {self.sysid1} and Drone {self.sysid2} "
                            f"too close! H: {distance:.2f} m, V: {vert_distance:.2f} m"
                        )
                        # Request HOLD mode for both drones
                        self._set_mode_hold(self.sysid1, self.conn1)
                        self._set_mode_hold(self.sysid2, self.conn2)

                    else:
                        print(
                            f"[INFO] Drone {self.sysid1} and Drone {self.sysid2} "
                            f"close (H: {distance:.2f} m), vertical separation safe"
                        )
                else:
                    if vert_distance is not None:
                        print(f"[INFO] Safe. H: {distance:.2f} m, V: {vert_distance:.2f} m")
                    else:
                        print(f"[INFO] Safe. H: {distance:.2f} m")

            time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Monitor proximity between two drones using pymavlink.",
        epilog=(
            "You can either run without arguments (defaults to --conn1 udp:127.0.0.1:14540 --conn2 udp:127.0.0.1:14541, "
            "--hthresh 15 m, --vthresh 5 m)\n"
            "or specify your own MAVLink connection strings and thresholds."
        )
    )
    parser.add_argument("--conn1", type=str, default="udp:127.0.0.1:14540", help="MAVLink connection string for Drone 1")
    parser.add_argument("--conn2", type=str, default="udp:127.0.0.1:14541", help="MAVLink connection string for Drone 2")
    parser.add_argument("--hthresh", type=float, default=15.0, help="Horizontal threshold in meters (default: 15.0)")
    parser.add_argument("--vthresh", type=float, default=5.0, help="Vertical threshold in meters (default: 5.0)")
    args = parser.parse_args()

    monitor = DroneProximityMonitor(
        conn_str1=args.conn1,
        conn_str2=args.conn2,
        h_threshold=args.hthresh,
        v_threshold=args.vthresh
    )
    monitor.monitor()
