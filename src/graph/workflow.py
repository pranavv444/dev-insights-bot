from typing import Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.agents.dataharvester import DataHarvesterAgent
from src.agents.diffanalyst import DiffAnalystAgent
from src.agents.insightnarrator import InsightNarratorAgent
from src.metrics.calculator import MetricsCalculator

class DevInsightsWorkflow:
    def __init__(self):
        self.harvester = DataHarvesterAgent()
        self.analyst = DiffAnalystAgent()
        self.narrator = InsightNarratorAgent()
        self.metrics_calc = MetricsCalculator()
        
        # Build workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("harvest_data", self.harvester.process)
        workflow.add_node("analyze_diffs", self._enhanced_analysis)
        workflow.add_node("generate_insights", self.narrator.process)
        
        # Add edges
        workflow.add_edge("harvest_data", "analyze_diffs")
        workflow.add_edge("analyze_diffs", "generate_insights")
        workflow.add_edge("generate_insights", END)
        
        # Set entry point
        workflow.set_entry_point("harvest_data")
        
        return workflow.compile()
    
    def _enhanced_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced analysis with metrics calculation"""
        # First run diff analyst
        state = self.analyst.process(state)
        
        # Enhance with additional metrics calculations
        commits = state.get("commits", [])
        prs = state.get("pull_requests", [])
        
        # Calculate additional metrics
        dora_metrics = self.metrics_calc.calculate_dora_metrics(commits, prs)
        code_health = self.metrics_calc.calculate_code_health_metrics(commits)
        
        # Merge with existing metrics
        if "metrics" in state:
            state["metrics"]["dora_metrics"] = dora_metrics
            state["metrics"]["code_health"] = code_health
        
        return state
    
    def run(self, command: str, time_range: str = "weekly", 
            target_user: str = None) -> Dict[str, Any]:
        """Execute the workflow"""
        initial_state = {
            "command": command,
            "time_range": time_range,
            "target_user": target_user,
            "timestamp": datetime.now()
        }
        
        return self.workflow.invoke(initial_state)