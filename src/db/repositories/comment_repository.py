from src.db.models.comment import Comment
from src.db.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    model = Comment
