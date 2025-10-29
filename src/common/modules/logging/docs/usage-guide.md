# Logging Module - Complete Usage Guide

## Quick Start

Get up and running with the logging module in seconds:

```python
from cli.modules.logging import Log, LogLevels, ConsoleHandlers

# Simple console logging
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)
logger.info("Hello, world!")

# Rich console logging with features
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH
)
logger.info("Beautiful Rich output!")
logger.table([["Name", "Value"], ["Status", "Ready"]], title="Quick Start")
```

## Core Features

- 🎨 **Rich Integration** - Beautiful tables, panels, progress bars, and more
- 📁 **File Logging** - Multiple file outputs with rotation strategies
- ⚙️ **Type-Safe Configuration** - IDE autocomplete and validation
- 🔧 **Flexible Formatting** - Multiple formatters and custom formats
- 🚀 **Easy API** - Simple create_logger() and update() methods
- 🛡️ **Graceful Fallbacks** - Works even when Rich is unavailable

## Basic Logging

### Console Logging

```python
from cli.modules.logging import Log, LogLevels, ConsoleHandlers, LogFormatters

# Simple console logging
logger = Log.create_logger("app", log_level=LogLevels.INFO)
logger.info("Simple logging message")

# Colored console logging
logger = Log.create_logger(
    "app",
    log_level=LogLevels.INFO,
    formatter_type=LogFormatters.COLORED
)
logger.info("Colored info message")
logger.warning("Colored warning message")
logger.error("Colored error message")

# Rich console logging
logger = Log.create_logger(
    "app",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH
)
logger.info("Beautiful Rich formatting")
```

### Custom Colors

```python
from cli.modules.logging import ColoredFormatterColors

# Custom color scheme
class CustomColors(ColoredFormatterColors):
    DEBUG = "\033[36m"    # Cyan
    INFO = "\033[32m"     # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"    # Red
    CRITICAL = "\033[35m" # Magenta

logger = Log.create_logger(
    "app",
    formatter_type=LogFormatters.COLORED,
    colors=CustomColors  # Pass the class, not an instance
)
```

### Rich Handler Configuration

```python
from cli.modules.logging import RichHandlerSettings

# Detailed Rich configuration
rich_settings = RichHandlerSettings(
    show_time=True,
    show_level=True,
    show_path=False,
    markup=True,
    rich_tracebacks=True,
    keywords=['SUCCESS', 'ERROR', 'WARNING']
)

logger = Log.create_logger(
    "app",
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=rich_settings
)
```

## Rich Features

The logging module provides powerful Rich integration for beautiful console output. Enable Rich features to access tables, panels, progress bars, and more.

### Enabling Rich Features

```python
from cli.modules.logging import (
    Log, LogLevels, ConsoleHandlers, RichFeatureSettings, RichHandlerSettings
)

# Enable Rich features
logger = Log.create_logger(
    "app",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_time=True, markup=True),
    rich_features=RichFeatureSettings(enabled=True)
)

# Now you can use Rich features
logger.info("Standard logging message")
logger.table([["Name", "Status"], ["App", "Running"]], title="Status")
logger.panel("Important message!", title="Alert")
```

### Rich Tables

Display data in beautiful tables with various formats:

```python
# List of rows format (with headers)
data = [
    ["Name", "Age", "City"],      # Header row
    ["Alice", "30", "New York"],
    ["Bob", "25", "London"],
    ["Charlie", "35", "Tokyo"]
]
logger.table(data, title="User Data", show_lines=True)

# Dictionary format (columns)
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": ["30", "25", "35"],
    "City": ["New York", "London", "Tokyo"]
}
logger.table(data, title="User Data", expand=True)

# Custom table styling
logger.table(
    data,
    title="Styled Table",
    show_header=True,
    show_lines=True,
    show_edge=True,
    expand=False
)
```

### Rich Panels

Create highlighted panels for important messages:

```python
# Simple panel
logger.panel("This is important information!")

# Styled panel
logger.panel(
    "Configuration loaded successfully",
    title="Success",
    subtitle="All systems ready",
    border_style="green",
    box_style="rounded"
)

# Panel with custom styling
logger.panel(
    "[bold red]Error occurred![/bold red]\nPlease check your configuration.",
    title="Error",
    border_style="red",
    box_style="double",
    expand=True
)
```

