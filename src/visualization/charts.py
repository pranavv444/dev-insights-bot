import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any
import io
import base64

class ChartGenerator:
    """Generate charts for metrics visualization"""
    
    @staticmethod
    def create_developer_activity_chart(dev_metrics: Dict[str, Dict]) -> bytes:
        """Create bar chart of developer activity"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Commits by Developer", "Code Changes by Developer")
        )
        
        developers = list(dev_metrics.keys())
        commits = [dev_metrics[dev]['commits'] for dev in developers]
        changes = [dev_metrics[dev]['additions'] + dev_metrics[dev]['deletions'] for dev in developers]
        
        # Commits bar chart
        fig.add_trace(
            go.Bar(x=developers, y=commits, name="Commits", marker_color='lightblue'),
            row=1, col=1
        )
        
        # Code changes bar chart
        fig.add_trace(
            go.Bar(x=developers, y=changes, name="Lines Changed", marker_color='lightgreen'),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False, title_text="Developer Activity")
        
        # Convert to PNG bytes
        return fig.to_image(format="png")
    
    @staticmethod
    def create_code_health_chart(metrics: Dict[str, Any]) -> bytes:
        """Create code health visualization"""
        fig = go.Figure()
        
        # Create gauge chart for code health score
        churn_rate = metrics.get('churn_rate', 0)
        health_score = max(0, 100 - (churn_rate * 10))  # Simple health score
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Code Health Score"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        return fig.to_image(format="png")
    
    @staticmethod
    def create_trend_chart(historical_data: List[Dict]) -> bytes:
        """Create trend chart for metrics over time"""
        if not historical_data:
            return ChartGenerator._create_empty_chart()
        
        df = pd.DataFrame(historical_data)
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Deployment Frequency Trend", "Lead Time Trend"),
            vertical_spacing=0.15
        )
        
        # Deployment frequency
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['deployment_frequency'],
                mode='lines+markers',
                name='Deployments',
                line=dict(color='green', width=2)
            ),
            row=1, col=1
        )
        
        # Lead time
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['lead_time_hours'],
                mode='lines+markers',
                name='Lead Time (hours)',
                line=dict(color='orange', width=2)
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=500, showlegend=False)
        return fig.to_image(format="png")
    
    @staticmethod
    def _create_empty_chart() -> bytes:
        """Create placeholder chart when no data available"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return buf.getvalue()