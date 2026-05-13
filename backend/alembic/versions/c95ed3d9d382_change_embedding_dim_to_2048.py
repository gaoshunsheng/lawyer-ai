"""change_embedding_dim_to_2048

Revision ID: c95ed3d9d382
Revises: 100d58d44e45
Create Date: 2026-05-13 21:14:15.751560

"""
from typing import Sequence, Union

from alembic import op
import pgvector.sqlalchemy.vector


# revision identifiers, used by Alembic.
revision: str = 'c95ed3d9d382'
down_revision: Union[str, Sequence[str], None] = '100d58d44e45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old HNSW indexes (2048-dim exceeds HNSW 2000 limit)
    op.drop_index('ix_law_embeddings_hnsw', table_name='law_embeddings')
    op.drop_index('ix_case_embeddings_hnsw', table_name='case_embeddings')

    op.alter_column('case_embeddings', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
               type_=pgvector.sqlalchemy.vector.VECTOR(dim=2048),
               existing_nullable=True)
    op.alter_column('law_embeddings', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
               type_=pgvector.sqlalchemy.vector.VECTOR(dim=2048),
               existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('law_embeddings', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=2048),
               type_=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
               existing_nullable=True)
    op.alter_column('case_embeddings', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=2048),
               type_=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
               existing_nullable=True)
