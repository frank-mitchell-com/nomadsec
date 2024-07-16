#!/usr/bin/env python3

import itertools
import random
import argparse
from collections.abc import Sequence
from dataclasses import dataclass

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


TRADE_CLASS_SETTLED: dict[int, str] = {
    2: "Garden",
    3: "Resource",
    4: "Poor",
    5: "Poor",
    6: "Non-Agricultural",
    7: "Non-Industrial",
    8: "Agricultural",
    9: "Agricultural",
    10: "Rich",
    11: "Rich",
    12: "Industrial",
}

TRADE_CLASS_UNEXPLORED: dict[int, str] = {
    2: "Poor",
    3: "Garden",
    4: "Garden",
    5: "Garden",
    6: "Resource",
    7: "Resource",
    8: "Poor",
    9: "Poor",
    10: "Poor",
    11: "Poor",
    12: "Poor",
}

CHARACTERISTICS: dict[str, list[str]] = {
    "Agricultural": [
        "Prime",
        "Prime",
        "Tainted",
        "Tainted",
        "Marginal",
        "Ocean",
    ],
    "Garden": [
        "Prime",
        "Tainted",
        "Marginal",
        "Ocean",
        "Desert",
        "Primordial",
    ],
    "Industrial": [
        "Asteroid",
        "Rockball",
        "Marginal",
        "Tainted",
        "Tainted",
        "Iceball",
    ],
    "Non-Agricultural": [
        "Asteroid",
        "Rockball",
        "Iceball",
        "Marginal",
        "Tainted",
        "Inert",
    ],
    "Non-Industrial": [
        "Asteroid",
        "Rockball",
        "Rockball",
        "Marginal",
        "Tainted",
        "Inert",
    ],
    "Poor": [
        "Rockball",
        "Rockball",
        "Iceball",
        "Asteroid",
        "Inert",
        "Corrosive",
    ],
    "Resource": [
        "Asteroid",
        "Rockball",
        "Iceball",
        "Marginal",
        "Inert",
        "Corrosive",
    ],
    "Rich": [
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


POPULATION: dict[str, Population_Spec] = {
    "Agricultural": Population_Spec(1, 0, 50_000_000),
    "Garden": Population_Spec(0, 0, 0),
    "Industrial": Population_Spec(2, 0, 500_000_000),
    "Non-Agricultural": Population_Spec(1, 0, 200_000_000),
    "Non-Industrial": Population_Spec(2, 0, 50_000),
    "Poor": Population_Spec(2, -8, 500),  # none if unexplored
    "Resource": Population_Spec(0, 0, 0),
    "Rich": Population_Spec(4, 0, 100_000_000),
}


TECHNOLOGY_AGES: list[str] = [
    "No Technology",
    "Early Primitive",
    "Late Primitive",
    "Early Mechanical",
    "Late Mechanical",
    "Early Atomic",
    "Late Atomic",
    "Early Space",
    "Late Space",
    "Early Interstellar",
    "Late Interstellar",
    "Early Galactic",
    "Late Galactic",
    "Cosmic",
]

TECHNOLOGY_AGES_ABBREVS: dict[str, str] = {
    "ep": "Early Primitive",
    "lp": "Late Primitive",
    "em": "Early Mechanical",
    "lm": "Late Mechanical",
    "ea": "Early Atomic",
    "la": "Late Atomic",
    "es": "Early Space",
    "ls": "Late Space",
    "ei": "Early Interstellar",
    "li": "Late Interstellar",
    "eg": "Early Galactic",
    "lg": "Late Galactic",
}

TECHNOLOGY_AGES_TABLE: dict[int, str] = {
    2: "Early Primitive",
    3: "Late Primitive",
    4: "Late Mechanical",
    5: "Late Atomic",
    6: "Early Space",
    7: "Late Space",
    8: "Early Interstellar",
    9: "Late Interstellar",
    10: "Early Interstellar",  # (sic)
    11: "Early Galactic",
    12: "Late Galactic",
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


def characteristic(trade_class: str) -> str:
    assert trade_class in CHARACTERISTICS
    return CHARACTERISTICS[trade_class][one_die() - 1]


def population(trade_class: str, settlement: str) -> int:
    if trade_class == "Poor" and settlement == "unexplored":
        return 0
    else:
        assert trade_class in POPULATION
        popspec: Population_Spec = POPULATION[trade_class]
        pop: int = (nomad_dice(popspec.ndice) + popspec.modifier) * popspec.multiplier
        return pop if pop >= 0 else 0


def tech_age() -> str:
    return TECHNOLOGY_AGES_TABLE[nomad_dice(2)]


def tech_age_offset(tech: str) -> str:
    offset: int = TECHNOLOGY_AGES_OFFSET_TABLE[nomad_dice(2)]
    index: int = TECHNOLOGY_AGES.index(tech)
    if index + offset < 0:
        return TECHNOLOGY_AGES[0]
    elif index + offset > len(TECHNOLOGY_AGES):
        return TECHNOLOGY_AGES[-1]
    else:
        return TECHNOLOGY_AGES[index + offset]


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
    trade_class: str
    characteristic: str
    population: int
    tech_age: str
    world_tag_1: str
    world_tag_2: str


def sector(height: int, width: int, density: int) -> Sequence[Star_Hex]:
    # Generate a number of stars proportional to density
    result: list[Star_Hex] = []
    for w, h in itertools.product(range(1, width + 1), range(1, height + 1)):
        if random.randint(MINIMUM_DENSITY, MAXIMUM_DENSITY) <= density:
            result.append(Star_Hex(w, h, "", "", "", 0, "", "", ""))
    return result


def trim_name(name: str, length: int) -> str:
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
    args = parser.parse_args()

    # initialize namemaker
    names = namemaker.make_name_set(args.namelist)

    # generate a map of unnamed stars
    stars: Sequence[Star_Hex] = sector(args.height, args.width, args.density)

    for star in stars:
        # generate a name for the star / planet
        star.name = trim_name(names.make_name(), args.length)
        # generate the trade type
        star.trade_class = trade_class(args.settlement)
        star.characteristic = characteristic(star.trade_class)
        star.population = population(star.trade_class, args.settlement)
        if star.population == 0:
            # This isn't in the rules, but it makes sense to me
            star.tech_age = TECHNOLOGY_AGES[0]  # No Technology
        elif args.tech:
            techname: str = TECHNOLOGY_AGES_ABBREVS[args.tech]
            star.tech_age = tech_age_offset(techname)
        else:
            star.tech_age = tech_age()
        star.world_tag_1 = world_tag(1)
        star.world_tag_2 = world_tag(2)

    # TODO: Customize format:
    #    - Default format, i.e. what's below.
    #    - Traveller format: see <https://travellermap.com/doc/fileformats>;
    #      need to generate or fake UPPs etc.

    # Print out the list of stars
    print(f"# width={args.width} height={args.height} density={args.density}")
    print(f"# settlement={args.settlement} tech={args.tech}")
    print(f"# stars={len(stars)}")
    print(
        f"#{'Star':{args.length}s} Hex Trade Class      Charactr. "
        "     Population Tech. Age          World Tags"
    )
    print(
        f"#{'-'*(args.length-1)} ---- ---------------- ----------"
        " -------------- ------------------ ------------------------------"
    )
    for s in stars:
        print(
            f"{s.name:{args.length}s} {s.width:02d}{s.height:02d}"
            f" {s.trade_class:16s} {s.characteristic:10s} {s.population:14_d}"
            f" {s.tech_age:18s} {s.world_tag_1}, {s.world_tag_2}"
        )


if __name__ == "__main__":
    main()
