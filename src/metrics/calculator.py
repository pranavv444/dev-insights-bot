# src/metrics/calculator.py
from typing import Dict, List, Any
from datetime import datetime, timedelta
import statistics

class MetricsCalculator:
    """Calculate engineering metrics aligned with CommitIQ approach"""
    
    @staticmethod
    def calculate_dora_metrics(commits: List[Dict], prs: List[Dict]) -> Dict[str, float]:
        """Calculate DORA's four key metrics"""
        
        # Deployment Frequency (using merged PRs as proxy)
        merged_prs = [pr for pr in prs if pr.get("merged_at")]
        deployment_frequency = len(merged_prs)
        
        # Lead Time for Changes
        lead_times = []
        for pr in merged_prs:
            if pr.get("created_at") and pr.get("merged_at"):
                lead_time = (pr["merged_at"] - pr["created_at"]).total_seconds() / 3600
                lead_times.append(lead_time)
        
        avg_lead_time = statistics.mean(lead_times) if lead_times else 0
        
        # Change Failure Rate (would need CI/CD data - placeholder)
        change_failure_rate = 0.0
        
        # Mean Time to Recovery (would need incident data - placeholder)
        mttr = 0.0
        
        return {
            "deployment_frequency": deployment_frequency,
            "lead_time_hours": avg_lead_time,
            "change_failure_rate": change_failure_rate,
            "mttr_hours": mttr
        }
    
    @staticmethod
    def calculate_code_health_metrics(commits: List[Dict]) -> Dict[str, Any]:
        """Calculate code health indicators"""
        
        if not commits:
            return {"churn_rate": 0, "commit_size_avg": 0, "refactor_ratio": 0}
        
        # Code churn analysis
        total_changes = sum(c.get("additions", 0) + c.get("deletions", 0) for c in commits)
        total_additions = sum(c.get("additions", 0) for c in commits)
        total_deletions = sum(c.get("deletions", 0) for c in commits)
        
        # Average commit size
        commit_sizes = [c.get("additions", 0) + c.get("deletions", 0) for c in commits]
        avg_commit_size = statistics.mean(commit_sizes) if commit_sizes else 0
        
        # Refactor ratio (deletions to additions)
        refactor_ratio = total_deletions / total_additions if total_additions > 0 else 0
        
        return {
            "total_churn": total_changes,
            "churn_rate": total_changes / len(commits),
            "commit_size_avg": avg_commit_size,
            "commit_size_std": statistics.stdev(commit_sizes) if len(commit_sizes) > 1 else 0,
            "refactor_ratio": refactor_ratio,
            "additions": total_additions,
            "deletions": total_deletions
        }
    
    @staticmethod
    def calculate_developer_velocity(dev_metrics: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate individual developer productivity metrics"""
        
        velocities = {}
        for dev, metrics in dev_metrics.items():
            commits = metrics.get("commits", 0)
            changes = metrics.get("additions", 0) + metrics.get("deletions", 0)
            
            velocities[dev] = {
                "commit_frequency": commits,
                "code_velocity": changes,
                "avg_commit_size": changes / commits if commits > 0 else 0,
                "pr_merge_rate": metrics.get("prs_merged", 0) / metrics.get("prs_created", 1) * 100
            }
        
        return velocities