
╔═════════════════════════════════════════════════════╗
║  ███████╗████████╗██████╗  █████╗ ████████╗███████╗ ║
║  ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██╔════╝ ║
║  ███████╗   ██║   ██████╔╝███████║   ██║   █████╗   ║
║  ╚════██║   ██║   ██╔══██╗██╔══██║   ██║   ██╔══╝   ║
║  ███████║   ██║   ██║  ██║██║  ██║   ██║   ███████╗ ║
║  ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ║
║                                                     ║
║  ██████╗ ███████╗ ██████╗██╗  ██╗                   ║
║  ██╔══██╗██╔════╝██╔════╝██║ ██╔╝                   ║
║  ██║  ██║█████╗  ██║     █████╔╝                    ║
║  ██║  ██║██╔══╝  ██║     ██╔═██╗                    ║
║  ██████╔╝███████╗╚██████╗██║  ██╗                   ║
║  ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝                   ║
╚═════════════════════════════════════════════════════╝


# StrategyDECK Icon Generation System Interconnection

## System Status
- Generated Icons: [icon_count] SVG and PNG files
- Configured Variants: Multiple variants available
- Current Integration: Ready for use

## System Integration Points

The StrategyDECK Icon Generation System provides multiple integration points:

### 1. Icon Generation API

```python
from scripts.generate_icons import generate_all_icons, generate_specific_variant

# Generate all icon variants
generate_all_icons(force_regenerate=True)  # Set to False to skip existing files

# Generate a specific variant
generate_specific_variant(
    mode="light",          # light or dark
    finish="flat-orange",  # flat-orange, matte-carbon, etc.
    size=16,               # 16, 32, 48 px
    context="web"          # web or print
)
```

### 2. Custom Variant Registration

```python
from scripts.generate_icons import register_new_variant

# Register a new icon variant
register_new_variant(
    mode="light",
    finish="holographic",
    size=64,
    context="web",
    custom_colors={
        "background": "#000000",
        "foreground": "#00FFFF"
    }
)
```

### 3. Icon Packaging

```python
from scripts.package_icons import create_icon_package

# Create a distributable package of icons
create_icon_package(
    output_format="zip",       # zip, tar.gz, or folder
    include_formats=["svg", "png"],
    variants=["light/flat-orange/16px/web", "dark/copper-foil/32px/web"],
    output_path="dist/icons"
)
```

## Integration with EpochCore Agents

### Strategic Cognitive Agent Integration

The StrategyDECK icons can be used as visual representations for agents:

```python
from strategy_cognitive import StrategicCognitiveAgent
from scripts.generate_icons import get_icon_path

# Initialize a cognitive agent with an icon
agent = StrategicCognitiveAgent(
    name="Primary Decision Agent",
    icon_path=get_icon_path(
        mode="light",
        finish="flat-orange",
        size=32,
        context="web",
        format="png"
    )
)
```

### Multi-Strategy Agent Visualization

For visualizing multiple strategy agents in a dashboard:

```python
from strategy_collaboration import StrategyCollaborationManager
from scripts.enhanced_icon_generator import generate_agent_icon_set

# Generate a coordinated set of icons for multiple agents
icon_paths = generate_agent_icon_set(
    agent_count=5,
    base_mode="dark",
    finish_variation=True,  # Use different finishes for each agent
    output_dir="assets/agent_icons"
)

# Initialize collaboration manager with the icons
collaboration = StrategyCollaborationManager()
collaboration.register_agents_with_icons(icon_paths)
```

## Command Line Usage

You can also generate icons from the command line:

```bash
# Generate all icon variants
python scripts/generate_icons.py

# Generate specific variants
python scripts/generate_icons.py --mode light --finish flat-orange --size 16

# Package icons for distribution
python scripts/package_icons.py --output dist/icons.zip --format zip
```

## Validation Workflow

Always run this validation sequence when modifying the icon generation system:

```bash
# Verify dependencies are installed
pip install -r requirements.txt

# Generate all icons
python scripts/generate_icons.py

# Run unit tests
pytest tests/test_generate_icons.py -v

# Check code style
flake8 scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics
black --check scripts/
```

## Documentation

For more detailed information, refer to:
- StrategyDECK Icon System: `.github/copilot-instructions.md`
- Color System Reference: `docs/brand/color_system.md`
- Agent Integration Guide: `docs/integration/agent_icons.md`

## Contributing

When contributing enhancements to the StrategyDECK icon system:
1. Add new variant configurations to `strategy_icon_variant_matrix.csv`
2. Update unit tests in `tests/test_generate_icons.py`
3. Run the full validation workflow before submitting

================================================================================
# StrategyDECK Integration for Cognitive Agents


## Cognitive Agent Integration

The StrategyDECK icon system provides visual representations for cognitive strategies
and decision-making processes. Cognitive agents should use these icons to:

1. Represent different reasoning models and cognitive frameworks
2. Visualize decision trees and inference processes
3. Indicate confidence levels and cognitive states
4. Denote different types of logical operations

### Recommended Icon Variants

For cognitive agents, the following icon variants are recommended:
- Light mode with blue gradient finish for analytical processes
- Dark mode with purple accent for intuitive processes
- Matte finish for general reasoning
- Metallic finish for high-confidence conclusions

### Integration Example for Cognitive Agents

```python
from strategy_cognitive import StrategyCognitiveAgent
from scripts.generate_icons import get_icon_set_for_agent

# Initialize the agent with appropriate icons
agent = StrategyCognitiveAgent(
    name="Cognitive Processing Agent",
    icon_set=get_icon_set_for_agent(
        agent_type="cognitive",
        size_range=[16, 32, 64],
        include_states=["active", "processing", "complete", "error"]
    )
)

# Use the icons in the agent's visualization methods
agent.visualize_process_state(
    process_id="task-12345",
    icon_size=32
)
```
