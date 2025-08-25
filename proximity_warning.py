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
        self.connection1 = mavutil.mavlink_connection(conn_str1)
        self.connection2 = mavutil.mavlink_connection(conn_str2)
        self.h_threshold = h_threshold
        self.v_threshold = v_threshold

        self.latlon1, self.latlon2 = None, None
        self.altitude1, self.altitude2 = None, None
        self.sysid1, self.sysid2 = None, None

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Compute haversine distance between two GPS coordinates (in meters)."""
        R = 6371000.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a_val = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
        c_val = 2 * math.atan2(math.sqrt(a_val), math.sqrt(1 - a_val))
        return R * c_val

    def _read_gps(self, conn):
        """Read GPS data from a MAVLink connection (lat, lon in degrees)."""
        msg = conn.recv_match(type="GPS_RAW_INT", blocking=False)
        if msg:
            return msg.lat / 1e7, msg.lon / 1e7
        return None

    def _read_local_position(self, conn):
        """Read local position (z) from a MAVLink connection (meters)."""
        msg = conn.recv_match(type="LOCAL_POSITION_NED", blocking=False)
        if msg:
            return msg.get_srcSystem(), msg.z
        return None

    def monitor(self):
        """Start monitoring the two drones for proximity."""
        while True:
            gps1, gps2 = self._read_gps(self.connection1), self._read_gps(self.connection2)
            pos1, pos2 = self._read_local_position(self.connection1), self._read_local_position(self.connection2)

            if gps1:
                lat1, lon1 = gps1
                self.latlon1 = (lat1, lon1)
            if gps2:
                lat2, lon2 = gps2
                self.latlon2 = (lat2, lon2)
            if pos1:
                self.sysid1, self.altitude1 = pos1
            if pos2:
                self.sysid2, self.altitude2 = pos2

            if self.latlon1 and self.latlon2:
                distance = self._haversine(
                    self.latlon1[0], self.latlon1[1],
                    self.latlon2[0], self.latlon2[1]
                )
                vert_distance = abs(self.altitude1 - self.altitude2) if (self.altitude1 is not None and self.altitude2 is not None) else None

                h_close = distance < self.h_threshold
                v_close = (vert_distance is not None and vert_distance < self.v_threshold)

                if h_close or v_close:
                    if vert_distance is not None:
                        print(
                            f"[WARNING] Drone {self.sysid1} and Drone {self.sysid2} - "
                            f"Horizontal: {distance:.2f} m (threshold {self.h_threshold} m), "
                            f"Vertical: {vert_distance:.2f} m (threshold {self.v_threshold} m)"
                        )
                    else:
                        print(
                            f"[WARNING] Drone {self.sysid1} and Drone {self.sysid2} - "
                            f"Horizontal: {distance:.2f} m (threshold {self.h_threshold} m)"
                        )
                else:
                    if vert_distance is not None:
                        print(
                            f"[INFO] Distance between Drone {self.sysid1} and Drone {self.sysid2}: "
                            f"{distance:.2f} m, Vertical separation: {vert_distance:.2f} m"
                        )
                    else:
                        print(
                            f"[INFO] Distance between Drone {self.sysid1} and Drone {self.sysid2}: "
                            f"{distance:.2f} m"
                        )

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
