from sqlalchemy import Enum

icon_category_enum = Enum("TASK_TYPE", "FILE_GROUP", "PROJECT", "CHANNEL", name="icon_category")

subject_type_enum = Enum("ROLE", "USER", name="subject_type")

sprint_status_enum = Enum("Планирование", "Активный", "Завершенный", name="sprint_status")
