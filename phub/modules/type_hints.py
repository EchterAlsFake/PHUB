from typing import Callable, Awaitable

type callback_hint = Callable[[int, int], None] | None
type on_error_hint = Callable[[str, Exception, int], Awaitable[bool]] | None