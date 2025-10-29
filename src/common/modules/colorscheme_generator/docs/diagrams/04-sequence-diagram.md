# Sequence Diagram

This diagram shows the sequence of interactions for generating a color scheme.

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Factory
    participant Settings
    participant Generator
    participant Image
    participant ColorScheme
    participant OutputMgr
    participant Templates
    participant FileSystem
    
    User->>CLI: generate colors from image
    CLI->>Settings: load settings
    Settings-->>CLI: AppConfig
    
    CLI->>Factory: create_auto(settings)
    
    Factory->>Factory: check wallust availability
    alt Wallust available
        Factory->>Generator: WallustGenerator(settings)
    else Pywal available
        Factory->>Generator: PywalGenerator(settings)
    else Neither available
        Factory->>Generator: CustomGenerator(settings)
    end
    
    Factory-->>CLI: generator instance
    
    CLI->>CLI: create GeneratorConfig
    CLI->>Generator: generate(image_path, config)
    
    Generator->>Image: validate image file
    alt Invalid image
        Image-->>Generator: InvalidImageError
        Generator-->>CLI: raise error
        CLI-->>User: error message
    else Valid image
        Image-->>Generator: validated path
        
        alt Pywal backend
            Generator->>Generator: check cache
            alt Cache exists
                Generator->>Generator: read from cache
            else No cache
                Generator->>Generator: run pywal command
            end
        else Wallust backend
            Generator->>Generator: run wallust --json
        else Custom backend
            Generator->>Image: load with PIL
            Image-->>Generator: image data
            Generator->>Generator: extract colors (k-means/median-cut/octree)
        end
        
        Generator->>ColorScheme: create ColorScheme object
        ColorScheme-->>Generator: scheme instance
        Generator-->>CLI: ColorScheme
        
        CLI->>OutputMgr: write_outputs(scheme, output_dir, formats)
        
        loop For each format
            OutputMgr->>Templates: load template
            Templates-->>OutputMgr: template
            
            OutputMgr->>OutputMgr: render template with scheme
            
            alt Render error
                OutputMgr-->>CLI: TemplateRenderError
                CLI-->>User: error message
            else Render success
                OutputMgr->>FileSystem: write file
                
                alt Write error
                    FileSystem-->>OutputMgr: OutputWriteError
                    OutputMgr-->>CLI: raise error
                    CLI-->>User: error message
                else Write success
                    FileSystem-->>OutputMgr: success
                    OutputMgr->>OutputMgr: add to output_files
                end
            end
        end
        
        OutputMgr-->>CLI: output_files dict
        CLI-->>User: success + file paths
    end
```

## Interaction Flow

### Phase 1: Initialization
1. User requests color generation
2. CLI loads settings from settings.toml
3. Factory auto-detects and creates appropriate backend
4. CLI creates runtime configuration

### Phase 2: Color Extraction
1. Generator validates image file
2. Backend-specific extraction:
   - **Pywal**: Check cache or run pywal
   - **Wallust**: Run wallust with JSON output
   - **Custom**: Load image with PIL and run algorithm
3. Parse colors into standardized format
4. Create ColorScheme object

### Phase 3: Output Generation
1. OutputManager receives ColorScheme
2. For each requested format:
   - Load Jinja2 template
   - Render template with color data
   - Write rendered content to file
3. Return dictionary of format → file path

### Phase 4: Completion
1. CLI receives output file paths
2. User is notified of success

