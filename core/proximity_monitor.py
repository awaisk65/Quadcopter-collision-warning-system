"""Core drone proximity monitoring logic."""

import math
import time
from pymavlink import mavutil


class DroneProximityMonitor:
    """Monitor proximity between two drones using MAVLink."""

    def __init__(self, conn_str1: str, conn_str2: str,
                 h_threshold: float = 15.0, v_threshold: float = 5.0) -> None:
        self.conn1 = mavutil.mavlink_connection(conn_str1)
        self.conn2 = mavutil.mavlink_connection(conn_str2)
        self.h_threshold = h_threshold
        self.v_threshold = v_threshold
        self.latlon1, self.latlon2 = None, None
        self.altitude1, self.altitude2 = None, None
        self.sysid1, self.sysid2 = None, None

    def _haversine(self, lat1, lon1, lat2, lon2) -> float:
        """Compute haversine distance in meters."""
        R = 6371000.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = (math.sin(dphi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

    def check_once(self) -> dict:
        """Check distances once and return results instead of infinite loop."""
        gps1 = self._read_gps(self.conn1)
        gps2 = self._read_gps(self.conn2)
        pos1 = self._read_altitude(self.conn1)
        pos2 = self._read_altitude(self.conn2)

        if gps1:
            self.latlon1 = gps1
        if gps2:
            self.latlon2 = gps2
        if pos1:
            self.sysid1, self.altitude1 = pos1
        if pos2:
            self.sysid2, self.altitude2 = pos2

        if self.latlon1 and self.latlon2:
            h_dist = self._haversine(self.latlon1[0], self.latlon1[1],
                                     self.latlon2[0], self.latlon2[1])
            v_dist = (abs(self.altitude1 - self.altitude2)
                      if self.altitude1 is not None and self.altitude2 is not None else None)

            status = "SAFE"
            if h_dist < self.h_threshold and v_dist is not None and v_dist < self.v_threshold:
                status = "DANGER"

            return {
                "horizontal_distance_m": round(h_dist, 2),
                "vertical_distance_m": round(v_dist, 2) if v_dist is not None else None,
                "status": status,
                "sysid1": self.sysid1,
                "sysid2": self.sysid2
            }
        return {"status": "NO DATA"}

    def _read_gps(self, conn):
        msg = conn.recv_match(type="GPS_RAW_INT", blocking=True, timeout=1)
        if msg:
            return msg.lat / 1e7, msg.lon / 1e7
        return None

    def _read_altitude(self, conn):
        msg = conn.recv_match(type="LOCAL_POSITION_NED", blocking=True, timeout=1)
        if msg:
            return msg.get_srcSystem(), -msg.z
        return None
