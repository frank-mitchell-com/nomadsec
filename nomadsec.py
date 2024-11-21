#!/usr/bin/env python3

# /// script
# requires-python = ">=3.12"
# dependencies = [
#    "namemaker"
# ]
# ///

import argparse
import csv
import itertools
import json
import random
import string
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import auto
from enum import Enum
from typing import Any, Protocol, Tuple

from namemaker import make_name_set  # type: ignore

###################### CONSTANTS ###############################

# Coordinates are expressed as (number across, number down) starting at 1
# ergo, the highest coordinate is f"{x+width-1:0d}{y+height-1:0d}"
DEFAULT_SECTOR_X: int = 1
DEFAULT_SECTOR_Y: int = 1
DEFAULT_SECTOR_HEIGHT: int = 10
DEFAULT_SECTOR_WIDTH: int = 8

# MINIMUM_DENSITY <= density < MAXIMUM_DENSITY
DEFAULT_DENSITY: int = 3
MAXIMUM_DENSITY: int = 6
MINIMUM_DENSITY: int = 1

##################### PROTOCOLS ##############################


class NomadDice(Protocol):
    def __call__(
        self, nkeep: int = 2, nadv: int = 0, nsides: int = 6, low: int = 1
    ) -> int:
        return 0    # keep type checkers happy


class NameSet(Protocol):
    def make_name(self) -> str:
        return ""   # keep type checkers happy

    def add_to_history(self, name_s) -> None: ...


####################### DICE #################################


def nomad_dice(nkeep: int = 2, nadv: int = 0, nsides: int = 6, low: int = 1) -> int:
    """
    Roll `nkeep` + abs(`nadv`) `nsides`-sided dice;
    if nadv is negative, keep the `nkeep`
    lowest, else keep the `nkeep` highest.
    """

    def one_die():
        return random.randint(low, nsides + low - 1)

    if nkeep == 1 and nadv == 0:
        return one_die()

    ntotal: int = nkeep + abs(nadv)
    rolls: list[int] = [one_die() for _ in range(ntotal)]
    rolls.sort()
    return sum(rolls[:nkeep]) if nadv < 0 else sum(rolls[-nkeep:])


####################### TABLES ################################

# All tables copied from the XD6 SRD.


class Settlement(Enum):
    CORE = auto()
    SETTLED = auto()
    CONFLICT = auto()
    FRONTIER = auto()
    UNEXPLORED = auto()


SETTLEMENT_TYPES: list[Settlement] = list(Settlement)


SETTLEMENT_TYPE_NAMES: dict[str, Settlement] = {
    "core": Settlement.CORE,
    "settled": Settlement.SETTLED,
    "conflict": Settlement.CONFLICT,
    "frontier": Settlement.FRONTIER,
    "unexplored": Settlement.UNEXPLORED,
}


class TradeClass(Enum):
    AGRICULTURAL = auto()
    GARDEN = auto()
    INDUSTRIAL = auto()
    NON_AGRICULTURAL = auto()
    NON_INDUSTRIAL = auto()
    POOR = auto()
    RESOURCE = auto()
    RICH = auto()


TRADE_CLASS_TYPES: list[TradeClass] = list(TradeClass)


TRADE_CLASS_TO_ABBREVS: dict[TradeClass, str] = {
    TradeClass.AGRICULTURAL: "Ag",
    TradeClass.GARDEN: "Ga",
    TradeClass.INDUSTRIAL: "In",
    TradeClass.NON_AGRICULTURAL: "Na",
    TradeClass.NON_INDUSTRIAL: "Ni",
    TradeClass.POOR: "Po",
    TradeClass.RESOURCE: "Re",
    TradeClass.RICH: "Ri",
}


TRADE_CLASS_SETTLED: dict[int, TradeClass] = {
    2: TradeClass.GARDEN,
    3: TradeClass.RESOURCE,
    4: TradeClass.POOR,
    5: TradeClass.POOR,
    6: TradeClass.NON_AGRICULTURAL,
    7: TradeClass.NON_INDUSTRIAL,
    8: TradeClass.AGRICULTURAL,
    9: TradeClass.AGRICULTURAL,
    10: TradeClass.RICH,
    11: TradeClass.RICH,
    12: TradeClass.INDUSTRIAL,
}


