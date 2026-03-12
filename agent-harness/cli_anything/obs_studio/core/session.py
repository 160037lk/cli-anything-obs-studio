"""Session management for OBS Studio CLI."""
import json
import os
from typing import Any, Dict, Optional
from ..utils.obs_websocket import OBSWebSocketClient


class Session:
    """OBS Studio session state."""
    
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = project_path
        self.client: Optional[OBSWebSocketClient] = None
        self.host = "localhost"
        self.port = 4455
        self.password: Optional[str] = None
        self.current_scene: Optional[str] = None
        self.modified = False
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from project file or environment."""
        # Check environment variables
        self.host = os.environ.get("OBS_WEBSOCKET_HOST", self.host)
        self.port = int(os.environ.get("OBS_WEBSOCKET_PORT", self.port))
        self.password = os.environ.get("OBS_WEBSOCKET_PASSWORD") or self.password
        
        # Load from project file if exists
        if self.project_path and os.path.exists(self.project_path):
            try:
                with open(self.project_path, 'r') as f:
                    config = json.load(f)
                    self.host = config.get("host", self.host)
                    self.port = config.get("port", self.port)
                    self.password = config.get("password", self.password)
                    self.current_scene = config.get("current_scene")
            except (json.JSONDecodeError, IOError):
                pass
    
    def connect(self) -> OBSWebSocketClient:
        """Connect to OBS WebSocket."""
        if self.client and self.client.connected:
            return self.client
        
        self.client = OBSWebSocketClient(
            host=self.host,
            port=self.port,
            password=self.password
        )
        self.client.connect()
        return self.client
    
    def disconnect(self) -> None:
        """Disconnect from OBS WebSocket."""
        if self.client:
            self.client.disconnect()
            self.client = None
    
    def save(self, path: Optional[str] = None) -> None:
        """Save session to file."""
        save_path = path or self.project_path
        if not save_path:
            raise ValueError("No project path specified")
        
        config = {
            "host": self.host,
            "port": self.port,
            "password": self.password,
            "current_scene": self.current_scene
        }
        
        with open(save_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.project_path = save_path
        self.modified = False
    
    def is_connected(self) -> bool:
        """Check if connected to OBS."""
        return self.client is not None and self.client.connected
    
    def get_status(self) -> Dict[str, Any]:
        """Get session status."""
        status = {
            "connected": self.is_connected(),
            "project_path": self.project_path,
            "host": f"{self.host}:{self.port}",
            "modified": self.modified
        }
        
        if self.is_connected() and self.client:
            try:
                version = self.client.get_version()
                status["obs_version"] = version.get("obs-studio-version", "unknown")
                status["websocket_version"] = version.get("obs-websocket-version", "unknown")
                
                recording = self.client.get_recording_status()
                status["recording"] = recording.get("outputActive", False)
                status["recording_paused"] = recording.get("outputPaused", False)
                
                streaming = self.client.get_streaming_status()
                status["streaming"] = streaming.get("outputActive", False)
                
                status["current_scene"] = self.client.get_current_scene()
            except Exception as e:
                status["error"] = str(e)
        
        return status
