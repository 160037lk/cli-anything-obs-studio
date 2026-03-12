"""Scene management for OBS Studio."""
from typing import Any, Dict, List, Optional
from ..utils.obs_websocket import OBSWebSocketClient


class SceneManager:
    """Manage OBS scenes."""
    
    def __init__(self, client: OBSWebSocketClient):
        self.client = client
    
    def list_scenes(self) -> List[Dict[str, Any]]:
        """List all scenes."""
        return self.client.get_scenes()
    
    def get_current(self) -> str:
        """Get current scene name."""
        return self.client.get_current_scene()
    
    def set_current(self, scene_name: str) -> None:
        """Set current scene."""
        self.client.set_current_scene(scene_name)
    
    def create_scene(self, scene_name: str) -> Dict[str, Any]:
        """Create a new scene."""
        return self.client.call("CreateScene", {"sceneName": scene_name})
    
    def remove_scene(self, scene_name: str) -> Dict[str, Any]:
        """Remove a scene."""
        return self.client.call("RemoveScene", {"sceneName": scene_name})
    
    def get_scene_info(self, scene_name: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed scene information."""
        if scene_name:
            return self.client.call("GetSceneList", {"sceneName": scene_name})
        return self.client.call("GetSceneList")
    
    def switch_to_scene(self, scene_name: str, transition: Optional[str] = None) -> None:
        """Switch to scene with optional transition."""
        if transition:
            self.client.call("SetCurrentSceneTransition", {"transitionName": transition})
        self.client.set_current_scene(scene_name)
    
    def get_transitions(self) -> List[Dict[str, Any]]:
        """Get available transitions."""
        response = self.client.call("GetSceneTransitionList")
        return response.get("transitions", [])
    
    def get_current_transition(self) -> Dict[str, Any]:
        """Get current transition."""
        return self.client.call("GetCurrentSceneTransition")
    
    def set_transition(self, transition_name: str, duration: Optional[int] = None) -> None:
        """Set transition."""
        self.client.call("SetCurrentSceneTransition", {"transitionName": transition_name})
        if duration is not None:
            self.client.call("SetCurrentSceneTransitionDuration", {"transitionDuration": duration})
