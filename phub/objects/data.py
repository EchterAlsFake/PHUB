from dataclasses import dataclass, field

@dataclass
class Tag:
    name: str
    count: int = field(default = None,
                       repr = False)


@dataclass
class Like:
    up: int
    down: int

# EOF