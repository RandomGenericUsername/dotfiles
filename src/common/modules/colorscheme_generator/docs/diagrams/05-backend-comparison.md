# Backend Comparison

This diagram compares the three backend implementations.

```mermaid
graph TB
    subgraph "Pywal Backend"
        P1[PywalGenerator]
        P2{Cache Exists?}
        P3[Read ~/.cache/wal/colors.json]
        P4[Run: wal -i image.png]
        P5[Parse JSON]
        P6[ColorScheme]
        
        P1 --> P2
        P2 -->|Yes| P3
        P2 -->|No| P4
        P3 --> P5
        P4 --> P5
        P5 --> P6
    end
    
    subgraph "Wallust Backend"
        W1[WallustGenerator]
        W2[Run: wallust --json image.png]
        W3[Capture stdout]
        W4[Parse JSON]
        W5[ColorScheme]
        
        W1 --> W2
        W2 --> W3
        W3 --> W4
        W4 --> W5
    end
    
    subgraph "Custom Backend"
        C1[CustomGenerator]
        C2[Load image with PIL]
        C3{Algorithm?}
        C4[K-means clustering]
        C5[Median-cut quantization]
        C6[Octree quantization]
        C7[Extract dominant colors]
        C8[Assign special colors]
        C9[ColorScheme]
        
        C1 --> C2
        C2 --> C3
        C3 -->|kmeans| C4
        C3 -->|median_cut| C5
        C3 -->|octree| C6
        C4 --> C7
        C5 --> C7
        C6 --> C7
        C7 --> C8
        C8 --> C9
    end
    
    style P1 fill:#e3f2fd
    style W1 fill:#f3e5f5
    style C1 fill:#e8f5e9
    style P6 fill:#fff3e0
    style W5 fill:#fff3e0
    style C9 fill:#fff3e0
```

## Feature Comparison

```mermaid
graph LR
    subgraph Features
        F1[Speed]
        F2[Quality]
        F3[Dependencies]
        F4[Customization]
        F5[Reliability]
    end
    
    subgraph "Pywal ⭐⭐⭐"
        PF1[Fast - uses cache]
        PF2[Good - proven algorithm]
        PF3[Requires pywal Python package]
        PF4[Limited - uses pywal settings]
        PF5[High - mature project]
    end
    
    subgraph "Wallust ⭐⭐⭐⭐"
        WF1[Very Fast - Rust binary]
        WF2[Excellent - advanced algorithm]
        WF3[Requires wallust binary]
        WF4[Medium - JSON output only]
        WF5[High - actively maintained]
    end
    
    subgraph "Custom ⭐⭐⭐⭐⭐"
        CF1[Medium - pure Python]
        CF2[Good - configurable]
        CF3[Only PIL required]
        CF4[High - 3 algorithms]
        CF5[Very High - no external deps]
    end
    
    F1 -.-> PF1
    F1 -.-> WF1
    F1 -.-> CF1
    
    F2 -.-> PF2
    F2 -.-> WF2
    F2 -.-> CF2
    
    F3 -.-> PF3
    F3 -.-> WF3
    F3 -.-> CF3
    
    F4 -.-> PF4
    F4 -.-> WF4
    F4 -.-> CF4
    
    F5 -.-> PF5
    F5 -.-> WF5
    F5 -.-> CF5
```

## Detailed Comparison Table

| Feature | Pywal | Wallust | Custom |
|---------|-------|---------|--------|
| **Language** | Python | Rust | Python |
| **Speed** | Fast (cached) | Very Fast | Medium |
| **Quality** | Good | Excellent | Good |
| **Dependencies** | pywal package | wallust binary | PIL only |
| **Algorithms** | 1 (pywal's) | 1 (wallust's) | 3 (k-means, median-cut, octree) |
| **Customization** | Low | Medium | High |
| **Cache Support** | Yes | No | No |
| **JSON Output** | Yes | Yes | N/A (internal) |
| **Reliability** | High | High | Very High |
| **Best For** | Quick generation with caching | High-quality colors, speed | Maximum portability, customization |

## Algorithm Details

### Pywal Algorithm
1. Reads from `~/.cache/wal/colors.json` if available
2. Otherwise runs `wal -i <image>` command
3. Pywal uses imagemagick for color extraction
4. Returns 16 colors + special colors

### Wallust Algorithm
1. Runs `wallust --json <image>` command
2. Wallust uses advanced color extraction (Rust implementation)
3. Captures JSON output from stdout
4. Parses colors and metadata

### Custom Algorithms

**K-means Clustering:**
- Groups pixels into K clusters
- Uses cluster centers as colors
- Fast and effective for most images

**Median-cut Quantization:**
- Recursively divides color space
- Finds median along longest axis
- Good for images with distinct color regions

**Octree Quantization:**
- Builds tree structure of colors
- Prunes tree to desired color count
- Excellent for gradients and smooth transitions

## When to Use Each Backend

```mermaid
flowchart TD
    Start{Choose Backend}
    
    Start -->|Need speed + have pywal| Pywal[Use Pywal]
    Start -->|Need quality + have wallust| Wallust[Use Wallust]
    Start -->|Need portability| Custom[Use Custom]
    Start -->|Need customization| Custom
    Start -->|Unsure| Auto[Use Auto-detection]
    
    Auto --> Check1{Wallust available?}
    Check1 -->|Yes| Wallust
    Check1 -->|No| Check2{Pywal available?}
    Check2 -->|Yes| Pywal
    Check2 -->|No| Custom
    
    Pywal --> Result[Generate Colors]
    Wallust --> Result
    Custom --> Result
    
    style Start fill:#e1f5ff
    style Auto fill:#fff3e0
    style Result fill:#e8f5e9
```

