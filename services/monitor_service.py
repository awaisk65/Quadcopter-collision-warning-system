"""Service layer wrapping DroneProximityMonitor."""

from core.proximity_monitor import DroneProximityMonitor


class MonitorService:
    """Service to manage DroneProximityMonitor."""

    def __init__(self, conn1: str, conn2: str, hthresh: float, vthresh: float) -> None:
        self.monitor = DroneProximityMonitor(conn1, conn2, hthresh, vthresh)

    def run_check(self) -> dict:
        """Run one proximity check and return results."""
        return self.monitor.check_once()
