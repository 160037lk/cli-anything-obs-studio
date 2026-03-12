"""OBS Studio CLI - Control OBS via WebSocket."""
import json
import os
import sys
from typing import Optional

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from .core.session import Session
from .core.scene import SceneManager
from .core.source import SourceManager
from .core.recording import RecordingManager
from .core.streaming import StreamingManager
from .core.replay_buffer import ReplayBufferManager
from .core.stats import StatsManager


# REPL style
REPL_STYLE = Style.from_dict({
    'prompt': '#00aa00 bold',
    'obs': '#0088ff bold',
    'recording': '#ff0000 bold',
    'streaming': '#ff8800 bold',
})


class OBSCLI:
    """OBS Studio CLI main class."""
    
    def __init__(self):
        self.session: Optional[Session] = None
        self.scene_manager: Optional[SceneManager] = None
        self.source_manager: Optional[SourceManager] = None
        self.recording_manager: Optional[RecordingManager] = None
        self.streaming_manager: Optional[StreamingManager] = None
        self.replay_buffer_manager: Optional[ReplayBufferManager] = None
        self.stats_manager: Optional[StatsManager] = None
    
    def connect(self, host: str = "localhost", port: int = 4455, 
                password: Optional[str] = None) -> None:
        """Connect to OBS."""
        if self.session is None:
            self.session = Session()
            self.session.host = host
            self.session.port = port
            self.session.password = password
        
        client = self.session.connect()
        
        # Initialize managers
        self.scene_manager = SceneManager(client)
        self.source_manager = SourceManager(client)
        self.recording_manager = RecordingManager(client)
        self.streaming_manager = StreamingManager(client)
        self.replay_buffer_manager = ReplayBufferManager(client)
        self.stats_manager = StatsManager(client)
    
    def disconnect(self) -> None:
        """Disconnect from OBS."""
        if self.session:
            self.session.disconnect()
            self.session = None
            self.scene_manager = None
            self.source_manager = None
            self.recording_manager = None
            self.streaming_manager = None
            self.replay_buffer_manager = None
            self.stats_manager = None
    
    def is_connected(self) -> bool:
        """Check if connected to OBS."""
        return self.session is not None and self.session.is_connected()


# Global CLI instance
cli_instance = OBSCLI()


@click.group(invoke_without_command=True)
@click.option('--host', '-h', default='localhost', help='OBS WebSocket host')
@click.option('--port', '-p', default=4455, type=int, help='OBS WebSocket port')
@click.option('--password', '-P', default=None, help='OBS WebSocket password')
@click.option('--project', '-j', default=None, help='Project file path')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON')
@click.pass_context
def cli(ctx, host, port, password, project, json_output):
    """OBS Studio CLI - Control OBS via WebSocket."""
    ctx.ensure_object(dict)
    ctx.obj['json_output'] = json_output
    ctx.obj['project'] = project
    
    if ctx.invoked_subcommand is None:
        # Start REPL
        ctx.invoke(repl, host=host, port=port, password=password, project=project)


