# Rich Features Integration Examples

This document demonstrates the Rich features integration with the logging system.

## Basic Setup

```python
from cli.modules.logging import (
    Log, LogLevels, ConsoleHandlers,
    RichHandlerSettings, RichFeatureSettings
)

# Create logger with Rich features enabled
logger = Log.create_logger(
    "app",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_time=True, markup=True),
    rich_features=RichFeatureSettings(enabled=True)
)
```

## Rich Tables

### Simple Table
```python
# List of rows format
data = [
    ["Name", "Age", "City"],  # Header row
    ["Alice", "30", "New York"],
    ["Bob", "25", "London"],
    ["Charlie", "35", "Tokyo"]
]

logger.table(data, title="User Information")
```

### Dictionary Format
```python
# Dictionary of columns format
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [30, 25, 35],
    "City": ["New York", "London", "Tokyo"]
}

logger.table(data, title="User Data", show_lines=True)
```

### Customized Table
```python
logger.table(
    data,
    title="Detailed Report",
    show_header=True,
    show_lines=True,
    show_edge=True,
    expand=True
)
```

## Rich Panels

### Simple Panel
```python
logger.panel("This is an important message!", title="Alert")
```

### Styled Panel
```python
logger.panel(
    "Configuration loaded successfully\nAll systems operational",
    title="System Status",
    subtitle="Ready",
    border_style="green",
    expand=False
)
```

### Panel with Custom Padding
```python
logger.panel(
    "Error: Database connection failed",
    title="Error",
    border_style="red",
    padding=(1, 2)  # (vertical, horizontal)
)
```

## Rich Rules (Separators)

### Simple Rule
```python
logger.rule("Processing Phase 1")
```

### Styled Rule
```python
logger.rule("Data Analysis", style="bold blue", align="left")
```

### Section Separators
```python
logger.info("Starting application...")
logger.rule("Initialization")
logger.info("Loading configuration...")
logger.info("Connecting to database...")
logger.rule("Main Processing")
logger.info("Processing data...")
```

## Progress Bars

### Simple Progress
```python
import time

with logger.progress("Processing files", total=100) as progress:
    task = progress.add_task("Processing", total=100)
    for i in range(100):
        time.sleep(0.01)  # Simulate work
        progress.update(task, advance=1)
```

### Multiple Progress Tasks
```python
with logger.progress() as progress:
    download_task = progress.add_task("Downloading", total=1000)
    process_task = progress.add_task("Processing", total=500)

    for i in range(1000):
        time.sleep(0.001)
        progress.update(download_task, advance=1)

        if i % 2 == 0 and i < 500:
            progress.update(process_task, advance=1)
```

### Custom Progress
```python
with logger.progress(
    description="Custom Progress",
    auto_refresh=True,
    refresh_per_second=20
) as progress:
    task = progress.add_task("Working", total=50)
    for i in range(50):
        time.sleep(0.1)
        progress.update(task, advance=1)
```

## Status Indicators

### Simple Status
```python
with logger.status("Loading data...") as status:
    time.sleep(2)  # Simulate work
    status.update("Processing data...")
    time.sleep(2)
    status.update("Saving results...")
    time.sleep(1)
```

### Custom Spinner
```python
with logger.status("Analyzing...", spinner="dots2") as status:
    time.sleep(3)
    status.update("Almost done...")
    time.sleep(2)
```

## Combined Usage Example

```python
from cli.modules.logging import (
    Log, LogLevels, ConsoleHandlers,
    RichHandlerSettings, RichFeatureSettings
)
import time

# Setup logger with Rich features
logger = Log.create_logger(
    "demo_app",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(
        show_time=True,
        show_path=False,
        markup=True
    ),
    rich_features=RichFeatureSettings(
        table_show_lines=True,
        panel_border_style="rounded"
    )
)

def demo_application():
    logger.info("Starting Demo Application")
    logger.rule("Initialization Phase")

    # Show configuration
    config_data = {
        "Setting": ["Database URL", "API Key", "Debug Mode"],
        "Value": ["postgresql://...", "sk-...", "True"],
        "Status": ["✓ Valid", "✓ Valid", "⚠ Enabled"]
    }

    logger.table(config_data, title="Configuration")

    # Processing with progress
    logger.rule("Data Processing")

    with logger.progress("Processing data", total=100) as progress:
        task = progress.add_task("Processing", total=100)
        for i in range(100):
            time.sleep(0.02)
            progress.update(task, advance=1)

    # Show results
    results = [
        ["Metric", "Value", "Status"],
        ["Records Processed", "1,000", "✓ Complete"],
        ["Errors", "0", "✓ None"],
        ["Duration", "2.1s", "✓ Fast"]
    ]

    logger.table(results, title="Processing Results")

    # Final status
    logger.panel(
        "Application completed successfully!\nAll data processed without errors.",
        title="Success",
        border_style="green"
    )

if __name__ == "__main__":
    demo_application()
```