### Rules and Separators

Create visual separators between sections:

```python
# Simple rule
logger.rule("Processing Phase 1")

# Styled rule
logger.rule("Data Analysis", style="bold blue", align="left")

# Section organization
logger.info("Starting application...")
logger.rule("Initialization")
logger.info("Loading configuration...")
logger.info("Connecting to database...")
logger.rule("Main Processing")
logger.info("Processing data...")
logger.rule("Cleanup")
logger.info("Application finished")
```

### Progress Bars

Show progress for long-running operations:

```python
import time

# Simple progress bar
with logger.progress("Processing files", total=100) as progress:
    task = progress.add_task("Processing", total=100)
    for i in range(100):
        time.sleep(0.01)  # Simulate work
        progress.update(task, advance=1)

# Multiple progress bars
with logger.progress() as progress:
    task1 = progress.add_task("Downloading", total=100)
    task2 = progress.add_task("Processing", total=50)

    for i in range(100):
        progress.update(task1, advance=1)
        if i % 2 == 0:
            progress.update(task2, advance=1)
        time.sleep(0.01)

# Progress with logging
with logger.progress("Processing data", total=100) as progress:
    task = progress.add_task("Work", total=100)
    for i in range(100):
        if i % 20 == 0:
            logger.info(f"Processed {i} items")
        progress.update(task, advance=1)
        time.sleep(0.01)
```

### Status Indicators

Show status with spinners:

```python
# Simple status
with logger.status("Loading data...") as status:
    time.sleep(2)  # Simulate work
    status.update("Processing data...")
    time.sleep(2)  # More work

# Custom spinner
with logger.status("Working...", spinner="dots") as status:
    time.sleep(1)
    status.update("Almost done...")
    time.sleep(1)
```

### Tree Display

Display hierarchical data as beautiful tree structures:

```python
# Simple tree from dictionary
file_structure = {
    "config/": {
        "nvim/": {
            "init.lua": "Neovim configuration",
            "plugins/": {
                "packer.lua": "Plugin manager",
                "lsp.lua": "Language server config"
            }
        },
        "zsh/": {
            "zshrc": "Zsh configuration",
            "aliases.zsh": "Shell aliases"
        }
    },
    "scripts/": {
        "install.sh": "Installation script",
        "backup.sh": "Backup script"
    }
}

logger.tree(file_structure, title="Dotfiles Structure")

# Tree with custom styling
logger.tree(
    file_structure,
    title="Project Files",
    guide_style="bold blue",
    expanded=True
)
```

### Multi-Column Layouts

Display content in organized columns:

```python
# Simple text columns
logger.columns("Column 1", "Column 2", "Column 3")

# Mixed content columns
system_info = logger.panel("OS: Linux\nShell: zsh\nTerminal: kitty", title="System")
progress_info = logger.panel("✓ Backup\n✓ Install\n⧗ Configure", title="Progress")
next_steps = logger.panel("• Restart shell\n• Test config\n• Enjoy!", title="Next Steps")

logger.columns(system_info, progress_info, next_steps, equal=True)

# Custom column layout
logger.columns(
    "Left content",
    "Center content",
    "Right content",
    equal=False,
    expand=True,
    padding=(1, 2)
)
```

### Syntax Highlighting

Display code with beautiful syntax highlighting:

```python
# Python code
python_code = '''
def install_dotfiles():
    """Install dotfiles with backup."""
    backup_existing_files()
    create_symlinks()
    print("Installation complete!")
'''

logger.syntax(python_code, lexer="python", title="install.py")

# Bash script with line numbers
bash_script = '''#!/bin/bash
echo "Starting installation..."
cp ~/.zshrc ~/.zshrc.backup
ln -sf ~/dotfiles/zshrc ~/.zshrc
echo "Done!"
'''

logger.syntax(bash_script, lexer="bash", line_numbers=True, title="install.sh")

# JSON configuration
json_config = '''
{
    "name": "dotfiles-installer",
    "version": "1.0.0",
    "features": ["backup", "symlink", "restore"]
}
'''

logger.syntax(json_config, lexer="json", theme="github-dark")
```

### Markdown Rendering

Render markdown text with Rich formatting:

