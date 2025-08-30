#!/usr/bin/env python3
"""
StrategyDECK Icon Framework Exporter

This script exports StrategyDECK icons in formats optimized for different web frameworks
and bundlers. It creates ready-to-use icon libraries for React, Vue, Angular, and other
popular frameworks.

Usage:
  python icon_framework_exporter.py --framework react --output ./my-react-icons
  python icon_framework_exporter.py --framework vue --output ./my-vue-icons
  python icon_framework_exporter.py --framework svelte --optimize
"""

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import from generate_icons
try:
    from generate_icons import CSV_PATH, OUT, ROOT
except ImportError:
    # Default values if import fails
    ROOT = Path(__file__).resolve().parent.parent
    OUT = ROOT / "assets" / "icons"
    CSV_PATH = ROOT / "strategy_icon_variant_matrix.csv"

# Supported frameworks
FRAMEWORKS = ["react", "vue", "angular", "svelte", "vanilla-js", "web-components"]


@dataclass
class FrameworkConfig:
    """Configuration for a specific framework"""
    name: str
    file_extension: str
    component_template: str
    index_template: str
    package_json: Dict
    extra_files: Dict[str, str] = None

    def __post_init__(self):
        if self.extra_files is None:
            self.extra_files = {}


# Template for React components
REACT_COMPONENT_TEMPLATE = '''import * as React from "react";

interface {ComponentName}Props extends React.SVGProps<SVGSVGElement> {{
  size?: number | string;
  title?: string;
}}

export const {ComponentName} = ({{
  size = 24,
  title = "{componentTitle}",
  ...props
}}: {ComponentName}Props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 {viewBoxSize} {viewBoxSize}"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    {svgContent}
    {title && <title>{componentTitle}</title>}
  </svg>
);
'''

REACT_INDEX_TEMPLATE = '''export * from "./{fileName}";
'''

REACT_ROOT_INDEX_TEMPLATE = '''// StrategyDECK Icons for React
{exports}
'''

REACT_PACKAGE_JSON = {
    "name": "strategydeck-icons-react",
    "version": "1.0.0",
    "description": "StrategyDECK Icons as React Components",
    "main": "dist/index.js",
    "module": "dist/index.esm.js",
    "types": "dist/index.d.ts",
    "license": "MIT",
    "peerDependencies": {
        "react": "^17.0.0 || ^18.0.0"
    },
    "scripts": {
        "build": "tsup src/index.tsx --dts --format esm,cjs --external react"
    }
}

# Template for Vue components
VUE_COMPONENT_TEMPLATE = '''<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 {viewBoxSize} {viewBoxSize}"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    v-bind="$attrs"
  >
    {svgContent}
    <title v-if="title">{{ title }}</title>
  </svg>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({{
  name: '{ComponentName}',
  props: {{
    size: {{
      type: [Number, String],
      default: 24
    }},
    title: {{
      type: String,
      default: '{componentTitle}'
    }}
  }}
}})
</script>
'''

VUE_INDEX_TEMPLATE = '''export {{ default }} from './{fileName}.vue'
'''

VUE_ROOT_INDEX_TEMPLATE = '''// StrategyDECK Icons for Vue
{exports}
'''

VUE_PACKAGE_JSON = {
    "name": "strategydeck-icons-vue",
    "version": "1.0.0",
    "description": "StrategyDECK Icons as Vue Components",
    "main": "dist/index.js",
    "module": "dist/index.esm.js",
    "types": "dist/index.d.ts",
    "license": "MIT",
    "peerDependencies": {
        "vue": "^3.0.0"
    }
}

# Template for Svelte components
SVELTE_COMPONENT_TEMPLATE = '''<script lang="ts">
  export let size: number | string = 24;
  export let title: string = "{componentTitle}";
  export let strokeWidth: number | string = 2;
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  width={{size}}
  height={{size}}
  viewBox="0 0 {viewBoxSize} {viewBoxSize}"
  fill="none"
  stroke="currentColor"
  stroke-width={{strokeWidth}}
  stroke-linecap="round"
  stroke-linejoin="round"
  {{...$$restProps}}
>
  {svgContent}
  {{#if title}}
    <title>{{title}}</title>
  {{/if}}
</svg>
'''

SVELTE_INDEX_TEMPLATE = '''export {{ default }} from './{fileName}.svelte';
'''

