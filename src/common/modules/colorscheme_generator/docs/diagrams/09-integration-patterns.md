# Integration Patterns

This diagram shows how the colorscheme_generator integrates with other systems.

```mermaid
graph TB
    subgraph "Colorscheme Generator"
        CSG[ColorScheme Generator]
        Output[Output Files]
    end
    
    subgraph "Wallpaper Manager"
        WM[Wallpaper Change Event]
        Hook[Post-change Hook]
    end
    
    subgraph "Terminal Emulators"
        Alacritty[Alacritty]
        Kitty[Kitty]
        WezTerm[WezTerm]
    end
    
    subgraph "Window Managers"
        I3[i3/Sway]
        Hyprland[Hyprland]
    end
    
    subgraph "Text Editors"
        Neovim[Neovim]
        Vim[Vim]
        VSCode[VSCode]
    end
    
    subgraph "System Services"
        Systemd[Systemd Service]
        Cron[Cron Job]
    end
    
    subgraph "Web Applications"
        Browser[Browser Extension]
        WebApp[Web Dashboard]
    end
    
    WM --> Hook
    Hook --> CSG
    CSG --> Output
    
    Output --> Alacritty
    Output --> Kitty
    Output --> WezTerm
    Output --> I3
    Output --> Hyprland
    Output --> Neovim
    Output --> Vim
    Output --> VSCode
    Output --> Browser
    Output --> WebApp
    
    Systemd --> CSG
    Cron --> CSG
    
    style CSG fill:#e1f5ff
    style Output fill:#fff3e0
```

## Wallpaper Manager Integration

```mermaid
sequenceDiagram
    participant User
    participant WallpaperMgr
    participant Hook
    participant CSG
    participant OutputMgr
    participant Apps
    
    User->>WallpaperMgr: change wallpaper
    WallpaperMgr->>WallpaperMgr: set new wallpaper
    WallpaperMgr->>Hook: trigger post-change hook
    
    Hook->>CSG: generate colors from new wallpaper
    CSG->>CSG: extract colors
    CSG->>OutputMgr: write output files
    OutputMgr->>OutputMgr: generate JSON, CSS, Shell, etc.
    OutputMgr-->>Hook: output files created
    
    Hook->>Apps: reload configurations
    
    Apps->>Apps: read new color files
    Apps->>Apps: apply new colors
    Apps-->>User: updated color scheme
```

## Terminal Emulator Integration

### Alacritty Integration
```mermaid
flowchart LR
    CSG[Generate Colors]
    Template[YAML Template]
    Output[colors.yaml]
    Config[~/.config/alacritty/alacritty.yml]
    Reload[Reload Alacritty]
    
    CSG --> Template
    Template --> Output
    Output --> Import["import: [colors.yaml]"]
    Import --> Config
    Config --> Reload
    
    style CSG fill:#e1f5ff
    style Output fill:#fff3e0
    style Reload fill:#e8f5e9
```

### Kitty Integration
```mermaid
flowchart LR
    CSG[Generate Colors]
    Template[Kitty Template]
    Output[colors.conf]
    Config[~/.config/kitty/kitty.conf]
    Reload[kitty @ set-colors]
    
    CSG --> Template
    Template --> Output
    Output --> Include["include colors.conf"]
    Include --> Config
    Config --> Reload
    
    style CSG fill:#e1f5ff
    style Output fill:#fff3e0
    style Reload fill:#e8f5e9
```

## Window Manager Integration

### i3/Sway Integration
```mermaid
sequenceDiagram
    participant CSG
    participant Shell
    participant I3Config
    participant I3
    
    CSG->>Shell: generate colors.sh
    Shell->>Shell: export COLOR_* variables
    
    I3Config->>Shell: source colors.sh
    Shell-->>I3Config: color variables
    
    I3Config->>I3Config: set $bg $COLOR_BACKGROUND
    I3Config->>I3Config: set $fg $COLOR_FOREGROUND
    I3Config->>I3Config: client.focused $bg $fg
    
    I3Config->>I3: reload config
    I3->>I3: apply new colors
```

## Application Configuration Flow

```mermaid
graph TB
    Start([Wallpaper Changed])
    
    Start --> Generate[Generate Color Scheme]
    Generate --> Formats{Output Formats}
    
    Formats --> JSON[colors.json]
    Formats --> CSS[colors.css]
    Formats --> Shell[colors.sh]
    Formats --> YAML[colors.yaml]
    
    JSON --> App1[Web Applications]
    JSON --> App2[Electron Apps]
    
    CSS --> App3[Browser Extensions]
    CSS --> App4[Web Dashboards]
    
    Shell --> App5[Shell Scripts]
    Shell --> App6[i3/Sway]
    
    YAML --> App7[Alacritty]
    YAML --> App8[Other YAML configs]
    
    App1 --> Reload1[Reload/Restart]
    App2 --> Reload1
    App3 --> Reload2[Reload/Restart]
    App4 --> Reload2
    App5 --> Reload3[Source/Restart]
    App6 --> Reload3
    App7 --> Reload4[Reload/Restart]
    App8 --> Reload4
    
    Reload1 --> End([Colors Applied])
    Reload2 --> End
    Reload3 --> End
    Reload4 --> End
    
    style Start fill:#e8f5e9
    style Generate fill:#e1f5ff
    style End fill:#e8f5e9
```

