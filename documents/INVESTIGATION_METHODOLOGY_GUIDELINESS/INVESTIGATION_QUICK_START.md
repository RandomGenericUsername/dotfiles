# Investigation Methodology - Quick Start Guide

**For:** Instructing AI tools to investigate codebases
**Methodology:** See `INVESTIGATION_METHODOLOGY.md` for full details

---

## TL;DR - Copy & Paste Template

Use this template to instruct any AI tool:

```
I need you to investigate a codebase module using the iterative investigation
methodology described in [HELPERS_DIR]/methodology/INVESTIGATION_METHODOLOGY.md.

TARGET MODULE: [path/to/module]
OUTPUT LOCATION: [path/to/output]
OUTPUT FORMAT: [single_file | multiple_files | directory_structure]
HELPERS DIRECTORY: [path/where/helpers/go]  (e.g., helpers/investigations/[MODULE_NAME]/)

OUTPUT STRUCTURE:
[Describe the sections/files you want]

FOCUS AREAS:
- [Area 1]
- [Area 2]
- [Area 3]

Follow the methodology exactly:
1. Create all helper documents in the specified HELPERS DIRECTORY
2. Work through all investigation phases
3. Document everything in INVESTIGATION_NOTES.md
4. Track progress in REQUIREMENTS_CHECKLIST.md
5. Keep INTERACTIVE_PROMPT.md updated for handovers
6. Synthesize final documentation at the end

This is an iterative process - update helper documents as you go.
```

---

## Real Examples

### Example 1: Single File Output

```
Use helpers/methodology/INVESTIGATION_METHODOLOGY.md to investigate:

TARGET: src/dotfiles/modules/template_renderer
OUTPUT: docs/template_renderer.md
FORMAT: Single file with sections
HELPERS DIRECTORY: helpers/investigations/template_renderer/

SECTIONS:
1. Introduction & Overview
2. Architecture & Design
3. API Reference
4. Usage Patterns
5. Integration with Container Manager
6. Security Considerations
7. Troubleshooting
8. Examples

FOCUS:
- Jinja2 template handling
- Placeholder validation
- Integration points
- Error handling

Create helper documents and produce comprehensive documentation.
```

### Example 2: Multiple Files Output

```
Use helpers/methodology/INVESTIGATION_METHODOLOGY.md to investigate:

TARGET: src/dotfiles/modules/colorscheme_generator
OUTPUT: docs/colorscheme_generator/
FORMAT: Multiple files
HELPERS DIRECTORY: docs/investigations/colorscheme_generator/

FILES:
- architecture.md (design patterns, structure)
- api_reference.md (all classes and methods)
- usage_guide.md (patterns and workflows)
- integration.md (with container_manager and template_renderer)
- examples.md (complete examples)
- troubleshooting.md (common issues)

FOCUS:
- Pywal integration
- Color extraction algorithms
- Template generation
- Container usage

Create helper documents and produce all output files.
```

### Example 3: Directory Structure Output

```
Use helpers/methodology/INVESTIGATION_METHODOLOGY.md to investigate:

TARGET: src/dotfiles/cli
OUTPUT: docs/cli/
FORMAT: Directory structure
HELPERS DIRECTORY: .investigation/cli/

STRUCTURE:
docs/cli/
├── README.md (overview)
├── architecture/
│   ├── command_structure.md
│   ├── config_system.md
│   └── plugin_system.md
├── commands/
│   ├── install.md
│   ├── configure.md
│   └── update.md
├── guides/
│   ├── getting_started.md
│   ├── configuration.md
│   └── extending.md
└── reference/
    ├── api.md
    └── troubleshooting.md

FOCUS:
- CLI command structure
- Configuration management
- Plugin architecture
- User workflows

Create helper documents and produce all documentation files.
```

---

## Customization Examples

### Focus on Security

```
Use helpers/methodology/INVESTIGATION_METHODOLOGY.md to investigate:

TARGET: src/dotfiles/modules/secrets_manager
OUTPUT: docs/secrets_manager.md
FORMAT: Single file
HELPERS DIRECTORY: helpers/investigations/secrets_manager/

EMPHASIS:
- Security considerations (detailed)
- Encryption methods
- Key management
- Threat model
- Best practices

ADDITIONAL PHASES:
- Phase 11: Security Audit (6 tasks)
- Phase 12: Compliance & Standards (4 tasks)

Standard phases + security-focused additions.
```

### Focus on Performance

```
Use helpers/INVESTIGATION_METHODOLOGY.md to investigate:

TARGET: src/dotfiles/modules/file_processor
OUTPUT: docs/file_processor.md
FORMAT: Single file

EMPHASIS:
- Performance characteristics
- Optimization strategies
- Benchmarking approaches
- Resource usage
- Scalability

ADDITIONAL SECTIONS:
- Performance benchmarks
- Optimization guide
- Resource limits
- Caching strategies
```

