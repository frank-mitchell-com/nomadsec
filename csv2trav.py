#!/usr/bin/env python3

# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import argparse
import csv
import json
import sys
from dataclasses import dataclass


EXTENDED_HEX = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"


GENIE_HEADER = (
    "#--------1---------2---------3---------4---------5-------\r\n"
    "#PlanetName   Loc. UPP Code   B   Notes         Z  PBG Al\r\n"
    "#----------   ---- ---------  - --------------- -  --- --\r\n"
)


TRADE_CLASS_CODES: dict[str, str] = {
    "Agricultural": "Ag",
    "Garden": "Ga",
    "Non-Agricultural": "Na",
    "Non-Industrial": "Ni",
    "Industrial": "In",
    "Poor": "Po",
    "Resource": "Re",
    "Rich": "Ri",
}


CHARA_TO_TRADE_CODES: dict[str, str] = {
    "Asteroid": "As",
    "Desert": "De",
    "Iceball": "IC",
    "Marginal": "Ba",
    "Ocean": "Wa",
}

PLANET_SIZE_DEFAULT: int = 8

ATMOSPHERE_CODE_DEFAULT: int = 6

CHARA_TO_ATMOSPHERE_CODES: dict[str, int] = {
    "Asteroid": 0,
    "Corrosive": 11,
    "Desert": 6,
    "Iceball": 3,
    "Inert": 10,
    "Marginal": 5,
    "Ocean": 6,
    "Prime": 6,
    "Primordial": 10,
    "Rockball": 3,
    "Tainted": 7,
}

HYDROGRAPHIC_CODE_DEFAULT: int = 5

CHARA_TO_HYDROGRAPHICS_CODES: dict[str, int] = {
    "Asteroid": 0,
    "Corrosive": 11,
    "Desert": 1,
    "Iceball": 6,
    "Inert": 4,
    "Marginal": 5,
    "Ocean": 9,
    "Prime": 7,
    "Primordial": 8,
    "Rockball": 2,
    "Tainted": 3,
}

GOVERNMENT_CODE_DEFAULT: int = 5

GOV_TAGS_TO_CODES: dict[str, int] = {
    "Athenian Democracy": 2,
    "Corporate": 1,
    "Captive Government": 6,
    "Charismatic Dictator": 10,
    "Democracy": 4,
    "Feudal": 5,
    "Multiple Govs.": 7,
    "Theocracy": 13,
}

LAW_CODE_DEFAULT: int = 5

LAW_TAGS_TO_CODES: dict[str, int] = {
    "Liberal": 2,
    "Minimal Laws": 1,
    "Police State": 9,
    "Restrictive Laws": 7,
}


AMBER_ZONE_TAGS: set[str] = {
    "Civil War",
    "Feral World",
    "Impending Doom",
    "Police State",
    "Radioactive",
    "Xenophobia",
    "Hostile Space",
    "Slavery",
}


RED_ZONE_TAGS: set[str] = {
    "Quarantined",
    "Zombies",
}


TECH_AGE_CODES_TO_LEVELS: dict[str, int] = {
    "NT": 0,
    "EP": 1,
    "LP": 2,
    "EM": 3,
    "LM": 4,
    "EA": 5,
    "LA": 6,
    "ES": 7,
    "LS": 8,
    "EI": 9,
    "LI": 10,
    "EG": 12,
    "LG": 15,
    "C": 20,
}

TECH_LEVEL_DEFAULT: int = 8

TECH_LEVEL_STARPORT_X: int = 4

TECH_LEVEL_STARPORT_E: int = 6

TECH_LEVEL_STARPORT_D: int = 8

TECH_LEVEL_STARPORT_A: int = 10

TECH_LEVEL_HIGH_TECH: int = 10

TECH_LEVEL_LOW_TECH: int = 2


@dataclass
class PlanetData:
    name: str
    loc: str
    trade_class: str
    chara: str
    population: int
    tech_age: str
    tags: set[str]


def _ehex(n: int) -> str:
    if n >= len(EXTENDED_HEX):
        raise ValueError
    return EXTENDED_HEX[n]


def _name(planet: PlanetData) -> str:
    return planet.name[:13]


def _trade_class_code(trade_class: str) -> str:
    if trade_class not in TRADE_CLASS_CODES:
        return ""
    return TRADE_CLASS_CODES[trade_class]


def _tech_age_code(tech_age: str) -> str:
    if tech_age == "Cosmic":
        return "C"
    words: list[str] = tech_age.split(" ")
    assert len(words) == 2
    return words[0][0] + words[1][0]


def _tech_level(planet: PlanetData) -> int:
    tac: str = _tech_age_code(planet.tech_age)
    if tac not in TECH_AGE_CODES_TO_LEVELS:
        return TECH_LEVEL_DEFAULT
    return TECH_AGE_CODES_TO_LEVELS[tac]


def _starport_code(planet: PlanetData) -> str:
    tl: int = _tech_level(planet)
    tcc: str = _trade_class_code(planet.trade_class)

    if planet.population == 0 or tl <= TECH_LEVEL_STARPORT_X:
        return "X"
    if tcc == "Ni" or tl <= TECH_LEVEL_STARPORT_E:
        return "E"
    if tl <= TECH_LEVEL_STARPORT_D:
        return "D"
    if tl >= TECH_LEVEL_STARPORT_A:
        return "A" if tcc in {"Ag", "Ri", "In"} else "B"
    return "B" if tcc in {"Ag", "Ri", "In"} else "C"


def _size_code(planet: PlanetData) -> int:
    return 0 if planet.chara == "Asteroid" else PLANET_SIZE_DEFAULT


