# src/storage/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class MetricsSnapshot(Base):
    __tablename__ = 'metrics_snapshots'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    time_range = Column(String(50))
    
    # DORA metrics
    deployment_frequency = Column(Float)
    lead_time_hours = Column(Float)
    change_failure_rate = Column(Float)
    mttr_hours = Column(Float)
    
    # Code health
    total_churn = Column(Integer)
    churn_rate = Column(Float)
    avg_commit_size = Column(Float)
    
    # Raw data
    raw_metrics = Column(JSON)
    
class AgentConversation(Base):
    __tablename__ = 'agent_conversations'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String(100))
    prompt = Column(Text)
    response = Column(Text)
    
class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev_insights.db"))
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def save_metrics(self, metrics: dict, time_range: str):
        """Save metrics snapshot"""
        snapshot = MetricsSnapshot(
            time_range=time_range,
            deployment_frequency=metrics['dora_metrics']['deployment_frequency'],
            lead_time_hours=metrics['dora_metrics']['lead_time_hours'],
            change_failure_rate=metrics['dora_metrics']['change_failure_rate'],
            mttr_hours=metrics['dora_metrics']['mttr_hours'],
            total_churn=metrics['team_metrics']['code_churn'],
            churn_rate=metrics['team_metrics']['churn_rate'],
            avg_commit_size=metrics['team_metrics'].get('avg_commit_size', 0),
            raw_metrics=metrics
        )
        self.session.add(snapshot)
        self.session.commit()
        
    def save_conversation(self, agent_name: str, prompt: str, response: str):
        """Save agent conversation for audit"""
        conv = AgentConversation(
            agent_name=agent_name,
            prompt=prompt[:1000],  # Truncate for storage
            response=response[:1000]
        )
        self.session.add(conv)
        self.session.commit()