```python
# Installation summary
summary = '''
# Installation Complete! 🎉

## What was installed:
- **Neovim** configuration with LSP support
- **Zsh** with Oh My Zsh and custom theme
- **Git** configuration and useful aliases
- **Tmux** configuration with custom key bindings

## Next steps:
1. Restart your terminal or run `source ~/.zshrc`
2. Open Neovim and run `:PackerInstall` to install plugins
3. Test your new configuration

## Need help?
Check the [documentation](https://github.com/user/dotfiles) or run `dotfiles --help`

```bash
# Test your setup
nvim --version
git --version
tmux -V
```
'''

logger.markdown(summary)

# Simple markdown
logger.markdown("## Configuration Updated\n\nYour dotfiles have been **successfully** installed!")
```

### JSON Pretty Printing

Display JSON data with syntax highlighting:

```python
# Configuration data
config_data = {
    "installation": {
        "type": "symlink",
        "backup": True,
        "timestamp": "2024-01-15T10:30:00Z"
    },
    "files_installed": [
        {"source": "zshrc", "target": "~/.zshrc", "status": "success"},
        {"source": "vimrc", "target": "~/.vimrc", "status": "success"},
        {"source": "gitconfig", "target": "~/.gitconfig", "status": "success"}
    ],
    "statistics": {
        "total_files": 15,
        "successful": 15,
        "failed": 0,
        "skipped": 2
    }
}

logger.json(config_data, title="Installation Report")

# JSON string
json_string = '{"status": "complete", "errors": [], "warnings": ["deprecated config"]}'
logger.json(json_string, indent=4, sort_keys=True)
```

### Live Updates

Create real-time updating displays:

```python
# Live updating table
from rich.table import Table

table = Table(title="Installation Progress")
table.add_column("File")
table.add_column("Status")
table.add_column("Progress")

files_to_install = ["zshrc", "vimrc", "gitconfig", "tmux.conf"]

with logger.live(table, refresh_per_second=2) as live:
    for i, file in enumerate(files_to_install):
        table.add_row(file, "Installing...", f"{i}/{len(files_to_install)}")
        live.update(table)

        # Simulate installation work
        time.sleep(1)

        # Update the last row to show completion
        table.rows[-1] = (file, "✓ Complete", f"{i+1}/{len(files_to_install)}")
        live.update(table)

# Live updating panel
panel = Panel("Starting installation...", title="Status")
with logger.live(panel) as live:
    for step in ["Backing up files", "Creating symlinks", "Setting permissions"]:
        panel = Panel(f"Current step: {step}", title="Installation Status")
        live.update(panel)
        time.sleep(2)
```

### Bar Charts

Display simple data visualizations:

```python
# Installation breakdown
file_counts = {
    "Config Files": 15,
    "Scripts": 8,
    "Themes": 12,
    "Plugins": 25,
    "Documentation": 6
}

logger.bar_chart(file_counts, title="Files by Category")

# Custom bar chart
performance_data = {
    "Backup": 2.5,
    "Install": 8.2,
    "Configure": 1.8,
    "Cleanup": 0.5
}

logger.bar_chart(
    performance_data,
    title="Installation Time (seconds)",
    width=30,
    character="▓",
    show_values=True
)
```

### Text Styling and Alignment

Advanced text formatting and alignment:

```python
# Styled text
logger.text("🎉 Installation Successful! 🎉", style="bold green", justify="center")
logger.text("Warning: Some files were skipped", style="yellow", justify="left")
logger.text("Error: Permission denied", style="bold red")

# Text with overflow handling
long_text = "This is a very long line that might need to be handled with overflow settings"
logger.text(long_text, overflow="ellipsis", no_wrap=True)

# Aligned content
from rich.panel import Panel

success_panel = Panel("All files installed successfully!", title="Success")
logger.align(success_panel, "center")

warning_panel = Panel("Some warnings occurred", title="Warning")
logger.align(warning_panel, "right", style="yellow")
```

### Interactive Prompts

Get user input with beautiful prompts:

```python
# Simple text input
user_name = logger.prompt("Enter your name")
install_path = logger.prompt("Installation directory", default="~/.config")

# Choice selection
install_type = logger.prompt(
    "Choose installation type",
    choices=["symlink", "copy", "template"],
    default="symlink"
)

# Confirmation prompts
if logger.confirm("Do you want to backup existing files?", default=True):
    backup_files()

if logger.confirm("Proceed with installation?"):
    install_dotfiles()
else:
    logger.text("Installation cancelled", style="yellow")
```

