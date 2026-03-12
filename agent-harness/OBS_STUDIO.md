# OBS Studio CLI - Project Documentation

## Overview

This CLI provides a command-line interface for controlling OBS Studio via the obs-websocket plugin. It supports both interactive REPL mode and one-shot commands for scripting.

## Architecture

### Backend Integration

The CLI uses OBS WebSocket protocol to communicate with OBS Studio:
- **Protocol**: WebSocket (RFC 6455)
- **Default Port**: 4455
- **Authentication**: Optional password-based

### Module Structure

```
cli_anything/obs_studio/
├── core/
│   ├── session.py         # WebSocket connection management
│   ├── scene.py           # Scene operations
│   ├── source.py          # Source management
│   ├── recording.py       # Recording control
│   ├── streaming.py       # Streaming control
│   ├── replay_buffer.py   # Replay buffer control
│   └── stats.py           # Performance statistics
├── utils/
│   └── obs_websocket.py   # WebSocket client implementation
├── obs_studio_cli.py      # Main CLI entry point
└── README.md              # User documentation
```

## Supported Operations

### Scenes
- List all scenes
- Get current scene
- Switch scenes
- Create/remove scenes

### Sources
- List sources in a scene
- Get/set source settings
- Control source visibility
- Get source transforms

### Recording
- Start/stop recording
- Pause/resume recording
- Get recording status

### Streaming
- Start/stop streaming
- Get streaming status
- Send stream captions

### Replay Buffer
- Start/stop replay buffer
- Save replay buffer

### Stats
- Get performance statistics
- Get video settings

## Implementation Notes

### WebSocket Protocol

The CLI implements a basic WebSocket client for communicating with OBS:
- Text frames for JSON-RPC requests/responses
- Supports authentication challenge-response
- Event handling for OBS state changes

### Error Handling

All operations include proper error handling:
- Connection errors (OBS not running)
- Authentication errors (wrong password)
- Request errors (invalid parameters)

### JSON Output Mode

All commands support `--json` flag for machine-readable output, suitable for:
- Scripting
- Integration with other tools
- Agent consumption

## Testing

### Manual Testing

1. Start OBS Studio with WebSocket enabled
2. Run CLI commands:
   ```bash
   cli-anything-obs-studio status
   cli-anything-obs-studio scenes
   cli-anything-obs-studio record start
   ```

### Automated Testing

See `tests/` directory for unit and E2E tests.

## Future Enhancements

- [ ] Support for OBS filters
- [ ] Transition control
- [ ] Virtual camera control
- [ ] Profile/scene collection management
- [ ] Hotkey triggering
