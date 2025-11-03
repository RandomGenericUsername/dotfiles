#!/bin/bash
# Script to install pre-commit hooks in all standardized projects

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
echo -e "${BLUE}Installing Pre-commit Hooks${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0

for project in "${PROJECTS[@]}"; do
    if [ -d "$project" ] && [ -f "$project/.pre-commit-config.yaml" ]; then
        PROJECT_NAME=$(basename "$project")
        echo -e "${BLUE}Installing pre-commit in: $PROJECT_NAME${NC}"
        
        cd "$project"
        
        if make pre-commit-install 2>&1; then
            echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo -e "${RED}❌ Failed to install pre-commit hooks${NC}"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
        
        cd - > /dev/null
        echo ""
    else
        echo -e "${YELLOW}⚠️  Skipping $project (no .pre-commit-config.yaml)${NC}"
        echo ""
    fi
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Successful: $SUCCESS_COUNT${NC}"
echo -e "${RED}❌ Failed: $FAIL_COUNT${NC}"
echo ""
echo -e "${GREEN}Pre-commit hooks are now active!${NC}"
echo "They will run automatically on 'git commit'"
echo ""