## Configuration Options

### RichFeatureSettings
```python
rich_settings = RichFeatureSettings(
    enabled=True,                    # Enable/disable Rich features
    table_show_header=True,          # Show table headers by default
    table_show_lines=False,          # Show lines between rows
    table_expand=False,              # Expand tables to full width
    panel_border_style="rounded",    # Panel border style
    panel_expand=True,               # Expand panels to full width
    rule_style="rule.line",          # Rule line style
    rule_align="center",             # Rule title alignment
    progress_auto_refresh=True,      # Auto-refresh progress bars
    status_spinner="dots"            # Default spinner style
)

logger = Log.create_logger(
    "app",
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)
```

## Fallback Behavior

When Rich is not available, all Rich feature methods become no-ops:

```python
# This works whether Rich is installed or not
logger.table(data, title="Data")  # Shows table if Rich available, no-op otherwise
logger.panel("Message")           # Shows panel if Rich available, no-op otherwise

# Context managers return dummy objects when Rich unavailable
with logger.progress("Working") as progress:
    # progress.add_task() and progress.update() are no-ops if Rich unavailable
    task = progress.add_task("Task")
    progress.update(task, advance=1)
```

## Integration with Standard Logging

Rich features work alongside standard logging:

```python
logger.info("Starting process...")
logger.table(data, title="Input Data")
logger.warning("Processing may take a while")

with logger.progress("Processing") as progress:
    task = progress.add_task("Work", total=100)
    for i in range(100):
        if i % 20 == 0:
            logger.info(f"Processed {i} items")
        progress.update(task, advance=1)

logger.panel("Process completed!", title="Success")
logger.info("All done!")
```

## Tree Display

Display hierarchical data structures:

```python
# File system structure
file_tree = {
    "src/": {
        "components/": {
            "Header.tsx": "React header component",
            "Footer.tsx": "React footer component"
        },
        "utils/": {
            "helpers.ts": "Utility functions",
            "constants.ts": "Application constants"
        },
        "main.tsx": "Application entry point"
    },
    "public/": {
        "index.html": "HTML template",
        "favicon.ico": "Site icon"
    }
}

logger.tree(file_tree, title="Project Structure")

# Configuration tree
config_tree = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp"
    },
    "cache": {
        "redis": {
            "host": "localhost",
            "port": 6379
        }
    },
    "features": ["auth", "api", "admin"]
}

logger.tree(config_tree, title="Configuration", guide_style="bold blue")
```

## Multi-Column Layouts

Organize content in columns:

```python
# System status dashboard
system_panel = Panel(
    "CPU: 45%\nMemory: 2.1GB\nDisk: 78%",
    title="System Resources"
)

network_panel = Panel(
    "Status: Connected\nLatency: 23ms\nBandwidth: 100Mbps",
    title="Network"
)

services_panel = Panel(
    "Database: ✓ Running\nCache: ✓ Running\nAPI: ✓ Running",
    title="Services"
)

logger.columns(system_panel, network_panel, services_panel, equal=True)

# Mixed content columns
logger.columns(
    "Left column content",
    Panel("Center panel", title="Info"),
    "Right column content",
    expand=True
)
```

## Syntax Highlighting

Display code with beautiful highlighting:

