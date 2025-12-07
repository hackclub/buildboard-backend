"""Initial schema with normalized user model

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-06

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table (core identity)
    op.create_table('users',
        sa.Column('user_id', sa.String(36), primary_key=True, index=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('slack_id', sa.String(64), nullable=True, unique=True, index=True),
        sa.Column('handle', sa.String(50), nullable=True, unique=True, index=True),
        sa.Column('referral_code', sa.String(8), nullable=False, unique=True, index=True),
        sa.Column('referred_by_user_id', sa.String(36), sa.ForeignKey('users.user_id'), nullable=True, index=True),
        sa.Column('storyline_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('hackatime_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('slack_linked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('idv_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('onboarding_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # User profiles table
    op.create_table('user_profiles',
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id'), primary_key=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('bio', sa.String(1000), nullable=True),
        sa.Column('is_public', sa.Boolean(), default=False, nullable=False),
        sa.Column('public_profile_url', sa.String(255), nullable=True, unique=True, index=True),
        sa.Column('birthday', sa.DateTime(timezone=True), nullable=True),
    )

    # User addresses table
    op.create_table('user_addresses',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id'), nullable=False, index=True),
        sa.Column('address_line_1', sa.String(255), nullable=False),
        sa.Column('address_line_2', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('post_code', sa.String(20), nullable=True),
        sa.Column('is_primary', sa.Boolean(), default=True, nullable=False),
    )

    # Roles table
    op.create_table('roles',
        sa.Column('role_id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
    )

    # User roles junction table
    op.create_table('user_roles',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id'), nullable=False, index=True),
        sa.Column('role_id', sa.String(50), sa.ForeignKey('roles.role_id'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )

    # User login events table
    op.create_table('user_login_events',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id'), nullable=False, index=True),
        sa.Column('logged_in_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Projects table
    op.create_table('projects',
        sa.Column('project_id', sa.String(36), primary_key=True, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id'), nullable=False, index=True),
        sa.Column('project_name', sa.String(200), nullable=False),
        sa.Column('project_description', sa.Text(), nullable=False),
        sa.Column('project_type', sa.String(50), nullable=True),
        sa.Column('attachment_urls', sa.JSON(), nullable=True),
        sa.Column('code_url', sa.String(500), nullable=True),
        sa.Column('live_url', sa.String(500), nullable=True),
        sa.Column('paper_url', sa.String(500), nullable=True),
        sa.Column('submission_week', sa.String(50), nullable=False),
        sa.Column('shipped', sa.Boolean(), default=False, nullable=False),
        sa.Column('sent_to_airtable', sa.Boolean(), default=False, nullable=False),
        sa.Column('github_installation_id', sa.String(100), nullable=True),
        sa.Column('github_repo_path', sa.String(200), nullable=True),
        sa.Column('time_spent', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Hackatime projects table
    op.create_table('hackatime_projects',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('seconds', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Project-Hackatime link table
    op.create_table('project_hackatime_links',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.project_id'), nullable=False, index=True),
        sa.Column('hackatime_project_id', sa.String(36), sa.ForeignKey('hackatime_projects.id'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('project_id', 'hackatime_project_id', name='uq_project_hackatime'),
    )

    # Reviews table
    op.create_table('reviews',
        sa.Column('review_id', sa.String(36), primary_key=True, index=True),
        sa.Column('reviewer_user_id', sa.String(36), sa.ForeignKey('users.user_id'), nullable=False, index=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.project_id'), nullable=False, index=True),
        sa.Column('review_comments', sa.Text(), nullable=False),
        sa.Column('review_decision', sa.String(50), nullable=False),
        sa.Column('review_timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Votes table
    op.create_table('votes',
        sa.Column('vote_id', sa.String(36), primary_key=True, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id'), nullable=False, index=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.project_id'), nullable=False, index=True),
        sa.Column('vote_ranking', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Onboarding events table
    op.create_table('onboarding_events',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),
        sa.Column('event', sa.String(50), nullable=False),
        sa.Column('slide', sa.Integer(), nullable=True),
        sa.Column('total_slides', sa.Integer(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # OTPs table
    op.create_table('otps',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), nullable=False, index=True),
        sa.Column('code', sa.String(6), nullable=False),
        sa.Column('used', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )

    # RSVPs table
    op.create_table('rsvps',
        sa.Column('email', sa.String(255), primary_key=True, index=True),
        sa.Column('ip_address', sa.String(45), nullable=False, index=True),
        sa.Column('rsvptime', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Seed default roles
    op.execute("""
        INSERT INTO roles (role_id, name, description) VALUES
        ('admin', 'Administrator', 'Full system access'),
        ('reviewer', 'Reviewer', 'Can review projects'),
        ('idv', 'IDV', 'Identity verified'),
        ('slack_member', 'Slack Member', 'Member of Slack workspace')
    """)


def downgrade() -> None:
    op.drop_table('rsvps')
    op.drop_table('otps')
    op.drop_table('onboarding_events')
    op.drop_table('votes')
    op.drop_table('reviews')
    op.drop_table('project_hackatime_links')
    op.drop_table('hackatime_projects')
    op.drop_table('projects')
    op.drop_table('user_login_events')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('user_addresses')
    op.drop_table('user_profiles')
    op.drop_table('users')
