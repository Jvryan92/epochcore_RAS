"""
Enhanced Game Library Configuration
Maps all available games with their training paths and mesh integration
"""

GAME_LIBRARY = {
    # TIER 1: FUNDAMENTAL GAMES
    "basic_games": {
        "tic_tac_toe": {
            "modes": ["vs_agent", "agent_vs_agent", "analysis"],
            "difficulty_range": (1, 10),
            "mesh_compatible": True,
            "learning_objectives": ["basic strategy", "pattern recognition"],
            "kid_safe": True
        },
        "connect_four": {
            "modes": ["vs_agent", "agent_vs_agent", "analysis"],
            "difficulty_range": (1, 15),
            "mesh_compatible": True,
            "learning_objectives": ["vertical thinking", "trap detection"],
            "kid_safe": True
        },
        "checkers": {
            "modes": ["vs_agent", "analysis", "puzzle_solve"],
            "difficulty_range": (1, 20),
            "mesh_compatible": True,
            "learning_objectives": ["capture chains", "position control"],
            "kid_safe": True
        }
    },

    # TIER 2: CLASSICAL STRATEGY
    "classical_games": {
        "chess": {
            "modes": ["vs_agent", "agent_vs_agent", "analysis", "puzzle_solve"],
            "difficulty_range": (800, 2800),  # ELO
            "mesh_compatible": True,
            "learning_objectives": ["tactical vision", "strategic planning"],
            "variants": ["blitz", "rapid", "classical"]
        },
        "go": {
            "modes": ["vs_agent", "analysis", "territory_calc"],
            "difficulty_range": (5, 19),  # board size
            "mesh_compatible": True,
            "learning_objectives": ["territory control", "influence"]
        },
        "shogi": {
            "modes": ["vs_agent", "analysis", "piece_drop_training"],
            "difficulty_range": (1, 25),
            "mesh_compatible": True,
            "learning_objectives": ["piece drops", "complex tactics"]
        }
    },

    # TIER 3: MODERN STRATEGY
    "modern_strategy": {
        "mesh_wars": {
            "modes": ["campaign", "skirmish", "analysis"],
            "difficulty_range": (1, 30),
            "mesh_compatible": True,
            "learning_objectives": ["resource management", "tech progression"],
            "economy_features": True
        },
        "crypto_commander": {
            "modes": ["market_sim", "trading_ai", "portfolio_opt"],
            "difficulty_range": (1, 25),
            "mesh_compatible": True,
            "learning_objectives": ["market analysis", "risk management"],
            "economy_features": True
        },
        "neural_networks": {
            "modes": ["train", "optimize", "evolve"],
            "difficulty_range": (1, 40),
            "mesh_compatible": True,
            "learning_objectives": ["network design", "hyperparameter tuning"]
        }
    },

    # TIER 4: PUZZLE GAMES
    "puzzle_games": {
        "sokoban": {
            "modes": ["solve", "generate", "analyze"],
            "difficulty_range": (1, 50),
            "mesh_compatible": True,
            "learning_objectives": ["path planning", "state space search"],
            "kid_safe": True
        },
        "mesh_bridge": {
            "modes": ["build", "optimize", "stress_test"],
            "difficulty_range": (1, 30),
            "mesh_compatible": True,
            "learning_objectives": ["structural analysis", "resource optimization"],
            "kid_safe": True
        },
        "quantum_puzzle": {
            "modes": ["solve", "design", "optimize"],
            "difficulty_range": (1, 45),
            "mesh_compatible": True,
            "learning_objectives": ["quantum concepts", "superposition logic"]
        }
    },

    # TIER 5: PLATFORMER & ACTION
    "action_games": {
        "tarzan_lite": {
            "modes": ["play", "ghost_record", "assist"],
            "difficulty_range": (1, 20),
            "mesh_compatible": True,
            "learning_objectives": ["timing", "momentum"],
            "kid_safe": True
        },
        "mesh_runner": {
            "modes": ["speedrun", "collect", "race"],
            "difficulty_range": (1, 35),
            "mesh_compatible": True,
            "learning_objectives": ["path optimization", "risk-reward"],
            "kid_safe": True
        },
        "echo_knight": {
            "modes": ["adventure", "combat", "puzzle"],
            "difficulty_range": (1, 40),
            "mesh_compatible": True,
            "learning_objectives": ["combat timing", "resource management"],
            "kid_safe": True
        }
    },

    # TIER 6: ECONOMIC GAMES
    "economic_games": {
        "mesh_market": {
            "modes": ["trade", "invest", "analyze"],
            "difficulty_range": (1, 50),
            "mesh_compatible": True,
            "learning_objectives": ["market dynamics", "portfolio theory"],
            "economy_features": True
        },
        "resource_empire": {
            "modes": ["build", "trade", "expand"],
            "difficulty_range": (1, 45),
            "mesh_compatible": True,
            "learning_objectives": ["resource chains", "market control"],
            "economy_features": True
        },
        "crypto_tycoon": {
            "modes": ["mine", "trade", "stake"],
            "difficulty_range": (1, 40),
            "mesh_compatible": True,
            "learning_objectives": ["blockchain mechanics", "yield farming"],
            "economy_features": True
        }
    },

    # TIER 7: NETWORK GAMES
    "network_games": {
        "packet_racer": {
            "modes": ["route", "optimize", "secure"],
            "difficulty_range": (1, 35),
            "mesh_compatible": True,
            "learning_objectives": ["network topology", "routing algorithms"]
        },
        "mesh_defense": {
            "modes": ["protect", "counter", "analyze"],
            "difficulty_range": (1, 45),
            "mesh_compatible": True,
            "learning_objectives": ["security patterns", "threat detection"]
        },
        "consensus_forge": {
            "modes": ["propose", "validate", "build"],
            "difficulty_range": (1, 40),
            "mesh_compatible": True,
            "learning_objectives": ["consensus algorithms", "Byzantine fault tolerance"]
        }
    },

    # TIER 8: SIMULATION GAMES
    "simulation_games": {
        "eco_sim": {
            "modes": ["balance", "evolve", "analyze"],
            "difficulty_range": (1, 50),
            "mesh_compatible": True,
            "learning_objectives": ["system dynamics", "feedback loops"],
            "kid_safe": True
        },
        "city_planner": {
            "modes": ["build", "optimize", "simulate"],
            "difficulty_range": (1, 45),
            "mesh_compatible": True,
            "learning_objectives": ["resource distribution", "growth patterns"],
            "kid_safe": True
        },
        "quantum_sim": {
            "modes": ["experiment", "measure", "entangle"],
            "difficulty_range": (1, 55),
            "mesh_compatible": True,
            "learning_objectives": ["quantum mechanics", "measurement theory"]
        }
    }
}

