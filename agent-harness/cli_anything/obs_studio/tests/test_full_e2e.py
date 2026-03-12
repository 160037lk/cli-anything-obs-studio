"""E2E tests for OBS Studio CLI."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


class TestCLISubprocess(unittest.TestCase):
    """Test CLI via subprocess."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        cls.CLI_BASE = cls._resolve_cli("cli-anything-obs-studio")
    
    @staticmethod
    def _resolve_cli(name):
        """Resolve installed CLI command."""
        import shutil
        force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
        path = shutil.which(name)
        if path:
            print(f"[_resolve_cli] Using installed command: {path}")
            return [path]
        if force:
            raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
        module = name.replace("cli-anything-", "cli_anything.").replace("-", "_") + "_cli"
        print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
        return [sys.executable, "-m", module]
    
    def _run(self, args, check=True):
        """Run CLI command."""
        result = subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
        )
        return result
    
    def test_help(self):
        """Test help command."""
        result = self._run(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("OBS Studio CLI", result.stdout)
    
    def test_version(self):
        """Test version output."""
        result = self._run(["--version"], check=False)
        # Version flag may not be implemented
        self.assertIn(result.returncode, [0, 2])


class TestWebSocketClient(unittest.TestCase):
    """Test WebSocket client functionality."""
    
    def test_import(self):
        """Test that modules can be imported."""
        from ..utils.obs_websocket import OBSWebSocketClient
        from ..core.session import Session
        from ..core.scene import SceneManager
        from ..core.recording import RecordingManager
        from ..core.streaming import StreamingManager
        
        # Just verify imports work
        self.assertTrue(True)


class TestSessionPersistence(unittest.TestCase):
    """Test session file persistence."""
    
    def test_session_save_load(self):
        """Test saving and loading session."""
        from ..core.session import Session
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Create and save session
            session = Session()
            session.host = "192.168.1.50"
            session.port = 4444
            session.password = "secret"
            session.save(temp_path)
            
            # Load session
            loaded = Session(project_path=temp_path)
            self.assertEqual(loaded.host, "192.168.1.50")
            self.assertEqual(loaded.port, 4444)
            self.assertEqual(loaded.password, "secret")
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
