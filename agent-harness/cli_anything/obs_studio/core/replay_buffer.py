"""Replay buffer management for OBS Studio."""
from typing import Any, Dict
from ..utils.obs_websocket import OBSWebSocketClient


class ReplayBufferManager:
    """Manage OBS replay buffer."""
    
    def __init__(self, client: OBSWebSocketClient):
        self.client = client
    
    def start(self) -> None:
        """Start replay buffer."""
        self.client.call("StartReplayBuffer")
    
    def stop(self) -> None:
        """Stop replay buffer."""
        self.client.call("StopReplayBuffer")
    
    def save(self) -> Dict[str, Any]:
        """Save replay buffer to file."""
        return self.client.save_replay_buffer()
    
    def get_status(self) -> Dict[str, Any]:
        """Get replay buffer status."""
        return self.client.get_replay_buffer_status()
    
    def toggle(self) -> Dict[str, Any]:
        """Toggle replay buffer on/off."""
        status = self.get_status()
        if status.get("outputActive", False):
            self.stop()
            return {"status": "stopped"}
        else:
            self.start()
            return {"status": "started"}
