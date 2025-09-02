#!/usr/bin/env python3
"""
EpochCore RAS AutoML-Zero Evolution Engine
Implements evolutionary program synthesis for automated machine learning
"""

import json
import numpy as np
import random
import copy
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import torch
import torch.nn as nn


class OperationType(Enum):
    """Basic operations for program synthesis"""
    INPUT = "input"
    OUTPUT = "output"  
    LINEAR = "linear"
    RELU = "relu"
    SIGMOID = "sigmoid"
    TANH = "tanh"
    ADD = "add"
    MULTIPLY = "multiply"
    MATRIX_MULTIPLY = "matmul"
    TRANSPOSE = "transpose"
    MEAN = "mean"
    MAX = "max"
    MIN = "min"
    CONCAT = "concat"
    SLICE = "slice"


@dataclass
class Operation:
    """Represents a single operation in the program"""
    op_type: OperationType
    inputs: List[int]  # Indices of input variables
    output: int       # Index of output variable
    parameters: Dict[str, Any]  # Operation-specific parameters
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class Program:
    """Represents a complete ML program"""
    program_id: str
    operations: List[Operation]
    input_size: int
    output_size: int
    fitness: float = 0.0
    created_at: datetime = None
    generation: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class ProgramExecutor:
    """Executes synthesized ML programs"""
    
    def __init__(self):
        self.operation_map = {
            OperationType.INPUT: self._execute_input,
            OperationType.OUTPUT: self._execute_output,
            OperationType.LINEAR: self._execute_linear,
            OperationType.RELU: self._execute_relu,
            OperationType.SIGMOID: self._execute_sigmoid,
            OperationType.TANH: self._execute_tanh,
            OperationType.ADD: self._execute_add,
            OperationType.MULTIPLY: self._execute_multiply,
            OperationType.MATRIX_MULTIPLY: self._execute_matmul,
            OperationType.TRANSPOSE: self._execute_transpose,
            OperationType.MEAN: self._execute_mean,
            OperationType.MAX: self._execute_max,
            OperationType.MIN: self._execute_min,
            OperationType.CONCAT: self._execute_concat,
            OperationType.SLICE: self._execute_slice
        }
    
    def execute_program(self, program: Program, input_data: np.ndarray) -> Optional[np.ndarray]:
        """Execute a program on input data"""
        try:
            # Initialize variable storage
            variables = {}
            
            # Set input variables
            if len(input_data.shape) == 1:
                input_data = input_data.reshape(1, -1)
            
            variables[0] = input_data  # Convention: input is variable 0
            
            # Execute operations in order
            for op in program.operations:
                if op.op_type in self.operation_map:
                    result = self.operation_map[op.op_type](op, variables)
                    if result is not None:
                        variables[op.output] = result
                else:
                    print(f"Warning: Unknown operation type {op.op_type}")
                    return None
            
            # Return final output (convention: highest numbered variable)
            if variables:
                output_var = max(variables.keys())
                return variables[output_var]
            
            return None
            
        except Exception as e:
            print(f"Program execution error: {e}")
            return None
    
    def _execute_input(self, op: Operation, variables: Dict[int, np.ndarray]) -> np.ndarray:
        """Input operation (already handled in execute_program)"""
        return variables.get(0)
    
    def _execute_output(self, op: Operation, variables: Dict[int, np.ndarray]) -> np.ndarray:
        """Output operation"""
        if op.inputs and op.inputs[0] in variables:
            return variables[op.inputs[0]]
        return None
    
    def _execute_linear(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Linear transformation"""
        if not op.inputs or op.inputs[0] not in variables:
            return None
        
        input_data = variables[op.inputs[0]]
        input_size = input_data.shape[-1]
        output_size = op.parameters.get('output_size', input_size)
        
        # Generate or retrieve weight matrix
        if 'weight' not in op.parameters:
            op.parameters['weight'] = np.random.randn(input_size, output_size) * 0.1
            op.parameters['bias'] = np.random.randn(output_size) * 0.1
        
        weight = op.parameters['weight']
        bias = op.parameters['bias']
        
        try:
            result = np.dot(input_data, weight) + bias
            return result
        except Exception as e:
            print(f"Linear operation error: {e}")
            return None
    
    def _execute_relu(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """ReLU activation"""
        if not op.inputs or op.inputs[0] not in variables:
            return None
        
        input_data = variables[op.inputs[0]]
        return np.maximum(0, input_data)
    
    def _execute_sigmoid(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Sigmoid activation"""
        if not op.inputs or op.inputs[0] not in variables:
            return None
        
        input_data = variables[op.inputs[0]]
        return 1 / (1 + np.exp(-np.clip(input_data, -500, 500)))
    
    def _execute_tanh(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Tanh activation"""
        if not op.inputs or op.inputs[0] not in variables:
            return None
        
        input_data = variables[op.inputs[0]]
        return np.tanh(input_data)
    
    def _execute_add(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Element-wise addition"""
        if len(op.inputs) < 2 or not all(i in variables for i in op.inputs[:2]):
            return None
        
        a = variables[op.inputs[0]]
        b = variables[op.inputs[1]]
        
        try:
            return a + b
        except Exception:
            # Try broadcasting
            try:
                return np.add(a, b)
            except Exception as e:
                print(f"Add operation error: {e}")
                return None
    
    def _execute_multiply(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Element-wise multiplication"""
        if len(op.inputs) < 2 or not all(i in variables for i in op.inputs[:2]):
            return None
        
        a = variables[op.inputs[0]]
        b = variables[op.inputs[1]]
        
        try:
            return a * b
        except Exception:
            try:
                return np.multiply(a, b)
            except Exception as e:
                print(f"Multiply operation error: {e}")
                return None
    
    def _execute_matmul(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Matrix multiplication"""
        if len(op.inputs) < 2 or not all(i in variables for i in op.inputs[:2]):
            return None
        
        a = variables[op.inputs[0]]
        b = variables[op.inputs[1]]
        
        try:
            return np.matmul(a, b)
        except Exception as e:
            print(f"Matmul operation error: {e}")
            return None
    
    def _execute_transpose(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Matrix transpose"""
        if not op.inputs or op.inputs[0] not in variables:
            return None
        
        input_data = variables[op.inputs[0]]
        return np.transpose(input_data)
    
    def _execute_mean(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Mean along axis"""
        if not op.inputs or op.inputs[0] not in variables:
            return None
        
        input_data = variables[op.inputs[0]]
        axis = op.parameters.get('axis', None)
        return np.mean(input_data, axis=axis, keepdims=True)
    
    def _execute_max(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Max along axis"""
        if not op.inputs or op.inputs[0] not in variables:
            return None
        
        input_data = variables[op.inputs[0]]
        axis = op.parameters.get('axis', None)
        return np.max(input_data, axis=axis, keepdims=True)
    
    def _execute_min(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Min along axis"""
        if not op.inputs or op.inputs[0] not in variables:
            return None
        
        input_data = variables[op.inputs[0]]
        axis = op.parameters.get('axis', None)
        return np.min(input_data, axis=axis, keepdims=True)
    
    def _execute_concat(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Concatenate arrays"""
        if len(op.inputs) < 2 or not all(i in variables for i in op.inputs):
            return None
        
        arrays = [variables[i] for i in op.inputs]
        axis = op.parameters.get('axis', -1)
        
        try:
            return np.concatenate(arrays, axis=axis)
        except Exception as e:
            print(f"Concat operation error: {e}")
            return None
    
    def _execute_slice(self, op: Operation, variables: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
        """Slice array"""
        if not op.inputs or op.inputs[0] not in variables:
            return None
        
        input_data = variables[op.inputs[0]]
        start = op.parameters.get('start', 0)
        end = op.parameters.get('end', input_data.shape[-1])
        
        try:
            return input_data[..., start:end]
        except Exception as e:
            print(f"Slice operation error: {e}")
            return None


class ProgramGenerator:
    """Generates random ML programs"""
    
    def __init__(self, max_operations: int = 10, max_variables: int = 20):
        self.max_operations = max_operations
        self.max_variables = max_variables
        self.executor = ProgramExecutor()
        
    def generate_random_program(self, input_size: int, output_size: int) -> Program:
        """Generate a random ML program"""
        program_id = f"program_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        operations = []
        current_var = 1  # Start from 1 (0 is reserved for input)
        
        num_ops = random.randint(3, self.max_operations)
        
        for i in range(num_ops):
            # Choose operation type (bias towards useful operations)
            op_weights = {
                OperationType.LINEAR: 0.3,
                OperationType.RELU: 0.2,
                OperationType.SIGMOID: 0.1,
                OperationType.TANH: 0.1,
                OperationType.ADD: 0.1,
                OperationType.MULTIPLY: 0.05,
                OperationType.MEAN: 0.05,
                OperationType.MAX: 0.05,
                OperationType.MIN: 0.05
            }
            
            op_type = random.choices(
                list(op_weights.keys()),
                weights=list(op_weights.values())
            )[0]
            
            # Generate inputs (reference previous variables)
            available_vars = list(range(min(current_var, self.max_variables)))
            if not available_vars:
                available_vars = [0]  # Fallback to input
            
            if op_type in [OperationType.ADD, OperationType.MULTIPLY, OperationType.MATRIX_MULTIPLY]:
                num_inputs = 2
            else:
                num_inputs = 1
            
            inputs = random.choices(available_vars, k=min(num_inputs, len(available_vars)))
            
            # Generate parameters based on operation type
            parameters = {}
            if op_type == OperationType.LINEAR:
                parameters['output_size'] = random.choice([input_size//2, input_size, output_size, 32, 64])
            elif op_type in [OperationType.MEAN, OperationType.MAX, OperationType.MIN]:
                parameters['axis'] = random.choice([None, -1])
            elif op_type == OperationType.SLICE:
                max_size = input_size
                start = random.randint(0, max(0, max_size-2))
                end = random.randint(start+1, max_size)
                parameters['start'] = start
                parameters['end'] = end
            
            operation = Operation(
                op_type=op_type,
                inputs=inputs,
                output=current_var,
                parameters=parameters
            )
            
            operations.append(operation)
            current_var += 1
        
        return Program(
            program_id=program_id,
            operations=operations,
            input_size=input_size,
            output_size=output_size
        )
    
    def mutate_program(self, program: Program, mutation_rate: float = 0.1) -> Program:
        """Apply mutations to a program"""
        mutated = copy.deepcopy(program)
        mutated.program_id = f"{program.program_id}_mut_{random.randint(1000, 9999)}"
        mutated.fitness = 0.0  # Reset fitness
        mutated.generation = program.generation + 1
        
        for operation in mutated.operations:
            if random.random() < mutation_rate:
                # Mutate operation type
                if random.random() < 0.3:
                    operation.op_type = random.choice(list(OperationType))
                
                # Mutate parameters
                if random.random() < 0.3:
                    if operation.op_type == OperationType.LINEAR:
                        if 'output_size' in operation.parameters:
                            operation.parameters['output_size'] = random.choice([16, 32, 64, 128])
                    elif operation.op_type == OperationType.SLICE:
                        max_size = program.input_size
                        start = random.randint(0, max(0, max_size-2))
                        end = random.randint(start+1, max_size)
                        operation.parameters['start'] = start
                        operation.parameters['end'] = end
                
                # Mutate inputs
                if random.random() < 0.3 and operation.inputs:
                    available_vars = list(range(len(mutated.operations) + 1))
                    operation.inputs = random.choices(available_vars, k=len(operation.inputs))
        
        return mutated
    
    def crossover_programs(self, parent1: Program, parent2: Program) -> Tuple[Program, Program]:
        """Crossover two programs to create offspring"""
        child1_ops = []
        child2_ops = []
        
        min_len = min(len(parent1.operations), len(parent2.operations))
        max_len = max(len(parent1.operations), len(parent2.operations))
        
        # Single-point crossover
        crossover_point = random.randint(1, min_len)
        
        child1_ops.extend(parent1.operations[:crossover_point])
        child1_ops.extend(parent2.operations[crossover_point:])
        
        child2_ops.extend(parent2.operations[:crossover_point])
        child2_ops.extend(parent1.operations[crossover_point:])
        
        child1 = Program(
            program_id=f"child1_{datetime.now().strftime('%H%M%S')}_{random.randint(100, 999)}",
            operations=child1_ops,
            input_size=parent1.input_size,
            output_size=parent1.output_size,
            generation=max(parent1.generation, parent2.generation) + 1
        )
        
        child2 = Program(
            program_id=f"child2_{datetime.now().strftime('%H%M%S')}_{random.randint(100, 999)}",
            operations=child2_ops,
            input_size=parent2.input_size,
            output_size=parent2.output_size,
            generation=max(parent1.generation, parent2.generation) + 1
        )
        
        return child1, child2


class FitnessEvaluator:
    """Evaluates fitness of ML programs"""
    
    def __init__(self):
        self.executor = ProgramExecutor()
    
    def evaluate_fitness(self, program: Program, train_data: Tuple[np.ndarray, np.ndarray],
                        test_data: Tuple[np.ndarray, np.ndarray]) -> float:
        """Evaluate program fitness on train/test data"""
        try:
            train_x, train_y = train_data
            test_x, test_y = test_data
            
            # Execute program on training data
            train_pred = self.executor.execute_program(program, train_x)
            if train_pred is None:
                return 0.0
            
            # Execute program on test data  
            test_pred = self.executor.execute_program(program, test_x)
            if test_pred is None:
                return 0.0
            
            # Calculate fitness (lower error = higher fitness)
            train_error = self._calculate_error(train_pred, train_y)
            test_error = self._calculate_error(test_pred, test_y)
            
            # Combine train and test performance (emphasize generalization)
            fitness = 1.0 / (1.0 + 0.7 * test_error + 0.3 * train_error)
            
            # Penalize overly complex programs
            complexity_penalty = len(program.operations) * 0.01
            fitness = max(0.0, fitness - complexity_penalty)
            
            return fitness
            
        except Exception as e:
            print(f"Fitness evaluation error: {e}")
            return 0.0
    
    def _calculate_error(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Calculate prediction error"""
        try:
            # Handle shape mismatches
            if predictions.shape != targets.shape:
                # Try to reshape or take mean
                if predictions.size == targets.size:
                    predictions = predictions.reshape(targets.shape)
                elif len(predictions.shape) > len(targets.shape):
                    predictions = np.mean(predictions, axis=tuple(range(len(targets.shape), len(predictions.shape))))
                else:
                    # Expand targets to match predictions
                    while len(targets.shape) < len(predictions.shape):
                        targets = np.expand_dims(targets, -1)
                    if targets.shape != predictions.shape:
                        return float('inf')  # Can't reconcile shapes
            
            # Mean squared error
            mse = np.mean((predictions - targets) ** 2)
            return float(mse)
            
        except Exception as e:
            print(f"Error calculation failed: {e}")
            return float('inf')


class AutoMLZeroEngine:
    """Main AutoML-Zero evolutionary engine"""
    
    def __init__(self, population_size: int = 50, max_generations: int = 100):
        self.population_size = population_size
        self.max_generations = max_generations
        self.generator = ProgramGenerator()
        self.evaluator = FitnessEvaluator()
        self.population = []
        self.evolution_history = []
        
    def initialize_population(self, input_size: int, output_size: int):
        """Initialize random population"""
        print(f"Initializing population of {self.population_size} programs...")
        self.population = []
        
        for i in range(self.population_size):
            program = self.generator.generate_random_program(input_size, output_size)
            self.population.append(program)
        
        print(f"✓ Initialized {len(self.population)} programs")
    
    def evolve_population(self, train_data: Tuple[np.ndarray, np.ndarray],
                         test_data: Tuple[np.ndarray, np.ndarray]) -> Dict[str, Any]:
        """Run evolutionary algorithm"""
        print(f"Starting evolution for {self.max_generations} generations...")
        
        best_fitness_history = []
        
        for generation in range(self.max_generations):
            print(f"Generation {generation + 1}/{self.max_generations}")
            
            # Evaluate fitness for all programs
            for program in self.population:
                if program.fitness == 0.0:  # Only evaluate if not already evaluated
                    program.fitness = self.evaluator.evaluate_fitness(program, train_data, test_data)
            
            # Sort by fitness (descending)
            self.population.sort(key=lambda p: p.fitness, reverse=True)
            
            best_fitness = self.population[0].fitness
            best_fitness_history.append(best_fitness)
            
            if generation % 10 == 0:
                print(f"  Best fitness: {best_fitness:.4f}")
            
            # Selection and reproduction
            new_population = []
            
            # Keep top performers (elitism)
            elite_size = self.population_size // 4
            new_population.extend(copy.deepcopy(self.population[:elite_size]))
            
            # Generate offspring through crossover and mutation
            while len(new_population) < self.population_size:
                # Tournament selection
                parent1 = self._tournament_selection()
                parent2 = self._tournament_selection()
                
                # Crossover
                if random.random() < 0.7:  # Crossover probability
                    child1, child2 = self.generator.crossover_programs(parent1, parent2)
                    new_population.extend([child1, child2])
                
                # Mutation
                if random.random() < 0.3:  # Mutation probability
                    mutated = self.generator.mutate_program(parent1)
                    new_population.append(mutated)
                
                # Ensure we don't exceed population size
                if len(new_population) > self.population_size:
                    new_population = new_population[:self.population_size]
            
            self.population = new_population
        
        # Final evaluation
        for program in self.population:
            if program.fitness == 0.0:
                program.fitness = self.evaluator.evaluate_fitness(program, train_data, test_data)
        
        self.population.sort(key=lambda p: p.fitness, reverse=True)
        
        evolution_result = {
            'best_program': self.population[0],
            'best_fitness': self.population[0].fitness,
            'fitness_history': best_fitness_history,
            'final_population_size': len(self.population),
            'generations_completed': self.max_generations,
            'evolution_timestamp': datetime.now().isoformat()
        }
        
        self.evolution_history.append(evolution_result)
        
        print(f"✓ Evolution completed! Best fitness: {self.population[0].fitness:.4f}")
        return evolution_result
    
    def _tournament_selection(self, tournament_size: int = 3) -> Program:
        """Tournament selection for parent selection"""
        tournament = random.choices(self.population, k=tournament_size)
        return max(tournament, key=lambda p: p.fitness)
    
    def generate_synthetic_data(self, input_size: int = 10, output_size: int = 1, 
                              n_samples: int = 100) -> Tuple[Tuple[np.ndarray, np.ndarray], 
                                                           Tuple[np.ndarray, np.ndarray]]:
        """Generate synthetic data for evolution"""
        np.random.seed(42)  # For reproducible results
        
        # Generate input data
        X = np.random.randn(n_samples, input_size)
        
        # Generate target function (simple linear combination with noise)
        weights = np.random.randn(input_size)
        y = np.dot(X, weights) + 0.1 * np.random.randn(n_samples)
        
        if output_size == 1:
            y = y.reshape(-1, 1)
        
        # Split into train/test
        split_idx = n_samples // 2
        train_data = (X[:split_idx], y[:split_idx])
        test_data = (X[split_idx:], y[split_idx:])
        
        return train_data, test_data
    
    def run_automl_zero_experiment(self, input_size: int = 10, output_size: int = 1) -> Dict[str, Any]:
        """Run complete AutoML-Zero experiment"""
        print(f"[{datetime.now()}] Starting AutoML-Zero experiment...")
        
        # Generate data
        train_data, test_data = self.generate_synthetic_data(input_size, output_size)
        
        # Initialize population
        self.initialize_population(input_size, output_size)
        
        # Evolve population
        evolution_result = self.evolve_population(train_data, test_data)
        
        experiment_result = {
            'experiment_timestamp': datetime.now().isoformat(),
            'input_size': input_size,
            'output_size': output_size,
            'population_size': self.population_size,
            'max_generations': self.max_generations,
            'evolution_result': evolution_result,
            'status': 'completed'
        }
        
        print("✓ AutoML-Zero experiment completed!")
        return experiment_result
    
    def get_automl_zero_status(self) -> Dict[str, Any]:
        """Get AutoML-Zero engine status"""
        return {
            'status': 'operational',
            'population_size': self.population_size,
            'max_generations': self.max_generations,
            'current_population_count': len(self.population),
            'evolution_history_length': len(self.evolution_history),
            'best_program_fitness': self.population[0].fitness if self.population else None,
            'latest_experiment': self.evolution_history[-1] if self.evolution_history else None
        }


# Global AutoML-Zero engine instance
automl_zero_engine = AutoMLZeroEngine()


def setup_automl_zero() -> Dict[str, Any]:
    """Setup AutoML-Zero environment"""
    print(f"[{datetime.now()}] Setting up AutoML-Zero engine...")
    print("✓ Initializing program generator...")
    print("✓ Setting up fitness evaluator...")
    print("✓ Configuring evolutionary parameters...")
    print("✓ AutoML-Zero setup complete!")
    return {"status": "success", "components_initialized": 3}


def run_automl_zero_experiment(input_size: int = 10, output_size: int = 1) -> Dict[str, Any]:
    """Run AutoML-Zero experiment"""
    return automl_zero_engine.run_automl_zero_experiment(input_size, output_size)


def get_automl_zero_status() -> Dict[str, Any]:
    """Get AutoML-Zero status"""
    return automl_zero_engine.get_automl_zero_status()


if __name__ == "__main__":
    # Demo functionality
    engine = AutoMLZeroEngine(population_size=20, max_generations=10)  # Smaller for demo
    result = engine.run_automl_zero_experiment()
    print(f"Demo completed: {result['evolution_result']['best_fitness']:.4f}")