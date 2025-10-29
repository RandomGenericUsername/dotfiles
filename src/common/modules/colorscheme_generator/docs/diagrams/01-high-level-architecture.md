# High-Level Architecture

This diagram shows the overall architecture of the colorscheme_generator module.

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[CLI Interface]
        API[Python API]
    end
    
    subgraph "Orchestration Layer"
        Factory[ColorSchemeGeneratorFactory]
        Settings[Settings Loader]
    end
    
    subgraph "Layer 1: Color Extraction"
        ABC[ColorSchemeGenerator ABC]
        Pywal[PywalGenerator]
        Wallust[WallustGenerator]
        Custom[CustomGenerator]
        
        ABC -.implements.-> Pywal
        ABC -.implements.-> Wallust
        ABC -.implements.-> Custom
    end
    
    subgraph "Data Layer"
        ColorScheme[ColorScheme Object]
        Color[Color Type]
        Config[GeneratorConfig]
    end
    
    subgraph "Layer 2: Output Generation"
        OutputMgr[OutputManager]
        Templates[Jinja2 Templates]
        
        OutputMgr --> Templates
    end
    
    subgraph "Output Files"
        JSON[colors.json]
        CSS[colors.css]
        Shell[colors.sh]
        YAML[colors.yaml]
    end
    
    CLI --> Factory
    API --> Factory
    CLI --> Settings
    API --> Settings
    
    Factory --> Pywal
    Factory --> Wallust
    Factory --> Custom
    
    Settings --> Config
    
    Pywal --> ColorScheme
    Wallust --> ColorScheme
    Custom --> ColorScheme
    
    ColorScheme --> Color
    
    ColorScheme --> OutputMgr
    Config --> OutputMgr
    
    OutputMgr --> JSON
    OutputMgr --> CSS
    OutputMgr --> Shell
    OutputMgr --> YAML
    
    style ABC fill:#e1f5ff
    style ColorScheme fill:#fff3e0
    style OutputMgr fill:#f3e5f5
```

## Key Components

### User Interface Layer
- **CLI Interface**: Command-line tool for generating color schemes
- **Python API**: Programmatic access to the module

### Orchestration Layer
- **Factory**: Creates backend instances based on selection/auto-detection
- **Settings Loader**: Loads and validates configuration from settings.toml

### Layer 1: Color Extraction
- **ColorSchemeGenerator ABC**: Abstract base class defining the interface
- **PywalGenerator**: Uses pywal for color extraction
- **WallustGenerator**: Uses wallust (Rust) for color extraction
- **CustomGenerator**: Pure Python implementation with PIL

### Data Layer
- **ColorScheme**: Complete color scheme with metadata
- **Color**: Single color in multiple formats (hex, RGB, HSL)
- **GeneratorConfig**: Runtime configuration

### Layer 2: Output Generation
- **OutputManager**: Renders templates and writes files
- **Jinja2 Templates**: Template files for each output format

### Output Files
- **JSON**: JSON format with colors and metadata
- **CSS**: CSS variables format
- **Shell**: Shell script with exported variables
- **YAML**: YAML format