### Object Inspection and Pretty Printing

Debug and display complex objects:

```python
# Inspect configuration object
class Config:
    def __init__(self):
        self.debug = True
        self.log_level = "INFO"
        self.features = ["backup", "symlink"]

    def get_status(self):
        return "ready"

config = Config()
logger.inspect(config, title="Configuration Object", methods=True)

# Pretty print complex data
complex_data = {
    "settings": {
        "theme": "dark",
        "plugins": ["git", "zsh", "vim"],
        "features": {
            "auto_backup": True,
            "notifications": False
        }
    },
    "recent_installs": [
        {"name": "nvim", "date": "2024-01-15", "status": "success"},
        {"name": "tmux", "date": "2024-01-14", "status": "success"}
    ]
}

logger.pretty(complex_data, indent_guides=True, max_depth=3)

# Pretty print with limits
large_list = list(range(100))
logger.pretty(large_list, max_length=10, max_string=50)
```

### Rich Feature Configuration

Configure Rich features with RichFeatureSettings:

```python
# Comprehensive Rich configuration
rich_features = RichFeatureSettings(
    enabled=True,

    # Table settings
    table_show_header=True,
    table_show_lines=True,
    table_show_edge=True,
    table_expand=False,

    # Panel settings
    panel_border_style="blue",
    panel_box_style="rounded",
    panel_expand=True,
    panel_padding=(0, 1),

    # Rule settings
    rule_style="rule.line",
    rule_align="center",

    # Progress settings
    progress_auto_refresh=True,
    progress_refresh_per_second=10,

    # Status settings
    status_spinner="dots",
    status_refresh_per_second=12.5
)

logger = Log.create_logger(
    "app",
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_features
)
```

## File Logging

### Basic File Logging

```python
from cli.modules.logging import (
    Log, LogLevels, ConsoleHandlers, RichHandlerSettings,
    FileHandlerSpec, FileHandlerTypes, FileHandlerSettings
)

# Console + file logging
logger = Log.create_logger(
    "app",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_time=True),
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="app.log")
        )
    ]
)

logger.info("This appears in both console and file")
logger.error("Error logged to both destinations")
```

### Multiple File Handlers

```python
from cli.modules.logging import (
    RotatingFileHandlerSettings, TimedRotatingFileHandlerSettings
)

# Multiple files for different purposes
logger = Log.create_logger(
    "app",
    log_level=LogLevels.DEBUG,
    console_handler_type=ConsoleHandlers.RICH,
    file_handlers=[
        # Debug log - all messages
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="debug.log")
        ),
        # Error log - rotating to prevent huge files
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename="errors.log",
                max_bytes=5_000_000,  # 5MB
                backup_count=3
            )
        ),
        # Daily log - rotates at midnight
        FileHandlerSpec(
            handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
            config=TimedRotatingFileHandlerSettings(
                filename="daily.log",
                when='midnight',
                backup_count=30
            )
        )
    ]
)
```

### File Handler Types

```python
# Basic File Handler
FileHandlerSettings(
    filename="app.log",
    mode='a',           # 'a' for append, 'w' for overwrite
    encoding='utf-8',
    delay=False         # Whether to delay file opening
)

# Rotating File Handler (size-based)
RotatingFileHandlerSettings(
    filename="app.log",
    max_bytes=10_485_760,  # 10MB (default)
    backup_count=5,        # Keep 5 backup files
    mode='a',
    encoding='utf-8',
    delay=False
)

# Timed Rotating File Handler (time-based)
TimedRotatingFileHandlerSettings(
    filename="app.log",
    when='midnight',       # 'S', 'M', 'H', 'D', 'midnight', 'W0'-'W6'
    interval=1,           # Interval between rotations
    backup_count=7,       # Keep 7 backup files
    encoding='utf-8',
    delay=False,
    utc=False            # Use UTC time for rotation
)
```

### Per-File Custom Formatting

