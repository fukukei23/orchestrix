from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ARRAY, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    goal = Column(Text, nullable=False)
    complexity_score = Column(Float)
    status = Column(String(50), default='pending')
    priority = Column(Integer, default=0)
    parent_task_id = Column(String, ForeignKey('tasks.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    scheduled_at = Column(DateTime(timezone=True))
    cron_expression = Column(String(100))


class TaskDependency(Base):
    __tablename__ = 'task_dependencies'

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    depends_on_task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    dependency_type = Column(String(50))


class Execution(Base):
    __tablename__ = 'executions'

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    agent_type = Column(String(50))
    model_used = Column(String(100))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    status = Column(String(50))
    exit_code = Column(Integer)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    cost_usd = Column(Float)
    git_branch = Column(String(255))
    git_worktree_path = Column(Text)


class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String, ForeignKey('executions.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    level = Column(String(20))
    message = Column(Text)
    context = Column(JSON)
    agent_output = Column(Text)


class AgentConfig(Base):
    __tablename__ = 'agent_configs'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    cli_command = Column(Text, nullable=False)
    default_model = Column(String(100))
    supports_features = Column(JSON)
    cost_per_1k_input = Column(Float)
    cost_per_1k_output = Column(Float)
    enabled = Column(Boolean, default=True)