# Learning paths for different skill levels
LEARNING_PATHS = {
    "beginner": [
        ("basic_games", ["tic_tac_toe", "connect_four"]),
        ("puzzle_games", ["sokoban"]),
        ("action_games", ["tarzan_lite"]),
        ("simulation_games", ["eco_sim"])
    ],

    "intermediate": [
        ("classical_games", ["chess", "go"]),
        ("modern_strategy", ["mesh_wars"]),
        ("economic_games", ["mesh_market"]),
        ("network_games", ["packet_racer"])
    ],

    "advanced": [
        ("modern_strategy", ["neural_networks", "crypto_commander"]),
        ("network_games", ["consensus_forge", "mesh_defense"]),
        ("simulation_games", ["quantum_sim"]),
        ("economic_games", ["crypto_tycoon"])
    ],

    "kids": [
        ("basic_games", ["tic_tac_toe", "connect_four", "checkers"]),
        ("puzzle_games", ["sokoban", "mesh_bridge"]),
        ("action_games", ["tarzan_lite", "mesh_runner", "echo_knight"]),
        ("simulation_games", ["eco_sim", "city_planner"])
    ]
}

# Training sequences for agents
AGENT_TRAINING = {
    "strategic": [
        "tic_tac_toe", "chess", "go", "mesh_wars",
        "neural_networks", "crypto_commander"
    ],
    "economic": [
        "mesh_market", "resource_empire", "crypto_tycoon",
        "consensus_forge"
    ],
    "puzzle": [
        "sokoban", "mesh_bridge", "quantum_puzzle",
        "packet_racer", "mesh_defense"
    ],
    "simulation": [
        "eco_sim", "city_planner", "quantum_sim",
        "neural_networks"
    ]
}

# Mesh enhancement factors for each game type
MESH_FACTORS = {
    "basic_games": 1.2,
    "classical_games": 1.5,
    "modern_strategy": 2.0,
    "puzzle_games": 1.8,
    "action_games": 1.3,
    "economic_games": 1.7,
    "network_games": 1.9,
    "simulation_games": 1.6
}

# Achievement system
ACHIEVEMENTS = {
    "quick_learner": {
        "description": "Complete a learning path in record time",
        "mesh_bonus": 1.5
    },
    "versatile_agent": {
        "description": "Master games from 3 different categories",
        "mesh_bonus": 2.0
    },
    "economy_expert": {
        "description": "Achieve high returns in all economic games",
        "mesh_bonus": 1.8
    },
    "puzzle_master": {
        "description": "Solve highest difficulty puzzles in all puzzle games",
        "mesh_bonus": 1.7
    },
    "network_sage": {
        "description": "Master all network protocols and defenses",
        "mesh_bonus": 1.9
    },
    "quantum_theorist": {
        "description": "Complete all quantum simulations and puzzles",
        "mesh_bonus": 2.1
    }
}