TRADE_CLASS_UNEXPLORED: dict[int, TradeClass] = {
    2: TradeClass.POOR,
    3: TradeClass.GARDEN,
    4: TradeClass.GARDEN,
    5: TradeClass.GARDEN,
    6: TradeClass.RESOURCE,
    7: TradeClass.RESOURCE,
    8: TradeClass.POOR,
    9: TradeClass.POOR,
    10: TradeClass.POOR,
    11: TradeClass.POOR,
    12: TradeClass.POOR,
}


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


CHARACTERISTICS_TO_ABBREVS: dict[Characteristic, str] = {
    Characteristic.ASTEROID: "As",
    Characteristic.CORROSIVE: "Co",
    Characteristic.DESERT: "De",
    Characteristic.ICEBALL: "Ic",
    Characteristic.INERT: "In",
    Characteristic.MARGINAL: "Ma",
    Characteristic.OCEAN: "Oc",
    Characteristic.PRIME: "Pr",
    Characteristic.PRIMORDIAL: "Pl",
    Characteristic.ROCKBALL: "Ro",
    Characteristic.TAINTED: "Ta",
}


CHARACTERISTICS: dict[TradeClass, list[Characteristic]] = {
    TradeClass.AGRICULTURAL: [
        Characteristic.PRIME,
        Characteristic.PRIME,
        Characteristic.TAINTED,
        Characteristic.TAINTED,
        Characteristic.MARGINAL,
        Characteristic.OCEAN,
    ],
    TradeClass.GARDEN: [
        Characteristic.PRIME,
        Characteristic.TAINTED,
        Characteristic.MARGINAL,
        Characteristic.OCEAN,
        Characteristic.DESERT,
        Characteristic.PRIMORDIAL,
    ],
    TradeClass.INDUSTRIAL: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.MARGINAL,
        Characteristic.TAINTED,
        Characteristic.TAINTED,
        Characteristic.ICEBALL,
    ],
    TradeClass.NON_AGRICULTURAL: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.ICEBALL,
        Characteristic.MARGINAL,
        Characteristic.TAINTED,
        Characteristic.INERT,
    ],
    TradeClass.NON_INDUSTRIAL: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.ROCKBALL,
        Characteristic.MARGINAL,
        Characteristic.TAINTED,
        Characteristic.INERT,
    ],
    TradeClass.POOR: [
        Characteristic.ROCKBALL,
        Characteristic.ROCKBALL,
        Characteristic.ICEBALL,
        Characteristic.ASTEROID,
        Characteristic.INERT,
        Characteristic.CORROSIVE,
    ],
    TradeClass.RESOURCE: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.ICEBALL,
        Characteristic.MARGINAL,
        Characteristic.INERT,
        Characteristic.CORROSIVE,
    ],
    TradeClass.RICH: [
        Characteristic.PRIME,
        Characteristic.PRIME,
        Characteristic.TAINTED,
        Characteristic.TAINTED,
        Characteristic.MARGINAL,
        Characteristic.OCEAN,
    ],
}


@dataclass(frozen=True, slots=True)
class PopulationSpec:
    ndice: int
    modifier: int
    multiplier: int


POPULATION: dict[TradeClass, PopulationSpec] = {
    TradeClass.AGRICULTURAL: PopulationSpec(1, 0, 50_000_000),
    TradeClass.GARDEN: PopulationSpec(0, 0, 0),
    TradeClass.INDUSTRIAL: PopulationSpec(2, 0, 500_000_000),
    TradeClass.NON_AGRICULTURAL: PopulationSpec(1, 0, 200_000_000),
    TradeClass.NON_INDUSTRIAL: PopulationSpec(2, 0, 50_000),
    TradeClass.POOR: PopulationSpec(2, -8, 500),  # none if unexplored
    TradeClass.RESOURCE: PopulationSpec(0, 0, 0),
    TradeClass.RICH: PopulationSpec(4, 0, 100_000_000),
}


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


TECHNOLOGY_AGES: list[TechAge] = list(TechAge)


TECHNOLOGY_AGES_ABBREVS: dict[str, TechAge] = {
    "ep": TechAge.EARLY_PRIMITIVE,
    "lp": TechAge.LATE_PRIMITIVE,
    "em": TechAge.EARLY_MECHANICAL,
    "lm": TechAge.LATE_MECHANICAL,
    "ea": TechAge.EARLY_ATOMIC,
    "la": TechAge.LATE_ATOMIC,
    "es": TechAge.EARLY_SPACE,
    "ls": TechAge.LATE_SPACE,
    "ei": TechAge.EARLY_INTERSTELLAR,
    "li": TechAge.LATE_INTERSTELLAR,
    "eg": TechAge.EARLY_GALACTIC,
    "lg": TechAge.LATE_GALACTIC,
}


