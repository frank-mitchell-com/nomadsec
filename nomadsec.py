#!/usr/bin/env python3

import argparse
import csv
import itertools
import json
import random
import string
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

# `pip install namemaker`
import namemaker # type: ignore

###################### CONSTANTS ###############################

# coordinates are always f"{width:0d}{height:0d}"
DEFAULT_SECTOR_HEIGHT: int = 10
DEFAULT_SECTOR_WIDTH: int = 8

# MINIMUM_DENSITY <= density < MAXIMUM_DENSITY
DEFAULT_DENSITY: int = 3
MAXIMUM_DENSITY: int = 6
MINIMUM_DENSITY: int = 1

####################### DICE #################################


def one_die() -> int:
    return random.randint(1, 6)


def nomad_dice(nkeep: int = 2, nadv: int = 0) -> int:
    """
    Roll `nkeep` + abs(`nadv`) 6-sided dice;
    if nadv is negative, keep the `nkeep`
    lowest, else keep the `nkeep` highest.
    """
    ntotal: int = nkeep + abs(nadv)
    rolls: list[int] = sorted((one_die() for _ in range(ntotal)))
    return sum(rolls[:nkeep]) if nadv < 0 else sum(rolls[-nkeep:])


####################### TABLES ################################

# All tables copied from the XD6 SRD.

SETTLEMENT_TYPES: list[str] = [
    "core",
    "settled",
    "conflict",
    "frontier",
    "unexplored",
]


class TradeClass(Enum):
    AGRICULTURAL = auto()
    GARDEN = auto()
    INDUSTRIAL = auto()
    NON_AGRICULTURAL = auto()
    NON_INDUSTRIAL = auto()
    POOR = auto()
    RESOURCE = auto()
    RICH = auto()


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


@dataclass
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


def trade_class(sector_type: str | None) -> TradeClass:
    result: int
    if sector_type == "unexplored":
        result = nomad_dice(2)
        return TRADE_CLASS_UNEXPLORED[result]
    if sector_type == "core":
        result = nomad_dice(2, +2)
    elif sector_type == "frontier":
        result = nomad_dice(2, -1)
    elif sector_type == "conflict":
        result = nomad_dice(2, +1)
    else:
        result = nomad_dice(2)
    return TRADE_CLASS_SETTLED[result]


def trade_class_str(trade: TradeClass | None) -> str:
    if not trade:
        return ""
    return string.capwords(trade.name.replace("_", " ")).replace(" ", "-")


def trade_class_abbrev(trade: TradeClass | None) -> str:
    return TRADE_CLASS_TO_ABBREVS[trade] if trade else ""


def characteristic(tc: TradeClass) -> Characteristic:
    assert tc in CHARACTERISTICS
    return CHARACTERISTICS[tc][one_die() - 1]


def chara_str(c: Characteristic | None) -> str:
    return c.name.capitalize() if c else ""


def chara_abbrev(c: Characteristic | None) -> str:
    return CHARACTERISTICS_TO_ABBREVS[c] if c else ""


def population(tc: TradeClass, settlement: str) -> int:
    if tc == TradeClass.POOR and settlement == "unexplored":
        return 0
    assert tc in POPULATION
    popspec: PopulationSpec = POPULATION[tc]
    pop: int = (nomad_dice(popspec.ndice) + popspec.modifier) * popspec.multiplier
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


def tech_age_random() -> TechAge:
    return TECHNOLOGY_AGES_TABLE[nomad_dice(2)]


def tech_age_offset(age: TechAge) -> TechAge:
    offset: int = TECHNOLOGY_AGES_OFFSET_TABLE[nomad_dice(2)]
    index: int = age.value
    if index + offset < TechAge.EARLY_PRIMITIVE.value:
        return TechAge.EARLY_PRIMITIVE
    if index + offset > TechAge.LATE_GALACTIC.value:
        return TechAge.LATE_GALACTIC
    return TECHNOLOGY_AGES[index + offset]


def tech_age(pop: int, avg_age: TechAge | None = None) -> TechAge:
    if pop == 0:
        return TechAge.NO_TECHNOLOGY
    return tech_age_offset(avg_age) if avg_age else tech_age_random()


def tech_age_str(age: TechAge | None) -> str:
    return string.capwords(age.name.replace("_", " ")) if age else ""


def tech_age_abbrev(age: TechAge | None) -> str:
    return TECHNOLOGY_AGES_TO_ABBREVS[age] if age else ""


def str_to_tech_age(agestr: str | None) -> TechAge | None:
    if agestr and agestr in TECHNOLOGY_AGES_ABBREVS:
        return TECHNOLOGY_AGES_ABBREVS[agestr]
    return None


def world_tag(index: int = 1) -> str:
    if index % 2 == 1:
        return WORLD_TAG_TABLE_1[one_die() - 1][one_die() - 1]
    return WORLD_TAG_TABLE_2[one_die() - 1][one_die() - 1]


####################### SECTORS ###############################


