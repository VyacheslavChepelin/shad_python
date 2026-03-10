from dataclasses import dataclass, field, InitVar
from abc import ABC, abstractmethod

DISCOUNT_PERCENTS = 15

@dataclass(frozen=True, order=True)
class Item:
    # note: you might want to change the order of fields
    item_id: int = field(compare=False)
    title: str
    cost: int

    def __post_init__(self):
        assert self.title != ''
        assert self.cost > 0

# You may set `# type: ignore` on this class
# It is [a really old issue](https://github.com/python/mypy/issues/5374)
# But seems to be solved
@dataclass
class Position(ABC):
    item: Item

    def __post_init__(self):
        assert isinstance(self, Position)  # todo: do i need to throw error here:?

    @property
    @abstractmethod
    def cost(self) -> float:
        pass

@dataclass
class CountedPosition(Position):
    count: int = field(default = 1)

    @property
    def cost(self) -> float:
        return self.count * self.item.cost

@dataclass
class WeightedPosition(Position):
    weight: float = field(default = 1)

    @property
    def cost(self) -> float:
        return self.weight * self.item.cost

@dataclass
class Order:
    order_id: int
    positions: list[Position] = field(default_factory=list)
    cost: int = field(init = False)
    have_promo:InitVar[bool] = False

    def __post_init__(self, have_promo: bool):
        sum = 0.0
        for position in self.positions:
            sum += position.cost
        self.cost = int(sum - (sum * DISCOUNT_PERCENTS / 100 if have_promo else 0))
