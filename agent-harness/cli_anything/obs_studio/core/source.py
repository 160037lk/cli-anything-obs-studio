"""Source management for OBS Studio."""
from typing import Any, Dict, List, Optional
from ..utils.obs_websocket import OBSWebSocketClient


class SourceManager:
    """Manage OBS sources."""
    
    def __init__(self, client: OBSWebSocketClient):
        self.client = client
    
    def list_sources(self, scene_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List sources in a scene."""
        return self.client.get_sources(scene_name)
    
    def get_source_types(self) -> List[Dict[str, Any]]:
        """Get available source types."""
        response = self.client.call("GetInputKindList")
        return response.get("inputKinds", [])
    
    def create_source(self, source_name: str, source_kind: str, scene_name: Optional[str] = None,
                     settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new source."""
        data = {
            "inputName": source_name,
            "inputKind": source_kind
        }
        if scene_name:
            data["sceneName"] = scene_name
        if settings:
            data["inputSettings"] = settings
        
        return self.client.call("CreateInput", data)
    
    def remove_source(self, source_name: str) -> Dict[str, Any]:
        """Remove a source."""
        return self.client.call("RemoveInput", {"inputName": source_name})
    
    def get_source_settings(self, source_name: str) -> Dict[str, Any]:
        """Get source settings."""
        return self.client.call("GetInputSettings", {"inputName": source_name})
    
    def set_source_settings(self, source_name: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Set source settings."""
        return self.client.call("SetInputSettings", {
            "inputName": source_name,
            "inputSettings": settings
        })
    
    def get_source_properties(self, source_name: str) -> Dict[str, Any]:
        """Get source properties."""
        return self.client.call("GetInputPropertiesListPropertyItems", {"inputName": source_name})
    
    def set_source_visible(self, source_name: str, visible: bool, scene_name: Optional[str] = None) -> None:
        """Set source visibility."""
        data = {
            "sceneItemId": source_name,
            "sceneItemEnabled": visible
        }
        if scene_name:
            data["sceneName"] = scene_name
        
        self.client.call("SetSceneItemEnabled", data)
    
    def get_source_visibility(self, source_name: str, scene_name: Optional[str] = None) -> bool:
        """Get source visibility."""
        data = {"sceneItemId": source_name}
        if scene_name:
            data["sceneName"] = scene_name
        
        response = self.client.call("GetSceneItemEnabled", data)
        return response.get("sceneItemEnabled", False)
    
    def set_source_position(self, source_name: str, x: float, y: float,
                           scene_name: Optional[str] = None) -> None:
        """Set source position."""
        data = {
            "sceneItemId": source_name,
            "sceneItemTransform": {"positionX": x, "positionY": y}
        }
        if scene_name:
            data["sceneName"] = scene_name
        
        self.client.call("SetSceneItemTransform", data)
    
    def set_source_scale(self, source_name: str, scale_x: float, scale_y: float,
                        scene_name: Optional[str] = None) -> None:
        """Set source scale."""
        data = {
            "sceneItemId": source_name,
            "sceneItemTransform": {"scaleX": scale_x, "scaleY": scale_y}
        }
        if scene_name:
            data["sceneName"] = scene_name
        
        self.client.call("SetSceneItemTransform", data)
    
    def get_source_transform(self, source_name: str, scene_name: Optional[str] = None) -> Dict[str, Any]:
        """Get source transform."""
        data = {"sceneItemId": source_name}
        if scene_name:
            data["sceneName"] = scene_name
        
        return self.client.call("GetSceneItemTransform", data)
    
    def get_source_screenshot(self, source_name: str, file_path: Optional[str] = None,
                             format: str = "png") -> Dict[str, Any]:
        """Get screenshot of a source."""
        return self.client.take_screenshot(
            source_name=source_name,
            embed_picture_format=format,
            save_to_file_path=file_path
        )
