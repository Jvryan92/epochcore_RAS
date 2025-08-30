#!/bin/bash
# Manual icon packaging script

set -e

DIST_DIR="dist"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PACKAGE_NAME="strategy_icons_${TIMESTAMP}"
ZIP_FILE="${DIST_DIR}/${PACKAGE_NAME}.zip"

# Create output directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Copy all SVG files to the temp directory with proper structure
echo "Copying SVG files..."
find assets/icons -name "*.svg" -exec cp --parents {} "$TEMP_DIR" \;

# Create metadata file
echo "Creating metadata.json..."
cat > "$TEMP_DIR/metadata.json" << EOL
{
  "name": "StrategyDECK Icons",
  "version": "1.0.0",
  "author": "StrategyDECK Team",
  "license": "Proprietary",
  "description": "StrategyDECK brand icons for use across platforms and applications",
  "created_at": "$(date -Iseconds)",
  "file_count": $(find assets/icons -name "*.svg" | wc -l)
}
EOL

# Create manifest file
echo "Creating manifest.json..."
MANIFEST_FILE="$TEMP_DIR/manifest.json"
echo "{" > "$MANIFEST_FILE"
echo "  \"icons\": [" >> "$MANIFEST_FILE"

# Add each icon to the manifest
find assets/icons -name "*.svg" | sort | while read -r file; do
    # Extract parts from the path
    parts=($(echo "$file" | tr '/' ' '))
    mode=${parts[2]}
    finish=${parts[3]}
    size=${parts[4]%px}
    context=${parts[5]}
    filename=$(basename "$file")
    
    echo "    {" >> "$MANIFEST_FILE"
    echo "      \"path\": \"$file\"," >> "$MANIFEST_FILE"
    echo "      \"mode\": \"$mode\"," >> "$MANIFEST_FILE"
    echo "      \"finish\": \"$finish\"," >> "$MANIFEST_FILE"
    echo "      \"size\": $size," >> "$MANIFEST_FILE"
    echo "      \"context\": \"$context\"," >> "$MANIFEST_FILE"
    echo "      \"format\": \"svg\"," >> "$MANIFEST_FILE"
    echo "      \"variant\": \"$mode/$finish/${size}px/$context\"" >> "$MANIFEST_FILE"
    echo "    }," >> "$MANIFEST_FILE"
done

# Remove the trailing comma from the last entry and close the JSON
sed -i '$ s/,$//' "$MANIFEST_FILE"
echo "  ]," >> "$MANIFEST_FILE"
echo "  \"variant_count\": $(find assets/icons -name "*.svg" -printf "%h\n" | sort | uniq | wc -l)," >> "$MANIFEST_FILE"
echo "  \"total_files\": $(find assets/icons -name "*.svg" | wc -l)" >> "$MANIFEST_FILE"
echo "}" >> "$MANIFEST_FILE"

# Create zip file
echo "Creating zip file: $ZIP_FILE..."
cd "$TEMP_DIR" && zip -r "$PWD/$ZIP_FILE" .

# Clean up temporary directory
echo "Cleaning up temporary directory..."
rm -rf "$TEMP_DIR"

echo "Package created successfully: $ZIP_FILE"
