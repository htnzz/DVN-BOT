from src.db.models.object_ref import ObjectRef
from src.db.repositories.base import BaseRepository


class ObjectRefRepository(BaseRepository[ObjectRef]):
    model = ObjectRef
