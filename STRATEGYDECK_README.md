# StrategyDECK

StrategyDECK is a comprehensive system for managing game assets, strategy icons, and AI agents within the EpochCore RAS (Recursive Autonomous Software) framework.

## Icon Generation System

The StrategyDECK Icon Generation System allows you to generate and package SVG and PNG icons with different modes, finishes, sizes, and contexts.

### Key Components

- **generate_strategydeck.sh**: Main script for generating and packaging icons
- **scripts/generate_icons.py**: Core icon generation logic
- **scripts/package_icons.py**: Icon packaging system
- **scripts/svg_to_png.py**: SVG to PNG conversion utility
- **icon_packager_config.json**: Configuration for the icon packaging system

### Icon Structure

Icons are organized in a hierarchical structure:

```
assets/icons/{mode}/{finish}/{size}px/{context}/{filename}.{ext}
```

Where:
- **mode**: Visual mode (e.g., light, dark)
- **finish**: Surface finish (e.g., flat-orange, matte-carbon)
- **size**: Icon size in pixels (e.g., 16px, 32px, 48px)
- **context**: Usage context (e.g., web, print)

### Usage

Generate icons:
```bash
./generate_strategydeck.sh
```

Clean and regenerate icons:
```bash
./generate_strategydeck.sh --clean
```

Generate and package icons:
```bash
./generate_strategydeck.sh --package
```

Specify package format:
```bash
./generate_strategydeck.sh --package --format zip|tar.gz|folder
```

Show help:
```bash
./generate_strategydeck.sh --help
```

### Icon Packaging

The icon packaging system supports multiple output formats:
- **ZIP**: Default format, creates a compressed archive
- **TAR.GZ**: Creates a tar.gz compressed archive
- **Folder**: Creates a directory structure with the icons

Each package includes:
- Icon files organized by mode/finish/size/context
- metadata.json with package information
- manifest.json with detailed information about each icon

### Plugin System

The icon packaging system supports plugins to extend its functionality. Plugins are located in `scripts/icon_packager_plugins/`.

Built-in plugins:
- **manifest**: Generates a manifest.json file with detailed information about each icon

### Configuration

The icon packaging system is configured through `icon_packager_config.json`, which includes:
- Supported formats (svg, png)
- Variant patterns to include
- Plugins to load
- Output directory
- Metadata information

## Integration with EpochCore RAS

StrategyDECK integrates with the EpochCore RAS framework to provide asset management capabilities for AI agents.

### Agent Architecture

The agent architecture consists of multiple specialized channels:
- **Intelligence**: Core reasoning and decision-making
- **Resilience**: Error handling and recovery
- **Collaboration**: Multi-agent coordination
- **Evolution**: Self-improvement and adaptation
- **Quantum**: Advanced computation strategies
- **Cognitive**: Pattern recognition and learning
- **Temporal**: Time-based operations
- **Ethical**: Ethical decision-making

### Assets Integration

StrategyDECK assets are used throughout the EpochCore RAS system for:
- Visual representation of agents and their states
- UI elements for dashboards and monitoring
- Documentation and communication materials
- Game assets and interactive elements

## Development

To contribute to the StrategyDECK system, see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines and best practices.

### Setting Up the Development Environment

1. Clone the repository
2. Run `./dev-setup.sh` to set up the development environment
3. Install dependencies with `pip install -r requirements.txt`

### Testing

Run tests with:
```bash
pytest tests/
```

## License

See the [LICENSE](LICENSE) file for license rights and limitations.
