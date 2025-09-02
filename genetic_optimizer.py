#!/usr/bin/env python3
"""
EpochCore RAS Genetic Optimizer
Implements genetic/evolutionary algorithms to evolve code/config parameters
"""

import numpy as np
import json
import random
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GeneticOptimizer:
    """
    Genetic algorithm implementation for optimizing system parameters.
    Evolves configuration parameters and validates improvements.
    """
    
    def __init__(self):
        self.population_size = 20
        self.generations = 10
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elite_size = 2
        
        # Define parameter space for optimization
        self.parameter_space = {
            "agent_pool_size": {"type": "int", "min": 5, "max": 20, "current": 12},
            "dag_timeout": {"type": "int", "min": 30, "max": 300, "current": 120},
            "capsule_batch_size": {"type": "int", "min": 1, "max": 10, "current": 5},
            "policy_check_interval": {"type": "int", "min": 10, "max": 60, "current": 30},
            "health_check_frequency": {"type": "float", "min": 0.5, "max": 5.0, "current": 2.0},
        }
        
        logger.info("Genetic Optimizer initialized")
    
    def optimize_parameters(self) -> Dict[str, Any]:
        """
        Run genetic algorithm to optimize system parameters.
        Returns optimization results and recommended improvements.
        """
        logger.info("Starting genetic parameter optimization")
        
        try:
            # Initialize population
            population = self._initialize_population()
            best_fitness_history = []
            
            for generation in range(self.generations):
                # Evaluate fitness for each individual
                fitness_scores = []
                for individual in population:
                    fitness = self._evaluate_fitness(individual)
                    fitness_scores.append(fitness)
                
                # Track best fitness
                best_fitness = max(fitness_scores)
                best_fitness_history.append(best_fitness)
                logger.info(f"Generation {generation + 1}: Best fitness = {best_fitness:.3f}")
                
                # Select parents and create next generation
                if generation < self.generations - 1:
                    population = self._evolve_population(population, fitness_scores)
            
            # Find best individual from final population
            final_fitness = [self._evaluate_fitness(ind) for ind in population]
            best_index = np.argmax(final_fitness)
            best_individual = population[best_index]
            best_fitness = final_fitness[best_index]
            
            # Generate improvements from best individual
            improvements = self._generate_improvements(best_individual)
            
            result = {
                "improvements_found": len(improvements) > 0,
                "improvements": improvements,
                "best_fitness": best_fitness,
                "generations_run": self.generations,
                "fitness_history": best_fitness_history,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Genetic optimization completed. Found {len(improvements)} improvements")
            return result
            
        except Exception as e:
            logger.error(f"Error in genetic optimization: {str(e)}")
            return {
                "improvements_found": False,
                "improvements": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _initialize_population(self) -> List[Dict[str, Any]]:
        """Initialize a random population of parameter configurations."""
        population = []
        
        for _ in range(self.population_size):
            individual = {}
            for param_name, param_config in self.parameter_space.items():
                if param_config["type"] == "int":
                    value = random.randint(param_config["min"], param_config["max"])
                elif param_config["type"] == "float":
                    value = random.uniform(param_config["min"], param_config["max"])
                else:
                    value = param_config["current"]
                
                individual[param_name] = value
            
            population.append(individual)
        
        return population
    
    def _evaluate_fitness(self, individual: Dict[str, Any]) -> float:
        """
        Evaluate the fitness of a parameter configuration.
        Higher fitness indicates better performance.
        """
        fitness = 0.0
        
        try:
            # Simulate system performance with these parameters
            # In a real implementation, this would test the actual system
            
            # Fitness components:
            
            # 1. Agent pool size optimization (sweet spot around 12-15)
            agent_pool_size = individual["agent_pool_size"]
            if 10 <= agent_pool_size <= 15:
                fitness += 1.0
            else:
                fitness += max(0, 1.0 - abs(agent_pool_size - 12.5) * 0.1)
            
            # 2. DAG timeout optimization (prefer reasonable timeouts)
            dag_timeout = individual["dag_timeout"]
            if 60 <= dag_timeout <= 180:
                fitness += 1.0
            else:
                fitness += max(0, 1.0 - abs(dag_timeout - 120) * 0.005)
            
            # 3. Capsule batch size (prefer moderate batching)
            batch_size = individual["capsule_batch_size"]
            if 3 <= batch_size <= 7:
                fitness += 1.0
            else:
                fitness += max(0, 1.0 - abs(batch_size - 5) * 0.2)
            
            # 4. Policy check interval (balance between responsiveness and overhead)
            policy_interval = individual["policy_check_interval"]
            if 20 <= policy_interval <= 40:
                fitness += 1.0
            else:
                fitness += max(0, 1.0 - abs(policy_interval - 30) * 0.02)
            
            # 5. Health check frequency (not too frequent, not too sparse)
            health_frequency = individual["health_check_frequency"]
            if 1.5 <= health_frequency <= 3.0:
                fitness += 1.0
            else:
                fitness += max(0, 1.0 - abs(health_frequency - 2.0) * 0.3)
            
            # Add small random component to prevent premature convergence
            fitness += random.uniform(-0.1, 0.1)
            
        except Exception as e:
            logger.error(f"Error evaluating fitness: {str(e)}")
            fitness = 0.0
        
        return max(0.0, fitness)
    
    def _evolve_population(self, population: List[Dict[str, Any]], fitness_scores: List[float]) -> List[Dict[str, Any]]:
        """Evolve the population through selection, crossover, and mutation."""
        new_population = []
        
        # Keep elite individuals
        elite_indices = np.argsort(fitness_scores)[-self.elite_size:]
        for idx in elite_indices:
            new_population.append(population[idx].copy())
        
        # Generate rest of population through crossover and mutation
        while len(new_population) < self.population_size:
            # Select parents
            parent1 = self._tournament_selection(population, fitness_scores)
            parent2 = self._tournament_selection(population, fitness_scores)
            
            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            if random.random() < self.mutation_rate:
                child1 = self._mutate(child1)
            if random.random() < self.mutation_rate:
                child2 = self._mutate(child2)
            
            new_population.extend([child1, child2])
        
        # Trim to exact population size
        return new_population[:self.population_size]
    
    def _tournament_selection(self, population: List[Dict[str, Any]], fitness_scores: List[float], tournament_size: int = 3) -> Dict[str, Any]:
        """Select an individual using tournament selection."""
        tournament_indices = random.sample(range(len(population)), min(tournament_size, len(population)))
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx].copy()
    
    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform crossover between two parents."""
        child1 = parent1.copy()
        child2 = parent2.copy()
        
        # Single-point crossover for each parameter
        for param_name in self.parameter_space.keys():
            if random.random() < 0.5:
                child1[param_name] = parent2[param_name]
                child2[param_name] = parent1[param_name]
        
        return child1, child2
    
    def _mutate(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mutation to an individual."""
        mutated = individual.copy()
        
        for param_name, param_config in self.parameter_space.items():
            if random.random() < 0.3:  # 30% chance to mutate each parameter
                if param_config["type"] == "int":
                    # Gaussian mutation with bounds checking
                    current_value = mutated[param_name]
                    mutation_range = (param_config["max"] - param_config["min"]) * 0.1
                    new_value = current_value + random.gauss(0, mutation_range)
                    new_value = max(param_config["min"], min(param_config["max"], int(new_value)))
                    mutated[param_name] = new_value
                    
                elif param_config["type"] == "float":
                    # Gaussian mutation with bounds checking
                    current_value = mutated[param_name]
                    mutation_range = (param_config["max"] - param_config["min"]) * 0.1
                    new_value = current_value + random.gauss(0, mutation_range)
                    new_value = max(param_config["min"], min(param_config["max"], new_value))
                    mutated[param_name] = new_value
        
        return mutated
    
    def _generate_improvements(self, best_individual: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate improvement recommendations from the best individual."""
        improvements = []
        
        for param_name, value in best_individual.items():
            current_value = self.parameter_space[param_name]["current"]
            
            # Only recommend changes that differ significantly from current
            if self.parameter_space[param_name]["type"] == "int":
                if abs(value - current_value) >= 1:
                    improvements.append({
                        "type": "genetic_parameter",
                        "parameter": param_name,
                        "current_value": current_value,
                        "recommended_value": value,
                        "improvement_type": "parameter_optimization",
                        "description": f"Optimize {param_name} from {current_value} to {value}",
                        "confidence": self._calculate_confidence(param_name, current_value, value),
                        "expected_benefit": self._estimate_benefit(param_name, current_value, value)
                    })
            else:  # float
                if abs(value - current_value) >= 0.1:
                    improvements.append({
                        "type": "genetic_parameter",
                        "parameter": param_name,
                        "current_value": current_value,
                        "recommended_value": round(value, 2),
                        "improvement_type": "parameter_optimization",
                        "description": f"Optimize {param_name} from {current_value} to {round(value, 2)}",
                        "confidence": self._calculate_confidence(param_name, current_value, value),
                        "expected_benefit": self._estimate_benefit(param_name, current_value, value)
                    })
        
        return improvements
    
    def _calculate_confidence(self, param_name: str, current_value: Any, new_value: Any) -> float:
        """Calculate confidence in the improvement recommendation."""
        # Simple confidence based on how much the parameter changed
        param_config = self.parameter_space[param_name]
        param_range = param_config["max"] - param_config["min"]
        
        if param_config["type"] == "int":
            change_ratio = abs(new_value - current_value) / param_range
        else:
            change_ratio = abs(new_value - current_value) / param_range
        
        # Higher confidence for moderate changes, lower for extreme changes
        if change_ratio < 0.1:
            return 0.9
        elif change_ratio < 0.3:
            return 0.8
        elif change_ratio < 0.5:
            return 0.6
        else:
            return 0.4
    
    def _estimate_benefit(self, param_name: str, current_value: Any, new_value: Any) -> str:
        """Estimate the expected benefit of the parameter change."""
        if param_name == "agent_pool_size":
            if new_value > current_value:
                return "Increased throughput and parallel processing capability"
            else:
                return "Reduced resource usage and improved efficiency"
        elif param_name == "dag_timeout":
            if new_value > current_value:
                return "Improved reliability for long-running tasks"
            else:
                return "Faster failure detection and resource recovery"
        elif param_name == "capsule_batch_size":
            if new_value > current_value:
                return "Improved I/O efficiency through larger batches"
            else:
                return "Lower latency and more responsive processing"
        elif param_name == "policy_check_interval":
            if new_value > current_value:
                return "Reduced overhead from policy checking"
            else:
                return "More responsive security policy enforcement"
        elif param_name == "health_check_frequency":
            if new_value > current_value:
                return "More frequent monitoring and faster issue detection"
            else:
                return "Reduced monitoring overhead and resource usage"
        
        return "General system performance improvement"


if __name__ == "__main__":
    # Test the genetic optimizer
    optimizer = GeneticOptimizer()
    result = optimizer.optimize_parameters()
    print(json.dumps(result, indent=2))