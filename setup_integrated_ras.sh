#!/usr/bin/env bash
# EpochCore RAS - Integrated Setup
# Combines RAS Product System with Game Infrastructure

set -euo pipefail

# Root paths
ROOT="${PWD}"
SCRIPTS="$ROOT/scripts"
TOOLS="$ROOT/tools"
GAME="$ROOT/game"
RAS="$ROOT/ras"
LEDGER_ROOT="${LEDGER_ROOT:-$HOME/epoch_ledger}"

# Create directory structure
mkdir -p "$SCRIPTS" "$TOOLS" "$GAME"/{design,docs,checklists,assets,build,export} "$RAS"/{agents,capsules,strategy}

# Helper functions
now(){ date -u +"%Y-%m-%dT%H:%M:%SZ"; }
if command -v sha256sum >/dev/null 2>&1; then SHACMD="sha256sum"; else SHACMD="shasum -a 256"; fi
log(){ printf '{"ts":"%s","event":"%s","note":"%s"}\n' "$(now)" "$1" "$2" >> "$LEDGER_ROOT/ledger_main.jsonl"; }

# Initialize RAS Strategy Integration
initialize_ras_strategies() {
    # Create RAS strategy directories
    mkdir -p "$RAS/strategy"/{evolution,self_improve,intelligence,quantum,recursion,compound}
    
    # Copy core strategies
    cp "$ROOT/strategy_evolution.py" "$RAS/strategy/evolution/"
    cp "$ROOT/strategy_self_improve.py" "$RAS/strategy/self_improve/"
    cp "$ROOT/strategy_intelligence.py" "$RAS/strategy/intelligence/"
    cp "$ROOT/strategy_quantum.py" "$RAS/strategy/quantum/"
    cp "$ROOT/strategy_recursion_enhancer.py" "$RAS/strategy/recursion/"
    cp "$ROOT/strategy_compound_recursion.py" "$RAS/strategy/compound/"
    
    # Initialize game integration hooks
    cat > "$RAS/strategy/game_hooks.py" <<'EOL'
"""Game Integration Hooks for RAS Strategies"""
from pathlib import Path
import json
from typing import Dict, Any

class GameIntegration:
    def __init__(self, state_dir: str = ".game_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
    def on_strategy_evolution(self, metrics: Dict[str, Any]):
        """Hook for evolution strategy events"""
        self._record_event("evolution", metrics)
        
    def on_strategy_improve(self, metrics: Dict[str, Any]):
        """Hook for self-improvement events"""
        self._record_event("improve", metrics)
        
    def on_strategy_intelligence(self, metrics: Dict[str, Any]):
        """Hook for intelligence events"""
        self._record_event("intelligence", metrics)
        
    def on_strategy_quantum(self, metrics: Dict[str, Any]):
        """Hook for quantum strategy events"""
        self._record_event("quantum", metrics)
        
    def _record_event(self, strategy: str, metrics: Dict[str, Any]):
        """Record strategy event in game state"""
        event_file = self.state_dir / f"{strategy}_events.jsonl"
        with event_file.open("a") as f:
            json.dump({
                "strategy": strategy,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }, f)
            f.write("\n")
EOL
    
    # Create strategy initialization
    cat > "$RAS/strategy/__init__.py" <<'EOL'
"""RAS Strategy Integration"""
from .evolution import AutonomousEvolution
from .self_improve import RecursiveSelfImprover
from .intelligence import IntelligenceStrategy
from .quantum import initialize_quantum_strategy
from .recursion import RecursiveEnhancer
from .compound import CompoundRecursion
from .game_hooks import GameIntegration

__all__ = [
    'AutonomousEvolution',
    'RecursiveSelfImprover', 
    'IntelligenceStrategy',
    'initialize_quantum_strategy',
    'RecursiveEnhancer',
    'CompoundRecursion',
    'GameIntegration'
]
EOL
}

# Initialize Game Integration
initialize_game() {
    # Copy game script
    cp "$1" "$GAME/epoch_game.sh"
    chmod +x "$GAME/epoch_game.sh"
    
    # Create RAS game hooks
    cat > "$GAME/ras_hooks.sh" <<'EOL'
#!/usr/bin/env bash
# RAS Integration Hooks for Game Events

# Record strategy evolution
ras_evolve() {
    strategy="$1"
    metrics="$2"
    echo "{\"ts\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"strategy\":\"$strategy\",\"metrics\":$metrics}" >> "$RAS/events.jsonl"
}

# Record self-improvement
ras_improve() {
    improvement="$1"
    echo "{\"ts\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"improvement\":$improvement}" >> "$RAS/improvements.jsonl"
}

# Record intelligence insight
ras_insight() {
    insight="$1"
    echo "{\"ts\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"insight\":$insight}" >> "$RAS/insights.jsonl"
}

# Record quantum state
ras_quantum() {
    state="$1"
    echo "{\"ts\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"quantum_state\":$state}" >> "$RAS/quantum.jsonl"
}
EOL
    chmod +x "$GAME/ras_hooks.sh"
}

# Main installation
main() {
    # Create main directories
    mkdir -p "$LEDGER_ROOT"/{logs,seals,capsules}
    
    # Initialize RAS strategies
    initialize_ras_strategies
    
    # Initialize game with RAS hooks
    initialize_game "$1"
    
    # Create integration manifest
    cat > "$ROOT/INTEGRATION.md" <<EOL
# EpochCore RAS - Game Integration

Integration structure:
- RAS Strategies: $RAS/strategy/
- Game System: $GAME/
- Integration Hooks:
  - Python: $RAS/strategy/game_hooks.py
  - Shell: $GAME/ras_hooks.sh
  
Usage:
1. Initialize RAS strategies:
   \`\`\`python
   from ras.strategy import GameIntegration
   game = GameIntegration()
   \`\`\`

2. Use game hooks:
   \`\`\`bash
   source "$GAME/ras_hooks.sh"
   ras_evolve "evolution" '{"score":100}'
   \`\`\`
EOL
    
    log "integrated_setup" "RAS+Game integration complete"
    
    echo "✅ Integration complete:"
    echo "- RAS strategies: $RAS/strategy/"
    echo "- Game system: $GAME/"
    echo "- Integration hooks installed"
    echo "- See INTEGRATION.md for usage details"
}

# Execute main installation
main "$@"
