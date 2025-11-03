# Iterative Investigation Methodology

**Version:** 1.0
**Created:** 2025-10-17
**Purpose:** A systematic approach for AI-assisted codebase investigation with handover support

---

## Overview

This methodology enables comprehensive, iterative investigation of any codebase module or component. It's designed for AI tools to produce thorough, well-organized documentation while supporting session handovers and progress tracking.

### Key Principles

1. **Iterative & Incremental** - Break investigation into phases and tasks
2. **Handover-Friendly** - Any AI can pick up where another left off
3. **Progress Tracking** - Clear visibility into what's done and what's next
4. **Comprehensive** - Cover architecture, API, usage, integration, troubleshooting
5. **Structured Output** - Organized findings ready for final documentation

---

## Investigation Structure

### Helper Documents (Always Create These)

Create a helper documents directory (location specified in investigation config) with these files:

**Default location:** `helpers/` at project root
**Configurable:** Can be placed anywhere (e.g., `docs/investigations/`, `.investigation/`, etc.)

#### 1. `README.md` - Investigation System Guide
**Purpose:** Explains the investigation system to AI tools
**Content:**
- Overview of the helper documents
- How to use each document
- Workflow for continuing investigation
- Quick start guide

#### 2. `INTERACTIVE_PROMPT.md` - AI Handover Document
**Purpose:** Entry point for AI sessions
**Structure:**
```markdown
## STATIC SECTION (Never Modified)
- Investigation approach explanation
- How to use the helper documents
- Workflow instructions

## DYNAMIC SECTION (Updated Each Session)
- Current status and phase
- Current task
- Recent accomplishments
- Next steps
- Context for next session
```

#### 3. `REQUIREMENTS_CHECKLIST.md` - Task Tracking
**Purpose:** Track all investigation tasks
**Structure:**
- Organized into phases (typically 8-10 phases)
- Each phase has 5-6 specific tasks
- Status indicators: ❌ Not Started | 🔄 In Progress | ✅ Complete
- Progress percentage at bottom

#### 4. `INVESTIGATION_NOTES.md` - Detailed Findings
**Purpose:** Repository of all discoveries
**Structure:**
- Table of contents
- Sections for each investigation area
- Code examples
- Architecture diagrams (ASCII)
- Usage patterns
- Integration points
- Troubleshooting guide

#### 5. `SESSION_SUMMARY.md` - Session Accomplishments
**Purpose:** Summary of what was accomplished
**Content:**
- Tasks completed this session
- Key discoveries
- Files created/modified
- Next steps

---

## Investigation Phases (Template)

Customize these phases based on what you're investigating:

### Phase 1: Architecture & Structure Understanding (5 tasks)
- Map directory structure
- Identify all files and their purposes
- Understand module organization
- Identify public API surface
- Document entry points

### Phase 2: Core Abstractions Deep Dive (5 tasks)
- Document all abstract base classes
- Document all interfaces
- Document core concepts
- Map inheritance hierarchies
- Understand design contracts

### Phase 3: Type System & Data Models (6 tasks)
- Document all enums
- Document all dataclasses/models
- Document type relationships
- Document validation logic
- Document default values
- Create type diagrams

### Phase 4: Exception Hierarchy (6 tasks)
- Map exception hierarchy
- Document all exception classes
- Document error contexts
- Provide usage examples
- Document error handling patterns
- Best practices

### Phase 5: Implementation Details (6 tasks)
- Document all concrete implementations
- Document utility functions
- Document helper modules
- Code walkthroughs for key features
- Implementation patterns
- Internal APIs

### Phase 6: Key Features & Capabilities (5 tasks)
- Identify unique features
- Document how features work
- Provide implementation details
- Benefits and trade-offs
- Usage examples

### Phase 7: Integration & Usage Patterns (5 tasks)
- Common usage patterns
- Integration with other modules
- Typical workflows
- Best practices
- Anti-patterns to avoid

### Phase 8: Advanced Topics (5 tasks)
- Security considerations
- Performance considerations
- Extensibility points
- Future roadmap
- Migration guides

### Phase 9: Documentation Synthesis (5 tasks)
- Create architecture diagrams
- Document all relationships
- Create comprehensive examples
- Organize findings
- Prepare for final output

### Phase 10: Validation & Review (5 tasks)
- Verify all code paths documented
- Ensure all public APIs covered
- Cross-reference with existing docs
- Validate examples
- Final completeness check

**Total:** 50 tasks across 10 phases (customize as needed)

---

## Output Formats

Specify one of these output formats:

### Format 1: Single File with Sections
**Best for:** Smaller modules, cohesive documentation
**Structure:**
```markdown
# [Module Name] Documentation

## 1. Introduction
## 2. Architecture
## 3. API Reference
## 4. Usage Guide
## 5. Integration
## 6. Advanced Topics
## 7. Troubleshooting
## 8. Examples
```

