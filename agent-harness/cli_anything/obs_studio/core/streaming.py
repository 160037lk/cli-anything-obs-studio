"""Streaming management for OBS Studio."""
from typing import Any, Dict
from ..utils.obs_websocket import OBSWebSocketClient


class StreamingManager:
    """Manage OBS streaming."""
    
    def __init__(self, client: OBSWebSocketClient):
        self.client = client
    
    def start(self) -> None:
        """Start streaming."""
        self.client.start_streaming()
    
    def stop(self) -> None:
        """Stop streaming."""
        self.client.stop_streaming()
    
    def toggle(self) -> Dict[str, Any]:
        """Toggle streaming on/off."""
        status = self.get_status()
        if status.get("active", False):
            self.stop()
            return {"status": "stopped"}
        else:
            self.start()
            return {"status": "started"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get streaming status."""
        response = self.client.get_streaming_status()
        return {
            "active": response.get("outputActive", False),
            "reconnecting": response.get("outputReconnecting", False),
            "timecode": response.get("outputTimecode"),
            "duration": response.get("outputDuration"),
            "congestion": response.get("outputCongestion"),
            "bytes": response.get("outputBytes"),
            "skipped_frames": response.get("outputSkippedFrames"),
            "total_frames": response.get("outputTotalFrames")
        }
    
    def get_settings(self) -> Dict[str, Any]:
        """Get stream settings."""
        return self.client.call("GetStreamSettings")
    
    def set_settings(self, settings: Dict[str, Any]) -> None:
        """Set stream settings."""
        self.client.call("SetStreamSettings", settings)
    
    def get_service_settings(self) -> Dict[str, Any]:
        """Get streaming service settings."""
        return self.client.call("GetStreamServiceSettings")
    
    def set_service_settings(self, service: str, server: str, key: str) -> None:
        """Set streaming service settings."""
        self.client.call("SetStreamServiceSettings", {
            "streamServiceSettings": {
                "service": service,
                "server": server,
                "key": key
            }
        })
    
    def send_caption(self, caption: str) -> None:
        """Send caption to stream."""
        self.client.call("SendStreamCaption", {"captionText": caption})
    
    def get_stream_key(self) -> str:
        """Get stream key."""
        response = self.client.call("GetStreamServiceSettings")
        settings = response.get("streamServiceSettings", {})
        return settings.get("key", "")
