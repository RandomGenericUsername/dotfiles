# How to Use the AI Integration Documents

## Quick Start

### Step 1: Copy the Prompt

Copy the entire content of this file and paste it to your AI tool:
```
SOCKET_INTEGRATION_PROMPT.txt
```

### Step 2: Let the AI Work

The AI will:
1. Read the integration guide (`WALLPAPER_ORCHESTRATOR_INTEGRATION.md`)
2. Read the requirements document (`AI_INTEGRATION_PROMPT.md`)
3. Implement the socket integration following the guide
4. Run quality checks and tests
5. Verify the implementation

### Step 3: Review the Changes

After the AI completes, review:
- New file: `src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/socket_manager.py`
- Modified: `src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/orchestrator.py`
- Modified: `src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/cli.py`
- Modified: `src/common/tools/wallpaper-orchestrator/pyproject.toml`

## Documents Overview

### 1. SOCKET_INTEGRATION_PROMPT.txt (ROOT LEVEL)
**Location**: `/home/inumaki/Development/new/SOCKET_INTEGRATION_PROMPT.txt`

**Purpose**: The actual prompt to give to the AI tool

**Content**: Concise instructions that tell the AI to:
- Read the integration guide first
- Follow it exactly
- Create/modify specific files
- Verify the implementation

**Usage**: Copy this entire file and paste it as your prompt to the AI tool.

---

### 2. WALLPAPER_ORCHESTRATOR_INTEGRATION.md
**Location**: `src/common/modules/socket/docs/WALLPAPER_ORCHESTRATOR_INTEGRATION.md`

**Purpose**: Complete technical integration guide with working code

**Content**:
- Architecture overview
- Step-by-step implementation (4 steps)
- Complete code examples (copy-paste ready)
- Testing instructions
- Message format specifications
- Configuration options
- Troubleshooting guide

**Key Feature**: Contains complete, tested code that can be used as-is.

---

### 3. AI_INTEGRATION_PROMPT.md
**Location**: `src/common/modules/socket/docs/AI_INTEGRATION_PROMPT.md`

**Purpose**: Detailed requirements and verification checklist

**Content**:
- Implementation requirements
- Code quality standards
- Testing requirements
- What NOT to do (common mistakes)
- Verification checklist (11 items)
- Example usage

**Key Feature**: Comprehensive checklist to ensure nothing is missed.

---

### 4. INTEGRATION_SUMMARY.md
**Location**: `src/common/modules/socket/docs/INTEGRATION_SUMMARY.md`

**Purpose**: Summary of all documents and quick reference

**Content**:
- Document descriptions
- Quick API reference
- Integration pattern examples
- File locations
- Success criteria

**Key Feature**: Quick reference for both humans and AI.

---

## The Exact Prompt to Use

```
Integrate the socket module into the wallpaper orchestrator tool to enable real-time progress updates during wallpaper changes.

CRITICAL INSTRUCTIONS:

1. FIRST, read and understand these documents IN ORDER:
   - src/common/modules/socket/docs/WALLPAPER_ORCHESTRATOR_INTEGRATION.md (COMPLETE integration guide with working code)
   - src/common/modules/socket/docs/AI_INTEGRATION_PROMPT.md (Detailed requirements and checklist)
   - src/common/modules/socket/README.md (Socket module API reference)

2. FOLLOW the integration guide EXACTLY - it contains complete, tested code examples.

3. CREATE/MODIFY these files only:
   - CREATE: src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/socket_manager.py
   - MODIFY: src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/orchestrator.py
   - MODIFY: src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/cli.py
   - MODIFY: src/common/tools/wallpaper-orchestrator/pyproject.toml

4. DO NOT modify the socket module itself - it's complete and tested.

5. VERIFY your implementation:
   - Run: make format && make lint && make type-check
   - Test with actual wallpaper change + client connection
   - Ensure all quality checks pass

The integration guide contains complete working code. Read it carefully and follow it exactly.
```

