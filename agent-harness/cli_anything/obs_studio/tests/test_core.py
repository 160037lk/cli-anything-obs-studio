"""Unit tests for OBS Studio CLI core modules."""
import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from ..core.session import Session
from ..core.scene import SceneManager
from ..core.source import SourceManager
from ..core.recording import RecordingManager
from ..core.streaming import StreamingManager


class TestSession(unittest.TestCase):
    """Test Session class."""
    
    def test_session_init(self):
        """Test session initialization."""
        session = Session()
        self.assertEqual(session.host, "localhost")
        self.assertEqual(session.port, 4455)
        self.assertIsNone(session.password)
        self.assertIsNone(session.project_path)
    
    def test_session_with_project(self):
        """Test session with project file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"host": "192.168.1.100", "port": 4444}, f)
            temp_path = f.name
        
        try:
            session = Session(project_path=temp_path)
            self.assertEqual(session.host, "192.168.1.100")
            self.assertEqual(session.port, 4444)
        finally:
            os.unlink(temp_path)
    
    def test_session_save(self):
        """Test saving session."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            session = Session()
            session.host = "testhost"
            session.port = 1234
            session.password = "testpass"
            session.save(temp_path)
            
            with open(temp_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(data["host"], "testhost")
                self.assertEqual(data["port"], 1234)
                self.assertEqual(data["password"], "testpass")
        finally:
            os.unlink(temp_path)


class TestSceneManager(unittest.TestCase):
    """Test SceneManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.scene_manager = SceneManager(self.mock_client)
    
    def test_list_scenes(self):
        """Test listing scenes."""
        self.mock_client.get_scenes.return_value = [
            {"sceneName": "Scene 1"},
            {"sceneName": "Scene 2"}
        ]
        
        scenes = self.scene_manager.list_scenes()
        self.assertEqual(len(scenes), 2)
        self.assertEqual(scenes[0]["sceneName"], "Scene 1")
    
    def test_get_current(self):
        """Test getting current scene."""
        self.mock_client.get_current_scene.return_value = "Test Scene"
        
        current = self.scene_manager.get_current()
        self.assertEqual(current, "Test Scene")
    
    def test_set_current(self):
        """Test setting current scene."""
        self.scene_manager.set_current("New Scene")
        self.mock_client.set_current_scene.assert_called_once_with("New Scene")


class TestSourceManager(unittest.TestCase):
    """Test SourceManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.source_manager = SourceManager(self.mock_client)
    
    def test_list_sources(self):
        """Test listing sources."""
        self.mock_client.get_sources.return_value = [
            {"sourceName": "Source 1", "sceneItemEnabled": True},
            {"sourceName": "Source 2", "sceneItemEnabled": False}
        ]
        
        sources = self.source_manager.list_sources()
        self.assertEqual(len(sources), 2)
        self.assertTrue(sources[0]["sceneItemEnabled"])


class TestRecordingManager(unittest.TestCase):
    """Test RecordingManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.recording_manager = RecordingManager(self.mock_client)
    
    def test_start_recording(self):
        """Test starting recording."""
        self.recording_manager.start()
        self.mock_client.start_recording.assert_called_once()
    
    def test_stop_recording(self):
        """Test stopping recording."""
        self.mock_client.stop_recording.return_value = {
            "outputPath": "/path/to/video.mkv"
        }
        
        result = self.recording_manager.stop()
        self.assertEqual(result["output_path"], "/path/to/video.mkv")
    
    def test_get_status(self):
        """Test getting recording status."""
        self.mock_client.get_recording_status.return_value = {
            "outputActive": True,
            "outputPaused": False,
            "outputDuration": 100
        }
        
        status = self.recording_manager.get_status()
        self.assertTrue(status["active"])
        self.assertFalse(status["paused"])
        self.assertEqual(status["duration"], 100)


class TestStreamingManager(unittest.TestCase):
    """Test StreamingManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.streaming_manager = StreamingManager(self.mock_client)
    
    def test_start_streaming(self):
        """Test starting streaming."""
        self.streaming_manager.start()
        self.mock_client.start_streaming.assert_called_once()
    
    def test_get_status(self):
        """Test getting streaming status."""
        self.mock_client.get_streaming_status.return_value = {
            "outputActive": True,
            "outputDuration": 500
        }
        
        status = self.streaming_manager.get_status()
        self.assertTrue(status["active"])
        self.assertEqual(status["duration"], 500)


if __name__ == "__main__":
    unittest.main()
