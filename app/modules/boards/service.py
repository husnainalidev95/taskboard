from sqlmodel import Session, select
from app.models import Board
from app.modules.boards.schemas import BoardCreate, BoardUpdate

# The session is passed in rather than created here, so the router controls its
# lifetime and tests can hand in one pointed at a test database.
def create_board(session: Session, data: BoardCreate) -> Board:
    # Copies the request fields onto a real table object. id is still None.
    board = Board.model_validate(data)
    # Only queues it - nothing reaches Postgres until commit
    session.add(board)
    # Runs the INSERT. Without this the board vanishes when the session closes.
    session.commit()
    # Reloads the row so board.id holds the value Postgres just generated
    session.refresh(board)
    return board

# Read-only, so there's nothing to commit - just a SELECT of every row
def list_boards(session: Session) -> list[Board]:
    return session.exec(select(Board)).all()

# session.get only looks up by primary key - for any other column use select().
# Returns None instead of raising, so the caller decides what "missing" means.
def get_board(session: Session, board_id: int) -> Board | None:
    return session.get(Board, board_id)

# Takes the board the router already loaded, so it isn't fetched twice. Changing
# that tracked object is what gets saved - a copy would be ignored by commit.
def update_board(session: Session, board: Board, data: BoardUpdate) -> Board:
    board.sqlmodel_update(data.model_dump(exclude_unset=True, exclude_none=True))
    session.add(board)
    session.commit()
    session.refresh(board)
    return board

# Like add, delete only marks the row - the DELETE runs on commit. Once tasks
# point at this board, Postgres will refuse it because of the foreign key.
def delete_board(session: Session, board: Board) -> None:
    session.delete(board)
    session.commit()
