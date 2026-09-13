"""
SQLAlchemy Relational Database Models for AgentForge AI
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from agentforge.db.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def current_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="USER", nullable=False)
    created_at = Column(DateTime, default=current_utc)
    updated_at = Column(DateTime, default=current_utc, onupdate=current_utc)

    runs = relationship("AgentRun", back_populates="user")
    documents = relationship("Document", back_populates="user")


class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    role = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    system_instruction = Column(Text, nullable=False)
    model_name = Column(String(100), default="gemini-2.5-flash")
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=current_utc)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    task_input = Column(Text, nullable=False)
    mode = Column(String(50), default="general")
    status = Column(String(50), default="pending")
    final_output = Column(Text, nullable=True)
    error_log = Column(JSON, default=list)
    start_time = Column(DateTime, default=current_utc)
    end_time = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="runs")
    events = relationship("ExecutionEvent", back_populates="run", cascade="all, delete-orphan")
    tool_executions = relationship("ToolExecution", back_populates="run", cascade="all, delete-orphan")


class ExecutionEvent(Base):
    __tablename__ = "execution_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("agent_runs.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    event_type = Column(String(100), nullable=False)
    tool_name = Column(String(100), nullable=True)
    status = Column(String(50), default="completed")
    safe_metadata = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=current_utc)

    run = relationship("AgentRun", back_populates="events")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False)
    status = Column(String(50), default="processed")
    meta_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=current_utc)

    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    chunk_metadata = Column(JSON, default=dict)

    document = relationship("Document", back_populates="chunks")
    embedding = relationship("Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(String, primary_key=True, default=generate_uuid)
    chunk_id = Column(String, ForeignKey("document_chunks.id"), nullable=False)
    embedding_model = Column(String(100), nullable=False)
    vector_data = Column(JSON, nullable=False)  # JSON array representation of vector for cross-db compatibility
    created_at = Column(DateTime, default=current_utc)

    chunk = relationship("DocumentChunk", back_populates="embedding")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_agent = Column(String(100), default="unassigned")
    status = Column(String(50), default="pending")
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=current_utc)


class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("agent_runs.id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    permission_category = Column(String(50), nullable=False)
    input_params = Column(JSON, default=dict)
    output_result = Column(JSON, default=dict)
    execution_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=current_utc)

    run = relationship("AgentRun", back_populates="tool_executions")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("agent_runs.id"), nullable=True)
    metrics = Column(JSON, default=dict)
    groundedness_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    citation_score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=current_utc)


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    graph_definition = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=current_utc)