```python
# Different formats for different files
logger = Log.create_logger(
    "app",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    file_handlers=[
        # Detailed debugging format
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="debug.log"),
            format_override="%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
        ),
        # Simple production format
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="simple.log"),
            format_override="%(levelname)s: %(message)s"
        ),
        # JSON-structured format
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="structured.log"),
            format_override='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        )
    ]
)
```

## Reference

### Format Placeholders

The logging module provides access to all standard Python logging placeholders via `FORMATTER_PLACEHOLDERS`:

```python
from cli.modules.logging import FORMATTER_PLACEHOLDERS

# Available placeholders for format strings:
# name          - Logger name
# levelno       - Log level number (10, 20, 30, 40, 50)
# levelname     - Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# pathname      - Full pathname of source file
# filename      - Filename portion of pathname
# module        - Module name
# lineno        - Source line number
# funcName      - Function name
# created       - Time when LogRecord was created (timestamp)
# asctime       - Human-readable time (created by formatter)
# msecs         - Millisecond portion of creation time
# relativeCreated - Time relative to module load
# thread        - Thread ID
# threadName    - Thread name
# process       - Process ID
# processName   - Process name
# message       - The logged message (formatted msg % args)

# Example using various placeholders
logger = Log.create_logger(
    "app",
    format="%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
)
```

### Utility Functions

```python
from cli.modules.logging import (
    get_log_level_from_verbosity,
    parse_log_level,
    validate_log_level_string
)

# Convert verbosity count to log level
level = get_log_level_from_verbosity(2)  # Returns LogLevels.INFO

# Parse log level with precedence: verbosity > log_level_str > fallback
level = parse_log_level("debug", verbosity=0, fallback=LogLevels.INFO)

# Validate log level string
level = validate_log_level_string("info")  # Returns LogLevels.INFO
level = validate_log_level_string("i")     # Also returns LogLevels.INFO
```

### Complete RichLogger API

The RichLogger wrapper provides all standard logging methods plus Rich features:

```python
# Standard logging methods (delegated to wrapped logger)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Rich feature methods (only available when Rich features enabled)
logger.table(data, title="Data Table")
logger.panel("Important message", title="Alert")
logger.rule("Section Separator")

# Context managers
with logger.progress("Working", total=100) as progress:
    task = progress.add_task("Task", total=100)
    progress.update(task, advance=1)

with logger.status("Loading...") as status:
    status.update("Processing...")

# Properties
print(logger.name)  # Logger name
```

### Configuration Presets

```python
from cli.modules.logging.presets import LOG_PRESETS

# Use predefined presets
logger = Log.create_logger("app", config=LOG_PRESETS["rich_install"])

# Available presets:
# - "rich_install": Rich console with install-optimized settings
# - "dev": Development preset with debug logging

# Override preset values
logger = Log.create_logger(
    "app",
    config=LOG_PRESETS["rich_install"],
    log_level=LogLevels.DEBUG  # Override preset's INFO level
)
```

## Advanced Configuration

### Complete RichHandlerSettings Reference

```python
# All available RichHandlerSettings options
rich_settings = RichHandlerSettings(
    # Core display options
    show_time=True,                    # Show timestamp
    show_level=True,                   # Show log level
    show_path=True,                    # Show file path and line number
    markup=False,                      # Enable Rich markup processing

    # Time formatting
    omit_repeated_times=True,          # Omit repeated timestamps
    log_time_format="[%x %X]",         # Time format string

    # Path options
    enable_link_path=True,             # Make paths clickable

    # Highlighting
    keywords=None,                     # Keywords to highlight

    # Traceback configuration
    rich_tracebacks=False,             # Use Rich tracebacks
    tracebacks_width=None,             # Traceback width
    tracebacks_code_width=88,          # Code snippet width
    tracebacks_extra_lines=3,          # Extra context lines
    tracebacks_theme=None,             # Syntax theme
    tracebacks_word_wrap=True,         # Word wrap long lines
    tracebacks_show_locals=False,      # Show local variables
    tracebacks_max_frames=100,         # Max frames to show

    # Local variable display
    locals_max_length=10,              # Max items in collections
    locals_max_string=80,              # Max string length
)
```

### Complete RichFeatureSettings Reference

