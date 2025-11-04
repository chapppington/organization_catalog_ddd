"""fix unique index for activities to handle NULL parent_id

Revision ID: fix_activities_unique
Revises: 4974a94bf6f4
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "fix_activities_unique"
down_revision: Union[str, Sequence[str], None] = "4974a94bf6f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Исправляет уникальный индекс для activities.

    Удаляет старый индекс и создает два частичных уникальных индекса:
    1. Для корневых элементов (parent_id IS NULL) - уникальность по name
    2. Для дочерних элементов (parent_id IS NOT NULL) - уникальность по (name, parent_id)
    """
    # Удаляем старый индекс
    op.drop_index("uq_activities_name_parent", table_name="activities")

    # Создаем частичный уникальный индекс для корневых элементов (parent_id IS NULL)
    op.execute(
        """
        CREATE UNIQUE INDEX uq_activities_name_root 
        ON activities (name) 
        WHERE parent_id IS NULL
        """
    )

    # Создаем частичный уникальный индекс для дочерних элементов (parent_id IS NOT NULL)
    op.execute(
        """
        CREATE UNIQUE INDEX uq_activities_name_parent 
        ON activities (name, parent_id) 
        WHERE parent_id IS NOT NULL
        """
    )


def downgrade() -> None:
    """Откатывает изменения."""
    op.drop_index("uq_activities_name_parent", table_name="activities")
    op.drop_index("uq_activities_name_root", table_name="activities")

    # Восстанавливаем старый индекс
    op.create_index(
        "uq_activities_name_parent", "activities", ["name", "parent_id"], unique=True
    )
