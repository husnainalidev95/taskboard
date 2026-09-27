from sqlmodel import Session, select
from app.models import Task, Board
from app.modules.tasks.schemas import TaskCreate, TaskUpdate

# Takes the whole Board, not just an id, so the caller has to have loaded it -
# which means it has already checked the board exists.
def create_task(session: Session, board: Board, data: TaskCreate) -> Task:
    # board_id comes from the URL, not the body, so it's merged in here. It has to
    # go in during validation - Task requires it and would reject the data without.
    task = Task.model_validate(data, update={"board_id": board.id})
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_board_tasks(session: Session, board: Board) -> list[Task]:
    return session.exec(select(Task).where(Task.board_id == board.id)).all()

def get_task(session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id)

def update_task(session: Session, task: Task, data: TaskUpdate) -> Task:
    task.sqlmodel_update(data.model_dump(exclude_unset=True, exclude_none=True))
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def delete_task(session: Session, task: Task) -> None:
    session.delete(task)
    session.commit()