```python
# All available RichFeatureSettings options
rich_features = RichFeatureSettings(
    # Global Rich features control
    enabled=True,                      # Enable/disable Rich features

    # Table settings
    table_show_header=True,            # Show table headers by default
    table_show_lines=False,            # Show lines between table rows
    table_show_edge=True,              # Show table border
    table_expand=False,                # Expand tables to fill width

    # Panel settings
    panel_border_style="blue",         # Default border color/style
    panel_box_style="rounded",         # Box style ('rounded', 'square', etc.)
    panel_expand=True,                 # Expand panels to fill width
    panel_padding=(0, 1),              # Padding (vertical, horizontal)

    # Rule settings
    rule_style="rule.line",            # Default style for rules
    rule_align="center",               # Rule title alignment

    # Progress settings
    progress_auto_refresh=True,        # Auto-refresh progress bars
    progress_refresh_per_second=10,    # Refresh rate
    progress_speed_estimate_period=30.0, # Speed estimation period

    # Status settings
    status_spinner="dots",             # Default spinner style
    status_refresh_per_second=12.5,    # Status refresh rate

    # Console settings
    console_width=None,                # Fixed console width (None for auto)
    console_height=None,               # Fixed console height (None for auto)
)
```

### Dynamic Configuration Updates

```python
# Create initial logger
logger = Log.create_logger(
    "app",
    log_level=LogLevels.WARNING,
    formatter_type=LogFormatters.DEFAULT
)

# Update to use Rich formatting
logger = Log.update(
    name="app",
    log_level=LogLevels.DEBUG,
    formatter_type=LogFormatters.RICH,
    format="[cyan]%(levelname)s[/cyan]: %(message)s"
)

# Update handler to Rich with settings
rich_settings = RichHandlerSettings(show_time=False, show_level=True)
logger = Log.update(
    name="app",
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=rich_settings
)

# Add file logging
file_handlers = [
    FileHandlerSpec(
        handler_type=FileHandlerTypes.ROTATING_FILE,
        config=RotatingFileHandlerSettings(filename="app.log", max_bytes=1_000_000)
    )
]
logger = Log.update(name="app", file_handlers=file_handlers)
```

## Real-World Examples

### Development Setup

```python
# Development: Rich console + comprehensive logging
dev_logger = Log.create_logger(
    "dev_app",
    log_level=LogLevels.DEBUG,
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(
        show_time=True,
        show_path=True,           # Show paths for debugging
        markup=True,              # Allow colors and markup
        rich_tracebacks=True,     # Beautiful tracebacks
        tracebacks_show_locals=True,
        keywords=['TODO', 'FIXME', 'DEBUG']
    ),
    rich_features=RichFeatureSettings(
        enabled=True,
        table_show_lines=True,
        panel_border_style="blue"
    ),
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="dev.log", mode='w')  # Overwrite each run
        )
    ]
)

# Use Rich features in development
dev_logger.info("Starting application...")
dev_logger.rule("Initialization")
dev_logger.table([["Component", "Status"], ["Database", "Connected"], ["Cache", "Ready"]], title="System Status")
```

### Production Setup

```python
# Production: Minimal console + comprehensive file logging
prod_logger = Log.create_logger(
    "prod_app",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(
        show_time=True,
        show_path=False,          # Hide paths in production
        markup=False,             # Disable markup for safety
        rich_tracebacks=False
    ),
    file_handlers=[
        # Application log - rotating
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename="app.log",
                max_bytes=10_000_000,  # 10MB
                backup_count=5
            )
        ),
        # Error log - separate file
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename="error.log",
                max_bytes=5_000_000,   # 5MB
                backup_count=10
            )
        ),
        # Audit log - daily rotation
        FileHandlerSpec(
            handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
            config=TimedRotatingFileHandlerSettings(
                filename="audit.log",
                when='midnight',
                backup_count=365,      # Keep 1 year
                utc=True
            )
        )
    ]
)
```

### Application Integration

