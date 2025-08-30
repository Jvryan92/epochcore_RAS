#!/bin/bash
# StrategyDECK Asset Clean and Rebuild Script
#
# This script completely cleans all generated icon assets and rebuilds them,
# verifying the integrity of the icon generation system.

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================================${NC}"
echo -e "${BLUE}     StrategyDECK Asset Clean and Rebuild Tool        ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# Project root is the directory containing this script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$ROOT_DIR/assets"
ICONS_DIR="$ASSETS_DIR/icons"
SCRIPTS_DIR="$ROOT_DIR/scripts"

# Check for python and dependencies
echo -e "\n${YELLOW}Checking Python environment...${NC}"
which python3 || { echo -e "${RED}Python 3 not found. Please install Python 3.${NC}"; exit 1; }
python3 -m pip --version >/dev/null 2>&1 || { echo -e "${RED}pip not found. Please install pip.${NC}"; exit 1; }

# Verify required scripts exist
echo -e "\n${YELLOW}Verifying scripts...${NC}"
GENERATOR_SCRIPT="$SCRIPTS_DIR/generate_icons.py"

if [ ! -f "$GENERATOR_SCRIPT" ]; then
    echo -e "${RED}Error: Icon generator script not found at $GENERATOR_SCRIPT${NC}"
    exit 1
fi
echo -e "${GREEN}Found generator script: $GENERATOR_SCRIPT${NC}"

# Check for CairoSVG
echo -e "\n${YELLOW}Checking for CairoSVG...${NC}"
if python3 -c "import cairosvg" 2>/dev/null; then
    echo -e "${GREEN}CairoSVG is installed.${NC}"
    CAIROSVG_INSTALLED=true
else
    echo -e "${YELLOW}CairoSVG is not installed. PNG export will be skipped.${NC}"
    echo -e "${YELLOW}To install CairoSVG: pip install cairosvg${NC}"
    CAIROSVG_INSTALLED=false
fi

# Clean all generated assets
echo -e "\n${YELLOW}Cleaning all generated assets...${NC}"
if [ -d "$ICONS_DIR" ]; then
    find "$ICONS_DIR" -type f \( -name "*.svg" -o -name "*.png" \) -delete
    echo -e "${GREEN}Removed all SVG and PNG files from $ICONS_DIR${NC}"
    
    # Remove empty directories
    find "$ICONS_DIR" -type d -empty -delete
    echo -e "${GREEN}Removed empty directories${NC}"
else
    echo -e "${YELLOW}No icons directory found. Creating $ICONS_DIR${NC}"
    mkdir -p "$ICONS_DIR"
fi

# Rebuild all assets
echo -e "\n${YELLOW}Rebuilding all assets...${NC}"
echo -e "${BLUE}Running: python3 $GENERATOR_SCRIPT${NC}"
python3 "$GENERATOR_SCRIPT"

# Verify generated assets
echo -e "\n${YELLOW}Verifying generated assets...${NC}"
SVG_COUNT=$(find "$ICONS_DIR" -name "*.svg" | wc -l)
PNG_COUNT=$(find "$ICONS_DIR" -name "*.png" | wc -l)

echo -e "${GREEN}Generated SVG files: $SVG_COUNT${NC}"
echo -e "${GREEN}Generated PNG files: $PNG_COUNT${NC}"

# Check for endless glyph system
GLYPH_SCRIPT="$SCRIPTS_DIR/endless_glyph_generator.py"
if [ -f "$GLYPH_SCRIPT" ]; then
    echo -e "\n${YELLOW}Found Endless Glyph System. Generating sample glyphs...${NC}"
    
    # Generate a sample of glyphs
    for theme in quantum cosmic circuit fractal neon organic digital; do
        echo -e "${BLUE}Generating $theme glyph...${NC}"
        python3 "$GLYPH_SCRIPT" --theme $theme --output "$ICONS_DIR/sample_$theme" --size 128 --animate
    done
    
    # Count generated glyph files
    GLYPH_SVG_COUNT=$(find "$ICONS_DIR" -name "sample_*.svg" | wc -l)
    GLYPH_PNG_COUNT=$(find "$ICONS_DIR" -name "sample_*.png" | wc -l)
    
    echo -e "${GREEN}Generated glyph SVG files: $GLYPH_SVG_COUNT${NC}"
    echo -e "${GREEN}Generated glyph PNG files: $GLYPH_PNG_COUNT${NC}"
fi

# Run diagnostic check if PNG conversion failed
if [ "$CAIROSVG_INSTALLED" = true ] && [ "$PNG_COUNT" -lt "$SVG_COUNT" ]; then
    echo -e "\n${YELLOW}Warning: Fewer PNG files than SVG files were generated.${NC}"
    echo -e "${YELLOW}Running PNG conversion diagnostic...${NC}"
    
    if [ -f "$ROOT_DIR/debug_png_conversion.py" ]; then
        python3 "$ROOT_DIR/debug_png_conversion.py"
    else
        echo -e "${RED}PNG conversion debug tool not found.${NC}"
        echo -e "${RED}Please run: python3 -m pip install cairosvg${NC}"
    fi
fi

echo -e "\n${BLUE}=======================================================${NC}"
echo -e "${GREEN}             Asset rebuild complete!                  ${NC}"
echo -e "${BLUE}=======================================================${NC}"

echo -e "\nSummary:"
echo -e "  SVG files: $SVG_COUNT"
echo -e "  PNG files: $PNG_COUNT"
if [ -f "$GLYPH_SCRIPT" ]; then
    echo -e "  Glyph SVG files: $GLYPH_SVG_COUNT"
    echo -e "  Glyph PNG files: $GLYPH_PNG_COUNT"
fi

# Provide useful commands
echo -e "\n${BLUE}Useful commands:${NC}"
echo -e "  ${YELLOW}View all assets:${NC} find $ICONS_DIR -type f | sort"
echo -e "  ${YELLOW}Check PNG conversion:${NC} python3 $ROOT_DIR/debug_png_conversion.py"
echo -e "  ${YELLOW}Run tests:${NC} pytest tests/ -v"

exit 0
