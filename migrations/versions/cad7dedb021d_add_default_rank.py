"""Add default rank

Revision ID: cad7dedb021d
Revises: 3b25a412794f
Create Date: 2025-09-19 11:22:25.074737

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = 'cad7dedb021d'
down_revision = '3b25a412794f'
branch_labels = None
depends_on = None

DEFAULT_RANK = {
    "id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
    "name": "default",
    "position": 99,
    "share": 0
}


def upgrade():
    conn = op.get_bind()
    conn.execute(
        sa.text("""
            INSERT INTO ranks (id, name, position, share)
            VALUES (:id, :name, :position, :share)
            ON CONFLICT (id) DO NOTHING
        """),
        {
            "id": DEFAULT_RANK["id"],
            "name": DEFAULT_RANK["name"],
            "position": DEFAULT_RANK["position"],
            "share": DEFAULT_RANK["share"],
        }
    )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        sa.text("DELETE FROM ranks WHERE id = :id"),
        {"id": DEFAULT_RANK["id"]}
    )
