from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from api_gateway.db import Base

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    price_usd = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class Sentiment(Base):
    __tablename__ = "sentiments"

    id = Column(Integer, primary_key=True, index=True)
    sentiment_score = Column(Float, nullable=False)
    source = Column(String, nullable=False)  # e.g., "twitter", "reddit"
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # e.g., "price_alert", "sentiment_alert"
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed = Column(Integer, default=0)  # 0: new, 1: processed

class DevQuery(Base):
    __tablename__ = "dev_queries"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    framework = Column(String)
    path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentHeartbeat(Base):
    __tablename__ = "agent_heartbeats"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, nullable=False)
    last_heartbeat = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False)  # "running", "stopped", "error"
    tasks_processed = Column(Integer, default=0)