@cli.command()
@click.option('--host', '-h', default='localhost', help='OBS WebSocket host')
@click.option('--port', '-p', default=4455, type=int, help='OBS WebSocket port')
@click.option('--password', '-P', default=None, help='OBS WebSocket password')
@click.option('--project', '-j', default=None, help='Project file path')
def repl(host, port, password, project):
    """Start interactive REPL."""
    print("\n" + "="*50)
    print("  OBS Studio CLI")
    print("  Control OBS via WebSocket")
    print("="*50 + "\n")
    
    # Connect to OBS
    try:
        cli_instance.connect(host, port, password)
        version = cli_instance.session.client.get_version()
        print(f"✓ Connected to OBS {version.get('obs-studio-version', 'unknown')}")
        print(f"  WebSocket version: {version.get('obs-websocket-version', 'unknown')}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("  Make sure OBS is running and WebSocket server is enabled.")
        return
    
    print("\nType 'help' for commands, 'exit' to quit.\n")
    
    # Setup prompt
    history_file = os.path.expanduser('~/.obs_cli_history')
    session = PromptSession(
        history=FileHistory(history_file),
        completer=WordCompleter([
            'help', 'exit', 'status', 'scenes', 'scene', 'sources', 'source',
            'record', 'stream', 'replay', 'stats', 'screenshot'
        ]),
        style=REPL_STYLE
    )
    
    while True:
        try:
            # Build prompt
            prompt_text = "obs> "
            if cli_instance.is_connected():
                try:
                    current = cli_instance.scene_manager.get_current()
                    prompt_text = f"obs[{current}]> "
                except:
                    prompt_text = "obs> "
            
            # Get input
            text = session.prompt(prompt_text).strip()
            if not text:
                continue
            
            # Parse command
            parts = text.split()
            cmd = parts[0].lower()
            args = parts[1:]
            
            # Execute command
            if cmd == 'exit' or cmd == 'quit':
                break
            elif cmd == 'help':
                _print_help()
            elif cmd == 'status':
                _print_status()
            elif cmd == 'scenes':
                _list_scenes()
            elif cmd == 'scene':
                if args:
                    _switch_scene(args[0])
                else:
                    print("Usage: scene <scene-name>")
            elif cmd == 'sources':
                _list_sources(args[0] if args else None)
            elif cmd == 'record':
                _handle_record(args)
            elif cmd == 'stream':
                _handle_stream(args)
            elif cmd == 'replay':
                _handle_replay(args)
            elif cmd == 'stats':
                _print_stats()
            elif cmd == 'screenshot':
                _take_screenshot(args[0] if args else None)
            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    # Cleanup
    cli_instance.disconnect()
    print("\nGoodbye!")


def _print_help():
    """Print help information."""
    print("""
Available commands:
  help              Show this help message
  status            Show OBS status
  scenes            List all scenes
  scene <name>      Switch to scene
  sources [scene]   List sources in current or specified scene
  record [start|stop|pause|status]  Control recording
  stream [start|stop|status]        Control streaming
  replay [start|stop|save|status]   Control replay buffer
  stats             Show performance stats
  screenshot [source]  Take a screenshot
  exit, quit        Exit the CLI
""")


def _print_status():
    """Print OBS status."""
    if not cli_instance.is_connected():
        print("Not connected to OBS")
        return
    
    status = cli_instance.session.get_status()
    print(f"Connected: {status.get('connected', False)}")
    print(f"OBS Version: {status.get('obs_version', 'unknown')}")
    print(f"Current Scene: {status.get('current_scene', 'none')}")
    print(f"Recording: {'Active' if status.get('recording') else 'Inactive'}")
    if status.get('recording_paused'):
        print("  (Paused)")
    print(f"Streaming: {'Active' if status.get('streaming') else 'Inactive'}")


def _list_scenes():
    """List all scenes."""
    if not cli_instance.is_connected():
        print("Not connected to OBS")
        return
    
    try:
        scenes = cli_instance.scene_manager.list_scenes()
        current = cli_instance.scene_manager.get_current()
        print(f"\nScenes ({len(scenes)} total):")
        for scene in scenes:
            name = scene.get('sceneName', 'unnamed')
            marker = "* " if name == current else "  "
            print(f"{marker}{name}")
        print()
    except Exception as e:
        print(f"Error listing scenes: {e}")


def _switch_scene(scene_name: str):
    """Switch to a scene."""
    if not cli_instance.is_connected():
        print("Not connected to OBS")
        return
    
    try:
        cli_instance.scene_manager.set_current(scene_name)
        print(f"Switched to scene: {scene_name}")
    except Exception as e:
        print(f"Error switching scene: {e}")


def _list_sources(scene_name: Optional[str] = None):
    """List sources in a scene."""
    if not cli_instance.is_connected():
        print("Not connected to OBS")
        return
    
    try:
        target_scene = scene_name or cli_instance.scene_manager.get_current()
        sources = cli_instance.source_manager.list_sources(target_scene)
        print(f"\nSources in '{target_scene}' ({len(sources)} total):")
        for source in sources:
            name = source.get('sourceName', 'unnamed')
            visible = "visible" if source.get('sceneItemEnabled') else "hidden"
            print(f"  - {name} ({visible})")
        print()
    except Exception as e:
        print(f"Error listing sources: {e}")


def _handle_record(args):
    """Handle record command."""
    if not cli_instance.is_connected():
        print("Not connected to OBS")
        return
    
    action = args[0] if args else "toggle"
    
    try:
        if action == "start":
            cli_instance.recording_manager.start()
            print("Recording started")
        elif action == "stop":
            result = cli_instance.recording_manager.stop()
            print(f"Recording stopped")
            if result.get('output_path'):
                print(f"  Saved to: {result['output_path']}")
        elif action == "pause":
            cli_instance.recording_manager.pause()
            print("Recording paused")
        elif action == "resume":
            cli_instance.recording_manager.resume()
            print("Recording resumed")
        elif action == "status":
            status = cli_instance.recording_manager.get_status()
            print(f"Recording: {'Active' if status.get('active') else 'Inactive'}")
            if status.get('active'):
                print(f"  Duration: {status.get('duration', 0)}s")
                print(f"  Size: {status.get('size', 0)} bytes")
        else:
            # Toggle
            result = cli_instance.recording_manager.toggle()
            print(f"Recording {result.get('status', 'toggled')}")
    except Exception as e:
        print(f"Error: {e}")


def _handle_stream(args):
    """Handle stream command."""
    if not cli_instance.is_connected():
        print("Not connected to OBS")
        return
    
    action = args[0] if args else "toggle"
    
    try:
        if action == "start":
            cli_instance.streaming_manager.start()
            print("Streaming started")
        elif action == "stop":
            cli_instance.streaming_manager.stop()
            print("Streaming stopped")
        elif action == "status":
            status = cli_instance.streaming_manager.get_status()
            print(f"Streaming: {'Active' if status.get('active') else 'Inactive'}")
            if status.get('active'):
                print(f"  Duration: {status.get('duration', 0)}s")
        else:
            # Toggle
            result = cli_instance.streaming_manager.toggle()
            print(f"Streaming {result.get('status', 'toggled')}")
    except Exception as e:
        print(f"Error: {e}")


def _handle_replay(args):
    """Handle replay buffer command."""
    if not cli_instance.is_connected():
        print("Not connected to OBS")
        return
    
    action = args[0] if args else "save"
    
    try:
        if action == "start":
            cli_instance.replay_buffer_manager.start()
            print("Replay buffer started")
        elif action == "stop":
            cli_instance.replay_buffer_manager.stop()
            print("Replay buffer stopped")
        elif action == "save":
            result = cli_instance.replay_buffer_manager.save()
            print("Replay saved")
        elif action == "status":
            status = cli_instance.replay_buffer_manager.get_status()
            print(f"Replay buffer: {'Active' if status.get('outputActive') else 'Inactive'}")
        else:
            result = cli_instance.replay_buffer_manager.toggle()
            print(f"Replay buffer {result.get('status', 'toggled')}")
    except Exception as e:
        print(f"Error: {e}")


def _print_stats():
    """Print performance stats."""
    if not cli_instance.is_connected():
        print("Not connected to OBS")
        return
    
    try:
        stats = cli_instance.stats_manager.get_performance_stats()
        print("\nPerformance Stats:")
        print(f"  CPU Usage: {stats.get('cpu_usage', 0):.1f}%")
        print(f"  Memory Usage: {stats.get('memory_usage', 0):.1f} MB")
        print(f"  FPS: {stats.get('active_frames', 0):.1f}")
        print(f"  Frame Render Time: {stats.get('average_frame_render_time', 0):.2f}ms")
        print()
    except Exception as e:
        print(f"Error getting stats: {e}")


def _take_screenshot(source_name: Optional[str] = None):
    """Take a screenshot."""
    if not cli_instance.is_connected():
        print("Not connected to OBS")
        return
    
    try:
        result = cli_instance.source_manager.get_source_screenshot(
            source_name or "",
            file_path=None,
            format="png"
        )
        print("Screenshot taken")
        if result.get('imageData'):
            print("  (Image data available in response)")
    except Exception as e:
        print(f"Error taking screenshot: {e}")


# Subcommands for one-shot usage
@cli.command()
@click.option('--host', '-h', default='localhost', help='OBS WebSocket host')
@click.option('--port', '-p', default=4455, type=int, help='OBS WebSocket port')
@click.option('--password', '-P', default=None, help='OBS WebSocket password')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON')
def status(host, port, password, json_output):
    """Get OBS status."""
    try:
        cli_instance.connect(host, port, password)
        obs_status = cli_instance.session.get_status()
        
        if json_output:
            print(json.dumps(obs_status, indent=2))
        else:
            print(f"Connected: {obs_status.get('connected')}")
            print(f"OBS Version: {obs_status.get('obs_version')}")
            print(f"Current Scene: {obs_status.get('current_scene')}")
            print(f"Recording: {'Active' if obs_status.get('recording') else 'Inactive'}")
            print(f"Streaming: {'Active' if obs_status.get('streaming') else 'Inactive'}")
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
            sys.exit(1)
    finally:
        cli_instance.disconnect()


@cli.command()
@click.option('--host', '-h', default='localhost', help='OBS WebSocket host')
@click.option('--port', '-p', default=4455, type=int, help='OBS WebSocket port')
@click.option('--password', '-P', default=None, help='OBS WebSocket password')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON')
def scenes(host, port, password, json_output):
    """List all scenes."""
    try:
        cli_instance.connect(host, port, password)
        scenes_list = cli_instance.scene_manager.list_scenes()
        current = cli_instance.scene_manager.get_current()
        
        if json_output:
            print(json.dumps({"scenes": scenes_list, "current": current}, indent=2))
        else:
            print(f"Scenes ({len(scenes_list)} total):")
            for scene in scenes_list:
                name = scene.get('sceneName', 'unnamed')
                marker = "* " if name == current else "  "
                print(f"{marker}{name}")
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
            sys.exit(1)
    finally:
        cli_instance.disconnect()


@cli.command()
@click.argument('scene_name')
@click.option('--host', '-h', default='localhost', help='OBS WebSocket host')
@click.option('--port', '-p', default=4455, type=int, help='OBS WebSocket port')
@click.option('--password', '-P', default=None, help='OBS WebSocket password')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON')
def scene(scene_name, host, port, password, json_output):
    """Switch to a scene."""
    try:
        cli_instance.connect(host, port, password)
        cli_instance.scene_manager.set_current(scene_name)
        
        if json_output:
            print(json.dumps({"status": "ok", "scene": scene_name}))
        else:
            print(f"Switched to scene: {scene_name}")
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
            sys.exit(1)
    finally:
        cli_instance.disconnect()


@cli.command()
@click.option('--scene', '-s', default=None, help='Scene name')
@click.option('--host', '-h', default='localhost', help='OBS WebSocket host')
@click.option('--port', '-p', default=4455, type=int, help='OBS WebSocket port')
@click.option('--password', '-P', default=None, help='OBS WebSocket password')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON')
def sources(scene, host, port, password, json_output):
    """List sources in a scene."""
    try:
        cli_instance.connect(host, port, password)
        target_scene = scene or cli_instance.scene_manager.get_current()
        sources_list = cli_instance.source_manager.list_sources(target_scene)
        
        if json_output:
            print(json.dumps({"scene": target_scene, "sources": sources_list}, indent=2))
        else:
            print(f"Sources in '{target_scene}' ({len(sources_list)} total):")
            for source in sources_list:
                name = source.get('sourceName', 'unnamed')
                visible = "visible" if source.get('sceneItemEnabled') else "hidden"
                print(f"  - {name} ({visible})")
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
            sys.exit(1)
    finally:
        cli_instance.disconnect()


@cli.command()
@click.argument('action', default='toggle')
@click.option('--host', '-h', default='localhost', help='OBS WebSocket host')
@click.option('--port', '-p', default=4455, type=int, help='OBS WebSocket port')
@click.option('--password', '-P', default=None, help='OBS WebSocket password')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON')
def record(action, host, port, password, json_output):
    """Control recording (start/stop/pause/status)."""
    try:
        cli_instance.connect(host, port, password)
        
        if action == "start":
            cli_instance.recording_manager.start()
            result = {"status": "started"}
        elif action == "stop":
            result = cli_instance.recording_manager.stop()
        elif action == "pause":
            cli_instance.recording_manager.pause()
            result = {"status": "paused"}
        elif action == "resume":
            cli_instance.recording_manager.resume()
            result = {"status": "resumed"}
        elif action == "status":
            result = cli_instance.recording_manager.get_status()
        else:
            result = cli_instance.recording_manager.toggle()
        
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"Recording {result.get('status', action)}")
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
            sys.exit(1)
    finally:
        cli_instance.disconnect()


