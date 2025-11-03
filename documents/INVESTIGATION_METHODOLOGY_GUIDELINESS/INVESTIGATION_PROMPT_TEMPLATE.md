# Investigation Prompt Template

**Purpose:** Copy this template, fill in the blanks, and give it to any AI tool
**Methodology:** See `INVESTIGATION_METHODOLOGY.md` for details

---

## Template (Copy Everything Below)

```
I need you to investigate a codebase module using the iterative investigation
methodology described in [HELPERS_DIR]/methodology/INVESTIGATION_METHODOLOGY.md.

═══════════════════════════════════════════════════════════════════════════
INVESTIGATION CONFIGURATION
═══════════════════════════════════════════════════════════════════════════

TARGET MODULE: [path/to/module/to/investigate]

OUTPUT LOCATION: [path/where/documentation/should/go]

OUTPUT FORMAT: [Choose one: single_file | multiple_files | directory_structure]

HELPERS DIRECTORY: [path/where/helper/documents/go]
  Examples:
  - helpers/investigations/[MODULE_NAME]/
  - docs/investigations/[MODULE_NAME]/
  - .investigation/[MODULE_NAME]/
  - investigation/
  Default: helpers/investigations/[MODULE_NAME]/

═══════════════════════════════════════════════════════════════════════════
OUTPUT STRUCTURE
═══════════════════════════════════════════════════════════════════════════

[Describe the structure you want. Examples below - delete what you don't need]

OPTION A - Single File:
Sections:
1. [Section Name]
2. [Section Name]
3. [Section Name]
...

OPTION B - Multiple Files:
Files:
- [filename1.md] ([what it contains])
- [filename2.md] ([what it contains])
- [filename3.md] ([what it contains])
...

OPTION C - Directory Structure:
Structure:
[output_dir]/
├── [subdir1]/
│   ├── [file1.md]
│   └── [file2.md]
├── [subdir2]/
│   ├── [file3.md]
│   └── [file4.md]
└── [file5.md]

═══════════════════════════════════════════════════════════════════════════
FOCUS AREAS
═══════════════════════════════════════════════════════════════════════════

Primary focus:
- [Focus area 1]
- [Focus area 2]
- [Focus area 3]

Secondary focus:
- [Focus area 4]
- [Focus area 5]

Skip/Minimize:
- [Area to skip or minimize]

═══════════════════════════════════════════════════════════════════════════
INVESTIGATION PHASES
═══════════════════════════════════════════════════════════════════════════

[Choose one option below - delete the others]

OPTION A - Standard (10 phases, 50 tasks):
Use the standard 10 phases from INVESTIGATION_METHODOLOGY.md

OPTION B - Simplified (6-8 phases, 30-40 tasks):
Phases:
1. [Phase name] ([X] tasks)
2. [Phase name] ([X] tasks)
3. [Phase name] ([X] tasks)
...

OPTION C - Extended (12-15 phases, 60-75 tasks):
Use standard 10 phases plus:
11. [Additional phase] ([X] tasks)
12. [Additional phase] ([X] tasks)
...

OPTION D - Custom:
Phases:
1. [Custom phase 1] ([X] tasks)
2. [Custom phase 2] ([X] tasks)
...

═══════════════════════════════════════════════════════════════════════════
QUALITY TARGETS
═══════════════════════════════════════════════════════════════════════════

INVESTIGATION_NOTES.md should have:
- [X]+ lines of content
- [X]+ code examples
- [X]+ usage patterns
- [X]+ architecture diagrams
- [X]+ complete workflows

Final documentation should include:
- [ ] [Requirement 1]
- [ ] [Requirement 2]
- [ ] [Requirement 3]

═══════════════════════════════════════════════════════════════════════════
SPECIAL REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════

[Add any special requirements, constraints, or notes]

Examples:
- Emphasize security considerations
- Include performance benchmarks
- Focus on integration with [other module]
- Must include migration guide from [old version]
- Target audience: [beginners | intermediate | advanced]

═══════════════════════════════════════════════════════════════════════════
METHODOLOGY INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════

Follow the investigation methodology exactly:

1. CREATE HELPER DOCUMENTS
   - Create the specified HELPERS DIRECTORY if it doesn't exist
   - Create all 5 helper documents in that directory:
     * README.md (investigation system guide)
     * INTERACTIVE_PROMPT.md (AI handover document)
     * REQUIREMENTS_CHECKLIST.md (task tracking)
     * INVESTIGATION_NOTES.md (detailed findings)
     * SESSION_SUMMARY.md (session accomplishments)

2. WORK THROUGH PHASES
   - Complete each phase systematically
   - Document findings immediately
   - Update helper documents continuously
   - Mark tasks complete as you go

3. MAINTAIN HANDOVER READINESS
   - Keep INTERACTIVE_PROMPT.md current
   - Update progress in REQUIREMENTS_CHECKLIST.md
   - Document everything in INVESTIGATION_NOTES.md
   - Any AI should be able to continue from any point

4. SYNTHESIZE FINAL DOCUMENTATION
   - Review all findings
   - Organize into specified output format
   - Create final documentation
   - Validate completeness

═══════════════════════════════════════════════════════════════════════════
COMPLETION CRITERIA
═══════════════════════════════════════════════════════════════════════════

Investigation is complete when:
- [ ] All phases finished (100% tasks complete)
- [ ] All helper documents created and updated
- [ ] INVESTIGATION_NOTES.md meets quality targets
- [ ] All public APIs documented
- [ ] Sufficient examples provided
- [ ] Integration points documented
- [ ] Troubleshooting guide exists
- [ ] Final documentation synthesized
- [ ] Validation checks passed

═══════════════════════════════════════════════════════════════════════════

Begin the investigation now.
```

