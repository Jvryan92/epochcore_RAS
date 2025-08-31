# strategy_cognitive.py
"""
Cognitive processing and decision making system
"""

__all__ = ['CognitiveArchitecture', 'CognitiveState', 'CognitiveDecision']

from typing import Dict, List, Any, Optional, Tuple, Union
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from dataclasses import dataclass
import numpy as np
from datetime import datetime
import json

@dataclass
class CognitiveState:
    """State representation for cognitive processing"""
    input_embedding: torch.Tensor
    context_embedding: torch.Tensor
    attention_weights: torch.Tensor
    emotional_influence: float
    confidence_score: float
    processing_time: float
    timestamp: datetime

@dataclass
class CognitiveDecision:
    """Decision output from cognitive processing"""
    chosen_option: Any
    confidence: float
    reasoning_path: List[str]
    alternatives: List[Any]
    decision_time: float
    state: CognitiveState

class MultiHeadAttention(nn.Module):
    """Multi-head attention layer"""
    
    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
    def scaled_dot_product_attention(
        self,
        Q: torch.Tensor,
        K: torch.Tensor,
        V: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        d_k = Q.size(-1)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
            
        attention_weights = F.softmax(scores, dim=-1)
        output = torch.matmul(attention_weights, V)
        
        return output, attention_weights
        
    def forward(
        self,
        Q: torch.Tensor,
        K: torch.Tensor,
        V: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_size = Q.size(0)
        
        Q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        output, attention = self.scaled_dot_product_attention(Q, K, V, mask)
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        
        return self.W_o(output), attention

class CognitiveArchitecture:
    """Neural architecture for cognitive processing."""
    
    def __init__(self, d_model: int = 256):
        """Initialize the cognitive architecture."""
        self.d_model = d_model
        
        # Initialize components
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.language_model = AutoModel.from_pretrained("bert-base-uncased")
        self.context_embedding = nn.Linear(768, d_model)  # BERT hidden size -> model dim
        self.attention = MultiHeadAttention(d_model, num_heads=8)
        
        # Memory components
        self.short_term_memory = []
        self.long_term_memory = {}
        
        # Emotional state (valence, arousal, dominance)
        self.emotional_state = torch.zeros(3)
        self.attention_threshold = 0.7
        
    def process_input(
        self,
        input_data: Union[str, Dict[str, Any], List[Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> CognitiveState:
        """Process input with attention and context awareness"""
        start_time = datetime.now()
        
        # Convert input to tensor representation
        if isinstance(input_data, str):
            inputs = self.tokenizer(input_data, return_tensors="pt", padding=True)
            with torch.no_grad():
                input_tensor = self.language_model(**inputs).last_hidden_state
                # Average over sequence length for fixed-size representation
                input_tensor = torch.mean(input_tensor, dim=1, keepdim=True)
        else:
            # Convert other types to tensor (simplified)
            encoded = str(input_data).encode()
            # Create fixed-size encoding
            encoding = np.zeros(self.context_embedding.in_features)
            encoding[:min(len(encoded), self.context_embedding.in_features)] = \
                [x / 255.0 for x in encoded[:self.context_embedding.in_features]]
            input_tensor = torch.tensor(encoding, dtype=torch.float32)\
                              .unsqueeze(0).unsqueeze(0)
        
        # Process context first to get tensor of correct size
        context_tensor = self._encode_context(context)
        
        # Project input to match context size
        input_tensor = torch.mean(input_tensor, dim=1, keepdim=True)
        
        # Make sure both tensors have the right dimensions (batch, seq_len, hidden_size)
        if input_tensor.ndim < 3:
            input_tensor = input_tensor.unsqueeze(0)
        if context_tensor.ndim < 3:
            context_tensor = context_tensor.unsqueeze(0)
        
        # Project both tensors to model dimension
        embedded_input = self.context_embedding(input_tensor)
        embedded_context = self.context_embedding(context_tensor)
        
        # Apply attention mechanism
        output, attention_weights = self.attention(
            embedded_input,
            embedded_context,
            embedded_context
        )
        
        # Calculate emotional influence
        emotional_influence = torch.mean(self.emotional_state).item()
        
        # Calculate confidence based on attention and emotion
        confidence_score = torch.mean(attention_weights).item() * (1 + emotional_influence)
        
        # Create cognitive state
        state = CognitiveState(
            input_embedding=embedded_input,
            context_embedding=embedded_context,
            attention_weights=attention_weights,
            emotional_influence=emotional_influence,
            confidence_score=confidence_score,
            processing_time=(datetime.now() - start_time).total_seconds(),
            timestamp=datetime.now()
        )
        
        # Update memory
        self._update_memory(state)
        
        return state
        
    def make_decision(
        self,
        state: CognitiveState,
        options: List[Any]
    ) -> CognitiveDecision:
        """Make a decision based on cognitive state and options"""
        start_time = datetime.now()
        
        # Encode options
        option_embeddings = torch.stack([
            self._encode_option(opt) for opt in options
        ])
        
        # Calculate attention between state and options
        attention_scores = F.softmax(torch.matmul(
            state.input_embedding.squeeze(),
            option_embeddings.squeeze().t()
        ), dim=0)
        
        # Select option with highest attention
        best_idx = torch.argmax(attention_scores)
        chosen_option = options[best_idx]
        confidence = attention_scores[best_idx].item()
        
        # Generate reasoning path
        reasoning = self._generate_reasoning_path(
            state,
            chosen_option,
            confidence
        )
        
        return CognitiveDecision(
            chosen_option=chosen_option,
            confidence=confidence,
            reasoning_path=reasoning,
            alternatives=[opt for i, opt in enumerate(options) if i != best_idx],
            decision_time=(datetime.now() - start_time).total_seconds(),
            state=state
        )
        
    def update_emotional_state(self,
                             valence: float,
                             arousal: float,
                             dominance: float):
        """Update emotional state values"""
        self.emotional_state = torch.tensor([valence, arousal, dominance])
        
    def _encode_context(self, context: Optional[Dict[str, Any]]) -> torch.Tensor:
        """Encode context dictionary into tensor representation"""
        if context is None:
            return torch.zeros(1, 1, 768)  # BERT hidden size
            
        context_str = json.dumps(context)
        inputs = self.tokenizer(context_str, return_tensors="pt", padding=True)
        with torch.no_grad():
            # Get base encoding
            output = self.language_model(**inputs).last_hidden_state
            # Average over sequence length
            output = torch.mean(output, dim=1, keepdim=True)
            return output
            
    def _encode_option(self, option: Any) -> torch.Tensor:
        """Encode decision option into tensor"""
        option_str = str(option)
        inputs = self.tokenizer(option_str, return_tensors="pt", padding=True)
        with torch.no_grad():
            # Get base encoding
            output = self.language_model(**inputs).last_hidden_state
            # Average over sequence length for fixed-size representation
            output = torch.mean(output, dim=1, keepdim=True)
            # Project to correct dimensionality
            output = self.context_embedding(output)
            return output
            
    def _update_memory(self, state: CognitiveState):
        """Update short and long-term memory"""
        self.short_term_memory.append(state)
        if len(self.short_term_memory) > 100:  # Keep last 100 states
            self.short_term_memory.pop(0)
            
        # Transfer to long-term memory if significant
        if state.confidence_score > self.attention_threshold:
            memory_key = f"memory_{datetime.now().timestamp()}"
            self.long_term_memory[memory_key] = {
                "state": state,
                "emotional_context": self.emotional_state.clone(),
                "timestamp": datetime.now()
            }
            
    def _generate_reasoning_path(
        self,
        state: CognitiveState,
        chosen_option: Any,
        confidence: float
    ) -> List[str]:
        """Generate explanation for decision reasoning"""
        reasoning = []
        
        # Input analysis
        reasoning.append(f"Analyzed input with confidence {state.confidence_score:.2f}")
        
        # Context consideration
        if state.context_embedding is not None:
            reasoning.append("Considered contextual information")
            
        # Emotional influence
        if abs(state.emotional_influence) > 0.1:
            influence = "positive" if state.emotional_influence > 0 else "negative"
            reasoning.append(f"Detected {influence} emotional influence")
            
        # Decision confidence
        reasoning.append(f"Selected option with {confidence:.2f} confidence")
        
        # Memory influence
        if len(self.short_term_memory) > 0:
            reasoning.append("Referenced recent experiences")
            
        if len(self.long_term_memory) > 0:
            reasoning.append("Incorporated historical knowledge")
            
        return reasoning
