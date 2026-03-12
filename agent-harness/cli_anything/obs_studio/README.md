# CLI-Anything OBS Studio

A command-line interface for controlling OBS Studio via WebSocket.

## Prerequisites

- OBS Studio installed
- obs-websocket plugin installed and enabled
- Python 3.8+

## Installation

```bash
pip install -e .
```

## Usage

### Interactive REPL Mode (Default)

```bash
cli-anything-obs-studio
```

### One-shot Commands

```bash
# Get status
cli-anything-obs-studio status

# List scenes
cli-anything-obs-studio scenes

# Switch scene
cli-anything-obs-studio scene "Game Capture"

# List sources
cli-anything-obs-studio sources
cli-anything-obs-studio sources -s "Scene Name"

# Control recording
cli-anything-obs-studio record start
cli-anything-obs-studio record stop
cli-anything-obs-studio record pause
cli-anything-obs-studio record status

# Control streaming
cli-anything-obs-studio stream start
cli-anything-obs-studio stream stop
cli-anything-obs-studio stream status

# Control replay buffer
cli-anything-obs-studio replay save
cli-anything-obs-studio replay start
cli-anything-obs-studio replay stop
```

### Connection Options

```bash
# Custom host/port
cli-anything-obs-studio -h 192.168.1.100 -p 4455 status

# With password
cli-anything-obs-studio -h localhost -p 4455 -P mypassword status

# JSON output
cli-anything-obs-studio --json status
```

## Environment Variables

- `OBS_WEBSOCKET_HOST` - Default host (default: localhost)
- `OBS_WEBSOCKET_PORT` - Default port (default: 4455)
- `OBS_WEBSOCKET_PASSWORD` - WebSocket password

## REPL Commands

When in interactive mode:

- `help` - Show available commands
- `status` - Show OBS status
- `scenes` - List all scenes
- `scene <name>` - Switch to scene
- `sources [scene]` - List sources
- `record [start|stop|pause|status]` - Control recording
- `stream [start|stop|status]` - Control streaming
- `replay [start|stop|save|status]` - Control replay buffer
- `stats` - Show performance stats
- `screenshot [source]` - Take a screenshot
- `exit` or `quit` - Exit REPL

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest cli_anything/obs_studio/tests/
```

## License

MIT
