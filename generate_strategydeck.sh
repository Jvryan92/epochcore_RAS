#!/bin/bash
# StrategyDECK Icon Generation Script
# This script generates StrategyDECK brand icons and packages them for distribution

set -e

# ANSI color codes for prettier output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}   StrategyDECK Icon Generator      ${NC}"
echo -e "${BLUE}=====================================${NC}"

# Check for Python and dependencies
echo -e "\n${YELLOW}Checking dependencies...${NC}"

PYTHON_PATH="/workspaces/epochcore_RAS/.venv/bin/python"

if [ ! -f "$PYTHON_PATH" ]; then
    echo -e "${RED}Error: Python virtual environment not found at $PYTHON_PATH${NC}"
    exit 1
fi

if ! $PYTHON_PATH -c "import cairosvg" &> /dev/null; then
    echo -e "${YELLOW}Warning: cairosvg is not installed. PNG export will be disabled.${NC}"
    echo -e "${YELLOW}Run 'pip install -r requirements.txt' to install all dependencies.${NC}"
fi

# Clean up existing icons if requested
if [ "$1" == "--clean" ] || [ "$1" == "-c" ]; then
    echo -e "\n${YELLOW}Cleaning up existing icons...${NC}"
    rm -rf assets/icons/*
    echo -e "${GREEN}✓ Cleaned up existing icons${NC}"
    shift
fi

# Generate icons
echo -e "\n${YELLOW}Generating icons...${NC}"
$PYTHON_PATH scripts/generate_icons.py "$@"
echo -e "${GREEN}✓ Icons generated successfully${NC}"

# Count generated files
SVG_COUNT=$(find assets/icons -name "*.svg" | wc -l)
PNG_COUNT=$(find assets/icons -name "*.png" | wc -l)
echo -e "${GREEN}✓ Generated ${SVG_COUNT} SVG files and ${PNG_COUNT} PNG files${NC}"

# Package icons if requested
if [ "$1" == "--package" ] || [ "$1" == "-p" ]; then
    echo -e "\n${YELLOW}Packaging icons...${NC}"
    
    # Create output directory if it doesn't exist
    mkdir -p dist
    
    # Package format (zip by default)
    FORMAT="zip"
    if [ "$2" == "--format" ] && [ -n "$3" ]; then
        FORMAT="$3"
    fi
    
    # Generate timestamp for package name
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    PACKAGE_NAME="strategy_icons_${TIMESTAMP}"
    
    # Run packager
    $PYTHON_PATH scripts/package_icons.py --format "$FORMAT" --package-all
    
    echo -e "${GREEN}✓ Icons packaged successfully: dist/${PACKAGE_NAME}.${FORMAT}${NC}"
fi

# Show help if requested
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo -e "\n${BLUE}Usage:${NC}"
    echo -e "  ${YELLOW}./generate_strategydeck.sh${NC} - Generate icons"
    echo -e "  ${YELLOW}./generate_strategydeck.sh --clean${NC} - Clean and regenerate icons"
    echo -e "  ${YELLOW}./generate_strategydeck.sh --package${NC} - Generate and package icons"
    echo -e "  ${YELLOW}./generate_strategydeck.sh --package --format zip|tar.gz|folder${NC} - Specify package format"
    echo -e "  ${YELLOW}./generate_strategydeck.sh --help${NC} - Show this help"
fi

echo -e "\n${BLUE}=====================================${NC}"
echo -e "${GREEN}Icon generation complete!${NC}"
echo -e "${BLUE}=====================================${NC}"
