"""Initial migration: Create all tables

Revision ID: 20260514163959_a1b2c3
Revises: 
Create Date: 2026-05-14 16:39:59.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# 修订标识符
revision = '20260514163959_a1b2c3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### 自动生成迁移命令开始 ###
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('unique_entity_id', sa.String(length=50), nullable=False),
        sa.Column('task_title', sa.String(length=255), nullable=False),
        sa.Column('task_description', sa.Text(), nullable=True),
        sa.Column('execution_status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED', name='taskstatusenum'), nullable=False),
        sa.Column('priority_level', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='taskpriorityenum'), nullable=False),
        sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('started_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_result_message', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        sa.Column('execution_steps_json', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('unique_entity_id'),
    )
    op.create_index(op.f('ix_tasks_unique_entity_id'), 'tasks', ['unique_entity_id'], unique=False)

    op.create_table(
        'memories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('unique_memory_id', sa.String(length=50), nullable=False),
        sa.Column('content_text_body', sa.Text(), nullable=False),
        sa.Column('summary_text', sa.Text(), nullable=True),
        sa.Column('category_type', sa.Enum('GENERAL', 'TECHNICAL', 'EXPERIENCE', 'KNOWLEDGE', 'CASE_STUDY', name='memorycategoryenum'), nullable=False),
        sa.Column('tags_json', sa.Text(), nullable=False),
        sa.Column('importance_score', sa.Integer(), nullable=False),
        sa.Column('access_count', sa.Integer(), nullable=False),
        sa.Column('last_accessed_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('source_task_id', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['source_task_id'], ['tasks.unique_entity_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('unique_memory_id'),
    )
    op.create_index(op.f('ix_memories_unique_memory_id'), 'memories', ['unique_memory_id'], unique=False)

    op.create_table(
        'experiences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('unique_experience_id', sa.String(length=50), nullable=False),
        sa.Column('task_reference_id', sa.String(length=50), nullable=False),
        sa.Column('task_type_label', sa.String(length=100), nullable=False),
        sa.Column('was_successful', sa.Boolean(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('lessons_learned_json', sa.Text(), nullable=False),
        sa.Column('patterns_json', sa.Text(), nullable=False),
        sa.Column('improvements_json', sa.Text(), nullable=False),
        sa.Column('recorded_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('unique_experience_id'),
    )
    op.create_index(op.f('ix_experiences_unique_experience_id'), 'experiences', ['unique_experience_id'], unique=False)

    op.create_table(
        'knowledge_nodes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('node_id', sa.String(length=50), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('properties_json', sa.Text(), nullable=False),
        sa.Column('memory_id', sa.String(length=50), nullable=True),
        sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('node_id'),
    )
    op.create_index(op.f('ix_knowledge_nodes_node_id'), 'knowledge_nodes', ['node_id'], unique=False)

    op.create_table(
        'knowledge_edges',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('edge_id', sa.String(length=50), nullable=False),
        sa.Column('source_node_id', sa.String(length=50), nullable=False),
        sa.Column('target_node_id', sa.String(length=50), nullable=False),
        sa.Column('relationship_type', sa.String(length=100), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['source_node_id'], ['knowledge_nodes.node_id'], ),
        sa.ForeignKeyConstraint(['target_node_id'], ['knowledge_nodes.node_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('edge_id'),
    )
    op.create_index(op.f('ix_knowledge_edges_edge_id'), 'knowledge_edges', ['edge_id'], unique=False)

    op.create_table(
        'system_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('total_tasks', sa.Integer(), nullable=False),
        sa.Column('completed_tasks', sa.Integer(), nullable=False),
        sa.Column('pending_tasks', sa.Integer(), nullable=False),
        sa.Column('failed_tasks', sa.Integer(), nullable=False),
        sa.Column('success_rate', sa.Float(), nullable=False),
        sa.Column('average_execution_time', sa.Float(), nullable=False),
        sa.Column('memory_usage_mb', sa.Float(), nullable=True),
        sa.Column('cpu_usage_percent', sa.Float(), nullable=True),
        sa.Column('current_mode', sa.Enum('TASK_EXECUTION', 'IDLE_IMPROVEMENT', 'PAUSED', name='agentmodeenum'), nullable=False),
        sa.Column('uptime_seconds', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    # ### 自动生成迁移命令结束 ###


def downgrade():
    # ### 自动生成降级命令开始 ###
    op.drop_index(op.f('ix_system_metrics_id'), table_name='system_metrics')
    op.drop_table('system_metrics')
    op.drop_index(op.f('ix_knowledge_edges_edge_id'), table_name='knowledge_edges')
    op.drop_table('knowledge_edges')
    op.drop_index(op.f('ix_knowledge_nodes_node_id'), table_name='knowledge_nodes')
    op.drop_table('knowledge_nodes')
    op.drop_index(op.f('ix_experiences_unique_experience_id'), table_name='experiences')
    op.drop_table('experiences')
    op.drop_index(op.f('ix_memories_unique_memory_id'), table_name='memories')
    op.drop_table('memories')
    op.drop_index(op.f('ix_tasks_unique_entity_id'), table_name='tasks')
    op.drop_table('tasks')
    # ### 自动生成降级命令结束 ###
