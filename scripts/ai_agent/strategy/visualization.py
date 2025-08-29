"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""Investment strategy visualization and analysis tools."""

from typing import Dict, Any, List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from decimal import Decimal
import io
import base64

class InvestmentVisualizer:
    """Generate visualizations for investment strategies."""

    def __init__(self):
        """Initialize visualizer with style settings."""
        # Set style for all plots
        plt.style.use('seaborn')
        sns.set_palette("husl")
        
    def _prepare_data(self, recommendations: List[Dict]) -> pd.DataFrame:
        """Convert recommendations to DataFrame for analysis."""
        df = pd.DataFrame(recommendations)
        
        # Convert string amounts to float
        df['initial_investment'] = df['initial_investment'].apply(
            lambda x: float(x)
        )
        df['expected_outcome'] = df['expected_outcome'].apply(
            lambda x: float(x)
        )
        
        # Extract growth rate percentage
        df['growth_rate'] = df['growth_rate'].apply(
            lambda x: float(x.strip('%'))
        )
        
        return df

    def create_growth_comparison(self, recommendations: List[Dict]) -> str:
        """Create growth comparison visualization.
        
        Returns:
            Base64 encoded PNG image
        """
        df = self._prepare_data(recommendations)
        
        # Create figure with multiple subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Initial vs Expected Returns
        ax1.bar(df['level'], df['initial_investment'], 
                label='Initial Investment', alpha=0.6)
        ax1.bar(df['level'], df['expected_outcome'], 
                label='Expected Outcome', alpha=0.6)
        ax1.set_title('Initial Investment vs Expected Outcome')
        ax1.set_xlabel('Strategy Level')
        ax1.set_ylabel('Amount ($)')
        ax1.legend()
        ax1.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f'${x:,.0f}')
        )
        
        # 2. Growth Rates
        ax2.plot(df['level'], df['growth_rate'], 
                marker='o', linewidth=2, markersize=8)
        ax2.set_title('Growth Rate Progression')
        ax2.set_xlabel('Strategy Level')
        ax2.set_ylabel('Growth Rate (%)')
        ax2.grid(True)
        
        # 3. Risk-Return Profile
        sns.scatterplot(data=df, x='growth_rate', y='expected_outcome',
                       size='initial_investment', hue='risk_level',
                       ax=ax3)
        ax3.set_title('Risk-Return Profile')
        ax3.set_xlabel('Growth Rate (%)')
        ax3.set_ylabel('Expected Outcome ($)')
        
        # 4. Time Horizon Analysis
        ax4.plot(df['time_horizon'], df['expected_outcome'], 
                marker='s', linewidth=2)
        ax4.set_title('Time Horizon vs Expected Outcome')
        ax4.set_xlabel('Time Horizon (Years)')
        ax4.set_ylabel('Expected Outcome ($)')
        ax4.grid(True)
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode()

    def create_risk_analysis(self, recommendations: List[Dict]) -> str:
        """Create risk analysis visualization.
        
        Returns:
            Base64 encoded PNG image
        """
        df = self._prepare_data(recommendations)
        
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 1. Risk Level Distribution
        risk_counts = df['risk_level'].value_counts()
        ax1.pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%',
                startangle=90)
        ax1.set_title('Risk Level Distribution')
        
        # 2. Risk-Adjusted Returns
        # Calculate Sharpe-like ratio (simplified)
        df['risk_adjusted_return'] = df['expected_outcome'] / df['growth_rate']
        ax2.bar(df['level'], df['risk_adjusted_return'])
        ax2.set_title('Risk-Adjusted Returns by Strategy Level')
        ax2.set_xlabel('Strategy Level')
        ax2.set_ylabel('Risk-Adjusted Return')
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode()

    def create_correlation_matrix(self, recommendations: List[Dict]) -> str:
        """Create correlation matrix visualization.
        
        Returns:
            Base64 encoded PNG image
        """
        df = self._prepare_data(recommendations)
        
        # Select numerical columns
        numerical_cols = ['level', 'initial_investment', 'growth_rate',
                         'time_horizon', 'expected_outcome']
        correlation_matrix = df[numerical_cols].corr()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', 
                   vmin=-1, vmax=1, center=0)
        plt.title('Correlation Matrix of Strategy Metrics')
        
        # Convert plot to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode()

    def generate_report(self, recommendations: List[Dict]) -> Dict[str, str]:
        """Generate comprehensive visual report.
        
        Returns:
            Dictionary with base64 encoded PNG images
        """
        return {
            "growth_comparison": self.create_growth_comparison(recommendations),
            "risk_analysis": self.create_risk_analysis(recommendations),
            "correlation_matrix": self.create_correlation_matrix(recommendations)
        }
