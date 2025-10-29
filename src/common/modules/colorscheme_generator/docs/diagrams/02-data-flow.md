# Data Flow Diagram

This diagram shows how data flows through the system from image input to file output.

```mermaid
flowchart TD
    Start([User Request]) --> LoadSettings[Load Settings]
    LoadSettings --> CreateConfig[Create GeneratorConfig]
    
    CreateConfig --> ChooseBackend{Choose Backend}
    
    ChooseBackend -->|Auto| AutoDetect[Auto-detect Backend]
    ChooseBackend -->|Manual| ManualSelect[Select Specific Backend]
    
    AutoDetect --> TryWallust{Wallust Available?}
    TryWallust -->|Yes| UseWallust[Use WallustGenerator]
    TryWallust -->|No| TryPywal{Pywal Available?}
    TryPywal -->|Yes| UsePywal[Use PywalGenerator]
    TryPywal -->|No| UseCustom[Use CustomGenerator]
    
    ManualSelect --> CreateGenerator[Create Generator Instance]
    UseWallust --> CreateGenerator
    UsePywal --> CreateGenerator
    UseCustom --> CreateGenerator
    
    CreateGenerator --> ValidateImage[Validate Image File]
    ValidateImage -->|Invalid| Error1[Raise InvalidImageError]
    ValidateImage -->|Valid| ExtractColors[Extract Colors from Image]
    
    ExtractColors -->|Pywal| RunPywal[Run pywal/Read cache]
    ExtractColors -->|Wallust| RunWallust[Run wallust --json]
    ExtractColors -->|Custom| RunCustom[PIL + K-means/Median-cut/Octree]
    
    RunPywal --> ParseColors[Parse Colors]
    RunWallust --> ParseColors
    RunCustom --> ParseColors
    
    ParseColors -->|Error| Error2[Raise ColorExtractionError]
    ParseColors -->|Success| CreateScheme[Create ColorScheme Object]
    
    CreateScheme --> SchemeData{ColorScheme}
    SchemeData --> Background[background: Color]
    SchemeData --> Foreground[foreground: Color]
    SchemeData --> Cursor[cursor: Color]
    SchemeData --> Colors[colors: list of 16 Colors]
    SchemeData --> Metadata[metadata: source, backend, timestamp]
    
    Background --> OutputMgr[OutputManager]
    Foreground --> OutputMgr
    Cursor --> OutputMgr
    Colors --> OutputMgr
    Metadata --> OutputMgr
    
    OutputMgr --> ForEachFormat{For Each Format}
    
    ForEachFormat --> LoadTemplate[Load Jinja2 Template]
    LoadTemplate -->|Error| Error3[Raise TemplateRenderError]
    LoadTemplate -->|Success| RenderTemplate[Render Template with ColorScheme]
    
    RenderTemplate --> WriteFile[Write to File]
    WriteFile -->|Error| Error4[Raise OutputWriteError]
    WriteFile -->|Success| AddToDict[Add to output_files dict]
    
    AddToDict --> MoreFormats{More Formats?}
    MoreFormats -->|Yes| ForEachFormat
    MoreFormats -->|No| UpdateScheme[Update scheme.output_files]
    
    UpdateScheme --> ReturnFiles[Return output_files dict]
    ReturnFiles --> End([Complete])
    
    Error1 --> End
    Error2 --> End
    Error3 --> End
    Error4 --> End
    
    style Start fill:#e8f5e9
    style End fill:#e8f5e9
    style SchemeData fill:#fff3e0
    style Error1 fill:#ffebee
    style Error2 fill:#ffebee
    style Error3 fill:#ffebee
    style Error4 fill:#ffebee
```

## Data Transformations

### Stage 1: Configuration
- **Input**: User request (image path, options)
- **Process**: Load settings.toml, merge with runtime overrides
- **Output**: GeneratorConfig object

### Stage 2: Backend Selection
- **Input**: Backend preference (or auto)
- **Process**: Check availability, create instance
- **Output**: ColorSchemeGenerator instance

### Stage 3: Color Extraction
- **Input**: Image file (PNG/JPG/etc.)
- **Process**: Backend-specific extraction algorithm
- **Output**: Raw color data

### Stage 4: Color Parsing
- **Input**: Raw color data (backend-specific format)
- **Process**: Parse and standardize colors
- **Output**: ColorScheme object with 16 colors + special colors

### Stage 5: Template Rendering
- **Input**: ColorScheme object + format selection
- **Process**: Render Jinja2 templates
- **Output**: Rendered content strings

### Stage 6: File Writing
- **Input**: Rendered content + output directory
- **Process**: Write files to disk
- **Output**: Dictionary of format → file path