## Systemd Service Integration

```mermaid
graph TB
    subgraph "Systemd Service"
        Service[colorscheme-generator.service]
        Timer[colorscheme-generator.timer]
    end
    
    subgraph "Service Configuration"
        ExecStart[ExecStart=colorscheme-generator]
        Type[Type=oneshot]
        User[User=%u]
    end
    
    subgraph "Timer Configuration"
        OnCalendar[OnCalendar=hourly]
        Persistent[Persistent=true]
    end
    
    subgraph "Execution"
        Run[Run Generator]
        Output[Generate Files]
        Notify[Notify Applications]
    end
    
    Timer --> Service
    Service --> ExecStart
    Service --> Type
    Service --> User
    
    Timer --> OnCalendar
    Timer --> Persistent
    
    ExecStart --> Run
    Run --> Output
    Output --> Notify
    
    style Service fill:#e1f5ff
    style Timer fill:#fff3e0
    style Output fill:#e8f5e9
```

## Event-Driven Integration

```mermaid
sequenceDiagram
    participant FileWatcher
    participant EventHandler
    participant CSG
    participant OutputMgr
    participant Apps
    
    FileWatcher->>FileWatcher: watch wallpaper directory
    
    loop Monitor for changes
        FileWatcher->>FileWatcher: inotify/fswatch
    end
    
    FileWatcher->>EventHandler: file changed event
    EventHandler->>EventHandler: debounce (wait 1s)
    EventHandler->>CSG: generate(new_wallpaper)
    
    CSG->>CSG: extract colors
    CSG->>OutputMgr: write outputs
    OutputMgr-->>EventHandler: files written
    
    EventHandler->>Apps: send reload signal
    
    par Parallel Reloads
        Apps->>Apps: reload terminal
    and
        Apps->>Apps: reload window manager
    and
        Apps->>Apps: reload editor
    end
```

## API Integration Pattern

```mermaid
graph LR
    subgraph "External Application"
        App[Application Code]
        Config[App Configuration]
    end
    
    subgraph "Python API"
        Import[from colorscheme_generator import ...]
        Factory[ColorSchemeGeneratorFactory]
        Generator[Generator Instance]
        Scheme[ColorScheme Object]
    end
    
    subgraph "Usage"
        Extract[Extract Colors]
        Process[Process Colors]
        Apply[Apply to App]
    end
    
    App --> Import
    Import --> Factory
    Factory --> Generator
    Generator --> Scheme
    
    Scheme --> Extract
    Extract --> Process
    Process --> Apply
    Apply --> Config
    
    style App fill:#e1f5ff
    style Scheme fill:#fff3e0
    style Apply fill:#e8f5e9
```

## Batch Processing Integration

```mermaid
flowchart TD
    Start([Batch Process Start])
    
    Start --> Input[Load Image List]
    Input --> Parallel{Process in Parallel}
    
    Parallel --> Worker1[Worker 1]
    Parallel --> Worker2[Worker 2]
    Parallel --> Worker3[Worker 3]
    Parallel --> Worker4[Worker 4]
    
    Worker1 --> Gen1[Generate Colors]
    Worker2 --> Gen2[Generate Colors]
    Worker3 --> Gen3[Generate Colors]
    Worker4 --> Gen4[Generate Colors]
    
    Gen1 --> Out1[Write Outputs]
    Gen2 --> Out2[Write Outputs]
    Gen3 --> Out3[Write Outputs]
    Gen4 --> Out4[Write Outputs]
    
    Out1 --> Collect[Collect Results]
    Out2 --> Collect
    Out3 --> Collect
    Out4 --> Collect
    
    Collect --> Summary[Generate Summary]
    Summary --> End([Batch Complete])
    
    style Start fill:#e8f5e9
    style Parallel fill:#e1f5ff
    style End fill:#e8f5e9
```

## Plugin Architecture

```mermaid
graph TB
    subgraph "Core System"
        Core[ColorScheme Generator Core]
        PluginMgr[Plugin Manager]
    end
    
    subgraph "Plugin Interface"
        IPlugin[Plugin Interface]
        Hooks[Hook Points]
    end
    
    subgraph "Custom Plugins"
        Plugin1[Color Adjustment Plugin]
        Plugin2[Export Plugin]
        Plugin3[Notification Plugin]
    end
    
    subgraph "Hook Points"
        PreExtract[pre_extract_colors]
        PostExtract[post_extract_colors]
        PreRender[pre_render_template]
        PostRender[post_render_template]
        PostWrite[post_write_files]
    end
    
    Core --> PluginMgr
    PluginMgr --> IPlugin
    IPlugin --> Hooks
    
    Plugin1 -.implements.-> IPlugin
    Plugin2 -.implements.-> IPlugin
    Plugin3 -.implements.-> IPlugin
    
    Hooks --> PreExtract
    Hooks --> PostExtract
    Hooks --> PreRender
    Hooks --> PostRender
    Hooks --> PostWrite
    
    Plugin1 -.hooks into.-> PostExtract
    Plugin2 -.hooks into.-> PostWrite
    Plugin3 -.hooks into.-> PostWrite
    
    style Core fill:#e1f5ff
    style IPlugin fill:#fff3e0
```

