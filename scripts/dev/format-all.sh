#!/bin/bash
# Script to format and lint all standardized projects

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
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
echo -e "${BLUE}Formatting and Linting All Projects${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0
FAILED_PROJECTS=()

for project in "${PROJECTS[@]}"; do
    if [ -d "$project" ] && [ -f "$project/Makefile" ]; then
        PROJECT_NAME=$(basename "$project")
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}Processing: $PROJECT_NAME${NC}"
        echo -e "${YELLOW}========================================${NC}"
        
        cd "$project"
        
        # Format
        echo -e "${BLUE}Formatting...${NC}"
        if make format 2>&1; then
            echo -e "${GREEN}✅ Formatting complete${NC}"
        else
            echo -e "${RED}❌ Formatting failed${NC}"
            FAIL_COUNT=$((FAIL_COUNT + 1))
            FAILED_PROJECTS+=("$PROJECT_NAME (format)")
            cd - > /dev/null
            echo ""
            continue
        fi
        
        # Lint
        echo -e "${BLUE}Linting...${NC}"
        if make lint 2>&1; then
            echo -e "${GREEN}✅ Linting complete${NC}"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo -e "${YELLOW}⚠️  Linting found issues (may need manual fixes)${NC}"
            FAIL_COUNT=$((FAIL_COUNT + 1))
            FAILED_PROJECTS+=("$PROJECT_NAME (lint)")
        fi
        
        cd - > /dev/null
        echo ""
    else
        echo -e "${RED}⚠️  Project not found or no Makefile: $project${NC}"
        echo ""
    fi
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Successful: $SUCCESS_COUNT${NC}"
echo -e "${RED}❌ Failed/Issues: $FAIL_COUNT${NC}"

if [ ${#FAILED_PROJECTS[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Projects with issues:${NC}"
    for failed in "${FAILED_PROJECTS[@]}"; do
        echo -e "  - $failed"
    done
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Next Steps:${NC}"
echo -e "${BLUE}========================================${NC}"
echo "1. Review any linting errors above"
echo "2. Fix manual issues (unused variables, type annotations, etc.)"
echo "3. Run 'make pre-commit-install' in each project"
echo "4. Run 'make test' to verify everything works"
echo ""

