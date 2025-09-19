# Add the default rank details -> remember to import uuid
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