### Format 2: Multiple Files
**Best for:** Large modules, separate concerns
**Structure:**
```
docs/
├── 01_introduction.md
├── 02_architecture.md
├── 03_api_reference.md
├── 04_usage_guide.md
├── 05_integration.md
├── 06_advanced_topics.md
├── 07_troubleshooting.md
└── 08_examples.md
```

### Format 3: Directory Structure
**Best for:** Complex modules, multiple subsystems
**Structure:**
```
docs/
├── README.md
├── architecture/
│   ├── overview.md
│   ├── design_patterns.md
│   └── diagrams.md
├── api/
│   ├── core.md
│   ├── managers.md
│   └── utilities.md
├── guides/
│   ├── getting_started.md
│   ├── usage_patterns.md
│   └── integration.md
└── reference/
    ├── troubleshooting.md
    └── examples.md
```

---

## Investigation Workflow

### Step 1: Setup
1. Create helper documents directory (at specified location)
2. Create all 5 helper documents
3. Define investigation phases and tasks
4. Set up output location

### Step 2: Investigate
For each phase:
1. Update INTERACTIVE_PROMPT.md with current task
2. Investigate the codebase
3. Document findings in INVESTIGATION_NOTES.md
4. Update REQUIREMENTS_CHECKLIST.md
5. Mark tasks as complete

### Step 3: Iterate
- Work through tasks systematically
- Update helper documents as you go
- Keep INTERACTIVE_PROMPT.md current for handovers
- Document discoveries immediately

### Step 4: Synthesize
- Review all findings in INVESTIGATION_NOTES.md
- Organize into final output format
- Create final documentation
- Validate completeness

---

## What to Document

### For Each Component (Class/Function/Module):
- **Purpose:** What it does
- **Signature:** Parameters, return types
- **Behavior:** How it works
- **Exceptions:** What errors it raises
- **Examples:** How to use it
- **Relationships:** Dependencies and dependents

### Architecture:
- Directory structure
- Module organization
- Design patterns used
- Component relationships
- Data flow

### Usage:
- Common patterns (10+)
- Complete workflows (5+)
- Code examples (50+)
- Best practices
- Anti-patterns

### Integration:
- How it connects to other modules
- Integration patterns
- Data exchange formats
- Dependencies

### Advanced:
- Security considerations
- Performance considerations
- Extensibility points
- Troubleshooting (common issues + solutions)

---

## Quality Metrics

A complete investigation should have:
- ✅ 100% of public APIs documented
- ✅ 50+ code examples
- ✅ 10+ usage patterns
- ✅ 5+ architecture diagrams
- ✅ 5+ complete workflows
- ✅ Troubleshooting guide with 5+ issues
- ✅ All design patterns identified
- ✅ All integration points documented
- ✅ Security and performance considerations
- ✅ All tasks in checklist complete

---

## Example Usage

**Prompt to AI:**
```
Use the investigation methodology in [HELPERS_DIR]/methodology/INVESTIGATION_METHODOLOGY.md to investigate:

Target: src/dotfiles/modules/[MODULE_NAME]
Output: docs/[MODULE_NAME]_documentation.md
Format: Single file with sections
Helpers Directory: [HELPERS_DIR]/investigations/[MODULE_NAME]/

Focus on:
- [SPECIFIC_AREA_1]
- [SPECIFIC_AREA_2]
- [SPECIFIC_AREA_3]

Create all helper documents in the specified helpers directory and produce comprehensive documentation.
```

**Note:** Replace `[HELPERS_DIR]` with your desired location (e.g., `helpers`, `docs/investigations`, `.investigation`, etc.)

---

## Customization Guide

### Adjust Phases
- Add/remove phases based on module complexity
- Typical range: 8-12 phases
- Each phase: 4-6 tasks

### Adjust Focus
- Emphasize certain areas (e.g., more on security)
- Skip irrelevant areas (e.g., no GUI for CLI tools)
- Add domain-specific phases

### Adjust Output
- Choose format based on module size
- Single file: < 5000 lines
- Multiple files: 5000-15000 lines
- Directory structure: > 15000 lines

### Adjust Helpers Location
- Default: `helpers/` at project root
- Alternative: `docs/investigations/`, `.investigation/`, `investigation/`, etc.
- Specify in investigation config
- AI will create directory structure at specified location

---

## Success Criteria

Investigation is complete when:
1. ✅ All phases finished (100% tasks complete)
2. ✅ All public APIs documented
3. ✅ Sufficient examples provided
4. ✅ Integration points clear
5. ✅ Troubleshooting guide exists
6. ✅ Final documentation synthesized
7. ✅ Validation checks passed

---

**End of Methodology Document**
