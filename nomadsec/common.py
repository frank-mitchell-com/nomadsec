#!/usr/bin/env python3

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import auto
from enum import Enum
from typing import Protocol


###################### CONSTANTS ###############################

# coordinates are always f"{width:0d}{height:0d}"
DEFAULT_SECTOR_HEIGHT: int = 10
DEFAULT_SECTOR_WIDTH: int = 8
DEFAULT_SECTOR_X: int = 1
DEFAULT_SECTOR_Y: int = 1

# MINIMUM_DENSITY <= density < MAXIMUM_DENSITY
DEFAULT_DENSITY: int = 3
MAXIMUM_DENSITY: int = 6
MINIMUM_DENSITY: int = 1

##################### PROTOCOLS ##############################


class NomadDice(Protocol):
    def __call__(
        self, nkeep: int = 2, nadv: int = 0, nsides: int = 6, low: int = 1
    ) -> int:
        pass


class NameSet(Protocol):
    def make_name(self) -> str:
        return ""

    def add_to_history(self, name: str) -> None: ...


##################### ENUMS ##############################


class Settlement(Enum):
    CORE = auto()
    SETTLED = auto()
    CONFLICT = auto()
    FRONTIER = auto()
    UNEXPLORED = auto()


class TradeClass(Enum):
    AGRICULTURAL = auto()
    GARDEN = auto()
    INDUSTRIAL = auto()
    NON_AGRICULTURAL = auto()
    NON_INDUSTRIAL = auto()
    POOR = auto()
    RESOURCE = auto()
    RICH = auto()


class Characteristic(Enum):
    ASTEROID = auto()
    CORROSIVE = auto()
    DESERT = auto()
    ICEBALL = auto()
    INERT = auto()
    MARGINAL = auto()
    OCEAN = auto()
    PRIME = auto()
    PRIMORDIAL = auto()
    ROCKBALL = auto()
    TAINTED = auto()


class TechAge(Enum):
    NO_TECHNOLOGY = 0
    EARLY_PRIMITIVE = 1
    LATE_PRIMITIVE = 2
    EARLY_MECHANICAL = 3
    LATE_MECHANICAL = 4
    EARLY_ATOMIC = 5
    LATE_ATOMIC = 6
    EARLY_SPACE = 7
    LATE_SPACE = 8
    EARLY_INTERSTELLAR = 9
    LATE_INTERSTELLAR = 10
    EARLY_GALACTIC = 11
    LATE_GALACTIC = 12
    COSMIC = 13


######################## DATA STRUCTURES #############################

@dataclass(frozen=True, order=True, kw_only=True, slots=True)
class StarHex:
    x: int
    y: int
    name: str

    @property
    def hexcode(self) -> str:
        return f"{self.x:02d}{self.y:02d}"

    def repr(self) -> str:
        return f"StarHex({self.hexcode}, {repr(self.name)})"


@dataclass(frozen=True, order=True, repr=True, kw_only=True, slots=True)
class Planet():
    name: str
    star: StarHex
    trade_class: TradeClass
    chara: Characteristic
    population: int
    tech_age: TechAge
    world_tag_1: str
    world_tag_2: str

    @property
    def hexcode(self) -> str:
        return self.star.hexcode if self.star else "????"


@dataclass(order=True, repr=True)
class StarSystem:
    star: StarHex
    planets: list[Planet] = field(default_factory=list)

    def add_planet(self, p: Planet) -> None:
        self.planets.append(p)


@dataclass(repr=True)
class SectorBounds:
    height: int = DEFAULT_SECTOR_HEIGHT
    width: int = DEFAULT_SECTOR_WIDTH
    x: int = DEFAULT_SECTOR_X
    y: int = DEFAULT_SECTOR_Y

    def x_range(self):
        return range(self.x, self.x + self.width)

    def y_range(self):
        return range(self.y, self.y + self.height)