```python
# Python code example
python_code = '''
class DatabaseManager:
    def __init__(self, connection_string):
        self.connection = create_connection(connection_string)

    async def fetch_users(self):
        query = "SELECT * FROM users WHERE active = true"
        return await self.connection.fetch(query)
'''

logger.syntax(python_code, lexer="python", title="database.py", line_numbers=True)

# Configuration file
yaml_config = '''
server:
  host: 0.0.0.0
  port: 8080
  debug: false

database:
  url: postgresql://user:pass@localhost/db
  pool_size: 10

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
'''

logger.syntax(yaml_config, lexer="yaml", title="config.yaml", theme="github-dark")

# Shell script
bash_script = '''#!/bin/bash
set -e

echo "Deploying application..."
docker build -t myapp:latest .
docker stop myapp || true
docker run -d --name myapp -p 8080:8080 myapp:latest
echo "Deployment complete!"
'''

logger.syntax(bash_script, lexer="bash", title="deploy.sh", line_numbers=True)
```

## Markdown Rendering

Rich markdown support:

```python
# Release notes
release_notes = '''
# Release v2.1.0 🚀

## New Features
- **Tree Display**: Hierarchical data visualization
- **Syntax Highlighting**: Code display with themes
- **Interactive Prompts**: User input with validation

## Improvements
- Better error handling
- Performance optimizations
- Updated documentation

## Bug Fixes
- Fixed memory leak in file handler
- Resolved color display issues
- Corrected timezone handling

## Breaking Changes
⚠️ **Important**: The `old_method()` has been deprecated. Use `new_method()` instead.

```python
# Migration example
# Old way (deprecated)
logger.old_method(data)

# New way
logger.new_method(data)
```

For more information, see the [migration guide](docs/migration.md).
'''

logger.markdown(release_notes)

# Simple status update
logger.markdown("## Deployment Status\n\n✅ **Success**: Application deployed to production")
```

## JSON Display

Pretty print JSON data:

```python
# API response
api_response = {
    "status": "success",
    "data": {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"}
        ],
        "pagination": {
            "page": 1,
            "per_page": 10,
            "total": 2
        }
    },
    "meta": {
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "v1.0",
        "request_id": "req_123456"
    }
}

logger.json(api_response, title="API Response", indent=2)

# Configuration dump
config_json = {
    "app": {
        "name": "MyApp",
        "version": "1.0.0",
        "environment": "production"
    },
    "features": {
        "authentication": True,
        "caching": True,
        "monitoring": True
    },
    "integrations": ["stripe", "sendgrid", "analytics"]
}

logger.json(config_json, title="Application Configuration", sort_keys=True)
```

## Live Updates

Real-time display updates:

```python
# Live deployment status
from rich.table import Table

deployment_table = Table(title="Deployment Progress")
deployment_table.add_column("Service")
deployment_table.add_column("Status")
deployment_table.add_column("Health")

services = ["api", "database", "cache", "frontend"]

with logger.live(deployment_table, refresh_per_second=1) as live:
    for service in services:
        deployment_table.add_row(service, "Deploying...", "⏳")
        live.update(deployment_table)

        # Simulate deployment
        time.sleep(2)

        # Update status
        deployment_table.rows[-1] = (service, "Running", "✅")
        live.update(deployment_table)

# Live metrics dashboard
metrics_panel = Panel("Initializing metrics...", title="System Metrics")

with logger.live(metrics_panel) as live:
    for i in range(10):
        cpu_usage = random.randint(20, 80)
        memory_usage = random.randint(30, 70)

        metrics_content = f"""
CPU Usage: {cpu_usage}%
Memory Usage: {memory_usage}%
Active Connections: {random.randint(50, 200)}
Requests/sec: {random.randint(100, 500)}
        """.strip()

        metrics_panel = Panel(metrics_content, title="System Metrics")
        live.update(metrics_panel)
        time.sleep(1)
```

## Bar Charts

Simple data visualization:

```python
# Performance metrics
performance_data = {
    "API Response Time": 45.2,
    "Database Query Time": 12.8,
    "Cache Hit Rate": 89.5,
    "Memory Usage": 67.3,
    "CPU Usage": 34.1
}

logger.bar_chart(performance_data, title="Performance Metrics (%)", width=25)

# File processing stats
file_stats = {
    "Processed": 1250,
    "Skipped": 45,
    "Errors": 3,
    "Warnings": 12
}

logger.bar_chart(
    file_stats,
    title="File Processing Results",
    character="▓",
    show_values=True
)

# Resource usage over time
resource_usage = {
    "00:00": 23.5,
    "06:00": 45.2,
    "12:00": 78.9,
    "18:00": 56.3,
    "24:00": 34.1
}

logger.bar_chart(resource_usage, title="CPU Usage Over Time (%)", width=30)
```

