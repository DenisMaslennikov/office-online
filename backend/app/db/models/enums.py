from sqlalchemy import Enum

icon_category_enum = Enum("TASK_TYPE", "FILE_GROUP", "PROJECT", name="icon_category")

subject_type_enum = Enum("ROLE", "USER", name="subject_type")