TECHNOLOGY_AGES_TO_ABBREVS: dict[TechAge, str] = {
    TechAge.NO_TECHNOLOGY: "NT",
    TechAge.EARLY_PRIMITIVE: "EP",
    TechAge.LATE_PRIMITIVE: "LP",
    TechAge.EARLY_MECHANICAL: "EM",
    TechAge.LATE_MECHANICAL: "LM",
    TechAge.EARLY_ATOMIC: "EA",
    TechAge.LATE_ATOMIC: "LA",
    TechAge.EARLY_SPACE: "ES",
    TechAge.LATE_SPACE: "LS",
    TechAge.EARLY_INTERSTELLAR: "EI",
    TechAge.LATE_INTERSTELLAR: "LI",
    TechAge.EARLY_GALACTIC: "EG",
    TechAge.LATE_GALACTIC: "LG",
    TechAge.COSMIC: "C",
}


TECHNOLOGY_AGES_TABLE: dict[int, TechAge] = {
    2: TechAge.EARLY_PRIMITIVE,
    3: TechAge.LATE_PRIMITIVE,
    4: TechAge.LATE_MECHANICAL,
    5: TechAge.LATE_ATOMIC,
    6: TechAge.EARLY_SPACE,
    7: TechAge.LATE_SPACE,
    8: TechAge.EARLY_INTERSTELLAR,
    9: TechAge.LATE_INTERSTELLAR,
    10: TechAge.EARLY_INTERSTELLAR,  # (sic)
    11: TechAge.EARLY_GALACTIC,
    12: TechAge.LATE_GALACTIC,
}


TECHNOLOGY_AGES_OFFSET_TABLE: dict[int, int] = {
    2: -2,
    3: -1,
    4: -1,
    5: -1,
    6: +0,
    7: +0,
    8: +0,
    9: +0,
    10: +1,
    11: +1,
    12: +2,
}


WORLD_TAG_TABLE_1: list[list[str]] = [
    [
        "Alien Ruins",
        "Ancient Ruins",
        "Battleground",
        "Capitalist",
        "Caste System",
        "Civil War",
    ],
    [
        "Corporate",
        "Declining Population",
        "Desert",
        "Feral World",
        "Forbidden Tech",
        "Glaciers",
    ],
    [
        "Historical Culture",
        "Honorable",
        "Impending Doom",
        "Liberal",
        "Mercenaries",
        "Misandry/Misogyny",
    ],
    [
        "Multiple Species",
        "Nomads",
        "Peaceful",
        "Police State",
        "Psionics",
        "Radioactive",
    ],
    [
        "Restrictive Laws",
        "Robots",
        "Segregated",
        "Separate Cultures",
        "Superstitious",
        "Terraforming",
    ],
    [
        "Trade Hub",
        "Underground Cities",
        "Unusual Tech",
        "Utopia",
        "Xeno-archeology",
        "Xenophobia",
    ],
]


WORLD_TAG_TABLE_2: list[list[str]] = [
    [
        "Altered Humanity",
        "Athenian Democracy",
        "Beautiful",
        "Captive Government",
        "Charismatic Dictator",
        "Cold War",
    ],
    [
        "Cyborgs",
        "Democracy",
        "Eugenics",
        "Feudal",
        "Freak Weather",
        "Gladiators",
    ],
    [
        "Holy War",
        "Hostile Space",
        "Jungle World",
        "Megafauna",
        "Minimal Laws",
        "Multiple Govs.",
    ],
    [
        "Night/Day",
        "Oceans",
        "Pleasure World",
        "Primitives",
        "Quarantined",
        "Religious",
    ],
    [
        "Rigid Culture",
        "Salvage Economy",
        "Seismic Instability",
        "Slavery",
        "Taboo Custom",
        "Theocracy",
    ],
    [
        "Transhuman",
        "Unusual Custom",
        "Unusual Weather",
        "Warlords",
        "Xenophiles",
        "Zombies",
    ],
]

####################### TABLE LOOKUPS #############################


def str_to_settlement(name: str | None) -> Settlement | None:
    return SETTLEMENT_TYPE_NAMES.get(name) if name else None


