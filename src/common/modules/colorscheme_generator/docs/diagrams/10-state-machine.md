# State Machine Diagrams

This diagram shows the state transitions during color scheme generation.

```mermaid
stateDiagram-v2
    [*] --> Initialized: Create Generator
    
    Initialized --> ValidatingImage: generate() called
    
    ValidatingImage --> ImageValid: Image exists and valid
    ValidatingImage --> Error: Invalid image
    
    ImageValid --> ExtractingColors: Start extraction
    
    ExtractingColors --> PywalExtraction: Using Pywal
    ExtractingColors --> WallustExtraction: Using Wallust
    ExtractingColors --> CustomExtraction: Using Custom
    
    PywalExtraction --> CheckingCache: Check cache
    CheckingCache --> ReadingCache: Cache exists
    CheckingCache --> RunningPywal: No cache
    ReadingCache --> ParsingColors: Cache read
    RunningPywal --> ParsingColors: Pywal complete
    
    WallustExtraction --> RunningWallust: Execute wallust
    RunningWallust --> ParsingJSON: Wallust complete
    ParsingJSON --> ParsingColors: JSON parsed
    
    CustomExtraction --> LoadingImage: Load with PIL
    LoadingImage --> RunningAlgorithm: Image loaded
    RunningAlgorithm --> ParsingColors: Algorithm complete
    
    ParsingColors --> ColorsExtracted: Colors parsed
    ParsingColors --> Error: Extraction failed
    
    ColorsExtracted --> CreatingScheme: Create ColorScheme
    CreatingScheme --> SchemeCreated: Scheme object ready
    
    SchemeCreated --> RenderingTemplates: Start rendering
    
    RenderingTemplates --> LoadingTemplate: For each format
    LoadingTemplate --> TemplateLoaded: Template found
    LoadingTemplate --> Error: Template not found
    
    TemplateLoaded --> Rendering: Render with context
    Rendering --> Rendered: Render success
    Rendering --> Error: Render failed
    
    Rendered --> WritingFile: Write to disk
    WritingFile --> FileWritten: Write success
    WritingFile --> Error: Write failed
    
    FileWritten --> MoreFormats: Check remaining
    MoreFormats --> LoadingTemplate: More formats
    MoreFormats --> AllFilesWritten: All complete
    
    AllFilesWritten --> Complete: Return results
    
    Complete --> [*]
    Error --> [*]
    
    note right of ValidatingImage
        Checks:
        - File exists
        - Valid format
        - Readable
        - Size limits
    end note
    
    note right of ParsingColors
        Standardizes colors:
        - Convert to Color objects
        - Validate count
        - Assign special colors
    end note
    
    note right of RenderingTemplates
        For each format:
        - Load template
        - Build context
        - Render
        - Write file
    end note
```

## Backend Selection State Machine

```mermaid
stateDiagram-v2
    [*] --> SelectingBackend: Factory.create_auto()
    
    SelectingBackend --> CheckingWallust: Check availability
    
    CheckingWallust --> WallustAvailable: Binary found
    CheckingWallust --> CheckingPywal: Not available
    
    WallustAvailable --> CreatingWallust: Create instance
    CreatingWallust --> BackendReady: Wallust ready
    
    CheckingPywal --> PywalAvailable: Package found
    CheckingPywal --> UsingCustom: Not available
    
    PywalAvailable --> CreatingPywal: Create instance
    CreatingPywal --> BackendReady: Pywal ready
    
    UsingCustom --> CreatingCustom: Always available
    CreatingCustom --> BackendReady: Custom ready
    
    BackendReady --> [*]
    
    note right of CheckingWallust
        Checks:
        - Binary in PATH
        - Executable permissions
        - Version compatibility
    end note
    
    note right of CheckingPywal
        Checks:
        - Python package installed
        - Cache directory exists
        - Import successful
    end note
```

## Configuration Loading State Machine

```mermaid
stateDiagram-v2
    [*] --> LoadingSettings: Settings.get()
    
    LoadingSettings --> ReadingFile: Read settings.toml
    ReadingFile --> FileRead: File exists
    ReadingFile --> UsingDefaults: File not found
    
    FileRead --> ReadingEnv: Read environment
    UsingDefaults --> ReadingEnv: Use defaults
    
    ReadingEnv --> MergingConfig: Merge sources
    
    MergingConfig --> Validating: Validate with Pydantic
    
    Validating --> ValidationSuccess: All valid
    Validating --> ValidationError: Invalid config
    
    ValidationSuccess --> CreatingAppConfig: Create AppConfig
    CreatingAppConfig --> ConfigReady: Config ready
    
    ValidationError --> [*]: Raise error
    ConfigReady --> [*]
    
    note right of MergingConfig
        Priority order:
        1. Runtime overrides
        2. Environment vars
        3. settings.toml
        4. Defaults
    end note
```

## Output Generation State Machine

