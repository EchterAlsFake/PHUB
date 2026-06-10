from typing import Callable

type callback_hint = Callable[[int, int], None] | None