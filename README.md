# CLI-Anything OBS Studio

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A command-line interface for controlling OBS Studio via WebSocket.

## Features

- 🎬 **Scene Management** - List and switch scenes
- 🎥 **Recording Control** - Start, stop, pause recordings
- 📡 **Streaming Control** - Start and stop streaming
- 🔄 **Replay Buffer** - Save instant replays
- 📊 **Performance Stats** - View CPU, memory, FPS metrics
- 💻 **Interactive REPL** - Full command-line interface
- 🤖 **JSON Output** - Machine-readable for automation

## Prerequisites

- [OBS Studio](https://obsproject.com/) installed
- [obs-websocket](https://github.com/obsproject/obs-websocket) plugin enabled
- Python 3.8+

## Installation

### From GitHub

```bash
pip install git+https://github.com/160037lk/cli-anything-obs-studio.git#subdirectory=agent-harness
```

### From Source

```bash
git clone https://github.com/160037lk/cli-anything-obs-studio.git
cd cli-anything-obs-studio/agent-harness
pip install -e .
```

## Quick Start

1. **Start OBS Studio** and enable WebSocket:
   - Go to `Tools` → `WebSocket Server Settings`
   - Enable WebSocket server
   - Set port (default: 4455)
   - Optional: Set password

2. **Launch the CLI**:
   ```bash
   cli-anything-obs-studio
   ```

3. **Start controlling OBS**:
   ```
   obs[当前场景]> scenes
   obs[当前场景]> scene "游戏画面"
   obs[游戏画面]> record start
   ```

## Usage

### Interactive REPL Mode (Default)

```bash
cli-anything-obs-studio
```

Available REPL commands:
- `help` - Show all commands
- `status` - Show OBS status
- `scenes` - List all scenes
- `scene <name>` - Switch to scene
- `sources [scene]` - List sources
- `record [start|stop|pause|status]` - Control recording
- `stream [start|stop|status]` - Control streaming
- `replay [start|stop|save|status]` - Control replay buffer
- `stats` - Show performance stats
- `exit` or `quit` - Exit CLI

### One-shot Commands

```bash
# Get OBS status
cli-anything-obs-studio status

# List all scenes
cli-anything-obs-studio scenes

# Switch to a scene
cli-anything-obs-studio scene "Game Capture"

# Control recording
cli-anything-obs-studio record start
cli-anything-obs-studio record stop
cli-anything-obs-studio record pause

# Control streaming
cli-anything-obs-studio stream start
cli-anything-obs-studio stream stop

# Save replay buffer
cli-anything-obs-studio replay save

# JSON output for scripting
cli-anything-obs-studio --json status
```

### Connection Options

```bash
# Custom host/port
cli-anything-obs-studio -h 192.168.1.100 -p 4455 status

# With password
cli-anything-obs-studio -h localhost -p 4455 -P mypassword status
```

## Environment Variables

- `OBS_WEBSOCKET_HOST` - Default host (default: localhost)
- `OBS_WEBSOCKET_PORT` - Default port (default: 4455)
- `OBS_WEBSOCKET_PASSWORD` - WebSocket password

## Project Structure

```
cli-anything-obs-studio/
├── agent-harness/
│   ├── setup.py              # Package configuration
│   ├── OBS_STUDIO.md         # Technical documentation
│   └── cli_anything/
│       └── obs_studio/
│           ├── README.md     # Usage documentation
│           ├── obs_studio_cli.py
│           ├── core/         # Core modules
│           │   ├── session.py
│           │   ├── scene.py
│           │   ├── source.py
│           │   ├── recording.py
│           │   ├── streaming.py
│           │   ├── replay_buffer.py
│           │   └── stats.py
│           ├── utils/
│           │   └── obs_websocket.py
│           └── tests/
│               ├── test_core.py
│               └── test_full_e2e.py
```

## Development

```bash
# Install in development mode
cd agent-harness
pip install -e .

# Run tests
python -m pytest cli_anything/obs_studio/tests/
```

## Built With

- [Click](https://click.palletsprojects.com/) - Command-line interface framework
- [prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/) - Interactive REPL
- [obs-websocket](https://github.com/obsproject/obs-websocket) - OBS WebSocket protocol

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [CLI-Anything](https://github.com/HKUDS/CLI-Anything) framework
- Thanks to the OBS Studio team for the amazing software

## Related

- [OBS Studio](https://obsproject.com/)
- [obs-websocket](https://github.com/obsproject/obs-websocket)
- [CLI-Anything](https://github.com/HKUDS/CLI-Anything)

---

**Made with ❤️ by [160037lk](https://github.com/160037lk)**
