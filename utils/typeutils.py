from typing import TypeAlias

# https://github.com/python/typing/issues/182#issuecomment-1320974824
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None 