@dataclass
class StarHex:
    width: int
    height: int
    name: str
    trade_class: TradeClass | None
    chara: Characteristic | None
    population: int
    tech_age: TechAge | None
    world_tag_1: str
    world_tag_2: str


def sector(
    width: int = 8, height: int = 10, density: int = 3, x: int = 1, y: int = 1
) -> list[StarHex]:
    return [
        StarHex(w, h, "", None, None, 0, None, "", "")
        for w, h in itertools.product(range(x, width + x), range(y, height + y))
        if random.randint(MINIMUM_DENSITY, MAXIMUM_DENSITY) <= density
    ]


def populate_star(star: StarHex, settlement: str, avg_age: TechAge | None) -> None:
    star.trade_class = trade_class(settlement)
    star.chara = characteristic(star.trade_class)
    star.population = population(star.trade_class, settlement)
    star.tech_age = tech_age(star.population, avg_age)
    star.world_tag_1 = world_tag(1)
    star.world_tag_2 = world_tag(2)


def write_as_xsv(outfile, stars: Iterable[StarHex], sep: str = ",") -> None:
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
    for s in stars:
        writer.writerow(
            [
                s.name,
                f"{s.width:02d}{s.height:02d}",
                trade_class_str(s.trade_class),
                chara_str(s.chara),
                str(s.population),
                tech_age_str(s.tech_age),
                s.world_tag_1,
                s.world_tag_2,
            ]
        )


def write_as_text(outfile, stars: Iterable[StarHex], length: int) -> None:
    outfile.write(
        f"|{'Planet':{length}s}|Hex |Trade Class     |Chara.    "
        "|    Population|Tech. Age         |World Tags\n"
    )
    outfile.write(
        f"|{'-'*(length)}|----|----------------|----------"
        "|-------------:|------------------|------------------------------\n"
    )
    for s in stars:
        outfile.write(
            f"|{s.name:{length}s}"
            f"|{s.width:02d}{s.height:02d}"
            f"|{trade_class_str(s.trade_class):16s}"
            f"|{chara_str(s.chara):10s}"
            f"|{s.population:14_d}"
            f"|{tech_age_str(s.tech_age):18s}"
            f"|{s.world_tag_1}, {s.world_tag_2}\n"
        )


def write_as_short_text(outfile, stars: Iterable[StarHex], length: int) -> None:
    outfile.write(f"|{'Planet':{length}s}|Hex |TC|Ch|    Population|TA|World Tags\n")
    outfile.write(
        f"|{'-'*(length)}|----|--|--|-----:|--|------------------------------\n"
    )
    for s in stars:
        outfile.write(
            f"|{s.name:{length}s}"
            f"|{s.width:02d}{s.height:02d}"
            f"|{trade_class_abbrev(s.trade_class):2s}"
            f"|{chara_abbrev(s.chara):2s}"
            f"|{population_abbrev(s.population):6s}"
            f"|{tech_age_abbrev(s.tech_age):2s}"
            f"|{s.world_tag_1}, {s.world_tag_2}\n"
        )


class StarHexEncoder(json.JSONEncoder):
    def default(self, o) -> dict[str, Any]:
        if isinstance(o, StarHex):
            s: StarHex = o
            return {
                "name": s.name,
                "hex": f"{s.width:02d}{s.height:02d}",
                "trade_class": trade_class_str(s.trade_class),
                "characteristic": chara_str(s.chara),
                "population": s.population,
                "technology_age": tech_age_str(s.tech_age),
                "world_tags": [s.world_tag_1, s.world_tag_2],
            }
        return json.JSONEncoder.default(self, o)


def write_as_json(outfile, args, stars: Iterable[StarHex]) -> None:
    obj: dict = {
        "x": args.start_width,
        "y": args.start_height,
        "width": args.width,
        "height": args.height,
        "planets": stars,
    }
    json.dump(obj, outfile, cls=StarHexEncoder, indent=4)


def read_exclude_file(nameset, infile) -> None:
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
        choices=SETTLEMENT_TYPES,
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
    names = namemaker.make_name_set(args.namelist)

    if args.exclude_list:
        read_exclude_file(names, args.exclude_list)

    # generate a map of unnamed stars
    stars: list[StarHex] = sector(
        height=args.height,
        width=args.width,
        density=args.density,
        x=args.start_width,
        y=args.start_height,
    )

    length: int = 0
    avg_age: TechAge | None = str_to_tech_age(args.tech)
    settlement: str = args.settlement

    for star in stars:
        # generate a name for the star / planet
        star.name = names.make_name()
        length = max(length, len(star.name))
        # add attributes to star
        populate_star(star, settlement, avg_age)

    if args.debug:
        debug(f"planets={len(stars)}")
        debug(f"max_name_length={length}")

    # Print out the list of stars
    with args.output as outfile:
        if args.json:
            write_as_json(outfile, args, stars)
        elif args.separator:
            write_as_xsv(outfile, stars, args.separator)
        elif args.abbreviate:
            write_as_short_text(outfile, stars, length)
        else:
            write_as_text(outfile, stars, length)


if __name__ == "__main__":
    main()
