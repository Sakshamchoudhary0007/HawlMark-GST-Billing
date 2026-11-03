"""add_cat_to_invoice_items

Revision ID: 29e54ee257ae
Revises: 5050c9b69137
"""

from alembic import op
import sqlalchemy as sa

revision = "29e54ee257ae"
down_revision = "5050c9b69137"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "invoice_items",
        sa.Column("cat", sa.String(length=50), nullable=True)
    )


def downgrade():
    op.drop_column("invoice_items", "cat")