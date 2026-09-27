from fastapi import APIRouter, HTTPException

from app.db import SessionDep
from app.modules.tasks.schemas import TaskPublic, TaskCreate, TaskUpdate
from app.modules.tasks.service import create_task, get_board_tasks, get_task, update_task, delete_task
from app.modules.boards.service import get_board

# No prefix, because routes here start with either /boards/... or /tasks/...
# (shallow nesting), so each route spells out its full path.
router = APIRouter(tags=["tasks"])

# Nested under the board because a task can't exist without one.
@router.post("/boards/{board_id}/tasks", response_model=TaskPublic, status_code=201)
def create_one(board_id: int, data: TaskCreate, session: SessionDep):
    # Check first so a bad board_id is a clear 404. Otherwise Postgres rejects
    # the insert on the foreign key and the client only sees a 500.
    board = get_board(session, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return create_task(session, board, data)

@router.get("/boards/{board_id}/tasks", response_model=list[TaskPublic])
def get_all_board_tasks(board_id: int, session: SessionDep):
    # Without this, a missing board would return [] and look like an empty one
    board = get_board(session, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return get_board_tasks(session, board)

# Single-task routes aren't nested - the task id alone is unique, so the client
# doesn't need to know which board it's on.
@router.get("/tasks/{task_id}", response_model=TaskPublic)
def get_one(task_id: int, session: SessionDep):
    task = get_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/tasks/{task_id}", response_model=TaskPublic)
def update_one(task_id: int, data: TaskUpdate, session: SessionDep):
    # Only when the task is being moved - check the new board exists, or the
    # foreign key would fail on commit and the client would get a 500.
    if data.board_id is not None:
        board = get_board(session, data.board_id)
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
    task = get_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return update_task(session, task, data)

@router.delete("/tasks/{task_id}", status_code=204)
def delete_one(task_id: int, session: SessionDep):
    task = get_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return delete_task(session, task)