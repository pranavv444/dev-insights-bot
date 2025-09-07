# src/agents/diff_analyst.py
from typing import Dict, Any, List
from collections import defaultdict
import numpy as np
from src.agents.base import BaseAgent

class DiffAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__("DiffAnalyst")
        
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code changes and detect patterns"""
        try:
            commits = state.get("commits", [])
            prs = state.get("pull_requests", [])
            
            # Calculate metrics
            metrics = self._calculate_metrics(commits, prs)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(commits, metrics)
            
            # Generate analysis prompt for LLM
            analysis_prompt = self._create_analysis_prompt(metrics, anomalies)
            
            # Get LLM insights on the patterns
            llm_analysis = self.llm.invoke(analysis_prompt)
            
            # Update state
            state["metrics"] = metrics
            state["anomalies"] = anomalies
            state["code_analysis"] = llm_analysis
            
            self.log_conversation(analysis_prompt, llm_analysis)
            
        except Exception as e:
            state["errors"].append(f"Diff analysis error: {str(e)}")
            self.logger.error(f"Error in diff analysis: {e}")
            
        return state
    
    def _calculate_metrics(self, commits: List[Dict], prs: List[Dict]) -> Dict[str, Any]:
        """Calculate DORA and churn metrics"""
        
        # Developer metrics
        dev_metrics = defaultdict(lambda: {
            "commits": 0,
            "additions": 0,
            "deletions": 0,
            "files_touched": 0,
            "prs_created": 0,
            "prs_merged": 0
        })
        
        # Aggregate commit data
        for commit in commits:
            author = commit.get("author", "unknown")
            dev_metrics[author]["commits"] += 1
            dev_metrics[author]["additions"] += commit.get("additions", 0)
            dev_metrics[author]["deletions"] += commit.get("deletions", 0)
            dev_metrics[author]["files_touched"] += commit.get("files", 0)
        
        # Aggregate PR data
        merged_prs = [pr for pr in prs if pr.get("merged_at")]
        
        for pr in prs:
            author = pr.get("author", "unknown")
            dev_metrics[author]["prs_created"] += 1
            if pr.get("merged_at"):
                dev_metrics[author]["prs_merged"] += 1
        
        # Calculate team-level metrics
        total_commits = len(commits)
        total_additions = sum(c.get("additions", 0) for c in commits)
        total_deletions = sum(c.get("deletions", 0) for c in commits)
        
        # Calculate cycle time for merged PRs
        cycle_times = []
        for pr in merged_prs:
            created = pr.get("created_at")
            merged = pr.get("merged_at")
            if created and merged:
                cycle_time = (merged - created).total_seconds() / 3600  # hours
                cycle_times.append(cycle_time)
        
        avg_cycle_time = np.mean(cycle_times) if cycle_times else 0
        
        # Code churn calculation
        code_churn = total_additions + total_deletions
        churn_rate = code_churn / total_commits if total_commits > 0 else 0
        
        return {
            "developer_metrics": dict(dev_metrics),
            "team_metrics": {
                "total_commits": total_commits,
                "total_prs": len(prs),
                "merged_prs": len(merged_prs),
                "total_additions": total_additions,
                "total_deletions": total_deletions,
                "code_churn": code_churn,
                "churn_rate": churn_rate,
                "avg_cycle_time_hours": avg_cycle_time,
                "deployment_frequency": len(merged_prs),  # Simplified for MVP
            },
            "dora_metrics": {
                "deployment_frequency": len(merged_prs),
                "lead_time_hours": avg_cycle_time,
                "change_failure_rate": 0,  # Would need CI/CD data
                "mttr_hours": 0  # Would need incident data
            }
        }
    
    def _detect_anomalies(self, commits: List[Dict], metrics: Dict) -> List[Dict]:
        """Detect unusual patterns in code changes"""
        anomalies = []
        
        # High churn detection
        churn_values = [c.get("additions", 0) + c.get("deletions", 0) for c in commits]
        if churn_values:
            mean_churn = np.mean(churn_values)
            std_churn = np.std(churn_values)
            threshold = mean_churn + 2 * std_churn  # 2 standard deviations
            
            for commit in commits:
                churn = commit.get("additions", 0) + commit.get("deletions", 0)
                if churn > threshold:
                    anomalies.append({
                        "type": "high_churn",
                        "commit": commit.get("sha", "")[:7],
                        "author": commit.get("author", "unknown"),
                        "churn": churn,
                        "message": f"High code churn detected: {churn} lines changed",
                        "risk_level": "high"
                    })
        
        # Large file changes
        for commit in commits:
            if commit.get("files", 0) > 20:
                anomalies.append({
                    "type": "many_files_changed",
                    "commit": commit.get("sha", "")[:7],
                    "author": commit.get("author", "unknown"),
                    "files": commit.get("files", 0),
                    "message": f"Many files changed in single commit: {commit.get('files', 0)} files",
                    "risk_level": "medium"
                })
        
        return anomalies
    
    def _create_analysis_prompt(self, metrics: Dict, anomalies: List[Dict]) -> str:
        """Create prompt for LLM analysis"""
        return f"""
        Analyze the following code metrics and provide insights:
        
        Team Metrics:
        - Total commits: {metrics['team_metrics']['total_commits']}
        - Code churn: {metrics['team_metrics']['code_churn']} lines
        - Average cycle time: {metrics['team_metrics']['avg_cycle_time_hours']:.1f} hours
        - Deployment frequency: {metrics['team_metrics']['deployment_frequency']} deployments
        
        Anomalies detected: {len(anomalies)}
        {self._format_anomalies(anomalies)}
        
        Provide:
        1. Key patterns in the code changes
        2. Risk assessment based on code churn
        3. Recommendations for improving development practices
        
        Keep the analysis concise and actionable.
        """
    
    def _format_anomalies(self, anomalies: List[Dict]) -> str:
        """Format anomalies for prompt"""
        if not anomalies:
            return "No significant anomalies detected."
        
        formatted = []
        for anomaly in anomalies[:5]:  # Top 5 anomalies
            formatted.append(f"- {anomaly['type']}: {anomaly['message']} (Risk: {anomaly['risk_level']})")
        
        return "\n".join(formatted)