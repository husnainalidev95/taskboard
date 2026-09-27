from sqlmodel import SQLModel

# Gives every index and constraint a predictable name. Without it Postgres
# picks the names, Alembic can't know them, and migrations that drop or change
# a constraint fail (you'd see a "constraint name is None" warning).
# It must come before the model imports below - names are decided when each
# table is defined, so tables imported first would miss the convention.
SQLModel.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Importing the models here is what registers their tables on SQLModel.metadata.
# That metadata is what Alembic reads when autogenerating migrations, so every
# new model file needs a line added below or its table will be invisible.
from app.models.board import Board
from app.models.task import Task, Status

# Lets other modules write "from app.models import Board, Task"
__all__ = ["Board", "Task", "Status"]
