# StrategyDECK Icon Generation Troubleshooting Guide

This guide provides solutions for common issues encountered with the StrategyDECK Icon Generation System.

## Table of Contents

1. [SVG Generation Issues](#svg-generation-issues)
2. [PNG Conversion Issues](#png-conversion-issues)
3. [CairoSVG Installation Problems](#cairosvg-installation-problems)
4. [Animation Issues](#animation-issues)
5. [Performance Optimization](#performance-optimization)
6. [Endless Glyph System](#endless-glyph-system)
7. [Diagnostic Tools](#diagnostic-tools)

## SVG Generation Issues

### Missing or Incomplete SVG Files

**Symptoms**:
- Some SVG files are missing or incomplete
- Icon variants are not generated for all combinations in the matrix

**Solutions**:

1. **Verify your matrix configuration**:
   ```bash
   cat strategy_icon_variant_matrix.csv
   ```
   Ensure it contains all the desired icon variants.

2. **Check master SVG files**:
   ```bash
   ls -l assets/masters/
   ```
   Verify both `strategy_icon_micro.svg` and `strategy_icon_standard.svg` exist.

3. **Clean and rebuild all assets**:
   ```bash
   ./clean_rebuild_assets.sh
   ```

### Malformed SVG Output

**Symptoms**:
- SVG files are generated but don't render correctly
- XML validation errors when opening SVGs

**Solutions**:

1. **Validate SVG structure**:
   Use the SVG debugger to inspect the SVG structure:
   ```bash
   python3 debug_bake_svg.py --gui
   ```

2. **Check for template token issues**:
   Ensure template tokens are properly defined and replaced.

3. **Verify color replacements**:
   Inspect the replacement process using the debug tool:
   ```bash
   python3 debug_bake_svg.py --svg assets/masters/strategy_icon_micro.svg --mode light --finish flat-orange
   ```

## PNG Conversion Issues

### Missing PNG Files

**Symptoms**:
- SVG files are generated but PNG files are missing
- Error messages about CairoSVG

**Solutions**:

1. **Check CairoSVG installation**:
   ```bash
   python3 -c "import cairosvg; print(cairosvg.__version__)"
   ```
   If this fails, CairoSVG is not properly installed.

2. **Install CairoSVG**:
   ```bash
   pip install cairosvg
   ```

3. **Run PNG conversion diagnostic**:
   ```bash
   python3 debug_png_conversion.py
   ```
   This will identify specific issues with PNG conversion.

### PNG Quality Issues

**Symptoms**:
- PNG files are generated but look blurry or distorted
- Color differences between SVG and PNG

**Solutions**:

1. **Check sizing parameters**:
   Ensure the size parameter matches the SVG viewBox.

2. **Inspect conversion process**:
   ```bash
   python3 debug_png_conversion.py --test-file assets/icons/light/flat-orange/16px/web/icon.svg
   ```

3. **Try alternative conversion methods**:
   If direct conversion fails, the BytesIO method might work.

## CairoSVG Installation Problems

### Linux Installation Issues

**Symptoms**:
- `pip install cairosvg` fails with compilation errors
- Missing dependencies errors

**Solutions**:

1. **Install system dependencies**:
   - Ubuntu/Debian:
     ```bash
     sudo apt-get update
     sudo apt-get install libcairo2-dev libfreetype6-dev libffi-dev libjpeg-dev libpng-dev
     ```
   - RHEL/CentOS:
     ```bash
     sudo yum install cairo-devel freetype-devel libffi-devel libjpeg-devel libpng-devel
     ```

2. **Install Python development headers**:
   ```bash
   sudo apt-get install python3-dev
   ```

3. **Try installing cairocffi instead**:
   ```bash
   pip install cairocffi
   pip install cairosvg
   ```

### macOS Installation Issues

**Symptoms**:
- `pip install cairosvg` fails on macOS
- "xcrun: error: invalid active developer path" errors

**Solutions**:

1. **Install XCode Command Line Tools**:
   ```bash
   xcode-select --install
   ```

2. **Install Cairo via Homebrew**:
   ```bash
   brew install cairo
   ```

3. **Install with PKG_CONFIG_PATH set**:
   ```bash
   export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:/usr/local/lib
   pip install cairosvg
   ```

### Windows Installation Issues

**Symptoms**:
- `pip install cairosvg` fails on Windows
- Missing MSVC compiler errors

**Solutions**:

1. **Install Visual C++ Build Tools**:
   Download and install from [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

2. **Use cairocffi instead**:
   ```bash
   pip install cairocffi
   pip install cairosvg
   ```

3. **Use a pre-compiled wheel**:
   ```bash
   pip install --only-binary=:all: cairosvg
   ```

## Animation Issues

### SVG Animations Not Working

**Symptoms**:
- Animations defined in SVG don't play in browsers
- Animations work in some browsers but not others

**Solutions**:

1. **Check animation compatibility**:
   SMIL animations (using `<animate>` tags) are not supported in all browsers.
   Consider using CSS animations instead.

2. **Verify animation syntax**:
   Ensure animation elements have proper attributes:
   ```xml
   <animate attributeName="opacity" from="0" to="1" dur="2s" repeatCount="indefinite" />
   ```

3. **Test in different browsers**:
   - Chrome and Firefox support SMIL animations
   - Safari has limited support
   - Internet Explorer does not support SMIL

### Endless Glyph Animation Issues

**Symptoms**:
- Glyph animations don't work
- Animation speed is incorrect

**Solutions**:

1. **Check animation type**:
   The Endless Glyph system supports both SMIL and CSS animations.
   Verify the correct type is used.

2. **Adjust animation parameters**:
   ```bash
   python3 scripts/endless_glyph_generator.py --theme quantum --animate --animation-type css --duration 3
   ```

3. **Test standalone SVG**:
   Save the SVG and open it directly in a browser to test animation.

## Performance Optimization

### Slow Generation Process

**Symptoms**:
- Icon generation takes too long
- High CPU usage during generation

**Solutions**:

1. **Reduce matrix complexity**:
   Consider generating only the icons you need.

2. **Optimize SVG files**:
   ```bash
   pip install svgoptimize
   svgoptimize assets/masters/strategy_icon_standard.svg
   ```

3. **Use multiprocessing**:
   If generating many icons, implement a multiprocessing approach.

### Large File Sizes

**Symptoms**:
- Generated SVG files are unusually large
- PNG files are larger than expected

**Solutions**:

1. **Optimize master SVGs**:
   Remove unnecessary elements, metadata, and comments.

2. **Use appropriate compression**:
   For PNG files, adjust compression level in CairoSVG:
   ```python
   cairosvg.svg2png(file_obj=open(svg_path, "rb"), write_to=png_path, dpi=96)
   ```

3. **Implement selective generation**:
   Only generate the sizes and formats you actually need.

## Endless Glyph System

### Missing Glyph Themes

**Symptoms**:
- Some glyph themes are not available
- Errors when specifying certain themes

**Solutions**:

1. **Check available themes**:
   ```bash
   python3 scripts/endless_glyph_generator.py --list-themes
   ```

2. **Update the glyph system**:
   Ensure you have the latest version of the Endless Glyph system.

3. **Add custom themes**:
   Follow the documentation to add your own custom themes.

### Glyph Generation Errors

**Symptoms**:
- Errors during glyph generation
- Incomplete or corrupted glyph SVGs

**Solutions**:

1. **Debug specific theme**:
   ```bash
   python3 scripts/endless_glyph_generator.py --theme quantum --debug
   ```

2. **Check for dependency issues**:
   Verify all required packages are installed.

3. **Review glyph parameters**:
   Ensure parameters are within valid ranges:
   ```bash
   python3 scripts/endless_glyph_generator.py --theme cosmic --complexity 3 --size 128
   ```

## Diagnostic Tools

### SVG Baking Debug Tool

The `debug_bake_svg.py` tool provides a visual interface for debugging the SVG color replacement process:

```bash
python3 debug_bake_svg.py --gui
```

Features:
- Load and preview SVG files
- Test different color combinations
- View color replacement steps
- Export debug reports

### PNG Conversion Debug Tool

The `debug_png_conversion.py` tool helps diagnose issues with SVG to PNG conversion:

```bash
python3 debug_png_conversion.py
```

Features:
- Check CairoSVG installation
- Test different conversion methods
- Identify system dependencies
- Generate comprehensive reports

To generate a full diagnostic report:

```bash
python3 debug_png_conversion.py --report
```

### Clean and Rebuild Tool

The `clean_rebuild_assets.sh` script completely cleans and regenerates all icon assets:

```bash
./clean_rebuild_assets.sh
```

Features:
- Removes all generated files
- Rebuilds all icons from scratch
- Verifies generated assets
- Runs diagnostics if issues are detected

## Additional Resources

- [CairoSVG Documentation](https://cairosvg.org/)
- [SVG Animation Guide](https://developer.mozilla.org/en-US/docs/Web/SVG/Element/animate)
- [Cairo Graphics Library](https://www.cairographics.org/)
- [SVG Optimization Tools](https://github.com/svg/svgo)

---

If you encounter issues not covered in this guide, please open an issue on the project repository with detailed information about the problem and the steps to reproduce it.