```mermaid
stateDiagram-v2
    [*] --> ReceivingScheme: OutputManager.write_outputs()
    
    ReceivingScheme --> ValidatingOutputDir: Check output directory
    
    ValidatingOutputDir --> DirExists: Directory exists
    ValidatingOutputDir --> CreatingDir: Directory missing
    
    CreatingDir --> DirCreated: mkdir success
    CreatingDir --> Error: mkdir failed
    
    DirExists --> ProcessingFormats: Start processing
    DirCreated --> ProcessingFormats: Start processing
    
    ProcessingFormats --> NextFormat: Get next format
    
    NextFormat --> LoadingTemplate: Format available
    NextFormat --> AllComplete: No more formats
    
    LoadingTemplate --> TemplateFound: Template exists
    LoadingTemplate --> Error: Template missing
    
    TemplateFound --> BuildingContext: Build render context
    BuildingContext --> RenderingTemplate: Context ready
    
    RenderingTemplate --> RenderSuccess: Render complete
    RenderingTemplate --> Error: Render failed
    
    RenderSuccess --> WritingOutput: Write to file
    WritingOutput --> WriteSuccess: File written
    WritingOutput --> Error: Write failed
    
    WriteSuccess --> AddingToDict: Add to output_files
    AddingToDict --> NextFormat: Continue
    
    AllComplete --> UpdatingScheme: Update scheme.output_files
    UpdatingScheme --> ReturningResults: Return dict
    
    ReturningResults --> [*]
    Error --> [*]
```

## Error Recovery State Machine

```mermaid
stateDiagram-v2
    [*] --> Operating: Normal operation
    
    Operating --> ErrorOccurred: Exception raised
    
    ErrorOccurred --> IdentifyingError: Identify error type
    
    IdentifyingError --> BackendError: BackendNotAvailableError
    IdentifyingError --> ExtractionError: ColorExtractionError
    IdentifyingError --> ImageError: InvalidImageError
    IdentifyingError --> TemplateError: TemplateRenderError
    IdentifyingError --> WriteError: OutputWriteError
    IdentifyingError --> ConfigError: ConfigurationError
    
    BackendError --> CheckingFallback: Check fallback available
    CheckingFallback --> TryingFallback: Fallback exists
    CheckingFallback --> Failed: No fallback
    
    TryingFallback --> Operating: Retry with fallback
    TryingFallback --> Failed: Fallback also failed
    
    ExtractionError --> CheckingAlternative: Check alternative algorithm
    CheckingAlternative --> TryingAlternative: Alternative exists
    CheckingAlternative --> Failed: No alternative
    
    TryingAlternative --> Operating: Retry with alternative
    TryingAlternative --> Failed: Alternative also failed
    
    ImageError --> LoggingError: Log error
    TemplateError --> CheckingDefault: Check default template
    WriteError --> CheckingAltPath: Check alternative path
    ConfigError --> UsingDefaults: Use default config
    
    CheckingDefault --> UsingDefault: Default exists
    CheckingDefault --> Failed: No default
    
    UsingDefault --> Operating: Retry with default
    
    CheckingAltPath --> TryingAltPath: Alternative exists
    CheckingAltPath --> Failed: No alternative
    
    TryingAltPath --> Operating: Retry with alt path
    TryingAltPath --> Failed: Alt path also failed
    
    UsingDefaults --> Operating: Retry with defaults
    
    LoggingError --> Failed: Cannot recover
    
    Failed --> Cleanup: Cleanup resources
    Cleanup --> [*]: Exit with error
    
    note right of CheckingFallback
        Fallback chain:
        1. Wallust
        2. Pywal
        3. Custom
    end note
```

## Cache State Machine (Pywal Backend)

```mermaid
stateDiagram-v2
    [*] --> CheckingCache: generate() called
    
    CheckingCache --> CacheExists: Check ~/.cache/wal/
    
    CacheExists --> ValidatingCache: Cache file found
    CacheExists --> NoCache: Cache not found
    
    ValidatingCache --> CacheValid: Valid and recent
    ValidatingCache --> CacheInvalid: Invalid or stale
    
    CacheValid --> ReadingCache: Read cache
    ReadingCache --> CacheRead: Parse JSON
    CacheRead --> ReturningColors: Return colors
    
    CacheInvalid --> RunningPywal: Generate new
    NoCache --> RunningPywal: Generate new
    
    RunningPywal --> PywalComplete: Pywal finished
    PywalComplete --> WritingCache: Write to cache
    WritingCache --> CacheWritten: Cache updated
    CacheWritten --> ReturningColors: Return colors
    
    ReturningColors --> [*]
    
    note right of ValidatingCache
        Validation checks:
        - File readable
        - Valid JSON
        - Correct structure
        - Timestamp recent
    end note
```

## Template Rendering State Machine

```mermaid
stateDiagram-v2
    [*] --> InitializingEnv: Initialize Jinja2
    
    InitializingEnv --> EnvReady: Environment created
    
    EnvReady --> LoadingTemplate: Load template
    
    LoadingTemplate --> TemplateLoaded: Template found
    LoadingTemplate --> TemplateNotFound: Template missing
    
    TemplateLoaded --> BuildingContext: Build context dict
    
    BuildingContext --> ContextReady: Context complete
    
    ContextReady --> Rendering: template.render(context)
    
    Rendering --> CheckingSyntax: Parse template
    
    CheckingSyntax --> SyntaxValid: Syntax OK
    CheckingSyntax --> SyntaxError: Syntax error
    
    SyntaxValid --> Evaluating: Evaluate expressions
    
    Evaluating --> EvaluationSuccess: All expressions OK
    Evaluating --> UndefinedError: Undefined variable
    Evaluating --> RuntimeError: Runtime error
    
    EvaluationSuccess --> RenderComplete: Rendered string
    
    RenderComplete --> [*]
    
    TemplateNotFound --> [*]: Raise error
    SyntaxError --> [*]: Raise error
    UndefinedError --> [*]: Raise error
    RuntimeError --> [*]: Raise error
```

