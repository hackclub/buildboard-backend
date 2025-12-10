"""auto_migration

Revision ID: 8c4686009abf
Revises: 9a4e89082f9e
Create Date: 2025-12-09 16:21:15.661383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8c4686009abf'
down_revision: Union[str, Sequence[str], None] = '9a4e89082f9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def index_exists(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
    return index_name in indexes


def upgrade() -> None:
    """Upgrade schema."""
    # Projects columns
    if not column_exists('projects', 'project_type'):
        op.add_column('projects', sa.Column('project_type', sa.String(length=50), nullable=True))
    if not column_exists('projects', 'github_installation_id'):
        op.add_column('projects', sa.Column('github_installation_id', sa.String(length=100), nullable=True))
    if not column_exists('projects', 'github_repo_path'):
        op.add_column('projects', sa.Column('github_repo_path', sa.String(length=200), nullable=True))
    if not column_exists('projects', 'hackatime_projects'):
        op.add_column('projects', sa.Column('hackatime_projects', sa.ARRAY(sa.String()), nullable=True))
    if not column_exists('projects', 'hackatime_hours'):
        op.add_column('projects', sa.Column('hackatime_hours', sa.Float(), nullable=True))

    # Index migrations for projects - skip if already done
    try:
        if index_exists('projects', 'idx_projects_project_id'):
            op.drop_index(op.f('idx_projects_project_id'), table_name='projects')
    except:
        pass
    try:
        if index_exists('projects', 'idx_projects_user_id'):
            op.drop_index(op.f('idx_projects_user_id'), table_name='projects')
    except:
        pass
    if not index_exists('projects', 'ix_projects_project_id'):
        op.create_index(op.f('ix_projects_project_id'), 'projects', ['project_id'], unique=False)
    if not index_exists('projects', 'ix_projects_user_id'):
        op.create_index(op.f('ix_projects_user_id'), 'projects', ['user_id'], unique=False)
    
    # Drop review_ids if exists
    if column_exists('projects', 'review_ids'):
        op.drop_column('projects', 'review_ids')

    # Index migrations for reviews - skip if already done
    try:
        if index_exists('reviews', 'idx_reviews_project_id'):
            op.drop_index(op.f('idx_reviews_project_id'), table_name='reviews')
    except:
        pass
    try:
        if index_exists('reviews', 'idx_reviews_review_id'):
            op.drop_index(op.f('idx_reviews_review_id'), table_name='reviews')
    except:
        pass
    try:
        if index_exists('reviews', 'idx_reviews_reviewer_user_id'):
            op.drop_index(op.f('idx_reviews_reviewer_user_id'), table_name='reviews')
    except:
        pass
    if not index_exists('reviews', 'ix_reviews_project_id'):
        op.create_index(op.f('ix_reviews_project_id'), 'reviews', ['project_id'], unique=False)
    if not index_exists('reviews', 'ix_reviews_review_id'):
        op.create_index(op.f('ix_reviews_review_id'), 'reviews', ['review_id'], unique=False)
    if not index_exists('reviews', 'ix_reviews_reviewer_user_id'):
        op.create_index(op.f('ix_reviews_reviewer_user_id'), 'reviews', ['reviewer_user_id'], unique=False)

    # Index migrations for rsvps
    try:
        if index_exists('rsvps', 'idx_rsvps_email'):
            op.drop_index(op.f('idx_rsvps_email'), table_name='rsvps')
    except:
        pass
    try:
        if index_exists('rsvps', 'idx_rsvps_ip'):
            op.drop_index(op.f('idx_rsvps_ip'), table_name='rsvps')
    except:
        pass
    if not index_exists('rsvps', 'ix_rsvps_email'):
        op.create_index(op.f('ix_rsvps_email'), 'rsvps', ['email'], unique=False)
    if not index_exists('rsvps', 'ix_rsvps_ip_address'):
        op.create_index(op.f('ix_rsvps_ip_address'), 'rsvps', ['ip_address'], unique=False)

    # Users columns
    if not column_exists('users', 'phone_number'):
        op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))
    if not column_exists('users', 'handle'):
        op.add_column('users', sa.Column('handle', sa.String(length=50), nullable=True))
    if not column_exists('users', 'referral_code'):
        op.add_column('users', sa.Column('referral_code', sa.String(length=8), nullable=True))
    if not column_exists('users', 'referred_by_user_id'):
        op.add_column('users', sa.Column('referred_by_user_id', sa.String(length=36), nullable=True))
    if not column_exists('users', 'storyline_completed_at'):
        op.add_column('users', sa.Column('storyline_completed_at', sa.DateTime(timezone=True), nullable=True))
    if not column_exists('users', 'hackatime_completed_at'):
        op.add_column('users', sa.Column('hackatime_completed_at', sa.DateTime(timezone=True), nullable=True))
    if not column_exists('users', 'slack_linked_at'):
        op.add_column('users', sa.Column('slack_linked_at', sa.DateTime(timezone=True), nullable=True))
    if not column_exists('users', 'idv_completed_at'):
        op.add_column('users', sa.Column('idv_completed_at', sa.DateTime(timezone=True), nullable=True))
    if not column_exists('users', 'identity_vault_id'):
        op.add_column('users', sa.Column('identity_vault_id', sa.String(length=255), nullable=True))
    if not column_exists('users', 'identity_vault_access_token'):
        op.add_column('users', sa.Column('identity_vault_access_token', sa.String(length=512), nullable=True))
    if not column_exists('users', 'idv_country'):
        op.add_column('users', sa.Column('idv_country', sa.String(length=10), nullable=True))
    if not column_exists('users', 'verification_status'):
        op.add_column('users', sa.Column('verification_status', sa.String(length=32), nullable=True))
    if not column_exists('users', 'ysws_eligible'):
        op.add_column('users', sa.Column('ysws_eligible', sa.Boolean(), nullable=True))
    if not column_exists('users', 'onboarding_completed_at'):
        op.add_column('users', sa.Column('onboarding_completed_at', sa.DateTime(timezone=True), nullable=True))

    # Index migrations for users
    try:
        if index_exists('users', 'idx_users_email'):
            op.drop_index(op.f('idx_users_email'), table_name='users')
    except:
        pass
    try:
        if index_exists('users', 'idx_users_slack_id'):
            op.drop_index(op.f('idx_users_slack_id'), table_name='users')
    except:
        pass
    try:
        if index_exists('users', 'idx_users_user_id'):
            op.drop_index(op.f('idx_users_user_id'), table_name='users')
    except:
        pass

    if not index_exists('users', 'ix_users_email'):
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    if not index_exists('users', 'ix_users_handle'):
        op.create_index(op.f('ix_users_handle'), 'users', ['handle'], unique=True)
    if not index_exists('users', 'ix_users_identity_vault_id'):
        op.create_index(op.f('ix_users_identity_vault_id'), 'users', ['identity_vault_id'], unique=True)
    if not index_exists('users', 'ix_users_referral_code'):
        op.create_index(op.f('ix_users_referral_code'), 'users', ['referral_code'], unique=True)
    if not index_exists('users', 'ix_users_referred_by_user_id'):
        op.create_index(op.f('ix_users_referred_by_user_id'), 'users', ['referred_by_user_id'], unique=False)
    if not index_exists('users', 'ix_users_slack_id'):
        op.create_index(op.f('ix_users_slack_id'), 'users', ['slack_id'], unique=True)
    if not index_exists('users', 'ix_users_user_id'):
        op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)

    # Drop old columns if they exist
    if column_exists('users', 'address_line_1'):
        op.drop_column('users', 'address_line_1')
    if column_exists('users', 'country'):
        op.drop_column('users', 'country')
    if column_exists('users', 'address_line_2'):
        op.drop_column('users', 'address_line_2')
    if column_exists('users', 'is_admin'):
        op.drop_column('users', 'is_admin')
    if column_exists('users', 'birthday'):
        op.drop_column('users', 'birthday')
    if column_exists('users', 'city'):
        op.drop_column('users', 'city')
    if column_exists('users', 'is_reviewer'):
        op.drop_column('users', 'is_reviewer')
    if column_exists('users', 'first_name'):
        op.drop_column('users', 'first_name')
    if column_exists('users', 'last_name'):
        op.drop_column('users', 'last_name')
    if column_exists('users', 'state'):
        op.drop_column('users', 'state')
    if column_exists('users', 'dates_logged_in'):
        op.drop_column('users', 'dates_logged_in')
    if column_exists('users', 'post_code'):
        op.drop_column('users', 'post_code')

    # Index migrations for votes
    try:
        if index_exists('votes', 'idx_votes_project_id'):
            op.drop_index(op.f('idx_votes_project_id'), table_name='votes')
    except:
        pass
    try:
        if index_exists('votes', 'idx_votes_user_id'):
            op.drop_index(op.f('idx_votes_user_id'), table_name='votes')
    except:
        pass
    try:
        if index_exists('votes', 'idx_votes_vote_id'):
            op.drop_index(op.f('idx_votes_vote_id'), table_name='votes')
    except:
        pass
    if not index_exists('votes', 'ix_votes_project_id'):
        op.create_index(op.f('ix_votes_project_id'), 'votes', ['project_id'], unique=False)
    if not index_exists('votes', 'ix_votes_user_id'):
        op.create_index(op.f('ix_votes_user_id'), 'votes', ['user_id'], unique=False)
    if not index_exists('votes', 'ix_votes_vote_id'):
        op.create_index(op.f('ix_votes_vote_id'), 'votes', ['vote_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    pass
