#!/bin/bash
# Script to fix all linting issues across projects

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Projects to process
PROJECTS=(
    "src/dotfiles-installer/cli"
    "src/common/modules/colorscheme-generator"
    "src/common/modules/container-manager"
    "src/common/modules/filesystem-path-builder"
    "src/common/modules/logging"
    "src/common/modules/package-manager"
    "src/common/modules/pipeline"
    "src/common/modules/template-renderer"
    "src/common/modules/wallpaper-processor"
    "src/common/tools/colorscheme-orchestrator"
    "src/common/tools/template-renderer"
    "src/common/tools/wallpaper-orchestrator"
)

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Fixing All Linting Issues${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

for project in "${PROJECTS[@]}"; do
    if [ -d "$project" ]; then
        PROJECT_NAME=$(basename "$project")
        echo -e "${YELLOW}Processing: $PROJECT_NAME${NC}"
        
        cd "$project"
        
        # Run black
        echo -e "${BLUE}  → Running black...${NC}"
        uv run black . 2>&1 | grep -E "(reformatted|unchanged|files)" || true
        
        # Run isort
        echo -e "${BLUE}  → Running isort...${NC}"
        uv run isort . 2>&1 | grep -E "(Fixing|Skipped)" || true
        
        # Run ruff with unsafe fixes (for SIM105, etc.)
        echo -e "${BLUE}  → Running ruff with unsafe fixes...${NC}"
        uv run ruff check --fix --unsafe-fixes . 2>&1 | tail -5 || true
        
        # Run ruff again with regular fixes
        echo -e "${BLUE}  → Running ruff final pass...${NC}"
        uv run ruff check --fix . 2>&1 | tail -5 || true
        
        cd - > /dev/null
        echo ""
    fi
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Auto-fixes Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Now checking for remaining issues..."
echo ""

# Run final lint check
for project in "${PROJECTS[@]}"; do
    if [ -d "$project" ] && [ -f "$project/Makefile" ]; then
        PROJECT_NAME=$(basename "$project")
        echo -e "${YELLOW}Checking: $PROJECT_NAME${NC}"
        
        cd "$project"
        if uv run ruff check . 2>&1 | grep -q "All checks passed"; then
            echo -e "${GREEN}  ✅ No issues${NC}"
        else
            echo -e "${YELLOW}  ⚠️  Still has issues (may need manual fixes)${NC}"
            uv run ruff check . 2>&1 | grep -E "Found [0-9]+ error" || true
        fi
        cd - > /dev/null
        echo ""
    fi
done

