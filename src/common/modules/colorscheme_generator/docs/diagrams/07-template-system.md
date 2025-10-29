# Template System

This diagram shows how the Jinja2 template system works.

```mermaid
graph TB
    subgraph "Input"
        ColorScheme[ColorScheme Object]
        Config[GeneratorConfig]
    end
    
    subgraph "OutputManager"
        OM[OutputManager]
        TemplateDir[Template Directory]
        JinjaEnv[Jinja2 Environment]
    end
    
    subgraph "Templates"
        JSON[colors.json.j2]
        CSS[colors.css.j2]
        Shell[colors.sh.j2]
        YAML[colors.yaml.j2]
        TOML[colors.toml.j2]
        Custom[custom.j2]
    end
    
    subgraph "Rendering Process"
        Load[Load Template]
        Context[Build Context]
        Render[Render Template]
        Validate[Validate Output]
    end
    
    subgraph "Output Files"
        OutJSON[colors.json]
        OutCSS[colors.css]
        OutShell[colors.sh]
        OutYAML[colors.yaml]
        OutTOML[colors.toml]
        OutCustom[custom.ext]
    end
    
    ColorScheme --> OM
    Config --> OM
    
    OM --> TemplateDir
    TemplateDir --> JinjaEnv
    
    JinjaEnv --> JSON
    JinjaEnv --> CSS
    JinjaEnv --> Shell
    JinjaEnv --> YAML
    JinjaEnv --> TOML
    JinjaEnv --> Custom
    
    JSON --> Load
    CSS --> Load
    Shell --> Load
    YAML --> Load
    TOML --> Load
    Custom --> Load
    
    Load --> Context
    ColorScheme -.data.-> Context
    Context --> Render
    Render --> Validate
    
    Validate --> OutJSON
    Validate --> OutCSS
    Validate --> OutShell
    Validate --> OutYAML
    Validate --> OutTOML
    Validate --> OutCustom
    
    style ColorScheme fill:#fff3e0
    style OM fill:#e1f5ff
    style OutJSON fill:#e8f5e9
    style OutCSS fill:#e8f5e9
    style OutShell fill:#e8f5e9
    style OutYAML fill:#e8f5e9
```

## Template Context

```mermaid
graph LR
    subgraph "ColorScheme Data"
        BG[background]
        FG[foreground]
        CUR[cursor]
        C0[colors[0]]
        C1[colors[1]]
        C15[colors[15]]
        SRC[source_image]
        BACK[backend]
        TIME[timestamp]
    end
    
    subgraph "Template Context"
        CTX[Context Dictionary]
    end
    
    subgraph "Available in Templates"
        T_BG["{{ background.hex }}"]
        T_FG["{{ foreground.rgb }}"]
        T_CUR["{{ cursor.hsl }}"]
        T_LOOP["{% for color in colors %}"]
        T_SRC["{{ source_image }}"]
        T_BACK["{{ backend }}"]
    end
    
    BG --> CTX
    FG --> CTX
    CUR --> CTX
    C0 --> CTX
    C1 --> CTX
    C15 --> CTX
    SRC --> CTX
    BACK --> CTX
    TIME --> CTX
    
    CTX --> T_BG
    CTX --> T_FG
    CTX --> T_CUR
    CTX --> T_LOOP
    CTX --> T_SRC
    CTX --> T_BACK
    
    style CTX fill:#fff3e0
```

## Template Rendering Flow

```mermaid
sequenceDiagram
    participant OM as OutputManager
    participant Jinja as Jinja2 Environment
    participant Template
    participant Context
    participant Output
    
    OM->>OM: for each format in formats
    OM->>Jinja: get_template(template_name)
    Jinja->>Template: load template file
    Template-->>Jinja: template object
    Jinja-->>OM: template
    
    OM->>Context: build context from ColorScheme
    Context-->>OM: context dict
    
    OM->>Template: render(context)
    
    alt Rendering Error
        Template-->>OM: TemplateError
        OM->>OM: raise TemplateRenderError
    else Rendering Success
        Template-->>OM: rendered string
        
        OM->>Output: write to file
        
        alt Write Error
            Output-->>OM: IOError
            OM->>OM: raise OutputWriteError
        else Write Success
            Output-->>OM: success
            OM->>OM: add to output_files dict
        end
    end
```

## Built-in Templates