---

## Quick Fill Examples

### Example 1: Quick Fill for Container Manager

```
TARGET MODULE: src/dotfiles/modules/container_manager
OUTPUT LOCATION: docs/container_manager.md
OUTPUT FORMAT: single_file
HELPERS DIRECTORY: helpers/investigations/container_manager/

OUTPUT STRUCTURE:
Sections:
1. Introduction
2. Architecture
3. API Reference
4. Usage Guide
5. Integration
6. Advanced Topics
7. Troubleshooting
8. Examples

FOCUS AREAS:
Primary focus:
- In-memory Dockerfile builds
- Runtime-agnostic design
- Manager interfaces

INVESTIGATION PHASES:
Standard (10 phases, 50 tasks)

QUALITY TARGETS:
- 3000+ lines of content
- 50+ code examples
- 10+ usage patterns
- 5+ architecture diagrams
```

### Example 2: Quick Fill for Template Renderer

```
TARGET MODULE: src/dotfiles/modules/template_renderer
OUTPUT LOCATION: docs/template_renderer/
OUTPUT FORMAT: multiple_files
HELPERS DIRECTORY: docs/investigations/template_renderer/

OUTPUT STRUCTURE:
Files:
- overview.md (introduction and architecture)
- api.md (all classes and methods)
- usage.md (patterns and examples)
- integration.md (with container_manager)
- troubleshooting.md (common issues)

FOCUS AREAS:
Primary focus:
- Jinja2 template handling
- Placeholder validation
- Integration with container_manager

INVESTIGATION PHASES:
Simplified (8 phases, 40 tasks)

QUALITY TARGETS:
- 2000+ lines of content
- 30+ code examples
- 8+ usage patterns
```

### Example 3: Quick Fill for CLI Module

```
TARGET MODULE: src/dotfiles/cli
OUTPUT LOCATION: docs/cli/
OUTPUT FORMAT: directory_structure
HELPERS DIRECTORY: .investigation/cli/

OUTPUT STRUCTURE:
docs/cli/
├── README.md
├── architecture/
│   ├── overview.md
│   └── commands.md
├── commands/
│   ├── install.md
│   ├── configure.md
│   └── update.md
└── guides/
    ├── getting_started.md
    └── extending.md

FOCUS AREAS:
Primary focus:
- Command structure
- Configuration system
- User workflows

INVESTIGATION PHASES:
Standard (10 phases, 50 tasks)

QUALITY TARGETS:
- 4000+ lines of content
- 60+ code examples
- 15+ usage patterns
```

---

## Tips for Filling the Template

1. **Be Specific:** The more specific you are, the better the results
2. **Prioritize:** Clearly indicate what's most important
3. **Set Realistic Targets:** Adjust quality targets based on module size
4. **Customize Phases:** Don't hesitate to modify phases for your needs
5. **Provide Context:** Mention how the module fits in the larger system

---

## That's It!

Just:
1. Copy the template
2. Fill in the blanks
3. Give it to any AI tool
4. Get comprehensive documentation

The AI will follow the methodology and produce consistent, high-quality results!
