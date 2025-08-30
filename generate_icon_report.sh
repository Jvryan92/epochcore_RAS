#!/bin/bash
# StrategyDECK Icon Report Generator
#
# This script generates a comprehensive report on the icon generation system
# and visualizes it in an HTML format.

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================================${NC}"
echo -e "${BLUE}     StrategyDECK Icon Report Generator              ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# Project root is the directory containing this script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="$ROOT_DIR/reports"
HTML_DIR="$REPORTS_DIR/html"

# Create reports directory if it doesn't exist
mkdir -p "$REPORTS_DIR"
mkdir -p "$HTML_DIR"

# Generate timestamp for report files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
JSON_REPORT="$REPORTS_DIR/icon_report_${TIMESTAMP}.json"
HTML_REPORT="$HTML_DIR/icon_report_${TIMESTAMP}.html"

# Parse command line arguments
VERBOSE=""
QUALITY=""
OPEN_BROWSER=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose)
      VERBOSE="--verbose"
      shift
      ;;
    --quality)
      QUALITY="--quality"
      shift
      ;;
    --open)
      OPEN_BROWSER="--open"
      shift
      ;;
    *)
      echo -e "${RED}Unknown argument: $1${NC}"
      echo "Usage: $0 [--verbose] [--quality] [--open]"
      exit 1
      ;;
  esac
done

# Run the icon report generator
echo -e "\n${YELLOW}Generating icon report...${NC}"
python "$ROOT_DIR/icon_report.py" --output "$JSON_REPORT" $VERBOSE $QUALITY

# Check if report was generated
if [ ! -f "$JSON_REPORT" ]; then
    echo -e "${RED}Error: Failed to generate JSON report${NC}"
    exit 1
fi

echo -e "${GREEN}JSON report generated: $JSON_REPORT${NC}"

# Generate HTML visualization
echo -e "\n${YELLOW}Generating HTML visualization...${NC}"
python "$ROOT_DIR/icon_report_visualize.py" "$JSON_REPORT" --output "$HTML_REPORT" $OPEN_BROWSER

# Check if HTML was generated
if [ ! -f "$HTML_REPORT" ]; then
    echo -e "${RED}Error: Failed to generate HTML report${NC}"
    exit 1
fi

echo -e "${GREEN}HTML report generated: $HTML_REPORT${NC}"

# Print summary and next steps
echo -e "\n${BLUE}=======================================================${NC}"
echo -e "${GREEN}     Report Generation Complete!                     ${NC}"
echo -e "${BLUE}=======================================================${NC}"

echo -e "\nReports:"
echo -e "  JSON: $JSON_REPORT"
echo -e "  HTML: $HTML_REPORT"

echo -e "\n${BLUE}Next Steps:${NC}"
echo -e "  ${YELLOW}View HTML report:${NC} $BROWSER \"$HTML_REPORT\""
echo -e "  ${YELLOW}Analyze JSON report:${NC} cat \"$JSON_REPORT\" | jq ."
echo -e "  ${YELLOW}Run diagnostics:${NC} python debug_png_conversion.py --report"

exit 0
