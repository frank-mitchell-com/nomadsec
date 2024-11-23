#!/usr/bin/env python3

import itertools
import sys
from collections.abc import Iterable
from typing import Tuple

from .common import (
    DEFAULT_DENSITY,
    MAXIMUM_DENSITY,
    MINIMUM_DENSITY,
    NameSet,
    NomadDice,
    Planet,
    SectorBounds,
    Settlement,
    StarHex,
    StarSystem,
    TechAge,
    TradeClass,
)
from .tables import (
    characteristic,
    nomad_dice,
    population,
    trade_class,
    tech_age,
    world_tag,
)

SETTLEMENT_TYPES = list(Settlement)

TECHNOLOGY_AGES = list(TechAge)

TRADE_CLASS_TYPES = list(TradeClass)


def collect_star_systems(
    planets: Iterable[Planet], stars: Iterable[StarHex] | None = None
) -> list[StarSystem]:
    starmap: dict[StarHex, StarSystem] = (
        {s: StarSystem(s) for s in stars} if stars else {}
    )
    for p in planets:
        s = p.star
        if s not in starmap:
            starmap[s] = StarSystem(s)
        starmap[s].add_planet(p)
    return sorted(starmap.values())


def make_stars(
    nameset: NameSet,
    density: int = DEFAULT_DENSITY,
    bounds: SectorBounds | None = None,
    roll: NomadDice = nomad_dice,
) -> list[StarHex]:
    if not bounds:
        bounds = SectorBounds() # use defaults

    # Check args
    assert MINIMUM_DENSITY <= density <= MAXIMUM_DENSITY
    assert bounds.x > 0
    assert bounds.y > 0
    assert bounds.height > 0
    assert bounds.width > 0
    assert roll

    return [
        StarHex(x=x, y=y, name=nameset.make_name())
        for x, y in itertools.product(bounds.x_range(), bounds.y_range())
        if roll(1, 0, MAXIMUM_DENSITY, MINIMUM_DENSITY) <= density
    ]


def make_planet(
    star: StarHex,
    name: str,
    settlement: Settlement | None = None,
    avg_age: TechAge | None = None,
    tcin: TradeClass | None = None,
    roll: NomadDice = nomad_dice,
) -> Planet:
    assert star
    assert name
    assert not settlement or settlement in SETTLEMENT_TYPES
    assert not avg_age or avg_age in TECHNOLOGY_AGES
    assert not tcin or tcin in TRADE_CLASS_TYPES
    assert roll

    tc: TradeClass = tcin or trade_class(settlement, roll)
    cha: Characteristic = characteristic(tc, roll)
    pop: int = population(tc, settlement, roll)
    ta: TechAge = tech_age(pop, avg_age, roll)

    return Planet(
        star=star,
        name=name,
        trade_class=tc,
        chara=cha,
        population=pop,
        tech_age=ta,
        world_tag_1=world_tag(1, roll),
        world_tag_2=world_tag(2, roll),
    )


def sector(
    nameset: NameSet,
    avg_age: TechAge | None = None,
    settlement: Settlement | None = None,
    density: int = DEFAULT_DENSITY,
    bounds: SectorBounds | None = None,
    roll: NomadDice = nomad_dice,
) -> Tuple[list[Planet], list[StarHex]]:

    # generate a map of stars
    stars: list[StarHex] = make_stars(
        nameset, density=density, bounds=bounds, roll=roll,
    )

    # generate (one) planet for each star
    planets: list[Planet] = [
        make_planet(s, s.name, settlement, avg_age, None, roll) for s in stars
    ]

    return planets, stars
