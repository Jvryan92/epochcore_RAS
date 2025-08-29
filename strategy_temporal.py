from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
from torch.nn import TransformerEncoder, TransformerEncoderLayer
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import json
import networkx as nx
from collections import defaultdict


@dataclass
class TimeSeriesData:
    timestamps: np.ndarray
    values: np.ndarray
    features: List[str]
    frequency: str
    metadata: Dict[str, Any]


@dataclass
class CausalRelation:
    cause: str
    effect: str
    strength: float
    confidence: float
    lag: int
    discovered_at: datetime


@dataclass
class TemporalPrediction:
    target: str
    timestamps: np.ndarray
    predictions: np.ndarray
    confidence_intervals: np.ndarray
    model_performance: Dict[str, float]
    generated_at: datetime


class TemporalTransformer(nn.Module):
    def __init__(self, d_model: int, nhead: int, num_layers: int, dropout: float = 0.1):
        super().__init__()

        self.pos_encoder = PositionalEncoding(d_model, dropout)
        encoder_layers = TransformerEncoderLayer(d_model, nhead, d_model * 4, dropout)
        self.transformer_encoder = TransformerEncoder(encoder_layers, num_layers)
        self.decoder = nn.Linear(d_model, 1)

        self.init_weights()

    def init_weights(self):
        initrange = 0.1
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def forward(self, src, src_mask=None):
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src, src_mask)
        return self.decoder(output)


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe)

    def forward(self, x):
        x = x + self.pe[: x.size(0)]
        return self.dropout(x)


