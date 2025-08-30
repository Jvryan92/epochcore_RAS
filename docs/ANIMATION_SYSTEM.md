# StrategyDECK Animation System

The StrategyDECK Animation System is a comprehensive framework for adding sophisticated animations to SVG icons and glyphs. It enables dynamic effects like rotation, pulsing, morphing, path animations, and more for web applications and interactive interfaces.

## Overview

The animation system consists of three integrated modules:

1. **Core Animation Engine** - Basic transformations and effects for any SVG
2. **Path Animation System** - Advanced path-specific animations and morphing
3. **Glyph Animation Bridge** - Specialized animations for procedurally generated glyphs

Together, these modules provide a complete solution for creating animated icons with consistent branding across different contexts.

## Features

### Core Animation Features

- **Transformation Effects**: Rotation, scaling, and translation animations
- **Opacity Effects**: Fade in/out and pulsing transparency
- **Color Effects**: Dynamic color transitions and theme changes
- **Interactive Controls**: Pause/resume and reset capabilities

### Path Animation Features

- **Path Drawing**: Animated stroke effects that simulate drawing
- **Path Morphing**: Smooth transitions between different path shapes
- **Motion Along Path**: Move elements along predefined paths
- **Stroke Effects**: Dash patterns, width variations, and flowing strokes

### Glyph Animation Features

- **Theme-Specific Animations**: Effects tailored to each glyph theme
- **Animation Sequences**: Multiple coordinated animations in sequence
- **Synchronized Effects**: Multi-element coordinated animations
- **Thematic Behaviors**: Animations that reinforce theme characteristics

## Installation

The StrategyDECK Animation System is included with the main StrategyDECK package:

```bash
# Clone the repository
git clone https://github.com/yourusername/strategydeck.git

# Install dependencies
cd strategydeck
pip install -r requirements.txt
```

## Usage

### Basic Animation

To add basic animations to an SVG icon:

```bash
python animate_icons.py --svg path/to/icon.svg --animation pulse
```

