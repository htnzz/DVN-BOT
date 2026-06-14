from __future__ import annotations

from enum import StrEnum


class MenuService:
    @staticmethod
    def get_main_menu_text() -> str:
        return (
            "Добрый день!\n\n"
            "Выберите нужный раздел меню"
                )

    @staticmethod
    def get_section_in_development_text() -> str:
        return "Раздел пока в разработке."

    @staticmethod
    def get_help_text() -> str:
        return (
            "Помощь\n\n"
            "Здесь будет описание возможностей бота и ответы на частые вопросы."
        )
