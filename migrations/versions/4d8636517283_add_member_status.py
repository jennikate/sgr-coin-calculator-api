"""Add member status

Revision ID: 4d8636517283
Revises: 982adf800c24
Create Date: 2025-09-08 11:39:39.527877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d8636517283'
down_revision = '982adf800c24'
branch_labels = None
depends_on = None


def upgrade():
    # Add the column with a server default and nullable=False
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'status',
                sa.Boolean(),
                nullable=False,
                server_default=sa.true()  # PostgreSQL TRUE
            )
        )

    # Remove the server default if you only want the SQLAlchemy model default to apply going forward
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.alter_column('status', server_default=None)

def downgrade():
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.drop_column('status')


    # ### end Alembic commands ###