### Minimal Investigation (Quick Overview)

```
Use helpers/INVESTIGATION_METHODOLOGY.md to investigate:

TARGET: src/dotfiles/utils/helpers.py
OUTPUT: docs/helpers_reference.md
FORMAT: Single file

SIMPLIFIED PHASES (6 phases, 30 tasks):
1. Structure & Organization (5 tasks)
2. Function Reference (5 tasks)
3. Usage Patterns (5 tasks)
4. Examples (5 tasks)
5. Integration (5 tasks)
6. Validation (5 tasks)

This is a smaller module - use simplified phase structure.
```

---

## Handover Example

If investigation is interrupted, the next AI can continue:

```
Continue the investigation started in helpers/.

Read helpers/INTERACTIVE_PROMPT.md for current status.
Check helpers/REQUIREMENTS_CHECKLIST.md for progress.
Review helpers/INVESTIGATION_NOTES.md for findings so far.

Pick up from the current task and continue following the methodology.
```

---

## Tips for Best Results

### 1. Be Specific About Output
- Clearly define sections/files wanted
- Specify level of detail
- Mention any special requirements

### 2. Highlight Focus Areas
- What's most important?
- What can be skipped?
- Any domain-specific concerns?

### 3. Customize Phases
- Add phases for special topics
- Remove irrelevant phases
- Adjust task counts

### 4. Set Expectations
- Mention if it's a large/small module
- Indicate complexity level
- Note any time constraints

### 5. Provide Context
- How module fits in larger system
- Known issues or concerns
- Existing documentation to reference

---

## Common Patterns

### Pattern 1: Full Investigation
- All 10 phases
- 50 tasks
- Comprehensive output
- Use for: Core modules, complex systems

### Pattern 2: Quick Reference
- 6-8 phases
- 30-40 tasks
- Focused output
- Use for: Utility modules, helpers

### Pattern 3: Deep Dive
- 12-15 phases
- 60-75 tasks
- Extensive output
- Use for: Critical systems, security-sensitive

### Pattern 4: Update Existing
- Focus on changes
- 4-6 phases
- Incremental output
- Use for: Updating old documentation

---

## Validation Checklist

Before considering investigation complete, verify:

- [ ] All helper documents created
- [ ] All phases completed (100% tasks)
- [ ] INVESTIGATION_NOTES.md has 2000+ lines
- [ ] 50+ code examples provided
- [ ] 10+ usage patterns documented
- [ ] Architecture diagrams included
- [ ] Troubleshooting guide exists
- [ ] Integration points documented
- [ ] Final documentation synthesized
- [ ] All public APIs covered

---

## Example Prompt (Complete)

Here's a complete, ready-to-use prompt:

```
I need you to investigate the container_manager module using the methodology
in helpers/INVESTIGATION_METHODOLOGY.md.

TARGET: src/dotfiles/modules/container_manager
OUTPUT: docs/container_manager_documentation.md
FORMAT: Single file with sections

OUTPUT STRUCTURE:
1. Introduction (purpose, features, when to use)
2. Architecture (structure, patterns, design)
3. API Reference (all classes, methods, types)
4. Usage Guide (patterns, workflows, best practices)
5. Integration (with other modules, examples)
6. Advanced Topics (security, performance, extensibility)
7. Troubleshooting (common issues, solutions, debugging)
8. Examples (complete workflows, real-world usage)

FOCUS AREAS:
- In-memory Dockerfile builds
- Runtime-agnostic design
- Integration with template_renderer
- Error handling and exceptions
- Usage patterns for all managers

PHASES: Use all 10 standard phases (50 tasks)

QUALITY TARGETS:
- 3000+ lines in INVESTIGATION_NOTES.md
- 50+ code examples
- 10+ usage patterns
- 5+ architecture diagrams
- Complete troubleshooting guide

Follow the methodology:
1. Create helpers/ directory with all 5 documents
2. Work through phases systematically
3. Update helper documents continuously
4. Document everything in INVESTIGATION_NOTES.md
5. Synthesize final documentation at end

This is iterative - keep INTERACTIVE_PROMPT.md updated for handovers.
```

---

## That's It!

You now have:
1. **INVESTIGATION_METHODOLOGY.md** - The complete methodology
2. **INVESTIGATION_QUICK_START.md** - This quick reference

Just copy a template from this guide, customize it, and hand it to any AI tool!

---

**Pro Tip:** Keep both documents in your `helpers/` directory as reference for future investigations.
