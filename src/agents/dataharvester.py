from typing import Dict, Any
from datetime import datetime, timedelta
from github import Github
import os
from src.agents.base import BaseAgent

class DataHarvesterAgent(BaseAgent):
    def __init__(self):
        super().__init__("DataHarvester")
        self.github = Github(os.getenv("GITHUB_TOKEN"))
        self.owner = os.getenv("GITHUB_OWNER")
        self.repo_name = os.getenv("GITHUB_REPO")
        
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch GitHub data based on time range"""
        try:
            repo = self.github.get_repo(f"{self.owner}/{self.repo_name}")
            
            # Calculate date range
            end_date = datetime.now()
            if state["time_range"] == "daily":
                start_date = end_date - timedelta(days=1)
            elif state["time_range"] == "weekly":
                start_date = end_date - timedelta(days=7)
            else:  # monthly
                start_date = end_date - timedelta(days=30)
            
            # Fetch commits
            commits = []
            for commit in repo.get_commits(since=start_date, until=end_date):
                commits.append({
                    "sha": commit.sha,
                    "author": commit.author.login if commit.author else "unknown",
                    "message": commit.commit.message,
                    "date": commit.commit.author.date,
                    "additions": commit.stats.additions,
                    "deletions": commit.stats.deletions,
                    "total": commit.stats.total,
                    "files": len(commit.files)
                })
            
            # Fetch pull requests
            pull_requests = []
            for pr in repo.get_pulls(state="all", sort="updated", direction="desc"):
                if pr.created_at >= start_date:
                    pull_requests.append({
                        "number": pr.number,
                        "title": pr.title,
                        "author": pr.user.login,
                        "state": pr.state,
                        "created_at": pr.created_at,
                        "merged_at": pr.merged_at,
                        "additions": pr.additions,
                        "deletions": pr.deletions,
                        "changed_files": pr.changed_files,
                        "review_comments": pr.review_comments
                    })
            
            state["commits"] = commits
            state["pull_requests"] = pull_requests
            
            self.logger.info(f"Harvested {len(commits)} commits and {len(pull_requests)} PRs")
            
        except Exception as e:
            state["errors"].append(f"Data harvesting error: {str(e)}")
            self.logger.error(f"Error in data harvesting: {e}")
            
        return state