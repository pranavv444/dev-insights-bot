from typing import Dict, Any, List
from datetime import datetime
from src.agents.base import BaseAgent
from src.visualization.charts import ChartGenerator
from src.storage.database import DatabaseManager
import base64

class InsightNarratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("InsightNarrator")
        self.chart_generator = ChartGenerator()
        self.db = DatabaseManager()
        
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate narrative insights and visualizations"""
        try:
            metrics = state.get("metrics", {})
            anomalies = state.get("anomalies", [])
            code_analysis = state.get("code_analysis", "")
            
            # Generate narrative
            narrative_prompt = self._create_narrative_prompt(
                metrics, anomalies, code_analysis, state.get("time_range", "weekly")
            )
            
            narrative = self.llm.invoke(narrative_prompt)
            
            # Log conversation
            self.log_conversation(narrative_prompt, narrative)
            self.db.save_conversation(self.name, narrative_prompt, narrative)
            
            # Generate charts
            charts = self._generate_charts(metrics)
            
            # Save metrics to database
            self.db.save_metrics(metrics, state.get("time_range", "weekly"))
            
            # Update state
            state["narrative"] = narrative
            state["charts"] = charts
            state["summary"] = self._create_executive_summary(metrics, anomalies)
            
        except Exception as e:
            state["errors"].append(f"Insight generation error: {str(e)}")
            self.logger.error(f"Error in insight generation: {e}")
            
        return state
    
    def _create_narrative_prompt(self, metrics: Dict, anomalies: List, 
                                code_analysis: str, time_range: str) -> str:
        """Create prompt for narrative generation"""
        team_metrics = metrics.get('team_metrics', {})
        dora_metrics = metrics.get('dora_metrics', {})
        
        return f"""
        Generate an actionable insight narrative for the {time_range} engineering performance report.
        
        Context from Diff Analyst:
        {code_analysis}
        
        Key Metrics:
        - Total Commits: {team_metrics.get('total_commits', 0)}
        - Deployment Frequency: {dora_metrics.get('deployment_frequency', 0)}
        - Average Lead Time: {dora_metrics.get('lead_time_hours', 0):.1f} hours
        - Code Churn: {team_metrics.get('code_churn', 0)} lines
        - Active Developers: {len(metrics.get('developer_metrics', {}))}
        
        Anomalies Detected: {len(anomalies)}
        
        Please provide:
        1. Executive summary (2-3 sentences)
        2. Key achievements and concerns
        3. Specific recommendations for improvement
        4. Risk areas that need attention
        Keep the narrative concise, actionable, and focused on business value.
        Use clear language suitable for engineering leadership.
        """
    
    def _generate_charts(self, metrics: Dict) -> List[Dict[str, Any]]:
        """Generate visualization charts"""
        charts = []
        
        try:
            # Developer activity chart
            if metrics.get('developer_metrics'):
                dev_chart = self.chart_generator.create_developer_activity_chart(
                    metrics['developer_metrics']
                )
                charts.append({
                    'type': 'developer_activity',
                    'data': base64.b64encode(dev_chart).decode('utf-8'),
                    'title': 'Developer Activity Overview'
                })
            
            # Code health chart
            if metrics.get('team_metrics'):
                health_chart = self.chart_generator.create_code_health_chart(
                    metrics['team_metrics']
                )
                charts.append({
                    'type': 'code_health',
                    'data': base64.b64encode(health_chart).decode('utf-8'),
                    'title': 'Code Health Score'
                })
            
            # Historical trend chart (if available)
            historical = self.db.session.query(DatabaseManager.MetricsSnapshot).all()
            if len(historical) > 1:
                trend_data = [{
                    'timestamp': h.timestamp,
                    'deployment_frequency': h.deployment_frequency,
                    'lead_time_hours': h.lead_time_hours
                } for h in historical[-10:]]  
                
                trend_chart = self.chart_generator.create_trend_chart(trend_data)
                charts.append({
                    'type': 'trends',
                    'data': base64.b64encode(trend_chart).decode('utf-8'),
                    'title': 'Performance Trends'
                })
                
        except Exception as e:
            self.logger.error(f"Chart generation error: {e}")
            
        return charts
    
    def _create_executive_summary(self, metrics: Dict, anomalies: List) -> str:
        """Create a brief executive summary"""
        team_metrics = metrics.get('team_metrics', {})
        risk_level = "High" if len(anomalies) > 5 else "Medium" if len(anomalies) > 2 else "Low"
        
        return (
            f"Team delivered {team_metrics.get('total_commits', 0)} commits with "
            f"{team_metrics.get('merged_prs', 0)} merged PRs. "
            f"Code health risk level: {risk_level}. "
            f"Average cycle time: {metrics.get('dora_metrics', {}).get('lead_time_hours', 0):.1f} hours."
        )