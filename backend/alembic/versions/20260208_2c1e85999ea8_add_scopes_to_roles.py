"""add_scopes_to_roles

Revision ID: 2c1e85999ea8
Revises: 0858598983f8
Create Date: 2026-02-08 23:19:46.317679

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '2c1e85999ea8'
down_revision = '0858598983f8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add scopes column to auth_roles
    op.add_column(
        'auth_roles',
        sa.Column(
            'scopes',
            postgresql.JSONB,
            nullable=False,
            server_default='[]'
        )
    )


def downgrade() -> None:
    # Remove scopes column from auth_roles
    op.drop_column('auth_roles', 'scopes')