def trade_class(settle: Settlement | None, roll: NomadDice = nomad_dice) -> TradeClass:
    assert not settle or settle in SETTLEMENT_TYPES
    assert roll

    result: int
    if settle == Settlement.UNEXPLORED:
        result = roll(2)
        return TRADE_CLASS_UNEXPLORED[result]
    if settle == Settlement.CORE:
        result = roll(2, +2)
    elif settle == Settlement.FRONTIER:
        result = roll(2, -1)
    elif settle == Settlement.CONFLICT:
        result = roll(2, +1)
    else:
        result = roll(2)
    return TRADE_CLASS_SETTLED[result]


def trade_class_str(trade: TradeClass | None) -> str:
    assert not trade or trade in TRADE_CLASS_TYPES
    if not trade:
        return ""
    return string.capwords(trade.name.replace("_", " ")).replace(" ", "-")


def trade_class_abbrev(trade: TradeClass | None) -> str:
    assert not trade or trade in TRADE_CLASS_TYPES
    return TRADE_CLASS_TO_ABBREVS[trade] if trade else ""


def characteristic(tc: TradeClass, roll: NomadDice = nomad_dice) -> Characteristic:
    assert tc in CHARACTERISTICS
    return CHARACTERISTICS[tc][roll(1) - 1]


def chara_str(c: Characteristic | None) -> str:
    return c.name.capitalize() if c else ""


def chara_abbrev(c: Characteristic | None) -> str:
    return CHARACTERISTICS_TO_ABBREVS[c] if c else ""


def population(
    tc: TradeClass, settle: Settlement | None, roll: NomadDice = nomad_dice
) -> int:
    assert tc in TRADE_CLASS_TYPES
    assert not settle or settle in SETTLEMENT_TYPES
    assert roll

    if tc == TradeClass.POOR and settle == Settlement.UNEXPLORED:
        return 0
    assert tc in POPULATION
    popspec: PopulationSpec = POPULATION[tc]
    pop: int = (roll(popspec.ndice) + popspec.modifier) * popspec.multiplier
    return max(pop, 0)


def population_abbrev(pop: int) -> str:
    # sourcery skip: assign-if-exp, reintroduce-else
    if pop == 0:
        return f"{pop:6d}"
    if pop % 1_000_000_000 == 0:
        return f"{pop//1_000_000_000:5d}B"
    if pop % 1_000_000 == 0:
        return f"{pop//1_000_000:5d}M"
    if pop % 1_000 == 0:
        return f"{pop//1_000:5d}K"
    return f"{pop:6d}"


def tech_age_random(roll: NomadDice = nomad_dice) -> TechAge:
    assert roll
    return TECHNOLOGY_AGES_TABLE[roll(2)]


def tech_age_offset(age: TechAge, roll: NomadDice = nomad_dice) -> TechAge:
    assert age in TECHNOLOGY_AGES
    assert roll

    offset: int = TECHNOLOGY_AGES_OFFSET_TABLE[roll(2)]
    index: int = age.value
    if index + offset < TechAge.EARLY_PRIMITIVE.value:
        return TechAge.EARLY_PRIMITIVE
    if index + offset > TechAge.LATE_GALACTIC.value:
        return TechAge.LATE_GALACTIC
    return TECHNOLOGY_AGES[index + offset]


def tech_age(
    pop: int, avg_age: TechAge | None = None, roll: NomadDice = nomad_dice
) -> TechAge:
    assert not avg_age or avg_age in TECHNOLOGY_AGES
    assert roll
    if pop == 0:
        return TechAge.NO_TECHNOLOGY
    return tech_age_offset(avg_age, roll) if avg_age else tech_age_random(roll)


def tech_age_str(age: TechAge | None) -> str:
    return string.capwords(age.name.replace("_", " ")) if age else ""


def tech_age_abbrev(age: TechAge | None) -> str:
    return TECHNOLOGY_AGES_TO_ABBREVS.get(age, "") if age else ""


def str_to_tech_age(agestr: str | None) -> TechAge | None:
    return TECHNOLOGY_AGES_ABBREVS.get(agestr) if agestr else None


def world_tag(index: int = 1, roll: NomadDice = nomad_dice) -> str:
    assert roll
    if index % 2 == 1:
        return WORLD_TAG_TABLE_1[roll(1) - 1][roll(1) - 1]
    return WORLD_TAG_TABLE_2[roll(1) - 1][roll(1) - 1]