### JSON Template Structure
```mermaid
graph TD
    JSON[colors.json.j2]
    
    JSON --> Root{JSON Object}
    Root --> Special[Special Colors]
    Root --> Colors[Colors Array]
    Root --> Meta[Metadata]
    
    Special --> BG["background: { hex, rgb, hsl }"]
    Special --> FG["foreground: { hex, rgb, hsl }"]
    Special --> CUR["cursor: { hex, rgb, hsl }"]
    
    Colors --> C0["colors[0]: { hex, rgb, hsl }"]
    Colors --> C1["colors[1]: { hex, rgb, hsl }"]
    Colors --> Dots[...]
    Colors --> C15["colors[15]: { hex, rgb, hsl }"]
    
    Meta --> Source["source_image: path"]
    Meta --> Backend["backend: name"]
    Meta --> Timestamp["timestamp: ISO8601"]
    
    style JSON fill:#e1f5ff
    style Root fill:#fff3e0
```

### CSS Template Structure
```mermaid
graph TD
    CSS[colors.css.j2]
    
    CSS --> Root[":root selector"]
    Root --> Vars[CSS Variables]
    
    Vars --> BG["--color-background: hex"]
    Vars --> FG["--color-foreground: hex"]
    Vars --> CUR["--color-cursor: hex"]
    Vars --> C0["--color-0: hex"]
    Vars --> C1["--color-1: hex"]
    Vars --> Dots[...]
    Vars --> C15["--color-15: hex"]
    
    style CSS fill:#e1f5ff
    style Root fill:#fff3e0
```

### Shell Template Structure
```mermaid
graph TD
    Shell[colors.sh.j2]
    
    Shell --> Shebang["#!/bin/bash"]
    Shell --> Exports[Export Statements]
    
    Exports --> BG["export COLOR_BACKGROUND='hex'"]
    Exports --> FG["export COLOR_FOREGROUND='hex'"]
    Exports --> CUR["export COLOR_CURSOR='hex'"]
    Exports --> C0["export COLOR_0='hex'"]
    Exports --> C1["export COLOR_1='hex'"]
    Exports --> Dots[...]
    Exports --> C15["export COLOR_15='hex'"]
    
    style Shell fill:#e1f5ff
    style Shebang fill:#fff3e0
```

## Custom Template Creation

```mermaid
flowchart TD
    Start([Create Custom Template])
    
    Start --> Step1[Create .j2 file in templates/]
    Step1 --> Step2[Define template structure]
    Step2 --> Step3[Use Jinja2 syntax]
    
    Step3 --> Vars{Available Variables}
    Vars --> V1["{{ background }}"]
    Vars --> V2["{{ foreground }}"]
    Vars --> V3["{{ cursor }}"]
    Vars --> V4["{{ colors }}"]
    Vars --> V5["{{ source_image }}"]
    Vars --> V6["{{ backend }}"]
    
    V1 --> Step4[Add filters/logic]
    V2 --> Step4
    V3 --> Step4
    V4 --> Step4
    V5 --> Step4
    V6 --> Step4
    
    Step4 --> Filters{Jinja2 Features}
    Filters --> F1["Loops: {% for %}"]
    Filters --> F2["Conditionals: {% if %}"]
    Filters --> F3["Filters: | upper"]
    Filters --> F4["Comments: {# #}"]
    
    F1 --> Step5[Test template]
    F2 --> Step5
    F3 --> Step5
    F4 --> Step5
    
    Step5 --> Step6[Add to ColorFormat enum]
    Step6 --> Step7[Use in configuration]
    Step7 --> End([Template Ready])
    
    style Start fill:#e8f5e9
    style End fill:#e8f5e9
    style Vars fill:#fff3e0
    style Filters fill:#e1f5ff
```

## Template Error Handling

```mermaid
graph TB
    Render[Render Template]
    
    Render --> Check1{Template Exists?}
    Check1 -->|No| E1[TemplateNotFound]
    Check1 -->|Yes| Check2{Valid Syntax?}
    
    Check2 -->|No| E2[TemplateSyntaxError]
    Check2 -->|Yes| Check3{Context Valid?}
    
    Check3 -->|No| E3[UndefinedError]
    Check3 -->|Yes| Check4{Render Success?}
    
    Check4 -->|No| E4[TemplateRuntimeError]
    Check4 -->|Yes| Success[Rendered Output]
    
    E1 --> Wrap[Wrap in TemplateRenderError]
    E2 --> Wrap
    E3 --> Wrap
    E4 --> Wrap
    
    Wrap --> Raise[Raise to caller]
    
    style Render fill:#e1f5ff
    style Success fill:#e8f5e9
    style E1 fill:#ffebee
    style E2 fill:#ffebee
    style E3 fill:#ffebee
    style E4 fill:#ffebee
```

