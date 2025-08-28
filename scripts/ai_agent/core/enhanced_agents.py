"""Enhanced multi-agent system with ML, visualization, and testing capabilities."""

from typing import Dict, Any, List, Optional, Type, Tuple
from dataclasses import dataclass
import asyncio
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from datetime import datetime
import yfinance as yf
import pytest
from enum import Enum


class AgentType(Enum):
    """Extended agent types with new specialized roles."""
    
    ANALYST = "analyst"
    STRATEGIST = "strategist"
    RISK_MANAGER = "risk"
    TAX_ADVISOR = "tax"
    MONITOR = "monitor"
    COORDINATOR = "coordinator"
    COMPLIANCE = "compliance"
    RESEARCH = "research"
    ML_OPTIMIZER = "ml_optimizer"
    MARKET_DATA = "market_data"
    VISUALIZATION = "visualization"


class MLCapability(Enum):
    """Machine learning capabilities for agents."""
    
    PREDICTION = "prediction"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    OPTIMIZATION = "optimization"


@dataclass
class MarketData:
    """Real-time market data structure."""
    
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    bid: float
    ask: float
    high: float
    low: float
    indicators: Dict[str, float]


class AgentNetwork:
    """Visualization and analysis of agent interactions."""

    def __init__(self):
        """Initialize agent network."""
        self.G = nx.DiGraph()
        self.message_counts = {}
        self.interaction_history = []

    def add_interaction(
        self,
        sender: AgentType,
        receiver: AgentType,
        message_type: str
    ):
        """Add interaction to network.
        
        Args:
            sender: Sending agent type
            receiver: Receiving agent type
            message_type: Type of message
        """
        edge_key = (sender.value, receiver.value)
        self.G.add_edge(sender.value, receiver.value)
        
        if edge_key not in self.message_counts:
            self.message_counts[edge_key] = {}
        if message_type not in self.message_counts[edge_key]:
            self.message_counts[edge_key][message_type] = 0
            
        self.message_counts[edge_key][message_type] += 1
        
        self.interaction_history.append({
            "timestamp": datetime.now(),
            "sender": sender.value,
            "receiver": receiver.value,
            "type": message_type
        })

    def visualize_network(self) -> str:
        """Generate network visualization.
        
        Returns:
            Base64 encoded PNG image
        """
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.G)
        
        # Draw nodes with different colors for different agent types
        colors = [
            "skyblue" if "analyst" in node else
            "lightgreen" if "strategist" in node else
            "salmon" if "risk" in node else
            "orange" if "tax" in node else
            "purple" if "monitor" in node else
            "yellow" for node in self.G.nodes()
        ]
        
        nx.draw(
            self.G, pos,
            with_labels=True,
            node_color=colors,
            node_size=2000,
            font_size=10,
            font_weight="bold",
            arrows=True,
            edge_color="gray",
            arrowsize=20
        )
        
        # Add edge labels with message counts
        edge_labels = {
            (s, r): sum(counts.values())
            for (s, r), counts in self.message_counts.items()
        }
        nx.draw_networkx_edge_labels(
            self.G, pos,
            edge_labels=edge_labels
        )
        
        plt.title("Agent Interaction Network")
        
        # Save to bytes
        import io
        import base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode()

    def generate_interaction_report(self) -> Dict[str, Any]:
        """Generate detailed interaction report.
        
        Returns:
            Dictionary containing interaction statistics
        """
        return {
            "total_interactions": len(self.interaction_history),
            "agent_activity": self._get_agent_activity(),
            "message_types": self._get_message_type_stats(),
            "busiest_paths": self._get_busiest_paths(),
            "temporal_analysis": self._get_temporal_analysis()
        }

    def _get_agent_activity(self) -> Dict[str, Dict[str, int]]:
        """Analyze agent activity levels."""
        activity = {}
        for agent in AgentType:
            sent = sum(
                1 for i in self.interaction_history
                if i["sender"] == agent.value
            )
            received = sum(
                1 for i in self.interaction_history
                if i["receiver"] == agent.value
            )
            activity[agent.value] = {
                "sent": sent,
                "received": received,
                "total": sent + received
            }
        return activity

    def _get_message_type_stats(self) -> Dict[str, int]:
        """Analyze message type frequencies."""
        return {
            msg_type: sum(
                1 for i in self.interaction_history
                if i["type"] == msg_type
            )
            for msg_type in set(i["type"] for i in self.interaction_history)
        }

    def _get_busiest_paths(self) -> List[Dict[str, Any]]:
        """Identify busiest communication paths."""
        path_counts = {}
        for i in self.interaction_history:
            path = (i["sender"], i["receiver"])
            if path not in path_counts:
                path_counts[path] = 0
            path_counts[path] += 1
            
        return sorted(
            [
                {
                    "sender": s,
                    "receiver": r,
                    "count": c
                }
                for (s, r), c in path_counts.items()
            ],
            key=lambda x: x["count"],
            reverse=True
        )[:5]

    def _get_temporal_analysis(self) -> Dict[str, Any]:
        """Analyze temporal patterns in interactions."""
        timestamps = [i["timestamp"] for i in self.interaction_history]
        if not timestamps:
            return {}
            
        return {
            "start_time": min(timestamps),
            "end_time": max(timestamps),
            "duration": str(max(timestamps) - min(timestamps)),
            "peak_hour": max(
                pd.DataFrame(timestamps)
                .groupby(lambda x: timestamps[x].hour)
                .size()
                .items(),
                key=lambda x: x[1]
            )[0]
        }