####################### SECTORS ###############################


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


    def x_range(self) -> Iterable[int]:
        return range(self.x, self.width + self.x)


    def y_range(self) -> Iterable[int]:
        return range(self.y, self.height + self.y)


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

    b: SectorBounds = bounds if bounds else SectorBounds()

    # Check args
    assert MINIMUM_DENSITY <= density <= MAXIMUM_DENSITY
    assert b.height > 0
    assert b.width > 0
    assert b.x > 0
    assert b.y > 0
    assert roll

    return [
        StarHex(x=x, y=y, name=nameset.make_name())
        for x, y in itertools.product(b.x_range(), b.y_range())
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
        nameset, density=density, bounds=bounds, roll=roll
    )

    # generate (one) planet for each star
    planets: list[Planet] = [
        make_planet(s, s.name, settlement, avg_age, None, roll) for s in stars
    ]

    return planets, stars


####################### OUTPUT #####################################


def max_name_length(planets: Iterable[Planet]) -> int:
    length: int = 0
    for p in planets:
        length = max(length, len(p.name), len(p.star.name))
    return length


def write_as_xsv(outfile, planets: Iterable[Planet], sep: str = ",") -> None:
    writer = csv.writer(
        outfile, delimiter=sep, quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    writer.writerow(
        [
            "Planet",
            "Hex",
            "Trade Class",
            "Chara.",
            "Population",
            "Tech. Age",
            "World Tag 1",
            "World Tag 2",
        ]
    )
    for p in planets:
        writer.writerow(
            [
                p.name,
                p.hexcode,
                trade_class_str(p.trade_class),
                chara_str(p.chara),
                str(p.population),
                tech_age_str(p.tech_age),
                p.world_tag_1,
                p.world_tag_2,
            ]
        )


def write_as_text(outfile, planets: Iterable[Planet]) -> None:
    length: int = max_name_length(planets)

    outfile.write(
        f"|{'Planet':{length}s}|Hex |Trade Class     |Chara.    "
        "|    Population|Tech. Age         |World Tags\n"
    )
    outfile.write(
        f"|{'-'*(length)}|----|----------------|----------"
        "|-------------:|------------------|------------------------------\n"
    )
    for p in planets:
        outfile.write(
            f"|{p.name:{length}s}"
            f"|{p.hexcode}"
            f"|{trade_class_str(p.trade_class):16s}"
            f"|{chara_str(p.chara):10s}"
            f"|{p.population:14_d}"
            f"|{tech_age_str(p.tech_age):18s}"
            f"|{p.world_tag_1}, {p.world_tag_2}\n"
        )


def write_as_short_text(outfile, planets: Iterable[Planet]) -> None:
    length: int = max_name_length(planets)

    outfile.write(f"|{'Planet':{length}s}|Hex |TC|Ch|    Population|TA|World Tags\n")
    outfile.write(
        f"|{'-'*(length)}|----|--|--|-----:|--|------------------------------\n"
    )
    for p in planets:
        outfile.write(
            f"|{p.name:{length}s}"
            f"|{p.hexcode}"
            f"|{trade_class_abbrev(p.trade_class):2s}"
            f"|{chara_abbrev(p.chara):2s}"
            f"|{population_abbrev(p.population):6s}"
            f"|{tech_age_abbrev(p.tech_age):2s}"
            f"|{p.world_tag_1}, {p.world_tag_2}\n"
        )


class StarPlanetEncoder(json.JSONEncoder):
    def default(self, o) -> dict[str, Any]:
        if isinstance(o, Planet):
            p: Planet = o
            return {
                "name": p.name,
                "hex": p.hexcode,
                "trade_class": trade_class_str(p.trade_class),
                "characteristic": chara_str(p.chara),
                "population": p.population,
                "technology_age": tech_age_str(p.tech_age),
                "world_tags": [p.world_tag_1, p.world_tag_2],
            }
        if isinstance(o, StarHex):
            s: StarHex = o
            return {
                "name": s.name,
                "hex": s.hexcode,
            }
        if isinstance(o, StarSystem):
            ss: StarSystem = o
            return {
                "star": ss.star,
                "planets": ss.planets,
            }
        return json.JSONEncoder.default(self, o)


def write_as_json(
    outfile,
    bounds: SectorBounds,
    planets: Iterable[Planet],
    stars: Iterable[StarHex] | None = None,
) -> None:
    systems: list[StarSystem] = collect_star_systems(planets, stars)
    obj: dict = {
        "x": bounds.x,
        "y": bounds.y,
        "width": bounds.width,
        "height": bounds.height,
        "planets": planets,
        "systems": systems,
    }
    json.dump(obj, outfile, cls=StarPlanetEncoder, indent=4)


######################### MAIN #########################################


def read_exclude_file(nameset: NameSet, infile) -> None:
    with infile:
        for line in infile.readlines():
            name: str = line.strip()
            nameset.add_to_history(name)


def debug(*args, **kwargs) -> None:
    print("DEBUG:", *args, file=sys.stderr, **kwargs)


def main() -> None:
    # sourcery skip: extract-method
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Generate a sector for the _FTL: Nomad_ RPG"
    )
    parser.add_argument(
        "-n",
        "--namelist",
        help="text file providing example names",
        default="Greek mythology.txt",
    )
    parser.add_argument(
        "-x",
        "--exclude-list",
        help="text file providing names NOT to use",
        type=argparse.FileType(mode="r", encoding="UTF-8"),
    )
    parser.add_argument(
        "-W",
        "--width",
        help="number of hexes/parsecs across",
        default=DEFAULT_SECTOR_WIDTH,
        type=int,
    )
    parser.add_argument(
        "-H",
        "--height",
        help="number of hexes/parsecs down",
        default=DEFAULT_SECTOR_HEIGHT,
        type=int,
    )
    parser.add_argument(
        "-X",
        "--start-width",
        help="first index across",
        default=1,
        type=int,
    )
    parser.add_argument(
        "-Y",
        "--start-height",
        help="first index down",
        default=1,
        type=int,
    )
    parser.add_argument(
        "-d",
        "--density",
        help="density of stars (n in 6)",
        default=DEFAULT_DENSITY,
        type=int,
        choices=range(MINIMUM_DENSITY, MAXIMUM_DENSITY),
    )
    parser.add_argument(
        "-s",
        "--settlement",
        help="settlement level of sector",
        default="settled",
        type=str,
        choices=list(SETTLEMENT_TYPE_NAMES),
    )
    parser.add_argument(
        "-t",
        "--tech",
        help="technology age of sector",
        type=str,
        choices=list(TECHNOLOGY_AGES_ABBREVS),
    )
    parser.add_argument(
        "-D",
        "--debug",
        help="write debugging info to error stream",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output file",
        default="-",
        type=argparse.FileType(mode="w", encoding="UTF-8"),
    )
    parser.add_argument(
        "-a",
        "--abbreviate",
        help="abbreviate common strings in default format",
        action="store_true",
    )
    parser.add_argument(
        "-j",
        "--json",
        help="write output as JSON",
        action="store_true",
    )
    parser.add_argument(
        "--separator",
        help="write with the given character as a separator",
    )
    parser.add_argument(
        "--csv",
        help="write as comma-separated values",
        action="store_const",
        dest="separator",
        const=",",
    )
    parser.add_argument(
        "--tsv",
        help="write as tab-separated values",
        action="store_const",
        dest="separator",
        const="\t",
    )
    args = parser.parse_args()

    if args.debug:
        debug(f"namelist={args.namelist}")
        debug(f"x={args.start_width} y={args.start_height}")
        debug(f"width={args.width} height={args.height}")
        debug(f"density={args.density}")
        debug(f"settlement={args.settlement}")
        debug(f"tech={args.tech}")

    # initialize namemaker
    nameset: NameSet = make_name_set(args.namelist)

    if args.exclude_list:
        read_exclude_file(nameset, args.exclude_list)

    bounds: SectorBounds = SectorBounds(
        height=args.height,
        width=args.width,
        x=args.start_width,
        y=args.start_height,
    )

    planets, stars = sector(
        nameset=nameset,
        settlement=str_to_settlement(args.settlement),
        avg_age=str_to_tech_age(args.tech),
        density=args.density,
        bounds=bounds,
    )

    if args.debug:
        debug(f"stars={len(stars)}")
        debug(f"planets={len(planets)}")

    # Print out the list of stars
    with args.output as outfile:
        if args.json:
            write_as_json(outfile, bounds, planets, stars)
        elif args.separator:
            write_as_xsv(outfile, planets, args.separator)
        elif args.abbreviate:
            write_as_short_text(outfile, planets)
        else:
            write_as_text(outfile, planets)


if __name__ == "__main__":
    main()
