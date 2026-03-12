"""Recording management for OBS Studio."""
from typing import Any, Dict, Optional
from ..utils.obs_websocket import OBSWebSocketClient


class RecordingManager:
    """Manage OBS recording."""
    
    def __init__(self, client: OBSWebSocketClient):
        self.client = client
    
    def start(self) -> None:
        """Start recording."""
        self.client.start_recording()
    
    def stop(self) -> Dict[str, Any]:
        """Stop recording and return output path."""
        response = self.client.stop_recording()
        return {
            "output_path": response.get("outputPath"),
            "output_duration": response.get("outputDuration"),
            "output_size": response.get("outputSize")
        }
    
    def pause(self) -> None:
        """Pause recording."""
        self.client.pause_recording()
    
    def resume(self) -> None:
        """Resume recording."""
        self.client.resume_recording()
    
    def toggle(self) -> Dict[str, Any]:
        """Toggle recording on/off."""
        status = self.get_status()
        if status.get("active", False):
            return self.stop()
        else:
            self.start()
            return {"status": "started"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get recording status."""
        response = self.client.get_recording_status()
        return {
            "active": response.get("outputActive", False),
            "paused": response.get("outputPaused", False),
            "path": response.get("outputPath"),
            "duration": response.get("outputDuration"),
            "size": response.get("outputSize"),
            "bytes_per_sec": response.get("outputBytesPerSecond"),
            "total_frames": response.get("outputTotalFrames"),
            "dropped_frames": response.get("outputSkippedFrames")
        }
    
    def get_settings(self) -> Dict[str, Any]:
        """Get recording settings."""
        return self.client.call("GetRecordSettings")
    
    def set_settings(self, settings: Dict[str, Any]) -> None:
        """Set recording settings."""
        self.client.call("SetRecordSettings", settings)
    
    def get_filename_formatting(self) -> str:
        """Get recording filename formatting."""
        response = self.client.call("GetRecordDirectory")
        return response.get("recordDirectory", "")
    
    def set_record_directory(self, directory: str) -> None:
        """Set recording directory."""
        self.client.call("SetRecordDirectory", {"recordDirectory": directory})
