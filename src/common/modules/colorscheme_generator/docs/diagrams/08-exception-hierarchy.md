# Exception Hierarchy

This diagram shows the exception hierarchy and error handling flow.

```mermaid
classDiagram
    class Exception {
        <<built-in>>
    }
    
    class ColorSchemeGeneratorError {
        +message: str
        +__init__(message)
        +__str__() str
    }
    
    class BackendNotAvailableError {
        +backend: str
        +__init__(backend, message)
    }
    
    class ColorExtractionError {
        +image_path: Path
        +backend: str
        +__init__(image_path, backend, message)
    }
    
    class TemplateRenderError {
        +template_name: str
        +original_error: Exception
        +__init__(template_name, original_error)
    }
    
    class OutputWriteError {
        +file_path: Path
        +original_error: Exception
        +__init__(file_path, original_error)
    }
    
    class InvalidImageError {
        +image_path: Path
        +reason: str
        +__init__(image_path, reason)
    }
    
    class ConfigurationError {
        +config_key: str
        +__init__(config_key, message)
    }
    
    Exception <|-- ColorSchemeGeneratorError
    ColorSchemeGeneratorError <|-- BackendNotAvailableError
    ColorSchemeGeneratorError <|-- ColorExtractionError
    ColorSchemeGeneratorError <|-- TemplateRenderError
    ColorSchemeGeneratorError <|-- OutputWriteError
    ColorSchemeGeneratorError <|-- InvalidImageError
    ColorSchemeGeneratorError <|-- ConfigurationError
```

## Error Flow Diagram

```mermaid
flowchart TD
    Start([Operation Start])
    
    Start --> Op1{Load Settings}
    Op1 -->|Error| E1[ConfigurationError]
    Op1 -->|Success| Op2{Create Backend}
    
    Op2 -->|Not Available| E2[BackendNotAvailableError]
    Op2 -->|Success| Op3{Validate Image}
    
    Op3 -->|Invalid| E3[InvalidImageError]
    Op3 -->|Valid| Op4{Extract Colors}
    
    Op4 -->|Error| E4[ColorExtractionError]
    Op4 -->|Success| Op5{Render Templates}
    
    Op5 -->|Error| E5[TemplateRenderError]
    Op5 -->|Success| Op6{Write Files}
    
    Op6 -->|Error| E6[OutputWriteError]
    Op6 -->|Success| Success([Success])
    
    E1 --> Handle[Error Handler]
    E2 --> Handle
    E3 --> Handle
    E4 --> Handle
    E5 --> Handle
    E6 --> Handle
    
    Handle --> Log[Log Error]
    Log --> Cleanup[Cleanup Resources]
    Cleanup --> Reraise[Reraise or Return Error]
    
    style Start fill:#e8f5e9
    style Success fill:#e8f5e9
    style E1 fill:#ffebee
    style E2 fill:#ffebee
    style E3 fill:#ffebee
    style E4 fill:#ffebee
    style E5 fill:#ffebee
    style E6 fill:#ffebee
```

## Exception Handling Patterns

### Pattern 1: Try-Except with Specific Exceptions

```mermaid
sequenceDiagram
    participant Code
    participant Generator
    participant Exception
    participant Handler
    
    Code->>Generator: generate(image_path, config)
    
    alt Invalid Image
        Generator->>Exception: raise InvalidImageError
        Exception->>Handler: catch InvalidImageError
        Handler->>Handler: log error
        Handler->>Code: return None or default
    else Extraction Failed
        Generator->>Exception: raise ColorExtractionError
        Exception->>Handler: catch ColorExtractionError
        Handler->>Handler: try fallback backend
        Handler->>Code: retry or fail
    else Success
        Generator->>Code: return ColorScheme
    end
```

### Pattern 2: Fallback Chain

```mermaid
flowchart TD
    Start([Try Primary Backend])
    
    Start --> Try1{Try Wallust}
    Try1 -->|Success| Success([Return ColorScheme])
    Try1 -->|BackendNotAvailableError| Try2{Try Pywal}
    Try1 -->|ColorExtractionError| Try2
    
    Try2 -->|Success| Success
    Try2 -->|BackendNotAvailableError| Try3{Try Custom}
    Try2 -->|ColorExtractionError| Try3
    
    Try3 -->|Success| Success
    Try3 -->|Error| Fail([Raise Final Error])
    
    style Start fill:#e1f5ff
    style Success fill:#e8f5e9
    style Fail fill:#ffebee
```

### Pattern 3: Context Manager