SVELTE_ROOT_INDEX_TEMPLATE = '''// StrategyDECK Icons for Svelte
{exports}
'''

SVELTE_PACKAGE_JSON = {
    "name": "strategydeck-icons-svelte",
    "version": "1.0.0",
    "description": "StrategyDECK Icons as Svelte Components",
    "main": "dist/index.js",
    "module": "dist/index.mjs",
    "svelte": "dist/index.js",
    "types": "dist/index.d.ts",
    "license": "MIT"
}

# Template for Angular components
ANGULAR_COMPONENT_TEMPLATE = '''import {{ Component, Input, ChangeDetectionStrategy }} from '@angular/core';

@Component({{
  selector: 'strategydeck-{kebabName}',
  template: `
    <svg
      xmlns="http://www.w3.org/2000/svg"
      [attr.width]="size"
      [attr.height]="size"
      viewBox="0 0 {viewBoxSize} {viewBoxSize}"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      {svgContent}
      <title *ngIf="title">{{title}}</title>
    </svg>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
}})
export class {ComponentName}Component {{
  @Input() size: string | number = 24;
  @Input() title: string = '{componentTitle}';
}}
'''

ANGULAR_INDEX_TEMPLATE = '''export * from './{fileName}.component';
'''

ANGULAR_ROOT_INDEX_TEMPLATE = '''// StrategyDECK Icons for Angular
import {{ NgModule }} from '@angular/core';
import {{ CommonModule }} from '@angular/common';

{imports}

@NgModule({{
  declarations: [
{declarations}
  ],
  imports: [
    CommonModule
  ],
  exports: [
{exports}
  ]
}})
export class StrategyDeckIconsModule {{ }}

{componentExports}
'''

ANGULAR_PACKAGE_JSON = {
    "name": "strategydeck-icons-angular",
    "version": "1.0.0",
    "description": "StrategyDECK Icons as Angular Components",
    "main": "dist/index.js",
    "module": "dist/index.esm.js",
    "types": "dist/index.d.ts",
    "license": "MIT",
    "peerDependencies": {
        "@angular/core": "^13.0.0 || ^14.0.0 || ^15.0.0 || ^16.0.0",
        "@angular/common": "^13.0.0 || ^14.0.0 || ^15.0.0 || ^16.0.0"
    }
}

# Template for Web Components
WEB_COMPONENT_TEMPLATE = '''class {ComponentName}Element extends HTMLElement {{
  constructor() {{
    super();
    this.attachShadow({{ mode: 'open' }});
  }}

  static get observedAttributes() {{
    return ['size', 'title'];
  }}

  attributeChangedCallback(name, oldValue, newValue) {{
    if (oldValue !== newValue) {{
      this.render();
    }}
  }}

  connectedCallback() {{
    this.render();
  }}

  render() {{
    const size = this.getAttribute('size') || 24;
    const title = this.getAttribute('title') || '{componentTitle}';

    this.shadowRoot.innerHTML = `
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="${{size}}"
        height="${{size}}"
        viewBox="0 0 {viewBoxSize} {viewBoxSize}"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        {svgContent}
        ${{title ? `<title>${{title}}</title>` : ''}}
      </svg>
    `;
  }}
}}

customElements.define('strategydeck-{kebabName}', {ComponentName}Element);
'''

WEB_COMPONENT_INDEX_TEMPLATE = '''export * from './{fileName}';
'''

WEB_COMPONENT_ROOT_INDEX_TEMPLATE = '''// StrategyDECK Icons as Web Components
{exports}
'''

WEB_COMPONENT_PACKAGE_JSON = {
    "name": "strategydeck-icons-webcomponents",
    "version": "1.0.0",
    "description": "StrategyDECK Icons as Web Components",
    "main": "dist/index.js",
    "module": "dist/index.esm.js",
    "license": "MIT"
}

