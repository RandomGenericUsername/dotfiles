# Configuration System

This diagram shows the configuration hierarchy and loading process.

```mermaid
graph TB
    subgraph "Configuration Sources"
        File[settings.toml]
        Env[Environment Variables]
        Runtime[Runtime Overrides]
    end
    
    subgraph "Dynaconf Layer"
        Dynaconf[Dynaconf Loader]
        Merge[Merge Strategy]
    end
    
    subgraph "Validation Layer"
        Pydantic[Pydantic Models]
        Validate[Validation]
    end
    
    subgraph "Configuration Objects"
        AppConfig[AppConfig]
        
        subgraph "Output Configuration"
            OutputSettings[OutputSettings]
            OutDir[directory: Path]
            OutFormats[formats: list]
        end
        
        subgraph "Generation Configuration"
            GenSettings[GenerationSettings]
            DefBackend[default_backend: Backend]
            ColorCount[color_count: int]
        end
        
        subgraph "Backend Configuration"
            BackendSettings[BackendSettings]
            PywalConf[pywal: PywalSettings]
            WallustConf[wallust: WallustSettings]
            CustomConf[custom: CustomSettings]
        end
    end
    
    subgraph "Runtime Configuration"
        GenConfig[GeneratorConfig]
        RuntimeDir[output_dir: Path]
        RuntimeFormats[formats: list]
        RuntimeOptions[backend_options: dict]
    end
    
    File --> Dynaconf
    Env --> Dynaconf
    Dynaconf --> Merge
    Merge --> Pydantic
    Pydantic --> Validate
    Validate --> AppConfig
    
    AppConfig --> OutputSettings
    AppConfig --> GenSettings
    AppConfig --> BackendSettings
    
    OutputSettings --> OutDir
    OutputSettings --> OutFormats
    
    GenSettings --> DefBackend
    GenSettings --> ColorCount
    
    BackendSettings --> PywalConf
    BackendSettings --> WallustConf
    BackendSettings --> CustomConf
    
    AppConfig -.from_settings.-> GenConfig
    Runtime -.override.-> GenConfig
    
    GenConfig --> RuntimeDir
    GenConfig --> RuntimeFormats
    GenConfig --> RuntimeOptions
    
    style File fill:#e3f2fd
    style Env fill:#e3f2fd
    style Runtime fill:#e3f2fd
    style AppConfig fill:#fff3e0
    style GenConfig fill:#e8f5e9
```

## Configuration Loading Process

```mermaid
sequenceDiagram
    participant App
    participant Settings
    participant Dynaconf
    participant FileSystem
    participant EnvVars
    participant Pydantic
    participant AppConfig
    
    App->>Settings: Settings.get()
    Settings->>Dynaconf: initialize
    
    Dynaconf->>FileSystem: read settings.toml
    FileSystem-->>Dynaconf: TOML data
    
    Dynaconf->>EnvVars: read COLORSCHEME_* vars
    EnvVars-->>Dynaconf: environment data
    
    Dynaconf->>Dynaconf: merge configurations
    Dynaconf-->>Settings: raw config dict
    
    Settings->>Pydantic: validate with AppConfig
    
    alt Validation Error
        Pydantic-->>Settings: ValidationError
        Settings-->>App: raise ConfigurationError
    else Validation Success
        Pydantic->>AppConfig: create instance
        AppConfig-->>Settings: validated config
        Settings-->>App: AppConfig instance
    end
```

## Configuration Hierarchy

```mermaid
graph TD
    subgraph "Priority Order (Highest to Lowest)"
        P1[1. Runtime Overrides]
        P2[2. Environment Variables]
        P3[3. settings.toml]
        P4[4. Default Values]
    end
    
    P1 --> Merge[Configuration Merger]
    P2 --> Merge
    P3 --> Merge
    P4 --> Merge
    
    Merge --> Final[Final Configuration]
    
    style P1 fill:#c8e6c9
    style P2 fill:#fff9c4
    style P3 fill:#e1bee7
    style P4 fill:#ffccbc
    style Final fill:#b3e5fc
```

## Configuration Schema

```mermaid
classDiagram
    class AppConfig {
        +output: OutputSettings
        +generation: GenerationSettings
        +backends: BackendSettings
    }
    
    class OutputSettings {
        +directory: Path
        +formats: list~ColorFormat~
    }
    
    class GenerationSettings {
        +default_backend: Backend
        +color_count: int
    }
    
    class BackendSettings {
        +pywal: PywalSettings
        +wallust: WallustSettings
        +custom: CustomSettings
    }
    
    class PywalSettings {
        +cache_dir: Path
        +use_cache: bool
    }
    
    class WallustSettings {
        +binary_path: Path
        +timeout: int
    }
    
    class CustomSettings {
        +algorithm: ColorAlgorithm
        +n_clusters: int
        +max_iterations: int
    }
    
    class GeneratorConfig {
        +output_dir: Path
        +formats: list~ColorFormat~
        +color_count: int
        +backend_options: dict
        +from_settings(settings, **overrides)$ GeneratorConfig
    }
    
    class Backend {
        <<enumeration>>
        PYWAL
        WALLUST
        CUSTOM
    }
    
    class ColorFormat {
        <<enumeration>>
        JSON
        CSS
        SHELL
        YAML
        TOML
    }
    
    class ColorAlgorithm {
        <<enumeration>>
        KMEANS
        MEDIAN_CUT
        OCTREE
    }
    
    AppConfig *-- OutputSettings
    AppConfig *-- GenerationSettings
    AppConfig *-- BackendSettings
    
    BackendSettings *-- PywalSettings
    BackendSettings *-- WallustSettings
    BackendSettings *-- CustomSettings
    
    OutputSettings ..> ColorFormat : uses
    GenerationSettings ..> Backend : uses
    CustomSettings ..> ColorAlgorithm : uses
    
    GeneratorConfig ..> AppConfig : from_settings
    GeneratorConfig ..> ColorFormat : uses
```

## Example Configuration Flow

```mermaid
flowchart LR
    subgraph "settings.toml"
        T1["[output]<br/>directory = '~/.cache/colors'<br/>formats = ['json', 'css']"]
        T2["[generation]<br/>default_backend = 'wallust'<br/>color_count = 16"]
        T3["[backends.custom]<br/>algorithm = 'kmeans'<br/>n_clusters = 16"]
    end
    
    subgraph "Environment"
        E1["COLORSCHEME_OUTPUT__DIRECTORY=<br/>/tmp/colors"]
    end
    
    subgraph "Runtime"
        R1["formats=['json', 'yaml']<br/>output_dir='/custom/path'"]
    end
    
    T1 --> Merge[Merge]
    T2 --> Merge
    T3 --> Merge
    E1 --> Merge
    R1 --> Merge
    
    Merge --> Final["Final Config:<br/>directory=/custom/path<br/>formats=['json','yaml']<br/>backend=wallust<br/>algorithm=kmeans"]
    
    style T1 fill:#e1bee7
    style T2 fill:#e1bee7
    style T3 fill:#e1bee7
    style E1 fill:#fff9c4
    style R1 fill:#c8e6c9
    style Final fill:#b3e5fc
```

