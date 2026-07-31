"""Add UniqueConstraint to VideoVisual

Revision ID: 072375ac7ed8
Revises: 909cb80d0c9d
Create Date: 2026-07-31 22:08:40.246384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '072375ac7ed8'
down_revision: Union[str, None] = '909cb80d0c9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('video_visuals', schema=None) as batch_op:
        batch_op.create_unique_constraint('uix_video_filename', ['video_id', 'filename'])


def downgrade() -> None:
    with op.batch_alter_table('video_visuals', schema=None) as batch_op:
        batch_op.drop_constraint('uix_video_filename', type_='unique')