# Framework configurations
FRAMEWORK_CONFIGS = {
    "react": FrameworkConfig(
        name="react",
        file_extension=".tsx",
        component_template=REACT_COMPONENT_TEMPLATE,
        index_template=REACT_INDEX_TEMPLATE,
        package_json=REACT_PACKAGE_JSON,
        extra_files={
            "tsconfig.json": json.dumps({
                "compilerOptions": {
                    "target": "ES2019",
                    "module": "ESNext",
                    "lib": ["DOM", "ESNext"],
                    "jsx": "react",
                    "declaration": true,
                    "moduleResolution": "node",
                    "esModuleInterop": true,
                    "strict": true,
                    "outDir": "dist"
                },
                "include": ["src/**/*"],
                "exclude": ["node_modules"]
            }, indent=2)
        }
    ),
    "vue": FrameworkConfig(
        name="vue",
        file_extension=".vue",
        component_template=VUE_COMPONENT_TEMPLATE,
        index_template=VUE_INDEX_TEMPLATE,
        package_json=VUE_PACKAGE_JSON,
        extra_files={
            "tsconfig.json": json.dumps({
                "compilerOptions": {
                    "target": "ES2019",
                    "module": "ESNext",
                    "lib": ["DOM", "ESNext"],
                    "declaration": true,
                    "moduleResolution": "node",
                    "esModuleInterop": true,
                    "strict": true,
                    "outDir": "dist"
                },
                "include": ["src/**/*"],
                "exclude": ["node_modules"]
            }, indent=2)
        }
    ),
    "svelte": FrameworkConfig(
        name="svelte",
        file_extension=".svelte",
        component_template=SVELTE_COMPONENT_TEMPLATE,
        index_template=SVELTE_INDEX_TEMPLATE,
        package_json=SVELTE_PACKAGE_JSON,
        extra_files={
            "tsconfig.json": json.dumps({
                "compilerOptions": {
                    "target": "ES2019",
                    "module": "ESNext",
                    "lib": ["DOM", "ESNext"],
                    "declaration": true,
                    "moduleResolution": "node",
                    "esModuleInterop": true,
                    "strict": true,
                    "outDir": "dist"
                },
                "include": ["src/**/*"],
                "exclude": ["node_modules"]
            }, indent=2)
        }
    ),
    "angular": FrameworkConfig(
        name="angular",
        file_extension=".component.ts",
        component_template=ANGULAR_COMPONENT_TEMPLATE,
        index_template=ANGULAR_INDEX_TEMPLATE,
        package_json=ANGULAR_PACKAGE_JSON,
        extra_files={
            "tsconfig.json": json.dumps({
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "ESNext",
                    "lib": ["DOM", "ESNext"],
                    "declaration": true,
                    "moduleResolution": "node",
                    "esModuleInterop": true,
                    "strict": true,
                    "outDir": "dist",
                    "experimentalDecorators": true,
                    "emitDecoratorMetadata": true
                },
                "include": ["src/**/*"],
                "exclude": ["node_modules"]
            }, indent=2)
        }
    ),
    "web-components": FrameworkConfig(
        name="web-components",
        file_extension=".js",
        component_template=WEB_COMPONENT_TEMPLATE,
        index_template=WEB_COMPONENT_INDEX_TEMPLATE,
        package_json=WEB_COMPONENT_PACKAGE_JSON,
        extra_files={}
    ),
    "vanilla-js": FrameworkConfig(
        name="vanilla-js",
        file_extension=".js",
        component_template="export const {camelName} = `\n{svgRaw}\n`;\n",
        index_template="export {{ {camelName} }} from './{fileName}';\n",
        package_json={
            "name": "strategydeck-icons-js",
            "version": "1.0.0",
            "description": "StrategyDECK Icons as JavaScript strings",
            "main": "dist/index.js",
            "module": "dist/index.esm.js",
            "license": "MIT"
        },
        extra_files={}
    )
}


