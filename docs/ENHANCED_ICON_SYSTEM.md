# StrategyDECK Enhanced Icon Generation System

This directory contains an enhanced version of the StrategyDECK icon generation system, with additional features and tools for managing and customizing icons.

## Overview

The StrategyDECK icon system allows you to generate SVG and PNG icons with different modes, finishes, sizes, and contexts. The enhanced version adds features like:

- Class-based approach to icon variants
- Parallel processing for faster generation
- Improved color palette management
- Framework-specific exports
- CLI interface for all tools

## Components

### Enhanced Icon Generator (`enhanced_icon_generator.py`)

The core enhanced generator that provides:

- `IconVariant` class for structured variant management
- Parallel processing for batch generation
- Custom color palette support
- Better error handling and reporting

```bash
# Generate icons from CSV matrix
python enhanced_icon_generator.py --from-csv

# Generate icons with custom palette
python enhanced_icon_generator.py --from-csv --palette neon

# Generate specific variants
python enhanced_icon_generator.py --create-variant "dark,neon-blue,32,web"
```

### Palette Manager (`palette_manager.py`)

A tool for creating and managing color palettes:

- Generate harmonious color schemes
- Preview palettes in terminal or browser
- Export palettes to various formats (CSS, SCSS, JSON)
- Apply palettes to icons

```bash
# List available palettes
python palette_manager.py --list

# Create a new palette
python palette_manager.py --create my-palette --base-color "#3366FF"

# Edit an existing palette
python palette_manager.py --edit neon

# Preview a palette
python palette_manager.py --preview metallic

# Export a palette to CSS
python palette_manager.py --export pastel --format css
```

### Framework Exporter (`icon_framework_exporter.py`)

A tool for exporting icons to various web frameworks:

- React components
- Vue components
- Angular components
- Svelte components
- Web Components
- Vanilla JavaScript

```bash
# Export to React
python icon_framework_exporter.py --framework react --output ./my-react-icons

# Export to Vue
python icon_framework_exporter.py --framework vue --output ./my-vue-icons

# Export with specific criteria
python icon_framework_exporter.py --framework svelte --output ./my-svelte-icons --sizes 16 24 --modes light
```

### StrategyDECK CLI (`strategydeck_cli.py`)

A unified CLI for all icon tools:

- Generate icons
- Customize and manage palettes
- Export to frameworks
- Get system information

```bash
# Generate all icons
python strategydeck_cli.py generate --all

# Generate with enhanced features
python strategydeck_cli.py generate --enhanced --parallel --optimize

# Manage palettes
python strategydeck_cli.py customize palette --list
python strategydeck_cli.py customize palette --create my-palette --base-color "#FF3366"

# Export to frameworks
python strategydeck_cli.py export --framework react --output ./my-react-icons

# Get system info
python strategydeck_cli.py info --dependencies
python strategydeck_cli.py info --stats
```

### Icon Generation Demo (`icon_generation_demo.py`)

A demonstration script that showcases the capabilities of the enhanced icon system:

- Generates example icons with different features
- Shows how to use the various components together
- Provides a good starting point for custom scripts

```bash
# Run the demo
python icon_generation_demo.py

# Run with custom output directory
python icon_generation_demo.py --output-dir ./my-demo-icons

# Skip specific parts
python icon_generation_demo.py --skip-csv --skip-batch
```

## Getting Started

1. Ensure you have the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create your SVG master files in `assets/masters/`

3. Define your icon variants in `strategy_icon_variant_matrix.csv`

4. Generate icons:
   ```bash
   python strategydeck_cli.py generate --all
   ```

5. Explore the generated icons in `assets/icons/`

## Testing

Run the tests to verify the system is working correctly:

```bash
python -m unittest discover tests
```

Or run specific test files:

```bash
python tests/test_enhanced_icon_generator.py
```

## Contributing

See the [CONTRIBUTING.md](../CONTRIBUTING.md) file for guidelines on contributing to the StrategyDECK icon system.

## License

This project is licensed under the terms specified in the [LICENSE](../LICENSE) file.
