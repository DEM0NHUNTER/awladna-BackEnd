"""create full schema"""
"""BackEnd/alembic/versions/b6a114632fc6_create_full_schema.py"""
from alembic import op
import sqlalchemy as sa

revision = 'b6a114632fc6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create user_profile table
    op.create_table(
        'user_profile',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )

    # Create child_profile table
    op.create_table(
        'child_profile',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('age', sa.Integer, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user_profile.id', ondelete='CASCADE'), nullable=False)
    )

    # Create chat_log table
    op.create_table(
        'chat_log',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user_profile.id', ondelete='CASCADE')),
        sa.Column('child_id', sa.Integer, sa.ForeignKey('child_profile.id', ondelete='CASCADE')),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('sender', sa.String(50), nullable=False),  # e.g., "user" or "ai"
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
        sa.Column(
            'status',
            sa.Enum('sent', 'delivered', 'read', name='chat_status'),
            server_default='sent'
        )
    )

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user_profile.id'), nullable=False),
        sa.Column('message', sa.String(255), nullable=False),
        sa.Column('read', sa.Boolean, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )

    # Create settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user_profile.id', ondelete='CASCADE')),
        sa.Column('language', sa.String(20), server_default='en'),
        sa.Column('notifications_enabled', sa.Boolean, server_default=sa.text('true'))
    )

    # Add indexes
    op.create_index('ix_chatlog_user_child', 'chat_log', ['user_id', 'child_id'])
    op.create_index('ix_notifications_user', 'notifications', ['user_id'])



def downgrade():
    op.drop_index('ix_notifications_user', table_name='notifications')
    op.drop_index('ix_chatlog_user_child', table_name='chat_log')
    op.drop_column('chat_log', 'status')
    op.drop_column('chat_log', 'timestamp')
    op.drop_table('settings')
    op.drop_table('notifications')
    op.drop_table('child_profile')
    op.drop_table('user_profile')