@cli.command()
@click.argument('action', default='toggle')
@click.option('--host', '-h', default='localhost', help='OBS WebSocket host')
@click.option('--port', '-p', default=4455, type=int, help='OBS WebSocket port')
@click.option('--password', '-P', default=None, help='OBS WebSocket password')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON')
def stream(action, host, port, password, json_output):
    """Control streaming (start/stop/status)."""
    try:
        cli_instance.connect(host, port, password)
        
        if action == "start":
            cli_instance.streaming_manager.start()
            result = {"status": "started"}
        elif action == "stop":
            cli_instance.streaming_manager.stop()
            result = {"status": "stopped"}
        elif action == "status":
            result = cli_instance.streaming_manager.get_status()
        else:
            result = cli_instance.streaming_manager.toggle()
        
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"Streaming {result.get('status', action)}")
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
            sys.exit(1)
    finally:
        cli_instance.disconnect()


@cli.command()
@click.argument('action', default='save')
@click.option('--host', '-h', default='localhost', help='OBS WebSocket host')
@click.option('--port', '-p', default=4455, type=int, help='OBS WebSocket port')
@click.option('--password', '-P', default=None, help='OBS WebSocket password')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON')
def replay(action, host, port, password, json_output):
    """Control replay buffer (start/stop/save/status)."""
    try:
        cli_instance.connect(host, port, password)
        
        if action == "start":
            cli_instance.replay_buffer_manager.start()
            result = {"status": "started"}
        elif action == "stop":
            cli_instance.replay_buffer_manager.stop()
            result = {"status": "stopped"}
        elif action == "save":
            result = cli_instance.replay_buffer_manager.save()
        elif action == "status":
            result = cli_instance.replay_buffer_manager.get_status()
        else:
            result = cli_instance.replay_buffer_manager.toggle()
        
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"Replay buffer {result.get('status', action)}")
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
            sys.exit(1)
    finally:
        cli_instance.disconnect()


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