class TemporalProcessor:
    """
    Advanced temporal processing system with time-series prediction,
    causal inference, and event sequence optimization.

    Features:
    - Multi-horizon time series forecasting
    - Causal relationship discovery
    - Event sequence pattern recognition
    - Temporal anomaly detection
    - Future state simulation
    """

    def __init__(
        self,
        temporal_dir: str = ".temporal",
        d_model: int = 256,
        nhead: int = 8,
        num_layers: int = 3,
    ):
        self.temporal_dir = Path(temporal_dir)
        self.temporal_dir.mkdir(parents=True, exist_ok=True)

        self.d_model = d_model
        self.model = TemporalTransformer(d_model, nhead, num_layers)

        # Store statistics for normalization
        self.means = {}
        self.stds = {}

        # Causal network
        self.causal_graph = nx.DiGraph()
        self.causal_relations: List[CausalRelation] = []

        # Time series storage
        self.time_series_data: Dict[str, TimeSeriesData] = {}
        self.predictions: Dict[str, TemporalPrediction] = {}

        # Pattern recognition
        self.pattern_memory: Dict[str, List[np.ndarray]] = defaultdict(list)
        self.seasonality_cache: Dict[str, Dict[str, Any]] = {}

    def add_time_series(
        self,
        name: str,
        data: Union[pd.Series, np.ndarray],
        timestamps: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TimeSeriesData:
        """Add a new time series for analysis"""
        if isinstance(data, pd.Series):
            values = data.values
            timestamps = data.index.values
            frequency = pd.infer_freq(data.index)
        else:
            values = data
            if timestamps is None:
                timestamps = np.arange(len(values))
            frequency = "inferred"

        # Convert to numpy array and ensure correct shape
        values = np.asarray(values)
        if values.ndim == 1:
            values = values.reshape(-1, 1, 1)  # (seq_len, batch_size=1, feature_dim=1)

        # Store normalization parameters
        self.means[name] = np.mean(values)
        self.stds[name] = np.std(values) if np.std(values) > 0 else 1.0

        # Apply normalization while preserving shape
        normalized_values = (values - self.means[name]) / self.stds[name]

        ts_data = TimeSeriesData(
            timestamps=timestamps,
            values=normalized_values,
            features=[name],
            frequency=frequency,
            metadata=metadata
            or {"mean": float(self.means[name]), "std": float(self.stds[name])},
        )

        self.time_series_data[name] = ts_data
        return ts_data

    def forecast(
        self, series_name: str, horizon: int, num_samples: int = 100
    ) -> TemporalPrediction:
        """Generate probabilistic forecasts with uncertainty estimation"""
        if series_name not in self.time_series_data:
            raise ValueError(f"Time series '{series_name}' not found")

        ts_data = self.time_series_data[series_name]

        # Convert to torch tensor, maintaining (seq_len, batch_size=1, feature_dim=1)
        values = ts_data.values
        if values.shape[1:] != (1, 1):
            values = values.reshape(-1, 1, 1)

        x = torch.FloatTensor(values)

        # Project each feature to model dimension while maintaining batch dimension
        batch_size = x.size(1)
        proj = nn.Linear(1, self.d_model)

        # Combine batch and sequence dimensions for projection
        x = x.view(-1, 1)  # Reshape to (seq_len*batch_size, feature_dim)
        x = proj(x)  # Project to (seq_len*batch_size, d_model)

        # Restore sequence and batch dimensions
        x = x.view(
            -1, batch_size, self.d_model
        )  # Shape: (seq_len, batch_size, d_model)

        # Generate multiple forecast samples
        predictions = []
        self.model.eval()
        with torch.no_grad():
            for _ in range(num_samples):
                output = self.model(x)
                predictions.append(output[-horizon:].numpy())

        predictions = np.array(predictions)
        mean_pred = np.mean(predictions, axis=0)
        confidence_intervals = np.percentile(predictions, [5, 95], axis=0)

        # Calculate future timestamps
        last_timestamp = ts_data.timestamps[-1]
        if isinstance(last_timestamp, (np.datetime64, datetime)):
            if isinstance(last_timestamp, datetime):
                last_timestamp = np.datetime64(last_timestamp)
            # Parse frequency string into pandas frequency
            freq_num = "1"  # Default to 1 if no number specified
            freq_unit = ts_data.frequency
            if freq_unit[0].isdigit():
                for i, c in enumerate(freq_unit):
                    if not c.isdigit():
                        freq_num = freq_unit[:i]
                        freq_unit = freq_unit[i:]
                        break
            freq = pd.Timedelta(f"{freq_num}{freq_unit}")
            future_timestamps = pd.date_range(
                start=last_timestamp, periods=horizon + 1, freq=freq
            )[1:].values
        else:
            future_timestamps = np.arange(
                int(last_timestamp) + 1, int(last_timestamp) + horizon + 1
            )

        # Inverse transform predictions back to original scale
        mean_pred_orig = mean_pred * self.stds[series_name] + self.means[series_name]

        # Calculate model performance metrics using un-normalized values
        values_orig = ts_data.values * self.stds[series_name] + self.means[series_name]
        performance = self._calculate_model_performance(values_orig, mean_pred_orig)
        conf_intervals_orig = (
            confidence_intervals * self.stds[series_name] + self.means[series_name]
        )

        prediction = TemporalPrediction(
            target=series_name,
            timestamps=future_timestamps,
            predictions=mean_pred_orig,
            confidence_intervals=conf_intervals_orig,
            model_performance=performance,
            generated_at=datetime.now(),
        )

        self.predictions[series_name] = prediction
        return prediction

    def discover_causal_relations(
        self,
        series_names: List[str],
        max_lag: int = 10,
        significance_threshold: float = 0.05,
    ) -> List[CausalRelation]:
        """Discover causal relationships between time series"""
        relations = []

        for cause in series_names:
            for effect in series_names:
                if cause != effect:
                    cause_data = self.time_series_data[cause].values
                    effect_data = self.time_series_data[effect].values

                    # Calculate Granger causality for different lags
                    for lag in range(1, max_lag + 1):
                        f_stat, p_value = self._granger_causality(
                            cause_data, effect_data, lag
                        )

                        if p_value < significance_threshold:
                            relation = CausalRelation(
                                cause=cause,
                                effect=effect,
                                strength=f_stat,
                                confidence=1 - p_value,
                                lag=lag,
                                discovered_at=datetime.now(),
                            )
                            relations.append(relation)

                            # Update causal graph
                            self.causal_graph.add_edge(
                                cause, effect, weight=f_stat, lag=lag
                            )

        self.causal_relations.extend(relations)
        return relations

    def detect_temporal_patterns(
        self, series_name: str, pattern_length: int = 24
    ) -> Dict[str, Any]:
        """Detect and analyze temporal patterns"""
        if series_name not in self.time_series_data:
            raise ValueError(f"Time series '{series_name}' not found")

        ts_data = self.time_series_data[series_name]
        values = ts_data.values

        # Extract subsequences
        subsequences = [
            values[i : i + pattern_length]
            for i in range(len(values) - pattern_length + 1)
        ]

        # Cluster similar patterns
        patterns = np.array(subsequences)
        self.pattern_memory[series_name].extend(patterns)

        # Detect seasonality
        seasonality = self._detect_seasonality(values)
        self.seasonality_cache[series_name] = seasonality

        return {
            "num_patterns": len(patterns),
            "seasonality": seasonality,
            "typical_length": pattern_length,
            "timestamp": datetime.now().isoformat(),
        }

    def simulate_future_state(
        self, initial_state: Dict[str, float], steps: int = 10
    ) -> Dict[str, np.ndarray]:
        """Simulate future states using causal relationships"""
        state_history = defaultdict(list)
        current_state = initial_state.copy()

        for _ in range(steps):
            # Update each variable based on causal relationships
            new_state = current_state.copy()

            for node in self.causal_graph.nodes():
                if node in current_state:
                    # Get all causal influences
                    influences = []
                    for pred in self.causal_graph.predecessors(node):
                        if pred in current_state:
                            edge_data = self.causal_graph.get_edge_data(pred, node)
                            weight = edge_data["weight"]
                            influences.append(current_state[pred] * weight)

                    if influences:
                        new_state[node] = np.mean(influences)

            # Store state
            for var, value in new_state.items():
                state_history[var].append(value)

            current_state = new_state

        return {var: np.array(values) for var, values in state_history.items()}

    def get_temporal_metrics(self) -> Dict[str, Any]:
        """Get metrics about temporal processing"""
        return {
            "num_time_series": len(self.time_series_data),
            "num_causal_relations": len(self.causal_relations),
            "causal_graph_density": nx.density(self.causal_graph),
            "pattern_memory_size": sum(
                len(patterns) for patterns in self.pattern_memory.values()
            ),
            "prediction_accuracy": {
                name: pred.model_performance for name, pred in self.predictions.items()
            },
        }

    def _calculate_model_performance(
        self, actual: np.ndarray, predicted: np.ndarray
    ) -> Dict[str, float]:
        """Calculate model performance metrics"""
        # Take just the last parts of the actual sequence that correspond to predicted values
        actual_horizon = actual[-len(predicted) :].reshape(-1)  # Flatten to 1D
        predicted_flat = predicted.reshape(-1)  # Flatten to 1D

        # Calculate metrics
        mse = np.mean((actual_horizon - predicted_flat) ** 2)
        mae = np.mean(np.abs(actual_horizon - predicted_flat))

        return {"mse": float(mse), "mae": float(mae), "rmse": float(np.sqrt(mse))}

    def _granger_causality(
        self, cause: np.ndarray, effect: np.ndarray, lag: int
    ) -> Tuple[float, float]:
        """Calculate Granger causality F-statistic and p-value"""
        # Simplified Granger causality test
        # In practice, you would use a proper statistical package
        from scipy import stats

        # Prepare lagged data
        X = np.column_stack([np.roll(cause, i) for i in range(lag)])[lag:, :]

        y = effect[lag:]

        # Fit restricted and unrestricted models
        restricted = np.mean(y)
        unrestricted = np.mean(X.dot(np.linalg.pinv(X).dot(y)))

        # Calculate F-statistic
        n = len(y)
        rss_restricted = np.sum((y - restricted) ** 2)
        rss_unrestricted = np.sum((y - unrestricted) ** 2)

        f_stat = ((rss_restricted - rss_unrestricted) / lag) / (
            rss_unrestricted / (n - lag)
        )
        p_value = 1 - stats.f.cdf(f_stat, lag, n - lag)

        return f_stat, p_value

    def _detect_seasonality(self, values: np.ndarray) -> Dict[str, Any]:
        """Detect seasonality patterns in time series"""
        from scipy import signal

        # Calculate periodogram
        freqs, power = signal.periodogram(values)

        # Find dominant frequencies
        peak_indices = signal.find_peaks(power)[0]
        dominant_freqs = freqs[peak_indices]
        dominant_powers = power[peak_indices]

        # Sort by power
        sorted_indices = np.argsort(dominant_powers)[::-1]
        dominant_freqs = dominant_freqs[sorted_indices]
        dominant_powers = dominant_powers[sorted_indices]

        return {
            "frequencies": dominant_freqs[:3].tolist(),
            "powers": dominant_powers[:3].tolist(),
            "strongest_period": (
                1 / dominant_freqs[0] if len(dominant_freqs) > 0 else None
            ),
        }
