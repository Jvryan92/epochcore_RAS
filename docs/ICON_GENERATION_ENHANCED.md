# StrategyDECK Icon Generation System

A comprehensive system for generating, customizing, and exporting StrategyDECK brand icons in various modes, finishes, sizes, and contexts.

## 🌟 Features

- **Multiple Icon Variants**: Generate icons in different modes (light/dark), finishes, sizes, and contexts
- **Batch Processing**: Generate multiple icon variants in parallel for faster processing
- **Custom Color Palettes**: Create and manage custom color palettes with an interactive editor
- **Framework Export**: Export icons as components for React, Vue, Angular, Svelte, and more
- **Format Support**: Generate SVG, PNG, WebP, and AVIF formats
- **Optimization**: Optimize SVG and PNG files for production use
- **Debug Tools**: Interactive GUI for debugging SVG color replacement process
- **CLI Interface**: Unified command-line interface for all icon operations

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Dependencies: `cairosvg`, `pillow`, `pytest`, `flake8`, `black`

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

Generate all icon variants:

```bash
python scripts/generate_icons.py
```

Or use the CLI for more options:

```bash
python scripts/strategydeck_cli.py generate --all
```

## 📋 Commands Reference

### Icon Generation

Generate standard icons:
```bash
make generate
```

Generate with enhanced options:
```bash
make generate-enhanced
```

Create a custom variant:
```bash
make generate-variant VARIANT="dark,neon-blue,32,web"
```

### Color Palettes

List available palettes:
```bash
make list-palettes
```

Create a new palette:
```bash
make create-palette NAME=my-brand COLOR="#FF5500"
```

Edit an existing palette:
```bash
make edit-palette NAME=my-brand
```

Preview a palette:
```bash
make preview-palette NAME=my-brand
```

### Framework Export

Export icons for React:
```bash
make export-react OPTIMIZE=1
```

Export for all frameworks:
```bash
make export-all
```

### System Tools

Show system information:
```bash
make info
```

Check icon statistics:
```bash
make stats
```

Validate system:
```bash
make validate
```

## 📂 Project Structure

```
StrategyDECK/
├── assets/
│   ├── masters/            # Master SVG files
│   └── icons/              # Generated variants
├── scripts/
│   ├── generate_icons.py           # Basic generator
│   ├── enhanced_icon_generator.py  # Enhanced generator
│   ├── palette_manager.py          # Color palette manager
│   ├── icon_framework_exporter.py  # Framework exporter
│   └── strategydeck_cli.py         # Unified CLI
├── config/                 # Custom palettes and configurations
├── tests/                  # Unit tests
│   └── test_generate_icons.py
├── dist/                   # Framework exports
├── debug_bake_svg.py       # Debug tool
├── icons.mk                # Makefile for common operations
├── strategy_icon_variant_matrix.csv  # Icon variant configuration
└── requirements.txt        # Python dependencies
```

## 🎨 Icon Variant Matrix

The `strategy_icon_variant_matrix.csv` file defines which icon variants will be generated. Each row represents a variant with the following columns:

- **Mode**: `light` or `dark`
- **Finish**: The finish style (e.g., `flat-orange`, `matte-carbon`, etc.)
- **Size (px)**: Icon size in pixels (e.g., `16`, `32`, `48`)
- **Context**: Usage context (e.g., `web`, `print`, `game`)
- **Filename**: Optional custom filename

## 🎯 Advanced Features

### Custom Palettes

Create custom color palettes for your brand:

```bash
python scripts/palette_manager.py --create my-brand --base-color "#FF5500"
```

### Framework Integration

Export icons for your framework of choice:

```bash
python scripts/icon_framework_exporter.py --framework react --output ./my-react-icons
```

### Debugging

Launch the interactive debugger to visualize color replacements:

```bash
python debug_bake_svg.py --gui
```

## 🔧 Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

Format code with Black:
```bash
black scripts/ tests/
```

Check linting:
```bash
flake8 scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Full Validation

Run the complete validation sequence:
```bash
make validate
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
