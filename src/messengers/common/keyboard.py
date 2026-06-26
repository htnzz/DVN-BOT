from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Button:
    text: str
    payload: str
    intent: str = "default"


Keyboard = list[list[Button]]