def _atmosphere_code(planet: PlanetData) -> int:
    if planet.chara not in CHARA_TO_ATMOSPHERE_CODES:
        return ATMOSPHERE_CODE_DEFAULT
    return CHARA_TO_ATMOSPHERE_CODES[planet.chara]


def _hydrographic_code(planet: PlanetData) -> int:
    if planet.chara not in CHARA_TO_HYDROGRAPHICS_CODES:
        return HYDROGRAPHIC_CODE_DEFAULT
    return CHARA_TO_HYDROGRAPHICS_CODES[planet.chara]


def _population_code(planet: PlanetData) -> int:
    # Gotta be a better way to do this
    mag: int = 0
    lastmag: int = 0
    while 10**mag <= planet.population:
        lastmag = mag
        mag += 1
    return lastmag


def _government_code(planet: PlanetData) -> int:
    if planet.population == 0:
        return 0
    if common := set(GOV_TAGS_TO_CODES) & planet.tags:
        return round(sum(GOV_TAGS_TO_CODES[x] for x in common) / len(common))
    return GOVERNMENT_CODE_DEFAULT


def _law_level_code(planet: PlanetData) -> int:
    if planet.population == 0:
        return 0
    if common := set(LAW_TAGS_TO_CODES) & planet.tags:
        return round(sum(LAW_TAGS_TO_CODES[x] for x in common) / len(common))
    return LAW_CODE_DEFAULT


def _upp(planet: PlanetData) -> str:
    return (
        f"{_starport_code(planet)}"
        f"{_ehex(_size_code(planet))}"
        f"{_ehex(_atmosphere_code(planet))}"
        f"{_ehex(_hydrographic_code(planet))}"
        f"{_ehex(_population_code(planet))}"
        f"{_ehex(_government_code(planet))}"
        f"{_ehex(_law_level_code(planet))}"
        f"-{_ehex(_tech_level(planet))}"
    )


def _notes(planet: PlanetData) -> str:
    result: list[str] = [_trade_class_code(planet.trade_class)]
    if planet.chara in CHARA_TO_TRADE_CODES:
        result.append(CHARA_TO_TRADE_CODES[planet.chara])
    if planet.population >= 1_000_000_000:
        result.append("Hi")
    if planet.population <= 5_000:
        result.append("Lo")
    tl: int = _tech_level(planet)
    if tl >= TECH_LEVEL_HIGH_TECH:
        result.append("Ht")
    if tl <= TECH_LEVEL_LOW_TECH:
        result.append("Lt")
    result.sort()
    return " ".join(result)


def _base(planet: PlanetData) -> str:
    return " "


def _zone(planet: PlanetData) -> str:
    # sourcery skip: assign-if-exp, reintroduce-else
    if planet.tags & RED_ZONE_TAGS:
        return "R"
    if planet.tags & AMBER_ZONE_TAGS:
        return "A"
    return " "


def _pbg(planet: PlanetData) -> str:
    # Population Multiplier
    popcode: int = _population_code(planet)
    popmul: int = round(planet.population / (10**popcode))
    # Bases
    bases: int = 1 if _tech_level(planet) >= TECH_LEVEL_STARPORT_D else 0
    # Gas Giants
    ggs: int = 1
    return f"{_ehex(popmul)}{_ehex(bases)}{_ehex(ggs)}"


def write_genie(out, planets: list[PlanetData]) -> None:
    out.write(GENIE_HEADER)
    for p in planets:
        out.write(
            f"{_name(p):14s}{p.loc} {_upp(p)}  {_base(p)}"
            f" {_notes(p):15s} {_zone(p)}  {_pbg(p)} --\r\n"
        )


def read_csv(reader) -> list[PlanetData]:
    result: list[PlanetData] = []
    for row in reader:
        data = PlanetData(
            row["Planet"],
            row["Hex"],
            row["Trade Class"],
            row["Chara."],
            int(row["Population"]),
            row["Tech. Age"],
            {row["World Tag 1"], row["World Tag 2"]},
        )

        if data.name[0] != "-" and data.loc[0] != "-":
            result.append(data)
    return result


def read_json(jsondata) -> list[PlanetData]:
    result: list[PlanetData] = []
    print("DEBUG", jsondata, file=sys.stderr)
    for p in jsondata["planets"]:
        print("DEBUG", p, file=sys.stderr)
        data = PlanetData(
            p["name"],
            p["hex"],
            p["trade_class"],
            p["characteristic"],
            int(p["population"]),
            p["technology_age"],
            set(p["world_tags"]),
        )
        result.append(data)
    return result


def main() -> None:
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Parse `nomadsec.py` data into _Traveller_ GEnie format"
    )
    parser.add_argument(
        "inputfile",
        help="file containing `nomadsec.py` data",
        type=argparse.FileType(mode="r", encoding="UTF-8"),
    )
    parser.add_argument(
        "outputfile",
        help="file to contain _Traveller_ GEnie data",
        type=argparse.FileType(mode="w", encoding="cp1252"),
    )
    parser.add_argument(
        "-j",
        "--json",
        help="read as JSON data",
        action="store_true",
    )
    args = parser.parse_args()

    planets: list[PlanetData]

    with args.inputfile as infile:
        if args.json:
            jsondata = json.load(infile)
            planets = read_json(jsondata)
        else:
            dialect = csv.Sniffer().sniff(infile.read(1024))
            infile.seek(0)
            reader = csv.DictReader(infile, dialect=dialect)
            planets = read_csv(reader)

    with args.outputfile as outfile:
        write_genie(outfile, planets)


if __name__ == "__main__":
    main()
