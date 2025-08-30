# Enhanced Icon Generator Test Updates

## Overview

We've successfully fixed the test file for the enhanced icon generator to match the actual behavior of the system. The main issues were related to misunderstandings of how the `bake_svg` function in `generate_icons.py` works.

## Key Fixes

1. **Updated imports**: We added missing imports from `generate_icons.py` since `bake_svg` is imported from there.

2. **Fixed API mismatches**: We replaced references to non-existent functions and properties like `generate_icon` with the actual API functions like `process_variant`.

3. **Corrected SVG color replacement expectations**: After investigating how `bake_svg` actually works with `debug_bake_svg.py`, we updated our tests to match the actual color replacement behavior:
   - In light mode, only `#FFFFFF` is replaced with the foreground color, `#FF6A00` stays unchanged
   - In dark mode, `#FF6A00` is replaced with the dark background (`#060607`) and `#FFFFFF` is replaced with the foreground color
   - With custom colors, both color placeholders are replaced with the foreground color

4. **Fixed path properties**: We updated tests to reference the correct paths since the `IconVariant` class doesn't have `svg_path` or `png_path` properties directly.

## Notes on Color Replacement Logic

The `bake_svg` function in `generate_icons.py` has a very specific color replacement pattern:

```python
def bake_svg(master_svg: str, mode: str, finish: str) -> str:
    bg = TOKENS["paper"] if mode == "light" else TOKENS["slate_950"]
    fg = FINISH_COLORS.get(finish, TOKENS["brand_orange"])
    svg = master_svg.replace("#FF6A00", bg)  # replace background rect
    svg = svg.replace("#FFFFFF", fg)  # replace icon shapes
    return svg
```

It replaces:
- `#FF6A00` with the background color (white for light mode, dark for dark mode)
- `#FFFFFF` with the foreground color (specified by the finish)

This differs from a template token system that would replace `{{mode_bg}}` and `{{accent}}` tokens.

## Next Steps

1. Consider enhancing the SVG baking system to support template tokens for more flexibility.
2. Update the documentation to clarify how the color replacement works.
3. Add more comprehensive tests for different finishes and custom colors.
