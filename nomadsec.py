#!/usr/bin/env python3

import argparse
import itertools
import random
import string
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, auto

# `pip install namemaker`
import namemaker

###################### CONSTANTS ###############################

# maximum retries to find a unique star name
MAX_RETRIES: int = 1_000_000

# default number of chars for star names
DEFAULT_MAX_NAME_LENGTH: int = 13

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


def nomad_dice(nkeep: int = 2, nadv: int = 0, disadvantage=True) -> int:
    """
    Roll `nkeep` + abs(`nadv`) 6-sided dice;
    if nadv is negative, keep the `nkeep`
    lowest, else keep the `nkeep` highest.
    """
    ntotal: int = nkeep + abs(nadv)
    rolls: list[int] = sorted((one_die() for _ in range(ntotal)))
    if nadv < 0 or disadvantage:
        return sum(rolls[:nkeep])
    else:
        return sum(rolls[-nkeep:])


####################### TABLES ################################

# All tables copied from the XD6 SRD.

SETTLEMENT_TYPES: list[str] = [
    "core",
    "settled",
    "conflict",
    "frontier",
    "unexplored",
]


class Trade_Class(Enum):
    AGRICULTURAL = auto()
    GARDEN = auto()
    INDUSTRIAL = auto()
    NON_AGRICULTURAL = auto()
    NON_INDUSTRIAL = auto()
    POOR = auto()
    RESOURCE = auto()
    RICH = auto()


TRADE_CLASS_SETTLED: dict[int, str] = {
    2: Trade_Class.GARDEN,
    3: Trade_Class.RESOURCE,
    4: Trade_Class.POOR,
    5: Trade_Class.POOR,
    6: Trade_Class.NON_AGRICULTURAL,
    7: Trade_Class.NON_INDUSTRIAL,
    8: Trade_Class.AGRICULTURAL,
    9: Trade_Class.AGRICULTURAL,
    10: Trade_Class.RICH,
    11: Trade_Class.RICH,
    12: Trade_Class.INDUSTRIAL,
}

TRADE_CLASS_UNEXPLORED: dict[int, str] = {
    2: Trade_Class.POOR,
    3: Trade_Class.GARDEN,
    4: Trade_Class.GARDEN,
    5: Trade_Class.GARDEN,
    6: Trade_Class.RESOURCE,
    7: Trade_Class.RESOURCE,
    8: Trade_Class.POOR,
    9: Trade_Class.POOR,
    10: Trade_Class.POOR,
    11: Trade_Class.POOR,
    12: Trade_Class.POOR,
}

CHARACTERISTICS: dict[Trade_Class, list[str]] = {
    Trade_Class.AGRICULTURAL: [
        "Prime",
        "Prime",
        "Tainted",
        "Tainted",
        "Marginal",
        "Ocean",
    ],
    Trade_Class.GARDEN: [
        "Prime",
        "Tainted",
        "Marginal",
        "Ocean",
        "Desert",
        "Primordial",
    ],
    Trade_Class.INDUSTRIAL: [
        "Asteroid",
        "Rockball",
        "Marginal",
        "Tainted",
        "Tainted",
        "Iceball",
    ],
    Trade_Class.NON_AGRICULTURAL: [
        "Asteroid",
        "Rockball",
        "Iceball",
        "Marginal",
        "Tainted",
        "Inert",
    ],
    Trade_Class.NON_INDUSTRIAL: [
        "Asteroid",
        "Rockball",
        "Rockball",
        "Marginal",
        "Tainted",
        "Inert",
    ],
    Trade_Class.POOR: [
        "Rockball",
        "Rockball",
        "Iceball",
        "Asteroid",
        "Inert",
        "Corrosive",
    ],
    Trade_Class.RESOURCE: [
        "Asteroid",
        "Rockball",
        "Iceball",
        "Marginal",
        "Inert",
        "Corrosive",
    ],
    Trade_Class.RICH: [
        "Prime",
        "Prime",
        "Tainted",
        "Tainted",
        "Marginal",
        "Ocean",
    ],
}


@dataclass
class Population_Spec:
    ndice: int
    modifier: int
    multiplier: int