```python
# Complete application example
import time
from cli.modules.logging import (
    Log, LogLevels, ConsoleHandlers, RichHandlerSettings, RichFeatureSettings,
    FileHandlerSpec, FileHandlerTypes, RotatingFileHandlerSettings
)

class MyApplication:
    def __init__(self):
        # Setup logger with Rich features
        self.logger = Log.create_logger(
            "myapp",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            handler_config=RichHandlerSettings(
                show_time=True,
                show_path=False,
                markup=True
            ),
            rich_features=RichFeatureSettings(
                enabled=True,
                table_show_lines=True,
                panel_border_style="blue"
            ),
            file_handlers=[
                FileHandlerSpec(
                    handler_type=FileHandlerTypes.ROTATING_FILE,
                    config=RotatingFileHandlerSettings(
                        filename="app.log",
                        max_bytes=5_000_000,
                        backup_count=3
                    )
                )
            ]
        )

    def run(self):
        self.logger.info("Starting application")
        self.logger.rule("Initialization")

        # Show configuration
        config_data = [
            ["Setting", "Value", "Status"],
            ["Database URL", "postgresql://...", "✓ Valid"],
            ["API Key", "sk-...", "✓ Valid"],
            ["Debug Mode", "False", "✓ Production"]
        ]
        self.logger.table(config_data, title="Configuration")

        # Processing with progress
        self.logger.rule("Data Processing")
        with self.logger.progress("Processing data", total=100) as progress:
            task = progress.add_task("Processing", total=100)
            for i in range(100):
                time.sleep(0.01)
                progress.update(task, advance=1)

        # Results
        self.logger.panel("Processing completed successfully!", title="Success")
        self.logger.info("Application finished")

# Usage
app = MyApplication()
app.run()
```

## Troubleshooting

### Rich Not Available
If Rich is not installed, the module gracefully falls back:
- `RichHandler` → `StreamHandler`
- `RichFormatter` → `logging.Formatter`
- Rich feature methods become no-ops

### Common Import Patterns
```python
# Basic imports
from cli.modules.logging import Log, LogLevels, ConsoleHandlers

# Rich features
from cli.modules.logging import RichHandlerSettings, RichFeatureSettings

# File logging
from cli.modules.logging import (
    FileHandlerSpec, FileHandlerTypes, FileHandlerSettings,
    RotatingFileHandlerSettings, TimedRotatingFileHandlerSettings
)

# Advanced usage
from cli.modules.logging import (
    LogFormatters, LogFormatterStyleChoices, ColoredFormatterColors,
    FORMATTER_PLACEHOLDERS
)
```

### Performance Tips

```python
# For high-performance logging, minimize Rich features in production
prod_logger = Log.create_logger(
    "prod",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.DEFAULT,  # Faster than RICH
    formatter_type=LogFormatters.COLORED,          # Faster than RICH
    rich_features=RichFeatureSettings(enabled=False)  # Disable Rich features
)

# Use file logging for detailed logs, minimal console for performance
fast_logger = Log.create_logger(
    "fast",
    log_level=LogLevels.WARNING,  # Only warnings and errors to console
    console_handler_type=ConsoleHandlers.DEFAULT,
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(filename="detailed.log")
        )
    ]
)
```

## Best Practices

1. **Enable Rich features for development** - Use tables, panels, and progress bars for better debugging
2. **Minimize Rich features in production** - Use basic handlers for better performance
3. **Use file rotation** - Prevent log files from growing too large
4. **Separate log files by purpose** - Different files for errors, audit, debug
5. **Configure once, use everywhere** - Create loggers early and reuse them
6. **Use type-safe settings** - Always use RichHandlerSettings and RichFeatureSettings
7. **Test fallback behavior** - Ensure your app works when Rich is not available

## Quick Reference

### Simple Console Logger
```python
logger = Log.create_logger("app", log_level=LogLevels.INFO)
```

### Rich Console Logger
```python
logger = Log.create_logger(
    "app",
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=RichFeatureSettings(enabled=True)
)
```

### Console + File Logger
```python
logger = Log.create_logger(
    "app",
    console_handler_type=ConsoleHandlers.RICH,
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(filename="app.log")
        )
    ]
)
```

### Rich Features Usage
```python
logger.table(data, title="Results")
logger.panel("Important message", title="Alert")
logger.rule("Section Separator")

with logger.progress("Working", total=100) as progress:
    task = progress.add_task("Task", total=100)
    progress.update(task, advance=1)

with logger.status("Loading...") as status:
    status.update("Processing...")
```

---

This comprehensive usage guide covers all features of the logging module. For architectural details, see the [Architecture Guide](architecture.md). For migration information, see the [Migration Guide](migration.md).
