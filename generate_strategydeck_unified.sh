#!/usr/bin/env bash
# StrategyDECK Icon Generator Wrapper
# This script provides a convenient interface to the unified icon generator

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATOR_SCRIPT="${SCRIPT_DIR}/scripts/unified_icon_generator.py"
CSV_CONFIG="${SCRIPT_DIR}/strategy_icon_variant_matrix.csv"
JSON_CONFIG="${SCRIPT_DIR}/config/icon_config.json"
OUTPUT_DIR="${SCRIPT_DIR}/assets/icons"
REPORT_FILE="${SCRIPT_DIR}/reports/icon_generation_report.json"

# Default parameters
SOURCE="both"
PARALLEL=true
DEBUG=false
CLEAN=false
SKIP_INSTALL=false

# Display help information
show_help() {
    echo "StrategyDECK Icon Generator"
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -s, --source <csv|json|both>  Source configuration (default: both)"
    echo "  -c, --csv <file>              Custom CSV file path"
    echo "  -j, --config <file>           Custom JSON config file path"
    echo "  -o, --output <dir>            Custom output directory"
    echo "  -p, --parallel                Enable parallel processing (default)"
    echo "  -S, --sequential              Disable parallel processing"
    echo "  -d, --debug                   Enable debug logging"
    echo "  -C, --clean                   Clean output directory before generation"
    echo "  --skip-install                Skip dependency installation"
    echo "  -h, --help                    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                            Generate icons using default settings"
    echo "  $0 --source csv               Generate icons using only CSV configuration"
    echo "  $0 --source json              Generate icons using only JSON configuration"
    echo "  $0 --clean --debug            Clean output directory and enable debug logging"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -s|--source)
            SOURCE="$2"
            shift 2
            ;;
        -c|--csv)
            CSV_CONFIG="$2"
            shift 2
            ;;
        -j|--config)
            JSON_CONFIG="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -S|--sequential)
            PARALLEL=false
            shift
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        -C|--clean)
            CLEAN=true
            shift
            ;;
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate arguments
if [[ "$SOURCE" != "csv" && "$SOURCE" != "json" && "$SOURCE" != "both" ]]; then
    echo "Error: Invalid source type. Must be one of: csv, json, both"
    exit 1
fi

# Check if files exist
if [[ "$SOURCE" == "csv" || "$SOURCE" == "both" ]]; then
    if [[ ! -f "$CSV_CONFIG" ]]; then
        echo "Error: CSV file not found: $CSV_CONFIG"
        exit 1
    fi
fi

if [[ "$SOURCE" == "json" || "$SOURCE" == "both" ]]; then
    if [[ ! -f "$JSON_CONFIG" ]]; then
        echo "Error: JSON config file not found: $JSON_CONFIG"
        exit 1
    fi
fi

# Clean output directory if requested
if [[ "$CLEAN" == true ]]; then
    echo "Cleaning output directory: $OUTPUT_DIR"
    rm -rf "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

# Create reports directory if it doesn't exist
mkdir -p "$(dirname "$REPORT_FILE")"

# Install dependencies if not skipped
if [[ "$SKIP_INSTALL" != true ]]; then
    echo "Installing dependencies..."
    pip install -r "${SCRIPT_DIR}/requirements.txt"
fi

# Build command
CMD="python3 ${GENERATOR_SCRIPT} --source ${SOURCE}"

if [[ "$SOURCE" == "csv" || "$SOURCE" == "both" ]]; then
    CMD="${CMD} --csv ${CSV_CONFIG}"
fi

if [[ "$SOURCE" == "json" || "$SOURCE" == "both" ]]; then
    CMD="${CMD} --config ${JSON_CONFIG}"
fi

if [[ -n "$OUTPUT_DIR" ]]; then
    CMD="${CMD} --output ${OUTPUT_DIR}"
fi

if [[ "$PARALLEL" == false ]]; then
    CMD="${CMD} --sequential"
fi

if [[ "$DEBUG" == true ]]; then
    CMD="${CMD} --debug"
fi

# Execute the command
echo "Running command: $CMD"
eval "$CMD"

exit_code=$?

# Check if generator succeeded
if [[ $exit_code -eq 0 ]]; then
    echo "Icon generation completed successfully!"
    
    # Count generated files
    SVG_COUNT=$(find "$OUTPUT_DIR" -name "*.svg" | wc -l)
    PNG_COUNT=$(find "$OUTPUT_DIR" -name "*.png" | wc -l)
    WEBP_COUNT=$(find "$OUTPUT_DIR" -name "*.webp" | wc -l)
    
    echo "Generated $SVG_COUNT SVG files, $PNG_COUNT PNG files, and $WEBP_COUNT WebP files"
    
    # Create simple report
    REPORT="{
  \"timestamp\": \"$(date +%s)\",
  \"date\": \"$(date)\",
  \"source\": \"$SOURCE\",
  \"parallel\": $PARALLEL,
  \"clean\": $CLEAN,
  \"files\": {
    \"svg\": $SVG_COUNT,
    \"png\": $PNG_COUNT,
    \"webp\": $WEBP_COUNT
  },
  \"status\": \"success\"
}"
    
    echo "$REPORT" > "$REPORT_FILE"
    echo "Generation report saved to: $REPORT_FILE"
    
    exit 0
else
    echo "Icon generation failed with exit code $exit_code"
    
    # Create error report
    REPORT="{
  \"timestamp\": \"$(date +%s)\",
  \"date\": \"$(date)\",
  \"source\": \"$SOURCE\",
  \"parallel\": $PARALLEL,
  \"clean\": $CLEAN,
  \"status\": \"failed\",
  \"exit_code\": $exit_code
}"
    
    echo "$REPORT" > "$REPORT_FILE"
    echo "Error report saved to: $REPORT_FILE"
    
    exit $exit_code
fi