## Interactive Features

User input and confirmation:

```python
# Configuration wizard
logger.panel("Welcome to the Configuration Wizard!", title="Setup")

app_name = logger.prompt("Enter application name", default="MyApp")
environment = logger.prompt(
    "Select environment",
    choices=["development", "staging", "production"],
    default="development"
)

enable_debug = logger.confirm("Enable debug mode?", default=False)
enable_monitoring = logger.confirm("Enable monitoring?", default=True)

# Confirmation summary
config_summary = f"""
Application: {app_name}
Environment: {environment}
Debug Mode: {'Enabled' if enable_debug else 'Disabled'}
Monitoring: {'Enabled' if enable_monitoring else 'Disabled'}
"""

logger.panel(config_summary, title="Configuration Summary")

if logger.confirm("Save this configuration?", default=True):
    logger.text("✅ Configuration saved!", style="bold green")
else:
    logger.text("❌ Configuration cancelled", style="bold red")

# Advanced prompts
database_url = logger.prompt(
    "Database URL",
    default="postgresql://localhost:5432/myapp"
)

log_level = logger.prompt(
    "Log level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    default="INFO"
)
```

## Object Inspection

Debug and explore objects:

```python
# Inspect application state
class ApplicationState:
    def __init__(self):
        self.version = "1.0.0"
        self.uptime = 3600
        self.active_connections = 42
        self.cache_size = 1024

    def get_status(self):
        return "running"

    def restart(self):
        pass

app_state = ApplicationState()
logger.inspect(app_state, title="Application State", methods=True, help=True)

# Pretty print complex configuration
complex_config = {
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "workers": 4,
        "timeout": 30
    },
    "database": {
        "connections": {
            "primary": "postgresql://localhost:5432/main",
            "replica": "postgresql://replica:5432/main"
        },
        "pool": {
            "min_size": 5,
            "max_size": 20
        }
    },
    "features": {
        "authentication": {
            "enabled": True,
            "providers": ["local", "oauth", "ldap"],
            "session_timeout": 3600
        },
        "caching": {
            "enabled": True,
            "backend": "redis",
            "ttl": 300
        }
    }
}

logger.pretty(complex_config, title="Application Configuration", indent_guides=True)

# Inspect with limits for large objects
large_data = {
    "items": list(range(1000)),
    "metadata": {
        "description": "A" * 200,
        "tags": [f"tag_{i}" for i in range(100)]
    }
}

logger.pretty(
    large_data,
    max_length=10,
    max_string=50,
    max_depth=2,
    title="Large Dataset (Limited View)"
)
```

## Advanced Integration Examples

Combining multiple Rich features:

```python
# Complete application monitoring dashboard
def show_monitoring_dashboard():
    logger.rule("System Monitoring Dashboard", style="bold blue")

    # System overview
    system_info = {
        "hostname": "web-server-01",
        "os": "Ubuntu 22.04",
        "uptime": "15 days, 3 hours",
        "load": "0.45, 0.52, 0.48"
    }

    logger.tree(system_info, title="System Information")

    # Resource usage
    resources = {
        "CPU": 45.2,
        "Memory": 67.8,
        "Disk": 23.1,
        "Network": 12.5
    }

    logger.bar_chart(resources, title="Resource Usage (%)")

    # Service status
    services_data = [
        ["Service", "Status", "Port", "Uptime"],
        ["nginx", "✅ Running", "80", "15d 3h"],
        ["postgresql", "✅ Running", "5432", "15d 3h"],
        ["redis", "✅ Running", "6379", "15d 3h"],
        ["app", "✅ Running", "8080", "2d 1h"]
    ]

    logger.table(services_data, title="Service Status", show_lines=True)

    # Recent logs summary
    log_summary = '''
## Recent Activity

### Last 24 Hours
- **Requests**: 45,231 (+12% from yesterday)
- **Errors**: 23 (-45% from yesterday)
- **Response Time**: 145ms (avg)

### Alerts
- ⚠️ High memory usage detected at 14:30
- ✅ All services healthy
    '''

    logger.markdown(log_summary)

# Usage
show_monitoring_dashboard()
```