---

## What the AI Will Do

### Phase 1: Reading (2-3 minutes)
- Read integration guide
- Read requirements document
- Read socket module README
- Understand architecture and requirements

### Phase 2: Implementation (5-10 minutes)
- Add socket dependency to pyproject.toml
- Run `uv sync`
- Create socket_manager.py with complete implementation
- Modify orchestrator.py to use socket manager
- Modify cli.py to add socket-dir option

### Phase 3: Verification (2-3 minutes)
- Run `make format && make lint && make type-check`
- Fix any issues
- Verify all quality checks pass

### Phase 4: Testing (3-5 minutes)
- Test basic functionality (server + client)
- Test error handling
- Verify messages are received correctly

**Total Time**: ~15-20 minutes

---

## Expected Output

After the AI completes, you should have:

1. **New File**: `socket_manager.py`
   - `WallpaperProgressSocketManager` class
   - Methods: `start()`, `stop()`, `send_progress()`, `send_error()`
   - Context manager support

2. **Modified**: `orchestrator.py`
   - Creates socket manager instance
   - Uses context manager for lifecycle
   - Wires pipeline callbacks to socket manager

3. **Modified**: `cli.py`
   - Added `--socket-dir` option
   - Passes option to orchestrator

4. **Modified**: `pyproject.toml`
   - Added `dotfiles-socket` dependency

5. **All Quality Checks Passing**
   - Formatting: ✅
   - Linting: ✅
   - Type checking: ✅

---

## Testing After Integration

### Terminal 1: Start Wallpaper Change
```bash
cd src/common/tools/wallpaper-orchestrator
uv run dotfiles-wallpaper-orchestrator change /path/to/wallpaper.jpg
```

### Terminal 2: Monitor Progress
```bash
cd src/common/modules/socket
uv run python -c "
from dotfiles_socket import create_client, SocketType

client = create_client(SocketType.UNIX, 'wallpaper_progress')
client.connect()

print('Connected! Waiting for progress updates...')
for msg in client.receive_iter():
    data = msg.data
    if data.get('status') == 'complete':
        print(f'✅ Complete!')
        break
    elif data.get('status') == 'error':
        print(f'❌ Error: {data.get(\"error\")}')
        break
    else:
        print(f'📊 {data.get(\"step\")}: {data.get(\"progress\")}%')

client.disconnect()
"
```

**Expected Output** (Terminal 2):
```
Connected! Waiting for progress updates...
📊 generate_colorscheme: 33.33%
📊 create_effects: 66.67%
📊 change_wallpaper: 100.0%
✅ Complete!
```

---

## Troubleshooting

### If AI doesn't read the documents:
- Emphasize "FIRST, read these documents"
- Provide the file paths explicitly
- Ask "Have you read the integration guide?"

### If AI creates wrong files:
- Point to the file list in the prompt
- Remind: "Only create/modify the files listed"

### If AI modifies socket module:
- Remind: "DO NOT modify the socket module"
- It's complete and tested

### If quality checks fail:
- Ask AI to run: `make format && make lint && make type-check`
- Ask AI to fix the issues
- Verify again

---

## Success Indicators

✅ Socket dependency added and synced
✅ Socket manager class created
✅ Orchestrator uses socket manager with context manager
✅ Pipeline callbacks wired correctly
✅ CLI updated with socket-dir option
✅ All quality checks passing
✅ Manual test successful (server sends, client receives)

---

## Additional Resources

- **Socket Module README**: `src/common/modules/socket/README.md`
- **Socket Module Architecture**: `src/common/modules/socket/docs/ARCHITECTURE.md`
- **Pipeline Module Docs**: (if available in your project)

---

## Notes

- The socket module is **production-ready** (52 tests, 100% passing)
- The integration is **straightforward** (mostly wiring)
- The code examples are **complete and tested**
- The AI should **follow the guide exactly**
