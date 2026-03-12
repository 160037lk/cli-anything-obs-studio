"""OBS WebSocket client for controlling OBS Studio."""
import json
import socket
import struct
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Union


class OBSWebSocketError(Exception):
    """Base exception for OBS WebSocket errors."""
    pass


class OBSWebSocketConnectionError(OBSWebSocketError):
    """Connection error."""
    pass


class OBSWebSocketAuthError(OBSWebSocketError):
    """Authentication error."""
    pass


class OBSWebSocketRequestError(OBSWebSocketError):
    """Request error."""
    pass


class OBSWebSocketClient:
    """OBS WebSocket client implementation."""
    
    def __init__(self, host: str = "localhost", port: int = 4455, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.password = password
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.authenticated = False
        self._message_id = 0
        self._callbacks: Dict[str, Callable] = {}
        self._response_events: Dict[str, threading.Event] = {}
        self._responses: Dict[str, Any] = {}
        self._receive_thread: Optional[threading.Thread] = None
        self._running = False
    
    def connect(self) -> None:
        """Connect to OBS WebSocket server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            self._running = True
            self._receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._receive_thread.start()
            
            # Wait for connection to establish
            time.sleep(0.5)
            self.connected = True
            
            # Authenticate if password is set
            if self.password:
                self._authenticate()
            else:
                self.authenticated = True
                
        except (socket.error, ConnectionRefusedError) as e:
            raise OBSWebSocketConnectionError(
                f"Failed to connect to OBS WebSocket at {self.host}:{self.port}. "
                f"Make sure OBS Studio is running and WebSocket server is enabled.\n"
                f"Error: {e}"
            )
    
    def disconnect(self) -> None:
        """Disconnect from OBS WebSocket server."""
        self._running = False
        self.connected = False
        self.authenticated = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
    
    def _authenticate(self) -> None:
        """Authenticate with password."""
        import hashlib
        import base64
        
        # Get authentication challenge
        response = self.call("GetAuthRequired")
        if not response.get("authRequired", False):
            self.authenticated = True
            return
        
        challenge = response.get("challenge", "")
        salt = response.get("salt", "")
        
        # Compute auth response
        secret = hashlib.sha256((self.password + salt).encode()).digest()
        auth_response = base64.b64encode(
            hashlib.sha256(secret + challenge.encode()).digest()
        ).decode()
        
        # Send authentication
        result = self.call("Authenticate", {"auth": auth_response})
        if result.get("status") == "ok":
            self.authenticated = True
        else:
            raise OBSWebSocketAuthError("Authentication failed. Check your password.")
    
    def _receive_loop(self) -> None:
        """Background thread to receive messages."""
        while self._running and self.socket:
            try:
                # Read WebSocket frame
                frame = self._read_frame()
                if frame:
                    self._handle_message(frame)
            except (socket.error, ConnectionResetError):
                if self._running:
                    self.connected = False
                break
            except Exception:
                continue
    
    def _read_frame(self) -> Optional[str]:
        """Read a WebSocket frame."""
        if not self.socket:
            return None
        
        try:
            # Simple WebSocket text frame parsing
            header = self.socket.recv(2)
            if len(header) < 2:
                return None
            
            opcode = header[0] & 0x0f
            masked = (header[1] & 0x80) != 0
            payload_len = header[1] & 0x7f
            
            if payload_len == 126:
                payload_len = struct.unpack("!H", self.socket.recv(2))[0]
            elif payload_len == 127:
                payload_len = struct.unpack("!Q", self.socket.recv(8))[0]
            
            if masked:
                mask = self.socket.recv(4)
            
            payload = self.socket.recv(payload_len)
            if masked:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            
            if opcode == 0x01:  # Text frame
                return payload.decode('utf-8')
            elif opcode == 0x08:  # Close frame
                self._running = False
                return None
            
        except (socket.timeout, BlockingIOError):
            return None
        except Exception:
            return None
        
        return None
    
    def _handle_message(self, message: str) -> None:
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            message_id = data.get("message-id")
            
            if message_id and message_id in self._response_events:
                self._responses[message_id] = data
                self._response_events[message_id].set()
            
            # Handle events
            if "update-type" in data:
                update_type = data.get("update-type")
                if update_type in self._callbacks:
                    self._callbacks[update_type](data)
                    
        except json.JSONDecodeError:
            pass
    
    def _send(self, data: Dict[str, Any]) -> None:
        """Send a WebSocket message."""
        if not self.socket:
            raise OBSWebSocketConnectionError("Not connected")
        
        message = json.dumps(data)
        
        # Build WebSocket text frame
        payload = message.encode('utf-8')
        frame = bytearray()
        frame.append(0x81)  # Text frame, FIN=1
        
        if len(payload) < 126:
            frame.append(len(payload))
        elif len(payload) < 65536:
            frame.append(126)
            frame.extend(struct.pack("!H", len(payload)))
        else:
            frame.append(127)
            frame.extend(struct.pack("!Q", len(payload)))
        
        frame.extend(payload)
        self.socket.send(frame)
    
    def call(self, request_type: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a synchronous call to OBS."""
        if not self.connected:
            raise OBSWebSocketConnectionError("Not connected to OBS")
        
        self._message_id += 1
        message_id = str(self._message_id)
        
        request = {
            "request-type": request_type,
            "message-id": message_id
        }
        if data:
            request.update(data)
        
        # Setup response event
        event = threading.Event()
        self._response_events[message_id] = event
        self._responses[message_id] = None
        
        try:
            self._send(request)
            
            # Wait for response (timeout 10 seconds)
            if event.wait(timeout=10):
                response = self._responses.get(message_id, {})
                
                # Check for error
                if response.get("status") == "error":
                    error = response.get("error", "Unknown error")
                    raise OBSWebSocketRequestError(f"OBS request failed: {error}")
                
                return response
            else:
                raise OBSWebSocketRequestError("Request timeout")
                
        finally:
            # Cleanup
            self._response_events.pop(message_id, None)
            self._responses.pop(message_id, None)
    
    def on_event(self, event_type: str, callback: Callable) -> None:
        """Register an event callback."""
        self._callbacks[event_type] = callback
    
    # Convenience methods for common operations
    
    def get_version(self) -> Dict[str, Any]:
        """Get OBS version info."""
        return self.call("GetVersion")
    
    def get_scenes(self) -> List[Dict[str, Any]]:
        """Get list of scenes."""
        response = self.call("GetSceneList")
        return response.get("scenes", [])
    
    def get_current_scene(self) -> str:
        """Get current scene name."""
        response = self.call("GetCurrentScene")
        return response.get("name", "")
    
    def set_current_scene(self, scene_name: str) -> None:
        """Set current scene."""
        self.call("SetCurrentScene", {"scene-name": scene_name})
    
    def get_sources(self, scene_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get sources in a scene."""
        if scene_name:
            response = self.call("GetSceneItemList", {"sceneName": scene_name})
        else:
            response = self.call("GetSceneItemList")
        return response.get("sceneItems", [])
    
    def start_recording(self) -> None:
        """Start recording."""
        self.call("StartRecording")
    
    def stop_recording(self) -> None:
        """Stop recording."""
        self.call("StopRecording")
    
    def pause_recording(self) -> None:
        """Pause recording."""
        self.call("PauseRecording")
    
    def resume_recording(self) -> None:
        """Resume recording."""
        self.call("ResumeRecording")
    
    def get_recording_status(self) -> Dict[str, Any]:
        """Get recording status."""
        return self.call("GetRecordStatus")
    
    def start_streaming(self) -> None:
        """Start streaming."""
        self.call("StartStreaming")
    
    def stop_streaming(self) -> None:
        """Stop streaming."""
        self.call("StopStreaming")
    
    def get_streaming_status(self) -> Dict[str, Any]:
        """Get streaming status."""
        return self.call("GetStreamStatus")
    
    def save_replay_buffer(self) -> None:
        """Save replay buffer."""
        self.call("SaveReplayBuffer")
    
    def get_replay_buffer_status(self) -> Dict[str, Any]:
        """Get replay buffer status."""
        return self.call("GetReplayBufferStatus")
    
    def take_screenshot(self, source_name: Optional[str] = None, 
                       embed_picture_format: Optional[str] = None,
                       save_to_file_path: Optional[str] = None) -> Dict[str, Any]:
        """Take a screenshot."""
        data = {}
        if source_name:
            data["sourceName"] = source_name
        if embed_picture_format:
            data["embedPictureFormat"] = embed_picture_format
        if save_to_file_path:
            data["saveToFilePath"] = save_to_file_path
        return self.call("TakeSourceScreenshot", data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get OBS stats."""
        return self.call("GetStats")
