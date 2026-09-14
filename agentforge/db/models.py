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

from agentforge.db.base import Base, generate_uuid, current_utc


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="USER", nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=current_utc, onupdate=current_utc, nullable=False)

    runs = relationship("AgentRun", back_populates="user")
    documents = relationship("Document", back_populates="user")
    workflows = relationship("Workflow", back_populates="owner")
    workflow_executions = relationship("WorkflowExecution", back_populates="user")
    audit_events = relationship("AuditEvent", back_populates="user")


class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    system_instruction = Column(Text, nullable=False)
    model_name = Column(String(100), default="gemini-2.5-flash")
    config = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    task_input = Column(Text, nullable=False)
    mode = Column(String(50), default="general")
    status = Column(String(50), default="pending", index=True)
    final_output = Column(Text, nullable=True)
    error_log = Column(JSON, default=list)
    start_time = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="runs")
    events = relationship("ExecutionEvent", back_populates="run", cascade="all, delete-orphan")
    tool_executions = relationship("ToolExecution", back_populates="run", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="run", cascade="all, delete-orphan")


class ExecutionEvent(Base):
    __tablename__ = "execution_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("agent_runs.id"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    event_type = Column(String(100), nullable=False)
    tool_name = Column(String(100), nullable=True)
    status = Column(String(50), default="completed")
    safe_metadata = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)

    run = relationship("AgentRun", back_populates="events")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(50), default="processed", index=True)
    meta_info = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)

    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    chunk_metadata = Column(JSON, default=dict)

    document = relationship("Document", back_populates="chunks")
    embedding = relationship("Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chunk_id = Column(String(36), ForeignKey("document_chunks.id"), nullable=False, index=True)
    embedding_model = Column(String(100), nullable=False)
    vector_data = Column(JSON, nullable=False)  # JSON array representation of vector for cross-db compatibility
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)

    chunk = relationship("DocumentChunk", back_populates="embedding")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_agent = Column(String(100), default="unassigned")
    status = Column(String(50), default="pending", index=True)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)


class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("agent_runs.id"), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False, index=True)
    permission_category = Column(String(50), nullable=False)
    input_params = Column(JSON, default=dict)
    output_result = Column(JSON, default=dict)
    execution_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)

    run = relationship("AgentRun", back_populates="tool_executions")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("agent_runs.id"), nullable=True, index=True)
    metrics = Column(JSON, default=dict)
    groundedness_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    citation_score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)

    run = relationship("AgentRun", back_populates="evaluations")


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    graph_definition = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)

    owner = relationship("User", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    status = Column(String(50), default="pending", index=True)  # pending, running, paused_approval, completed, failed, cancelled
    node_states = Column(JSON, default=dict)
    current_node = Column(String(100), nullable=True)
    inputs = Column(JSON, default=dict)
    outputs = Column(JSON, default=dict)
    error_details = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)

    workflow = relationship("Workflow", back_populates="executions")
    user = relationship("User", back_populates="workflow_executions")
    approvals = relationship("ApprovalRequest", back_populates="execution", cascade="all, delete-orphan")


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    execution_id = Column(String(36), ForeignKey("workflow_executions.id"), nullable=True, index=True)
    run_id = Column(String(36), ForeignKey("agent_runs.id"), nullable=True, index=True)
    tool_name = Column(String(100), nullable=False)
    risk_level = Column(String(50), default="DESTRUCTIVE")
    status = Column(String(50), default="pending", index=True)  # pending, approved, rejected
    approved_by = Column(String(255), nullable=True)
    request_payload = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)

    execution = relationship("WorkflowExecution", back_populates="approvals")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # LOGIN, LOGOUT, ROLE_CHANGE, UPLOAD, EXECUTE
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)

    user = relationship("User", back_populates="audit_events")