```mermaid
sequenceDiagram
    participant Code
    participant Context
    participant Resource
    participant Exception
    
    Code->>Context: __enter__()
    Context->>Resource: acquire resource
    Resource-->>Context: resource handle
    Context-->>Code: resource
    
    Code->>Code: perform operations
    
    alt Operation Success
        Code->>Context: __exit__(None, None, None)
        Context->>Resource: release resource
        Resource-->>Context: success
        Context-->>Code: success
    else Operation Error
        Code->>Exception: error occurs
        Exception->>Context: __exit__(exc_type, exc_val, exc_tb)
        Context->>Resource: release resource (cleanup)
        Resource-->>Context: cleaned up
        Context->>Exception: reraise or suppress
        Exception-->>Code: exception propagated
    end
```

## Error Recovery Strategies

```mermaid
graph TB
    Error[Error Occurs]
    
    Error --> Type{Error Type}
    
    Type -->|BackendNotAvailableError| S1[Try Next Backend]
    Type -->|ColorExtractionError| S2[Retry with Different Algorithm]
    Type -->|InvalidImageError| S3[Validate and Reject]
    Type -->|TemplateRenderError| S4[Use Default Template]
    Type -->|OutputWriteError| S5[Try Alternative Path]
    Type -->|ConfigurationError| S6[Use Defaults]
    
    S1 --> Check1{Fallback Available?}
    Check1 -->|Yes| Retry1[Retry with Fallback]
    Check1 -->|No| Fail1[Fail Gracefully]
    
    S2 --> Check2{Alternative Algorithm?}
    Check2 -->|Yes| Retry2[Retry with Alternative]
    Check2 -->|No| Fail2[Fail Gracefully]
    
    S3 --> Fail3[Return Error to User]
    
    S4 --> Check4{Default Available?}
    Check4 -->|Yes| Retry4[Use Default]
    Check4 -->|No| Fail4[Fail Gracefully]
    
    S5 --> Check5{Alternative Path?}
    Check5 -->|Yes| Retry5[Try Alternative]
    Check5 -->|No| Fail5[Fail Gracefully]
    
    S6 --> Retry6[Use Default Config]
    
    Retry1 --> Success[Success]
    Retry2 --> Success
    Retry4 --> Success
    Retry5 --> Success
    Retry6 --> Success
    
    Fail1 --> Log[Log Error]
    Fail2 --> Log
    Fail3 --> Log
    Fail4 --> Log
    Fail5 --> Log
    
    Log --> Notify[Notify User]
    
    style Error fill:#ffebee
    style Success fill:#e8f5e9
    style Fail1 fill:#ffccbc
    style Fail2 fill:#ffccbc
    style Fail3 fill:#ffccbc
    style Fail4 fill:#ffccbc
    style Fail5 fill:#ffccbc
```

## Exception Context Information

```mermaid
graph LR
    subgraph "BackendNotAvailableError"
        B1[backend: str]
        B2[message: str]
        B3[Available backends list]
    end
    
    subgraph "ColorExtractionError"
        C1[image_path: Path]
        C2[backend: str]
        C3[message: str]
        C4[Original exception]
    end
    
    subgraph "InvalidImageError"
        I1[image_path: Path]
        I2[reason: str]
        I3[Supported formats]
    end
    
    subgraph "TemplateRenderError"
        T1[template_name: str]
        T2[original_error: Exception]
        T3[Template path]
    end
    
    subgraph "OutputWriteError"
        O1[file_path: Path]
        O2[original_error: Exception]
        O3[Permissions info]
    end
    
    subgraph "ConfigurationError"
        CF1[config_key: str]
        CF2[message: str]
        CF3[Expected type/value]
    end
    
    style B1 fill:#e3f2fd
    style C1 fill:#e3f2fd
    style I1 fill:#e3f2fd
    style T1 fill:#e3f2fd
    style O1 fill:#e3f2fd
    style CF1 fill:#e3f2fd
```

## Error Logging Flow

```mermaid
sequenceDiagram
    participant Code
    participant Exception
    participant Logger
    participant Handler
    participant User
    
    Code->>Exception: raise ColorSchemeGeneratorError
    Exception->>Logger: log.error(exception details)
    Logger->>Logger: format error message
    Logger->>Logger: add context (stack trace, etc.)
    Logger->>Handler: send to error handler
    
    Handler->>Handler: determine severity
    
    alt Critical Error
        Handler->>User: show error dialog
        Handler->>Logger: log to file
        Handler->>Code: exit with error code
    else Recoverable Error
        Handler->>User: show warning
        Handler->>Logger: log to file
        Handler->>Code: return error result
    else Minor Error
        Handler->>Logger: log to file
        Handler->>Code: continue with defaults
    end
```

