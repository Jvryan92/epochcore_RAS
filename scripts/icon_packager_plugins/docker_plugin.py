
'''
Docker packager plugin for StrategyDECK icons
'''
import os
import shutil
from pathlib import Path
from typing import Dict

# Import the packager_plugin decorator from the main script
from scripts.package_icons import packager_plugin

@packager_plugin("docker")
def create_docker_package(metadata: Dict, config: Dict, output_dir: Path) -> Path:
    '''
    Create a Docker image package for the icons.
    
    Args:
        metadata: Icon metadata
        config: Package configuration
        output_dir: Output directory for the package
        
    Returns:
        Path to the created Docker package directory
    '''
    package_name = config.get("package_name", "strategydeck-icons")
    package_version = config.get("package_version", "1.0.0")
    
    docker_dir = output_dir / "docker"
    if docker_dir.exists():
        shutil.rmtree(docker_dir)
    docker_dir.mkdir(parents=True)
    
    # Create Dockerfile
    with open(docker_dir / "Dockerfile", "w", encoding="utf-8") as f:
        f.write(f'''FROM nginx:alpine
LABEL maintainer="{config.get('package_author', 'EpochCore RAS')}"
LABEL version="{package_version}"
LABEL description="{config.get('package_description', 'StrategyDECK icons')}"

# Copy icons to nginx serve directory
COPY icons /usr/share/nginx/html/icons

# Copy metadata
COPY metadata.json /usr/share/nginx/html/metadata.json

# Copy index page
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
''')
    
    # Create icons directory
    icons_dir = docker_dir / "icons"
    icons_dir.mkdir()
    
    # Copy icons
    for variant in metadata["variants"]:
        src_path = Path(variant["path"])
        
        # Create the directory structure
        dest_dir = icons_dir / variant["mode"] / variant["finish"] / variant["size"] / variant["context"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        dest_path = dest_dir / variant["filename"]
        shutil.copy2(src_path, dest_path)
    
    # Save metadata.json
    with open(docker_dir / "metadata.json", "w", encoding="utf-8") as f:
        import json
        json.dump(metadata, f, indent=2)
    
    # Create index.html
    with open(docker_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{package_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .icon-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 16px; }}
        .icon-item {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; text-align: center; }}
        .icon-item img {{ max-width: 64px; max-height: 64px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{package_name} v{package_version}</h1>
        <p>{config.get('package_description', 'StrategyDECK icons')}</p>
        
        <h2>Icon Gallery</h2>
        <div class="icon-grid" id="icon-grid">
            <!-- Icons will be inserted here via JavaScript -->
        </div>
    </div>
    
    <script>
        // Fetch and display icons
        fetch('/metadata.json')
            .then(response => response.json())
            .then(data => {{
                const iconGrid = document.getElementById('icon-grid');
                
                data.variants.forEach(icon => {{
                    if (icon.format === 'svg') {{
                        const item = document.createElement('div');
                        item.className = 'icon-item';
                        
                        const img = document.createElement('img');
                        img.src = '/' + icon.path;
                        img.alt = icon.filename;
                        
                        const info = document.createElement('p');
                        info.textContent = `${{icon.mode}} / ${{icon.finish}} / ${{icon.size}}`;
                        
                        item.appendChild(img);
                        item.appendChild(info);
                        iconGrid.appendChild(item);
                    }}
                }});
            }})
            .catch(error => console.error('Error loading icons:', error));
    </script>
</body>
</html>
''')
    
    # Create build script
    with open(docker_dir / "build.sh", "w", encoding="utf-8") as f:
        f.write(f'''#!/bin/bash
# Build Docker image for {package_name}
docker build -t {package_name}:{package_version} .
echo "Built Docker image: {package_name}:{package_version}"
echo "Run with: docker run -p 8080:80 {package_name}:{package_version}"
''')
    
    # Make build script executable
    os.chmod(docker_dir / "build.sh", 0o755)
    
    return docker_dir
