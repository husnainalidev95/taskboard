from enum import Enum
from sqlmodel import SQLModel, Field


# Inheriting from str means these serialise as "triage" in JSON instead of
# "Status.triage". Postgres gets a real enum type built from these values,
# so it rejects anything not in this list.
class Status(str, Enum):
    triage = "triage"
    backlog = "backlog"
    todo = "todo"
    in_progress = "in_progress"
    in_review = "in_review"
    done = "done"
    closed = "closed"


class Task(SQLModel, table=True):
    # Primary key - Postgres generates the value, so it's empty until saved
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str = Field(default="")
    # New tasks land in triage unless the caller says otherwise
    status: Status = Field(default=Status.triage)
    # Points at board.id - that's the TABLE name, not the class name.
    # Postgres will refuse a task whose board_id doesn't exist.
    # ondelete="CASCADE" makes Postgres delete a board's tasks along with it,
    # instead of refusing to delete the board. Changing it needs a migration.
    # index=True because Postgres doesn't index foreign keys on its own, and
    # listing a board's tasks and the cascade both look rows up by board_id.
    board_id: int = Field(foreign_key="board.id", ondelete="CASCADE", index=True)
