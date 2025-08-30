# StrategyDECK Game Integration Guide

This guide explains how to integrate StrategyDECK icons with your game and SaaS products.

## Overview

StrategyDECK provides a versatile icon system that can be used across different platforms and applications. This integration guide explains how to:

1. Generate StrategyDECK icons
2. Sync icons with your game and SaaS products
3. Use StrategyDECK icons in different contexts

## Quick Start

To quickly get up and running with StrategyDECK integration:

```bash
# Generate all icons
./generate_strategydeck.sh --clean

# Sync icons with game and SaaS targets
python strategydeck_game_assets_connector.py sync

# Start the full EpochCore RAS system with StrategyDECK
./strategydeck_epoch_runner.sh
```

## Integration Targets

StrategyDECK supports the following integration targets:

### Unity Game

Icons are synced to the `dist/game-assets/unity` directory with the following configuration:

- Formats: PNG
- Sizes: 16px, 32px, 64px, 128px
- Contexts: game

To use icons in Unity:

1. Import the icons from the `dist/game-assets/unity` directory into your Unity project
2. Create a SpriteAtlas to organize and optimize the icons
3. Reference the icons in your UI through the SpriteAtlas

Example Unity C# code:

```csharp
using UnityEngine;
using UnityEngine.UI;

public class StrategyIconManager : MonoBehaviour
{
    public SpriteAtlas iconAtlas;
    
    public void SetIcon(Image targetImage, string iconName)
    {
        Sprite sprite = null;
        iconAtlas.GetSprite(iconName, out sprite);
        
        if (sprite != null)
        {
            targetImage.sprite = sprite;
        }
    }
}
```

### Web Dashboard

Icons are synced to the `dist/game-assets/web` directory with the following configuration:

- Formats: SVG, PNG
- Sizes: 16px, 24px, 32px, 48px
- Contexts: web

To use icons in your web dashboard:

1. Import the icons from the `dist/game-assets/web` directory into your web project
2. Use SVG icons for scalable UI elements
3. Use PNG icons for fixed-size UI elements or when SVG is not supported

Example HTML/CSS:

```html
<div class="icon-container">
    <img src="path/to/strategy_icon-light-flat-orange-32px.svg" alt="Strategy Icon" class="strategy-icon">
</div>

<style>
.strategy-icon {
    width: 32px;
    height: 32px;
}
</style>
```

### SaaS Platform

Icons are synced to the `dist/game-assets/saas` directory with the following configuration:

- Formats: SVG
- Sizes: 16px, 24px, 32px
- Contexts: web

To use icons in your SaaS platform:

1. Import the SVG icons from the `dist/game-assets/saas` directory
2. Use a frontend framework like React or Vue to render the icons
3. Consider using an icon component library to manage the icons

Example React component:

```jsx
import React from 'react';

const StrategyIcon = ({ mode, finish, size }) => {
  const iconPath = `/assets/icons/${mode}/${finish}/${size}px/web/strategy_icon-${mode}-${finish}-${size}px.svg`;
  
  return (
    <div className="strategy-icon-wrapper">
      <img src={iconPath} alt={`Strategy Icon - ${mode} ${finish} ${size}px`} />
    </div>
  );
};

export default StrategyIcon;
```

## Custom Integration

To add a custom integration target:

```bash
python strategydeck_game_assets_connector.py add-target "my-target" "/path/to/target" --types svg png --sizes 16 32 64 --contexts web game
```

## Automatic Syncing

The StrategyDECK system can automatically sync icons when changes are detected. To enable automatic syncing:

1. Edit the `game_assets_sync_config.json` file
2. Set `"auto_sync": true`
3. Set `"sync_on_changes": true`

## Icon Naming Conventions

StrategyDECK icons follow a consistent naming convention:

```
strategy_icon-{mode}-{finish}-{size}px[-{context}].{format}
```

For example:
- `strategy_icon-light-flat-orange-32px.svg`
- `strategy_icon-dark-matte-carbon-64px-game.png`

## Integration with EpochCore RAS

The StrategyDECK icons are used by the EpochCore RAS agents to represent different aspects of the agent system:

- **Intelligence Channel**: Uses flat-orange icons
- **Resilience Channel**: Uses matte-carbon icons
- **Collaboration Channel**: Uses copper-foil icons
- **Evolution Channel**: Uses burnt-orange icons
- **Quantum Channel**: Uses satin-black icons
- **Cognitive Channel**: Uses embossed-paper icons
- **Temporal Channel**: Uses flat-orange icons
- **Ethical Channel**: Uses matte-carbon icons

Each agent channel can be customized to use different icon variants based on the context and requirements.

## Troubleshooting

If you encounter issues with icon integration:

1. Check that icons are properly generated: `./generate_strategydeck.sh --clean`
2. Verify sync targets are configured: `python strategydeck_game_assets_connector.py list`
3. Run sync manually: `python strategydeck_game_assets_connector.py sync`
4. Check error logs in the `logs` directory
5. Run the integration test: `pytest tests/test_strategydeck_game_integration.py`

## Support

For additional support, please contact the StrategyDECK team or refer to the `STRATEGYDECK_README.md` file.
