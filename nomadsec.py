#!/usr/bin/env python3

import argparse
import itertools
import json
import random
import string
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, auto

# `pip install namemaker`
import namemaker

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
    if nadv < 0:
        return sum(rolls[:nkeep])
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


TRADE_CLASS_TO_ABBREVS: dict[Trade_Class, str] = {
    Trade_Class.AGRICULTURAL: "Ag",
    Trade_Class.GARDEN: "Ga",
    Trade_Class.INDUSTRIAL: "In",
    Trade_Class.NON_AGRICULTURAL: "Na",
    Trade_Class.NON_INDUSTRIAL: "Ni",
    Trade_Class.POOR: "Po",
    Trade_Class.RESOURCE: "Re",
    Trade_Class.RICH: "Ri",
}


TRADE_CLASS_SETTLED: dict[int, Trade_Class] = {
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


TRADE_CLASS_UNEXPLORED: dict[int, Trade_Class] = {
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


CHARACTERISTICS: dict[Trade_Class, list[Characteristic]] = {
    Trade_Class.AGRICULTURAL: [
        Characteristic.PRIME,
        Characteristic.PRIME,
        Characteristic.TAINTED,
        Characteristic.TAINTED,
        Characteristic.MARGINAL,
        Characteristic.OCEAN,
    ],
    Trade_Class.GARDEN: [
        Characteristic.PRIME,
        Characteristic.TAINTED,
        Characteristic.MARGINAL,
        Characteristic.OCEAN,
        Characteristic.DESERT,
        Characteristic.PRIMORDIAL,
    ],
    Trade_Class.INDUSTRIAL: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.MARGINAL,
        Characteristic.TAINTED,
        Characteristic.TAINTED,
        Characteristic.ICEBALL,
    ],
    Trade_Class.NON_AGRICULTURAL: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.ICEBALL,
        Characteristic.MARGINAL,
        Characteristic.TAINTED,
        Characteristic.INERT,
    ],
    Trade_Class.NON_INDUSTRIAL: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.ROCKBALL,
        Characteristic.MARGINAL,
        Characteristic.TAINTED,
        Characteristic.INERT,
    ],
    Trade_Class.POOR: [
        Characteristic.ROCKBALL,
        Characteristic.ROCKBALL,
        Characteristic.ICEBALL,
        Characteristic.ASTEROID,
        Characteristic.INERT,
        Characteristic.CORROSIVE,
    ],
    Trade_Class.RESOURCE: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.ICEBALL,
        Characteristic.MARGINAL,
        Characteristic.INERT,
        Characteristic.CORROSIVE,
    ],
    Trade_Class.RICH: [
        Characteristic.PRIME,
        Characteristic.PRIME,
        Characteristic.TAINTED,
        Characteristic.TAINTED,
        Characteristic.MARGINAL,
        Characteristic.OCEAN,
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


TECHNOLOGY_AGES_TO_ABBREVS: dict[Tech_Age, str] = {
    Tech_Age.NO_TECHNOLOGY: "NT",
    Tech_Age.EARLY_PRIMITIVE: "EP",
    Tech_Age.LATE_PRIMITIVE: "LP",
    Tech_Age.EARLY_MECHANICAL: "EM",
    Tech_Age.LATE_MECHANICAL: "LM",
    Tech_Age.EARLY_ATOMIC: "EA",
    Tech_Age.LATE_ATOMIC: "LA",
    Tech_Age.EARLY_SPACE: "ES",
    Tech_Age.LATE_SPACE: "LS",
    Tech_Age.EARLY_INTERSTELLAR: "EI",
    Tech_Age.LATE_INTERSTELLAR: "LI",
    Tech_Age.EARLY_GALACTIC: "EG",
    Tech_Age.LATE_GALACTIC: "LG",
    Tech_Age.COSMIC: "C",
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


def trade_class(sector_type: str | None) -> Trade_Class:
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


def trade_class_str(trade: Trade_Class | None) -> str:
    if not trade:
        return ""
    return string.capwords(trade.name.replace("_", " ")).replace(" ", "-")


def trade_class_abbrev(trade: Trade_Class | None) -> str:
    if not trade:
        return ""
    return TRADE_CLASS_TO_ABBREVS[trade]


def characteristic(trade_class: Trade_Class) -> Characteristic:
    assert trade_class in CHARACTERISTICS
    return CHARACTERISTICS[trade_class][one_die() - 1]


def chara_str(c: Characteristic | None) -> str:
    if not c:
        return ""
    return c.name.capitalize()


def chara_abbrev(c: Characteristic | None) -> str:
    if not c:
        return ""
    return CHARACTERISTICS_TO_ABBREVS[c]


def population(trade_class: Trade_Class, settlement: str) -> int:
    if trade_class == Trade_Class.POOR and settlement == "unexplored":
        return 0
    assert trade_class in POPULATION
    popspec: Population_Spec = POPULATION[trade_class]
    pop: int = (nomad_dice(popspec.ndice) + popspec.modifier) * popspec.multiplier
    if pop < 0:
        return 0
    return pop


def population_abbrev(pop: int) -> str:
    if pop == 0:
        return f"{pop:6d}"
    if pop % 1_000_000_000 == 0:
        return f"{pop//1_000_000_000:5d}B"
    if pop % 1_000_000 == 0:
        return f"{pop//1_000_000:5d}M"
    if pop % 1_000 == 0:
        return f"{pop//1_000:5d}K"
    return f"{pop:6d}"


def tech_age() -> Tech_Age:
    return TECHNOLOGY_AGES_TABLE[nomad_dice(2)]


def tech_age_offset(age: Tech_Age) -> Tech_Age:
    offset: int = TECHNOLOGY_AGES_OFFSET_TABLE[nomad_dice(2)]
    index: int = age.value
    if index + offset < 0:
        return Tech_Age.NO_TECHNOLOGY
    if index + offset > Tech_Age.LATE_GALACTIC.value:
        return Tech_Age.LATE_GALACTIC
    return TECHNOLOGY_AGES[index + offset]


def tech_age_str(age: Tech_Age | None) -> str:
    if not age:
        return ""
    return string.capwords(age.name.replace("_", " "))


def tech_age_abbrev(age: Tech_Age | None) -> str:
    if not age:
        return ""
    return TECHNOLOGY_AGES_TO_ABBREVS[age]


def str_to_tech_age(agestr: str | None) -> Tech_Age | None:
    if agestr and agestr in TECHNOLOGY_AGES_ABBREVS:
        return TECHNOLOGY_AGES_ABBREVS[agestr]
    return None


def world_tag(index: int = 1) -> str:
    if index % 2 == 1:
        return WORLD_TAG_TABLE_1[one_die() - 1][one_die() - 1]
    return WORLD_TAG_TABLE_2[one_die() - 1][one_die() - 1]


####################### SECTORS ###############################


@dataclass
class Star_Hex:
    width: int
    height: int
    name: str
    trade_class: Trade_Class | None
    chara: Characteristic | None
    population: int
    tech_age: Tech_Age | None
    world_tag_1: str
    world_tag_2: str


def sector(
    width: int = 8, height: int = 10, density: int = 3, x: int = 1, y: int = 1
) -> Sequence[Star_Hex]:
    # Generate a number of stars proportional to density
    result: list[Star_Hex] = []
    for w, h in itertools.product(range(x, width + x), range(y, height + y)):
        if random.randint(MINIMUM_DENSITY, MAXIMUM_DENSITY) <= density:
            result.append(Star_Hex(w, h, "", None, None, 0, None, "", ""))
    return result


def write_as_csv(outfile, stars: Sequence[Star_Hex]) -> None:
    outfile.write(
        '"Planet","Hex","Trade Class","Chara.",'
        '"Population","Tech. Age","World Tag 1","World Tag 2"\r\n'
    )
    for s in stars:
        outfile.write(
            f'"{s.name}"'
            f',"{s.width:02d}{s.height:02d}"'
            f',"{trade_class_str(s.trade_class)}"'
            f',"{chara_str(s.chara)}"'
            f",{s.population}"
            f',"{tech_age_str(s.tech_age)}"'
            f',"{s.world_tag_1}"'
            f',"{s.world_tag_2}"\r\n'
        )


def write_as_xsv(outfile, stars: Sequence[Star_Hex], sep: str = "\t") -> None:
    outfile.write(
        f"Planet{sep}Hex{sep}Trade Class{sep}Chara.{sep}"
        f"Population{sep}Tech. Age{sep}World Tag 1{sep}World Tag 2\r\n"
    )
    for s in stars:
        outfile.write(
            f"{s.name}"
            f"{sep}{s.width:02d}{s.height:02d}"
            f"{sep}{trade_class_str(s.trade_class)}"
            f"{sep}{chara_str(s.chara)}"
            f"{sep}{s.population}"
            f"{sep}{tech_age_str(s.tech_age)}"
            f"{sep}{s.world_tag_1}"
            f"{sep}{s.world_tag_2}\r\n"
        )


def write_as_text(outfile, stars: Sequence[Star_Hex], length: int) -> None:
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


def write_as_short_text(outfile, stars: Sequence[Star_Hex], length: int) -> None:
    outfile.write(
        f"|{'Planet':{length}s}|Hex |TC|Ch|    Population|TA|World Tags\n"
    )
    outfile.write(
        f"|{'-'*(length)}|----|--|--|-----:|--"
        "|------------------------------\n"
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
    def default(self, obj):
        if isinstance(obj, Star_Hex):
            s: Star_Hex = obj
            return {
                "name": s.name,
                "hex": f"{s.width:02d}{s.height:02d}",
                "trade_class": trade_class_str(s.trade_class),
                "characteristic": chara_str(s.chara),
                "population": s.population,
                "technology_age": tech_age_str(s.tech_age),
                "world_tags": [s.world_tag_1, s.world_tag_2],
            }
        return json.JSONEncoder.default(self, obj)


def write_as_json(outfile, args, stars: Sequence[Star_Hex]) -> None:
    obj: dict = {
        "x": args.start_width,
        "y": args.start_height,
        "width": args.width,
        "height": args.height,
        "planets": stars,
    }
    json.dump(obj, outfile, cls=StarHexEncoder, indent=4)


def debug(*args, **kwargs) -> None:
    print("DEBUG:", *args, file=sys.stderr, **kwargs)


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

    # generate a map of unnamed stars
    stars: Sequence[Star_Hex] = sector(
        height=args.height,
        width=args.width,
        density=args.density,
        x=args.start_width,
        y=args.start_height,
    )

    length: int = 0
    avg_age: Tech_Age = str_to_tech_age(args.tech)

    for star in stars:
        # generate a name for the star / planet
        star.name = names.make_name()
        length = max(length, len(star.name))
        # generate the trade type
        star.trade_class = trade_class(args.settlement)
        star.chara = characteristic(star.trade_class)
        star.population = population(star.trade_class, args.settlement)
        if star.population == 0:
            star.tech_age = Tech_Age.NO_TECHNOLOGY  # No Technology
        elif avg_age:
            star.tech_age = tech_age_offset(avg_age)
        else:
            star.tech_age = tech_age()
        star.world_tag_1 = world_tag(1)
        star.world_tag_2 = world_tag(2)

    if args.debug:
        debug(f"planets={len(stars)}")
        debug(f"max_name_length={length}")

    # Print out the list of stars
    with args.output as outfile:
        if args.json:
            write_as_json(outfile, args, stars)
        elif args.separator:
            if args.separator == ",":
                write_as_csv(outfile, stars)
            else:
                write_as_xsv(outfile, stars, args.separator)
        elif args.abbreviate:
            write_as_short_text(outfile, stars, length)
        else:
            write_as_text(outfile, stars, length)


if __name__ == "__main__":
    main()
