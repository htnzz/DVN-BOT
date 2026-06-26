from typing import Any

from aiomax.fsm import FSMCursor


class MaxStateStorage:
    def __init__(self, cursor: FSMCursor) -> None:
        self.cursor = cursor

    def get_state(self) -> str | None:
        return self.cursor.get_state()

    def change_state(self, state: str) -> None:
        self.cursor.change_state(state)

    def get_data(self) -> dict[str, Any] | None:
        return self.cursor.get_data()

    def change_data(self, data: dict[str, Any]) -> None:
        self.cursor.change_data(data)

    def clear(self) -> None:
        self.cursor.clear()