Options:
- `--animation`: Type of animation (pulse, rotate, bounce, fade, morph, color-shift)
- `--target`: Elements to animate (e.g., all, foreground, background, #elementId)
- `--duration`: Animation duration (e.g., 2s, 500ms)
- `--demo`: Create an HTML demo page
- `--open`: Open the result in a browser

### Path Animation

For advanced path-based animations:

```bash
python scripts/path_animation_system.py --svg path/to/icon.svg --animation draw
```

Path animation types:
- `draw`: Simulate drawing the path
- `flow`: Continuous flowing stroke
- `reveal`: Appear/disappear effect
- `pulse-path`: Pulsing stroke width
- `morph-geometric`: Morph between geometric shapes
- `morph-organic`: Morph between organic shapes
- `follow-path`: Move elements along a path
- `orbit`: Circular motion
- `zigzag`: Zig-zag movement
- `wave`: Wave-like transformations

### Glyph Animation

To apply animations to procedurally generated glyphs:

```bash
python scripts/glyph_animation_bridge.py --theme cosmic --animation rotate
```

Options:
- `--theme`: Glyph theme (biome, urban, mystic, cosmic, etc.)
- `--animation`: Animation type to apply
- `--sequence`: Animation sequence to apply
- `--showcase`: Generate a complete showcase of all themes

### Unified Animation System

The integrated animation system provides a unified interface:

```bash
python scripts/animation_system_integration.py --svg path/to/icon.svg --animation draw
```

Additional features:
- `--list`: List all available animations
- `--analyze`: Analyze SVG and recommend animations
- `--preview`: Create an interactive preview UI
- `--demo`: Create a comprehensive animation showcase

## Animation Types

### Basic Animations

| Animation | Description | Example Use Case |
|-----------|-------------|------------------|
| pulse | Scaling in/out with opacity changes | Emphasize important elements |
| rotate | Circular rotation | Loading indicators, settings icons |
| bounce | Vertical bouncing motion | Interactive buttons, notifications |
| fade | Opacity transitions | Subtle background elements |
| morph | Simple path transformations | State transitions, abstract icons |
| color-shift | Color transitions | Theme changes, status indicators |

### Path Animations

| Animation | Description | Example Use Case |
|-----------|-------------|------------------|
| draw | Simulated drawing effect | Onboarding, tutorials, diagrams |
| flow | Continuous stroke movement | Data flow, network connections |
| reveal | Progressive appearance | Step-by-step instructions |
| pulse-path | Stroke width pulsing | Attention to specific paths |
| morph-geometric | Morphing between geometric shapes | Abstract visualizations |
| morph-organic | Morphing between organic shapes | Natural elements, biomorphic UI |
| follow-path | Element movement along path | Guided tours, path animations |
| orbit | Circular orbit motion | Planetary icons, circular indicators |
| zigzag | Zig-zag movement | Energy, electricity, dynamic elements |
| wave | Wave-like transformations | Fluid interfaces, sound visualization |

### Glyph Sequences

| Sequence | Description | Theme |
|----------|-------------|-------|
| cosmic-pulsar | Pulsing combined with rotation | cosmic |
| mystic-ritual | Fade with color transitions | mystic |
| primal-energy | Pulse with color shifting | primal |
| shadow-stealth | Subtle fade with morphing | shadow |
| urban-techno | Bounce with color transitions | urban |
| raid-alert | Rapid pulse with rotation | raid |
| renaissance-flow | Rotation with path morphing | renaissance |
| biome-growth | Slow pulse with color transitions | biome |
| underworld-portal | Path morphing with rotation | underworld |

## Integration with Web Projects

### Embedding Animated SVGs

Animated SVGs can be embedded directly in HTML:

```html
<img src="path/to/animated_icon.svg" width="64" height="64" alt="Animated Icon">
```

For more control, inline the SVG code:

```html
<div class="icon-container">
  <!-- SVG code here -->
</div>
```

### JavaScript Interaction

You can interact with animations using JavaScript:

```javascript
// Pause/resume animations
const animatedElements = document.querySelectorAll('[class*="-animation"]');
animatedElements.forEach(el => {
  el.style.animationPlayState = 'paused'; // or 'running'
});

// Reset animations
animatedElements.forEach(el => {
  const classes = el.getAttribute('class').split(' ');
  const animationClass = classes.find(c => c.includes('-animation'));
  
  if (animationClass) {
    el.classList.remove(animationClass);
    setTimeout(() => {
      el.classList.add(animationClass);
    }, 10);
  }
});
```

## Creating Custom Animations

### Custom Basic Animations

Add new animations to `ANIMATION_PRESETS` in `animate_icons.py`:

```python
"custom-animation": {
    "type": "custom",
    "keyframes": [
        {"time": "0%", "custom-property": "value1"},
        {"time": "50%", "custom-property": "value2"},
        {"time": "100%", "custom-property": "value3"}
    ],
    "duration": "3s",
    "iteration": "infinite",
    "timing": "ease-in-out"
}
```

### Custom Path Animations

Add new path animations to `PATH_ANIMATION_PRESETS` in `path_animation_system.py`:

```python
"custom-path-effect": {
    "type": "custom-path",
    "keyframes": [
        # Custom keyframes
    ],
    "duration": "4s",
    "iteration": "infinite",
    "timing": "ease-in-out"
}
```

### Custom Glyph Sequences

Add new animation sequences to `ANIMATION_SEQUENCES` in `glyph_animation_bridge.py`:

```python
"theme-name": [
    {"type": "animation1", "duration": "2s", "target": "foreground"},
    {"type": "animation2", "duration": "3s", "target": "background"}
]
```

## Animation Development Tools

### Interactive Preview UI

The animation system includes an interactive UI for previewing animations:

```bash
python scripts/animation_system_integration.py --svg path/to/icons/ --preview --open
```

This tool allows you to:
- Select different SVG files
- Try various animation types
- Adjust duration and timing
- View recommended animations based on SVG analysis
- See real-time previews

### Path Animation Editor

For detailed path animation editing:

```bash
python scripts/path_animation_system.py --svg path/to/icon.svg --editor --open
```

This specialized editor provides:
- Path-specific animation controls
- Interactive visualization
- Code generation for reuse
- Direct SVG editing capabilities

### Batch Processing

Process multiple files with:

```bash
python scripts/animation_system_integration.py --svg path/to/icons/ --animation pulse --demo
```

## Performance Considerations

- Animations use CSS and SMIL for maximum compatibility
- Path animations can be CPU-intensive on complex SVGs
- For optimal performance in production:
  - Limit animations to essential elements
  - Use simpler animations for mobile devices
  - Consider providing static fallbacks

## Troubleshooting

### Common Issues

1. **Animations not visible:**
   - Ensure the browser supports SVG animations
   - Check that the SVG is properly referenced/embedded
   - Verify CSS is not being blocked

2. **Path animations not working:**
   - Confirm paths have proper attributes (d, stroke, etc.)
   - Check for malformed path data
   - Ensure no CSS conflicts with animation properties

3. **Jerky animations:**
   - Simplify path data for smoother performance
   - Adjust animation duration to be longer
   - Reduce the number of simultaneous animations

### Browser Compatibility

- Modern browsers support CSS animations and SMIL
- For older browsers, the system can generate simplified animations
- Internet Explorer has limited support for SVG animations

## Examples

### Basic Pulse Animation

```bash
python animate_icons.py --svg assets/icons/light/flat-orange/32px/web/strategy_icon-light-flat-orange-32px.svg --animation pulse
```

### Path Drawing Animation

```bash
python scripts/path_animation_system.py --svg assets/icons/dark/matte-carbon/48px/web/strategy_icon-dark-matte-carbon-48px.svg --animation draw
```

### Cosmic Theme Sequence

```bash
python scripts/glyph_animation_bridge.py --theme cosmic --sequence cosmic-pulsar
```

### Complete Animation Showcase

```bash
python scripts/animation_system_integration.py --svg assets/icons/ --demo --open
```

## Contributing

Contributions to the StrategyDECK Animation System are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b new-animation-feature`
3. Commit your changes: `git commit -m 'Add new animation type'`
4. Push to the branch: `git push origin new-animation-feature`
5. Submit a pull request

## License

See the [LICENSE](LICENSE) file for license rights and limitations.