class MLAgent:
    """Machine learning capabilities for agents."""

    def __init__(self, capability: MLCapability):
        """Initialize ML agent.
        
        Args:
            capability: Type of ML capability
        """
        self.capability = capability
        self.models = {}
        self.scalers = {}
        self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models based on capability."""
        if self.capability == MLCapability.PREDICTION:
            self.models["price"] = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            self.models["volume"] = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            
        elif self.capability == MLCapability.CLASSIFICATION:
            self.models["trend"] = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
            
        self.scalers = {
            name: StandardScaler()
            for name in self.models.keys()
        }

    def train(
        self,
        data: pd.DataFrame,
        target_col: str,
        feature_cols: List[str]
    ):
        """Train ML model.
        
        Args:
            data: Training data
            target_col: Target column name
            feature_cols: Feature column names
        """
        if target_col not in self.models:
            raise ValueError(f"No model initialized for {target_col}")
            
        X = data[feature_cols]
        y = data[target_col]
        
        # Scale features
        X_scaled = self.scalers[target_col].fit_transform(X)
        
        # Train model
        self.models[target_col].fit(X_scaled, y)

    def predict(
        self,
        data: pd.DataFrame,
        target_col: str,
        feature_cols: List[str]
    ) -> np.ndarray:
        """Make predictions.
        
        Args:
            data: Input data
            target_col: Target column name
            feature_cols: Feature column names
            
        Returns:
            Predictions
        """
        if target_col not in self.models:
            raise ValueError(f"No model initialized for {target_col}")
            
        X = data[feature_cols]
        X_scaled = self.scalers[target_col].transform(X)
        
        return self.models[target_col].predict(X_scaled)


class MarketDataFeed:
    """Real-time market data handler."""

    def __init__(self):
        """Initialize market data feed."""
        self.subscriptions = {}
        self.data_cache = {}
        self.running = False

    async def subscribe(self, symbol: str):
        """Subscribe to market data for a symbol.
        
        Args:
            symbol: Stock symbol
        """
        if symbol not in self.subscriptions:
            self.subscriptions[symbol] = yf.Ticker(symbol)
            self.data_cache[symbol] = []

    async def start(self):
        """Start market data feed."""
        self.running = True
        while self.running:
            await self._update_data()
            await asyncio.sleep(1)  # 1-second update interval

    async def stop(self):
        """Stop market data feed."""
        self.running = False

    async def _update_data(self):
        """Update market data for all subscriptions."""
        for symbol, ticker in self.subscriptions.items():
            try:
                data = ticker.history(period="1m")
                if not data.empty:
                    latest = data.iloc[-1]
                    market_data = MarketData(
                        symbol=symbol,
                        price=latest["Close"],
                        volume=latest["Volume"],
                        timestamp=latest.name,
                        bid=latest["Close"] - 0.01,  # Simplified
                        ask=latest["Close"] + 0.01,  # Simplified
                        high=latest["High"],
                        low=latest["Low"],
                        indicators={
                            "sma_20": data["Close"].rolling(20).mean().iloc[-1],
                            "rsi_14": self._calculate_rsi(data["Close"], 14)
                        }
                    )
                    self.data_cache[symbol].append(market_data)
                    
                    # Keep last 1000 data points
                    if len(self.data_cache[symbol]) > 1000:
                        self.data_cache[symbol].pop(0)
                        
            except Exception as e:
                logging.error(f"Error updating {symbol}: {e}")

    def _calculate_rsi(
        self,
        prices: pd.Series,
        period: int = 14
    ) -> float:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]


@pytest.fixture
def agent_network():
    """Fixture for testing agent network."""
    return AgentNetwork()


@pytest.fixture
def ml_agent():
    """Fixture for testing ML agent."""
    return MLAgent(MLCapability.PREDICTION)


@pytest.fixture
def market_data_feed():
    """Fixture for testing market data feed."""
    return MarketDataFeed()


def test_agent_network_visualization(agent_network):
    """Test agent network visualization."""
    # Add some test interactions
    agent_network.add_interaction(
        AgentType.ANALYST,
        AgentType.STRATEGIST,
        "analysis"
    )
    agent_network.add_interaction(
        AgentType.STRATEGIST,
        AgentType.RISK_MANAGER,
        "strategy"
    )
    
    # Generate visualization
    viz = agent_network.visualize_network()
    assert viz is not None
    assert isinstance(viz, str)


def test_ml_agent_training(ml_agent):
    """Test ML agent training."""
    # Create test data
    data = pd.DataFrame({
        "price": np.random.random(100),
        "volume": np.random.random(100),
        "feature1": np.random.random(100),
        "feature2": np.random.random(100)
    })
    
    # Train model
    ml_agent.train(
        data,
        "price",
        ["feature1", "feature2"]
    )
    
    # Make predictions
    preds = ml_agent.predict(
        data,
        "price",
        ["feature1", "feature2"]
    )
    
    assert len(preds) == len(data)


@pytest.mark.asyncio
async def test_market_data_feed(market_data_feed):
    """Test market data feed."""
    # Subscribe to a symbol
    await market_data_feed.subscribe("AAPL")
    
    # Start feed
    feed_task = asyncio.create_task(market_data_feed.start())
    
    # Wait for some data
    await asyncio.sleep(5)
    
    # Stop feed
    await market_data_feed.stop()
    await feed_task
    
    # Check data
    assert "AAPL" in market_data_feed.data_cache
    assert len(market_data_feed.data_cache["AAPL"]) > 0