POPULATION: dict[Trade_Class, Population_Spec] = {
    Trade_Class.AGRICULTURAL: Population_Spec(1, 0, 50_000_000),
    Trade_Class.GARDEN: Population_Spec(0, 0, 0),
    Trade_Class.INDUSTRIAL: Population_Spec(2, 0, 500_000_000),
    Trade_Class.NON_AGRICULTURAL: Population_Spec(1, 0, 200_000_000),
    Trade_Class.NON_INDUSTRIAL: Population_Spec(2, 0, 50_000),
    Trade_Class.POOR: Population_Spec(2, -8, 500),  # none if unexplored
    Trade_Class.RESOURCE: Population_Spec(0, 0, 0),
    Trade_Class.RICH: Population_Spec(4, 0, 100_000_000),
}


class Tech_Age(Enum):
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


TECHNOLOGY_AGES: list[Tech_Age] = list(Tech_Age)

TECHNOLOGY_AGES_ABBREVS: dict[str, Tech_Age] = {
    "ep": Tech_Age.EARLY_PRIMITIVE,
    "lp": Tech_Age.LATE_PRIMITIVE,
    "em": Tech_Age.EARLY_MECHANICAL,
    "lm": Tech_Age.LATE_MECHANICAL,
    "ea": Tech_Age.EARLY_ATOMIC,
    "la": Tech_Age.LATE_ATOMIC,
    "es": Tech_Age.EARLY_SPACE,
    "ls": Tech_Age.LATE_SPACE,
    "ei": Tech_Age.EARLY_INTERSTELLAR,
    "li": Tech_Age.LATE_INTERSTELLAR,
    "eg": Tech_Age.EARLY_GALACTIC,
    "lg": Tech_Age.LATE_GALACTIC,
}