def camel_to_kebab(name: str) -> str:
    """Convert camelCase to kebab-case"""
    name = re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()
    return name


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase"""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def kebab_to_camel(name: str) -> str:
    """Convert kebab-case to camelCase"""
    components = name.split('-')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_component_name(name: str) -> str:
    """Convert a filename to a component name"""
    # Remove extension if present
    name = Path(name).stem

    # Handle special cases
    if '-' in name:
        parts = name.split('-')
        return ''.join(part.capitalize() for part in parts) + 'Icon'
    elif '_' in name:
        parts = name.split('_')
        return ''.join(part.capitalize() for part in parts) + 'Icon'
    else:
        return name.capitalize() + 'Icon'


def extract_svg_content(svg_file: Path) -> tuple:
    """Extract the content from an SVG file, returning the inner content and viewBox size"""
    with open(svg_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract viewBox size
    viewbox_match = re.search(r'viewBox="0 0 (\d+) (\d+)"', content)
    if viewbox_match:
        width = viewbox_match.group(1)
        height = viewbox_match.group(2)
        # Use the larger dimension
        viewbox_size = max(int(width), int(height))
    else:
        # Default to 24 if not found
        viewbox_size = 24

    # Extract the inner content (remove outer svg tag)
    inner_match = re.search(r'<svg[^>]*>(.*?)</svg>', content, re.DOTALL)
    if inner_match:
        inner_content = inner_match.group(1).strip()
    else:
        inner_content = ""

    return inner_content, viewbox_size, content


def generate_component(
    svg_file: Path,
    output_dir: Path,
    framework_config: FrameworkConfig,
    optimize: bool = False
) -> tuple:
    """Generate a component for the given SVG file"""
    # Extract file details
    file_stem = svg_file.stem
    component_name = to_component_name(file_stem)
    kebab_name = camel_to_kebab(component_name.replace('Icon', ''))
    camel_name = kebab_to_camel(kebab_name)

    # Extract SVG content
    svg_content, viewbox_size, svg_raw = extract_svg_content(svg_file)

    # Create component content
    component_content = framework_config.component_template.format(
        ComponentName=component_name,
        componentTitle=kebab_name.replace('-', ' ').title(),
        kebabName=kebab_name,
        camelName=camel_name,
        svgContent=svg_content,
        viewBoxSize=viewbox_size,
        svgRaw=svg_raw
    )

    # Create index file content
    index_content = framework_config.index_template.format(
        fileName=file_stem,
        ComponentName=component_name,
        camelName=camel_name
    )

    # Save files
    component_file = output_dir / f"{file_stem}{framework_config.file_extension}"
    index_file = output_dir / f"index{framework_config.file_extension.split('.')[0]}.ts"

    component_file.write_text(component_content, encoding='utf-8')

    return file_stem, component_name, kebab_name, camel_name


def create_root_index(
    output_dir: Path,
    framework_config: FrameworkConfig,
    component_data: List[tuple]
) -> None:
    """Create the root index file for the framework"""

    if framework_config.name == "angular":
        # Angular requires special handling for the module
        imports = "\n".join([
            f"import {{ {data[1]}Component }} from './{data[0]}.component';"
            for data in component_data
        ])

        declarations = "\n".join([
            f"    {data[1]}Component,"
            for data in component_data
        ])

        exports = "\n".join([
            f"    {data[1]}Component,"
            for data in component_data
        ])

        component_exports = "\n".join([
            f"export * from './{data[0]}.component';"
            for data in component_data
        ])

        root_content = ANGULAR_ROOT_INDEX_TEMPLATE.format(
            imports=imports,
            declarations=declarations,
            exports=exports,
            componentExports=component_exports
        )
    else:
        # Generic handling for other frameworks
        if framework_config.name == "vanilla-js":
            exports = "\n".join([
                f"export {{ {data[3]} }} from './{data[0]}';"
                for data in component_data
            ])
        else:
            exports = "\n".join([
                f"export * from './{data[0]}';"
                for data in component_data
            ])

        if framework_config.name == "react":
            root_content = REACT_ROOT_INDEX_TEMPLATE.format(exports=exports)
        elif framework_config.name == "vue":
            root_content = VUE_ROOT_INDEX_TEMPLATE.format(exports=exports)
        elif framework_config.name == "svelte":
            root_content = SVELTE_ROOT_INDEX_TEMPLATE.format(exports=exports)
        elif framework_config.name == "web-components":
            root_content = WEB_COMPONENT_ROOT_INDEX_TEMPLATE.format(exports=exports)
        else:
            root_content = f"// StrategyDECK Icons\n{exports}"

    # Determine file extension
    if framework_config.name == "vanilla-js" or framework_config.name == "web-components":
        ext = ".js"
    else:
        ext = ".ts"

    # Write the index file
    index_file = output_dir / f"index{ext}"
    index_file.write_text(root_content, encoding='utf-8')


def create_package_json(output_dir: Path, framework_config: FrameworkConfig) -> None:
    """Create package.json for the framework"""
    package_json_path = output_dir / "package.json"
    package_json_path.write_text(
        json.dumps(framework_config.package_json, indent=2),
        encoding='utf-8'
    )


def create_extra_files(output_dir: Path, framework_config: FrameworkConfig) -> None:
    """Create extra files needed for the framework"""
    for filename, content in framework_config.extra_files.items():
        file_path = output_dir / filename
        file_path.write_text(content, encoding='utf-8')


def find_svg_files(include_sizes: Optional[List[int]] = None,
                   include_modes: Optional[List[str]] = None,
                   include_contexts: Optional[List[str]] = None) -> List[Path]:
    """Find SVG files in the assets directory matching the given criteria"""
    svg_files = []

    # Collect all SVG files
    for svg_file in OUT.glob("**/*.svg"):
        # Parse path components
        parts = svg_file.relative_to(OUT).parts

        if len(parts) >= 4:  # mode/finish/size/context/filename
            mode = parts[0]
            size_str = parts[2]
            context = parts[3]

            # Extract size from folder name (e.g., "16px" -> 16)
            size = int(size_str.replace("px", "")) if "px" in size_str else None

            # Apply filters
            if include_sizes and size and size not in include_sizes:
                continue

            if include_modes and mode not in include_modes:
                continue

            if include_contexts and context not in include_contexts:
                continue

            svg_files.append(svg_file)

    return svg_files


def optimize_svg(svg_file: Path) -> None:
    """Optimize an SVG file (simple version)"""
    try:
        with open(svg_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove unnecessary attributes and whitespace
        # (This is a very basic optimization - a real implementation would use a proper SVG optimizer)
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'>\s+<', '><', content)

        with open(svg_file, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error optimizing {svg_file}: {e}")


def export_icons(framework: str, output_path: str, optimize: bool = False,
                 include_sizes: Optional[List[int]] = None,
                 include_modes: Optional[List[str]] = None,
                 include_contexts: Optional[List[str]] = None,
                 clear_output: bool = True) -> None:
    """Export icons for the specified framework"""
    if framework not in FRAMEWORK_CONFIGS:
        print(f"Error: Unsupported framework '{framework}'")
        print(f"Supported frameworks: {', '.join(FRAMEWORKS)}")
        return

    # Get framework configuration
    framework_config = FRAMEWORK_CONFIGS[framework]

    # Setup output directory
    output_dir = Path(output_path) / "src"
    if clear_output and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find SVG files
    svg_files = find_svg_files(include_sizes, include_modes, include_contexts)

    if not svg_files:
        print("No SVG files found matching the specified criteria")
        return

    print(f"Exporting {len(svg_files)} icons for {framework}...")

    # Generate components
    component_data = []
    for svg_file in svg_files:
        data = generate_component(svg_file, output_dir, framework_config, optimize)
        component_data.append(data)
        print(f"Generated component for {svg_file.name}")

    # Create root index file
    create_root_index(output_dir, framework_config, component_data)

    # Create package.json
    create_package_json(Path(output_path), framework_config)

    # Create extra files
    create_extra_files(Path(output_path), framework_config)

    print(f"Successfully exported {len(component_data)} icons to {output_path}")
    print(
        f"To build the package, run: cd {output_path} && npm install && npm run build")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="StrategyDECK Icon Framework Exporter")

    parser.add_argument("--framework", choices=FRAMEWORKS, required=True,
                        help="Target framework")

    parser.add_argument("--output", required=True,
                        help="Output directory path")

    parser.add_argument("--optimize", action="store_true",
                        help="Optimize SVG files")

    parser.add_argument("--sizes", type=int, nargs="+",
                        help="Include only these sizes (e.g., 16 24 32)")

    parser.add_argument("--modes", nargs="+",
                        help="Include only these modes (e.g., light dark)")

    parser.add_argument("--contexts", nargs="+",
                        help="Include only these contexts (e.g., web print)")

    parser.add_argument("--no-clear", action="store_true",
                        help="Don't clear output directory before generating")

    args = parser.parse_args()

    export_icons(
        framework=args.framework,
        output_path=args.output,
        optimize=args.optimize,
        include_sizes=args.sizes,
        include_modes=args.modes,
        include_contexts=args.contexts,
        clear_output=not args.no_clear
    )


if __name__ == "__main__":
    main()
