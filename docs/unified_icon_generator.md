# StrategyDECK Unified Icon Generation System

The StrategyDECK Unified Icon Generation System is a comprehensive framework for generating branded icons in multiple variants, formats, and styles. This system is designed to be flexible, maintainable, and highly efficient.

## System Overview

The Unified Icon Generator provides the following capabilities:

- Generate SVG and PNG icons in multiple variants
- Support for WebP format for modern web applications
- Parallel processing for improved performance
- Multiple PNG conversion methods with automatic fallback
- Configurable color systems via JSON configuration
- Detailed metrics and reporting
- Comprehensive error handling and logging

## Getting Started

### Prerequisites

- Python 3.8+ 
- Required Python packages: cairosvg, Pillow (for additional formats)
- Optional system tools: Inkscape, rsvg-convert, ImageMagick (as fallbacks)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install system dependencies (optional but recommended):
   ```bash
   # For Debian/Ubuntu
   apt-get update && apt-get install -y libcairo2-dev python3-dev inkscape librsvg2-bin imagemagick
   
   # For Red Hat/CentOS
   yum install -y cairo-devel python3-devel inkscape librsvg2-tools ImageMagick
   
   # For macOS
   brew install cairo python3 inkscape librsvg imagemagick
   ```

### Basic Usage

The easiest way to use the Unified Icon Generator is through the wrapper script:

```bash
./generate_strategydeck_unified.sh
```

This will generate all icon variants defined in both the CSV matrix and JSON configuration.

For more control, you can specify various options:

```bash
# Generate icons from CSV configuration only
./generate_strategydeck_unified.sh --source csv

# Generate icons from JSON configuration only
./generate_strategydeck_unified.sh --source json

# Clean output directory and enable debug logging
./generate_strategydeck_unified.sh --clean --debug

# Use sequential processing (disable parallel)
./generate_strategydeck_unified.sh --sequential
```

### Advanced Usage

For more control, you can directly use the Python script:

```bash
# Generate all variants from both CSV and JSON
python scripts/unified_icon_generator.py

# Generate from CSV only
python scripts/unified_icon_generator.py --source csv

# Generate from JSON only
python scripts/unified_icon_generator.py --source json

# Use custom config files
python scripts/unified_icon_generator.py --csv custom_matrix.csv --config custom_config.json
```

## Configuration

### CSV Configuration (Legacy)

The CSV configuration is maintained for backward compatibility. It defines icon variants with the following columns:

- Mode: light, dark
- Finish: flat-orange, matte-carbon, etc.
- Size (px): 16, 32, 48, etc.
- Context: web, print, etc.
- Filename: Optional custom filename

### JSON Configuration (Recommended)

The JSON configuration provides more flexibility and control. The main sections are:

1. **color_tokens**: Defines named color values
2. **modes**: Defines background colors for different modes
3. **finish_colors**: Maps finishes to color tokens
4. **contexts**: Defines output formats and options for different contexts
5. **size_thresholds**: Defines size thresholds for different master SVGs
6. **processing_options**: Configuration for parallel processing and optimization
7. **custom_variants**: Additional variant definitions

Example:

```json
{
  "color_tokens": {
    "orange": "#FF6A00",
    "white": "#FFFFFF",
    "slate": "#060607"
  },
  "modes": {
    "light": {
      "background": "white"
    },
    "dark": {
      "background": "slate"
    }
  },
  "finish_colors": {
    "flat-orange": "orange"
  },
  "contexts": {
    "web": {
      "formats": ["svg", "png", "webp"],
      "optimize": true
    }
  }
}
```

## Performance Benchmarking

The system includes a benchmarking tool to measure performance:

```bash
python scripts/benchmark_icon_generators.py
```

This will compare the performance of the original and unified generators, reporting on:
- Execution time
- Memory usage
- File generation counts
- Success rates

## Troubleshooting

### PNG Generation Issues

If PNG generation fails, the system will automatically try multiple methods:

1. CairoSVG (primary method)
2. Inkscape CLI (fallback)
3. rsvg-convert (fallback)
4. ImageMagick (fallback)

If all methods fail, check your system dependencies:

```bash
# Install system dependencies for Cairo
apt-get install -y libcairo2-dev python3-dev

# Verify CairoSVG installation
pip install cairosvg
python -c "import cairosvg; print(cairosvg.__version__)"
```

### Debug Logging

Enable debug logging for more detailed information:

```bash
./generate_strategydeck_unified.sh --debug
```

## System Architecture

The Unified Icon Generator is built on several key components:

1. **ConfigManager**: Manages configuration from both CSV and JSON sources
2. **IconVariant**: Represents a single icon variant to be generated
3. **IconGenerator**: Handles the actual generation of icons
4. **GenerationMetrics**: Collects and reports on generation metrics

## Contributors

- The StrategyDECK Team
- Epoch Core RAS Project

## License

See LICENSE file for details.