TECHNOLOGY_AGES_TABLE: dict[int, Tech_Age] = {
    2: Tech_Age.EARLY_PRIMITIVE,
    3: Tech_Age.LATE_PRIMITIVE,
    4: Tech_Age.LATE_MECHANICAL,
    5: Tech_Age.LATE_ATOMIC,
    6: Tech_Age.EARLY_SPACE,
    7: Tech_Age.LATE_SPACE,
    8: Tech_Age.EARLY_INTERSTELLAR,
    9: Tech_Age.LATE_INTERSTELLAR,
    10: Tech_Age.EARLY_INTERSTELLAR,  # (sic)
    11: Tech_Age.EARLY_GALACTIC,
    12: Tech_Age.LATE_GALACTIC,
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


def trade_class(sector_type: str | None) -> str:
    result: int
    if sector_type == "unexplored":
        result = nomad_dice(2)
        return TRADE_CLASS_UNEXPLORED[result]
    else:
        if sector_type == "core":
            result = nomad_dice(2, +2)
        elif sector_type == "frontier":
            result = nomad_dice(2, -1)
        elif sector_type == "conflict":
            result = nomad_dice(2, +1)
        else:
            result = nomad_dice(2)
        return TRADE_CLASS_SETTLED[result]


def trade_class_str(trade: Trade_Class) -> str:
    return string.capwords(trade.name.replace("_", " ")).replace(" ", "-")


def characteristic(trade_class: str) -> str:
    assert trade_class in CHARACTERISTICS
    return CHARACTERISTICS[trade_class][one_die() - 1]


def population(trade_class: Trade_Class, settlement: str) -> int:
    if trade_class == Trade_Class.POOR and settlement == "unexplored":
        return 0
    else:
        assert trade_class in POPULATION
        popspec: Population_Spec = POPULATION[trade_class]
        pop: int = (nomad_dice(popspec.ndice) + popspec.modifier) * popspec.multiplier
        if pop < 0:
            return 0
        return pop


def tech_age() -> Tech_Age:
    return TECHNOLOGY_AGES_TABLE[nomad_dice(2)]


def tech_age_offset(age: Tech_Age) -> Tech_Age:
    offset: int = TECHNOLOGY_AGES_OFFSET_TABLE[nomad_dice(2)]
    index: int = age.value
    if index + offset < 0:
        return Tech_Age.NO_TECHNOLOGY
    elif index + offset > len(Tech_Age):
        return Tech_Age.COSMIC
    else:
        return TECHNOLOGY_AGES[index + offset]


def tech_age_str(age: Tech_Age) -> str:
    return string.capwords(age.name.replace("_", " "))


def world_tag(index: int = 1) -> str:
    if index % 2 == 1:
        return WORLD_TAG_TABLE_1[one_die() - 1][one_die() - 1]
    else:
        return WORLD_TAG_TABLE_2[one_die() - 1][one_die() - 1]


####################### SECTORS ###############################


@dataclass
class Star_Hex:
    width: int
    height: int
    name: str
    trade_class: Trade_Class | None
    characteristic: str
    population: int
    tech_age: Tech_Age | None
    world_tag_1: str
    world_tag_2: str


def sector(height: int, width: int, density: int) -> Sequence[Star_Hex]:
    # Generate a number of stars proportional to density
    result: list[Star_Hex] = []
    for w, h in itertools.product(range(1, width + 1), range(1, height + 1)):
        if random.randint(MINIMUM_DENSITY, MAXIMUM_DENSITY) <= density:
            result.append(Star_Hex(w, h, "", None, "", 0, None, "", ""))
    return result


def trim_str(name: str, length: int) -> str:
    return name[:length]


def main() -> None:
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
        "--width",
        help="number of hexes/parsecs across",
        default=DEFAULT_SECTOR_WIDTH,
        type=int,
    )
    parser.add_argument(
        "-y",
        "--height",
        help="number of hexes/parsecs down",
        default=DEFAULT_SECTOR_HEIGHT,
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
        "-l",
        "--length",
        help="maximum length of star names",
        default=DEFAULT_MAX_NAME_LENGTH,
        type=int,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output file",
        default="-",
        type=argparse.FileType(mode="w", encoding="UTF-8"),
    )
    args = parser.parse_args()

    # initialize namemaker
    names = namemaker.make_name_set(args.namelist)

    # generate a map of unnamed stars
    stars: Sequence[Star_Hex] = sector(args.height, args.width, args.density)

    for star in stars:
        # generate a name for the star / planet
        star.name = trim_str(names.make_name(), args.length)
        # generate the trade type
        star.trade_class = trade_class(args.settlement)
        star.characteristic = characteristic(star.trade_class)
        star.population = population(star.trade_class, args.settlement)
        if star.population == 0:
            # This isn't in the rules, but it makes sense to me
            star.tech_age = Tech_Age.NO_TECHNOLOGY  # No Technology
        elif args.tech:
            age: Tech_Age = TECHNOLOGY_AGES_ABBREVS[args.tech]
            star.tech_age = tech_age_offset(age)
        else:
            star.tech_age = tech_age()
        star.world_tag_1 = world_tag(1)
        star.world_tag_2 = world_tag(2)

    # TODO: Customize format:
    #    - Default format, i.e. what's below.
    #    - Traveller format: see <https://travellermap.com/doc/fileformats>;
    #      need to generate or fake UPPs etc.

    # Print out the list of stars
    with args.output as outfile:
        outfile.write(
            f"# width={args.width} height={args.height} density={args.density}\n"
        )
        outfile.write(f"# settlement={args.settlement} tech={args.tech}\n")
        outfile.write(f"# planets={len(stars)}\n")
        outfile.write(
            f"#{'Planet':{args.length}s} Hex Trade Class      Charactr. "
            "     Population Tech. Age          World Tags\n"
        )
        outfile.write(
            f"#{'-'*(args.length-1)} ---- ---------------- ----------"
            " -------------- ------------------ ------------------------------\n"
        )
        for s in stars:
            outfile.write(
                f"{s.name:{args.length}s}"
                f" {s.width:02d}{s.height:02d}"
                f" {trade_class_str(s.trade_class):16s}"
                f" {s.characteristic:10s}"
                f" {s.population:14_d}"
                f" {tech_age_str(s.tech_age):18s}"
                f" {s.world_tag_1}, {s.world_tag_2}\n"
            )


if __name__ == "__main__":
    main()
