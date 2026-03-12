"""Stats management for OBS Studio."""
from typing import Any, Dict
from ..utils.obs_websocket import OBSWebSocketClient


class StatsManager:
    """Manage OBS stats."""
    
    def __init__(self, client: OBSWebSocketClient):
        self.client = client
    
    def get_stats(self) -> Dict[str, Any]:
        """Get OBS stats."""
        return self.client.get_stats()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance stats."""
        response = self.client.call("GetPerformanceStatistics")
        return {
            "cpu_usage": response.get("cpuUsage"),
            "memory_usage": response.get("memoryUsage"),
            "available_disk_space": response.get("availableDiskSpace"),
            "active_frames": response.get("activeFps"),
            "average_frame_render_time": response.get("averageFrameRenderTime"),
            "render_missed_frames": response.get("renderMissedFrames"),
            "render_total_frames": response.get("renderTotalFrames"),
            "output_skipped_frames": response.get("outputSkippedFrames"),
            "output_total_frames": response.get("outputTotalFrames")
        }
    
    def get_video_settings(self) -> Dict[str, Any]:
        """Get video settings."""
        return self.client.call("GetVideoSettings")
    
    def set_video_settings(self, settings: Dict[str, Any]) -> None:
        """Set video settings."""
        self.client.call("SetVideoSettings", settings)
