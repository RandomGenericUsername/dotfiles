# AI Tool Integration Prompt

## Task: Integrate Socket Module for Real-Time Wallpaper Progress Updates

You are tasked with integrating the socket module into the wallpaper orchestrator tool to enable real-time progress updates during wallpaper changes.

## CRITICAL: Read the Integration Guide First

**BEFORE making ANY changes**, you MUST:

1. **Read the complete integration guide**:
   ```
   src/common/modules/socket/docs/WALLPAPER_ORCHESTRATOR_INTEGRATION.md
   ```

2. **Understand the architecture** described in the guide:
   - Socket module location and capabilities
   - Wallpaper orchestrator structure
   - Pipeline module integration points
   - Message format and lifecycle

3. **Follow the implementation steps EXACTLY** as documented:
   - Step 1: Add socket dependency
   - Step 2: Create socket manager class
   - Step 3: Integrate with pipeline module
   - Step 4: Update CLI command

## Implementation Requirements

### 1. Code Location and Structure

**Wallpaper Orchestrator Location**:
- Tool path: `src/common/tools/wallpaper-orchestrator/`
- Package name: `dotfiles-wallpaper-orchestrator`

**Files to Create/Modify**:
- CREATE: `src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/socket_manager.py`
- MODIFY: `src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/orchestrator.py`
- MODIFY: `src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/cli.py`
- MODIFY: `src/common/tools/wallpaper-orchestrator/pyproject.toml`

### 2. Socket Manager Implementation

The socket manager class (`WallpaperProgressSocketManager`) MUST:
- Use the socket module's factory functions (`create_server`, `create_message`)
- Support context manager protocol (`__enter__`, `__exit__`)
- Provide methods: `start()`, `stop()`, `send_progress()`, `send_error()`
- Use event name: `"wallpaper_progress"` (default)
- Handle errors gracefully without breaking wallpaper changes

**IMPORTANT**: The complete implementation is provided in the integration guide. Use it EXACTLY as shown.

### 3. Pipeline Integration

The orchestrator MUST:
- Start socket server BEFORE pipeline execution
- Stop socket server AFTER pipeline execution (use context manager)
- Connect pipeline callbacks to socket manager:
  - `on_progress` → `socket_manager.send_progress()`
  - `on_error` → `socket_manager.send_error()`
- Send final completion message after pipeline succeeds

**IMPORTANT**: The pipeline module already supports progress callbacks. You just need to wire them to the socket manager.

### 4. Message Format

Progress messages MUST include:
- `step`: Name of current step (string)
- `progress`: Progress percentage 0-100 (float)
- `status`: One of "processing", "complete", "error" (string)

Error messages MUST include:
- `error`: Error description (string)
- `step`: Step where error occurred (string, optional)
- `status`: "error" (string)

### 5. Dependencies

Add to `pyproject.toml`:
```toml
dependencies = [
    "dotfiles-socket",
    # ... existing dependencies
]
```

Then run: `uv sync`

## Testing Requirements

After implementation, you MUST:

1. **Run quality checks**:
   ```bash
   cd src/common/tools/wallpaper-orchestrator
   make format && make lint && make type-check
   ```

2. **Test basic functionality**:
   - Start wallpaper change in one terminal
   - Connect client in another terminal to receive updates
   - Verify progress messages are received
   - Verify completion message is received

3. **Test error handling**:
   - Trigger an error in the pipeline
   - Verify error message is sent via socket
   - Verify wallpaper change fails gracefully

## Code Quality Standards

Your implementation MUST:
- Follow existing code style (79 char line length)
- Use type hints for all functions and methods
- Include docstrings for all classes and public methods
- Handle exceptions gracefully with proper logging
- Pass all linting and type checking (mypy strict mode)

## What NOT to Do

❌ **DO NOT**:
- Modify the socket module itself (it's complete and tested)
- Change the pipeline module (it already has callback support)
- Create new socket implementations (use the factory functions)
- Hardcode socket paths (use config or defaults)
- Block the main thread (socket server runs in separate thread)
- Create documentation files (only code changes)

## Verification Checklist

Before considering the task complete, verify:

- [ ] Socket dependency added to pyproject.toml
- [ ] `uv sync` executed successfully
- [ ] `socket_manager.py` created with complete implementation
- [ ] Orchestrator modified to use socket manager with context manager
- [ ] Pipeline callbacks wired to socket manager methods
- [ ] CLI command updated (optional socket-dir parameter)
- [ ] All quality checks passing (format, lint, type-check)
- [ ] Manual testing completed (server + client)
- [ ] Error handling tested
- [ ] No new files created beyond what's specified

## Example Usage After Implementation

```bash
# Terminal 1: Change wallpaper
dotfiles-wallpaper-orchestrator change /path/to/wallpaper.jpg

# Terminal 2: Monitor progress
python -c "
from dotfiles_socket import create_client, SocketType
client = create_client(SocketType.UNIX, 'wallpaper_progress')
client.connect()
for msg in client.receive_iter():
    print(f'{msg.data}')
    if msg.data.get('status') in ('complete', 'error'):
        break
client.disconnect()
"
```

## Getting Help

If you encounter issues:

1. **Re-read the integration guide** - The answer is likely there
2. **Check socket module README** - `src/common/modules/socket/README.md`
3. **Review socket module examples** - They show correct usage patterns
4. **Check existing pipeline usage** - See how other tools use pipeline callbacks

## Final Notes

- The socket module is **production-ready** and **fully tested** (52 tests, 100% passing)
- The integration is **straightforward** - mostly wiring existing components
- The socket server is **non-blocking** - won't slow down wallpaper changes
- Multiple clients can connect simultaneously (broadcast mode)
- Messages are queued if no clients connected (up to 100 messages)

**Remember**: Read the integration guide thoroughly before starting. It contains complete, working code examples that you should follow exactly.
