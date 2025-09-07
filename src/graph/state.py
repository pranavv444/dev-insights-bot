from typing import List, Dict, Any, Optional
from datetime import datetime
from langgraph.graph import GraphState

class AgentState(GraphState):
    # Input context
    command: str = ""
    time_range: str = "weekly"  # daily, weekly, monthly
    target_user: Optional[str] = None
    
    # GitHub data
    commits: List[Dict[str, Any]] = []
    pull_requests: List[Dict[str, Any]] = []
    code_changes: Dict[str, Any] = {}
    
    # Analyzed metrics
    metrics: Dict[str, Any] = {}
    anomalies: List[Dict[str, Any]] = []
    
    # Generated insights
    narrative: str = ""
    charts: List[Dict[str, Any]] = []
    
    # Metadata
    timestamp: datetime = datetime.now()
    errors: List[str] = []