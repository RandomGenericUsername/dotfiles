# Investigation Methodology

**Version:** 1.0
**Created:** 2025-10-17
**Purpose:** Reusable methodology for AI-assisted codebase investigation

---

## 📚 What's This?

This directory contains a **complete, reusable methodology** for investigating any codebase module with AI assistance. Use these documents to instruct any AI tool (ChatGPT, Claude, etc.) to produce comprehensive, well-organized documentation.

---

## 📖 Documents

### 1. **INVESTIGATION_METHODOLOGY.md** ⭐ MAIN DOCUMENT
**The complete methodology** (300 lines)

**Contains:**
- Investigation principles and approach
- Helper document structure (5 documents)
- 10-phase investigation template (customizable)
- Output format options (single file, multiple files, directory structure)
- Quality metrics and success criteria
- Customization guide
- What to document (components, architecture, usage, integration)

**Read this:** To understand the full methodology

---

### 2. **INVESTIGATION_QUICK_START.md** 🚀 QUICK REFERENCE
**Quick reference with examples** (250 lines)

**Contains:**
- TL;DR copy-paste template
- Real-world examples:
  - Single file output
  - Multiple files output
  - Directory structure output
- Customization patterns:
  - Security-focused investigation
  - Performance-focused investigation
  - Minimal/quick investigation
- Handover instructions
- Tips for best results

**Read this:** To get started quickly with examples

---

### 3. **INVESTIGATION_PROMPT_TEMPLATE.md** 📋 COPY-PASTE TEMPLATE
**Fill-in-the-blanks template** (200 lines)

**Contains:**
- Complete prompt template with all configuration options
- Quick fill examples for common scenarios
- Tips for filling the template

**Use this:** To create a prompt for any AI tool

---

## 🚀 Quick Start

### Step 1: Choose Your Approach

**Option A - Use the Template (Easiest):**
1. Open `INVESTIGATION_PROMPT_TEMPLATE.md`
2. Copy the template
3. Fill in the blanks
4. Give to AI tool

**Option B - Use an Example:**
1. Open `INVESTIGATION_QUICK_START.md`
2. Find similar example
3. Customize it
4. Give to AI tool

**Option C - Read Full Methodology:**
1. Open `INVESTIGATION_METHODOLOGY.md`
2. Understand the approach
3. Create custom prompt
4. Give to AI tool

---

### Step 2: Example Prompt

Here's what you'd say to an AI tool:

```
Use the investigation methodology in helpers/methodology/INVESTIGATION_METHODOLOGY.md
to investigate:

TARGET: src/dotfiles/modules/[MODULE_NAME]
OUTPUT: docs/[MODULE_NAME].md
FORMAT: Single file with sections
HELPERS DIRECTORY: helpers/investigations/[MODULE_NAME]/

SECTIONS:
1. Introduction
2. Architecture
3. API Reference
4. Usage Guide
5. Integration
6. Examples

FOCUS:
- [Key area 1]
- [Key area 2]
- [Key area 3]

Follow the methodology - create helper documents in the specified directory
and produce documentation.
```

**Helpers Directory Options:**
- `helpers/investigations/[MODULE_NAME]/` (default)
- `docs/investigations/[MODULE_NAME]/`
- `.investigation/[MODULE_NAME]/`
- Any location you prefer

---

### Step 3: AI Does the Work

The AI will:
1. ✅ Create the specified helpers directory
2. ✅ Create all 5 helper documents
3. ✅ Work through investigation phases systematically
4. ✅ Document everything in INVESTIGATION_NOTES.md
5. ✅ Track progress in REQUIREMENTS_CHECKLIST.md
6. ✅ Keep INTERACTIVE_PROMPT.md updated for handovers
7. ✅ Synthesize final documentation

---

## 🎯 Key Features

### 1. Iterative & Incremental
- Break investigation into 8-12 phases
- Each phase has 4-6 specific tasks
- Clear progress tracking

### 2. Handover-Friendly
- Any AI can pick up where another left off
- INTERACTIVE_PROMPT.md provides context
- Clear current task and next steps

### 3. Comprehensive
- Covers architecture, API, usage, integration
- 50+ code examples
- 10+ usage patterns
- Architecture diagrams
- Troubleshooting guide

### 4. Flexible Output
- Single file with sections
- Multiple files
- Directory structure
- Customizable to your needs

### 5. Quality Metrics
- 100% API coverage
- Sufficient examples
- Complete workflows
- Validation checks

---

## 📁 Investigation Structure

When you use this methodology, the AI creates:

```
helpers/investigations/[MODULE_NAME]/
├── README.md                      # Investigation overview
├── INTERACTIVE_PROMPT.md          # AI handover document
├── REQUIREMENTS_CHECKLIST.md      # Task tracking (50 tasks)
├── INVESTIGATION_NOTES.md         # Detailed findings (2000+ lines)
└── SESSION_SUMMARY.md             # Session accomplishments
```

Plus final documentation at your specified output location.

---

## 🔄 Investigation Workflow

1. **Setup** - AI creates helper documents
2. **Investigate** - AI works through phases
3. **Document** - AI records findings
4. **Track** - AI updates progress
5. **Handover** - AI updates context for next session
6. **Synthesize** - AI creates final documentation

---

## 📊 Quality Targets

A complete investigation typically has:
- ✅ 2000-4000 lines in INVESTIGATION_NOTES.md
- ✅ 50+ code examples
- ✅ 10+ usage patterns
- ✅ 5+ architecture diagrams
- ✅ 5+ complete workflows
- ✅ Troubleshooting guide with 5+ issues
- ✅ 100% public API coverage

---

## 🌟 Example Investigations

See `helpers/investigations/` for examples:
- **container_manager** - Complete investigation (3,900+ lines, 100% complete)

---

## 💡 Tips

1. **Be Specific** - Clearly define what you want documented
2. **Prioritize** - Indicate what's most important
3. **Customize Phases** - Adjust for module complexity
4. **Set Realistic Targets** - Match quality targets to module size
5. **Provide Context** - Explain how module fits in larger system

---

## 📖 Reference

- **Full Methodology:** `INVESTIGATION_METHODOLOGY.md`
- **Quick Examples:** `INVESTIGATION_QUICK_START.md`
- **Copy-Paste Template:** `INVESTIGATION_PROMPT_TEMPLATE.md`

---

## ❓ Questions?

If something is unclear:
1. Read `INVESTIGATION_METHODOLOGY.md` for full details
2. Check `INVESTIGATION_QUICK_START.md` for examples
3. Look at `helpers/investigations/container_manager/` for a complete example

---

**This methodology is reusable for ANY codebase investigation!** 🎉
