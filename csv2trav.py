#!/usr/bin/env python3

import argparse
import csv
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
# from unidecode import unidecode # must `pip install unidecode`

GENIE_HEADER = (
"#--------1---------2---------3---------4---------5-------\n"
"#PlanetName   Loc. UPP Code   B   Notes         Z  PBG Al\n"
"#----------   ---- ---------  - --------------- -  --- --\n"
)

@dataclass
class PlanetData:
    name: str
    loc: str
    trade_class: str
    chara: str
    population: int
    tech_age: str
    tags: list[str]


def _name(planet: PlanetData) -> str:
    return planet.name[:13]


def _upp(planet: PlanetData) -> str:
    # TODO: derive some of this from PlanetData
    # Exactly 9 characters
    #   - starport
    #   - size
    #   - atmosphere
    #   - hydrographics
    #   - population
    #   - government
    #   - law level
    #   - tech level
    return "C777777-7"


def _notes(planet: PlanetData) -> str:
    # TODO: derive some of this from PlanetData
    # "Ag" =
    # "Ba" =
    # "Co" =
    # "Cp" =
    # "De" =
    # "Fl" =
    # "Hi" =
    # "Lo" =
    # "Na" =
    # "Ni" =
    # "Po" =
    # "Va" =
    return ""


def _base(planet: PlanetData) -> str:
    # TODO: derive some of this from PlanetData
    # "N" = Naval Base, "S" = Scout Base
    return " "


def _zone(planet: PlanetData) -> str:
    # TODO: derive some of this from PlanetData
    # "A" = Amber, "R" = Red, " " = otherwise
    return " "


def _pbg(planet: PlanetData) -> str:
    # TODO: derive some of this from PlanetData
    # Population Multiplier
    # Belts
    # Gas Giants
    return "100"


def write_genie(out, planets: Sequence[PlanetData]) -> None:
    out.write(GENIE_HEADER)
    for p in planets:
        # HEADER:
        # - Standard "commented" header, for reference
        # Each ROW:
        # - name -> PlanetName: 01-13
        # - hex -> Loc: 15-18
        # - ??? -> UPP Code: 20-28
        # - ??? -> "B": 31
        # - ??? -> Notes: 33-47 [Safe to leave blank?]
        # - ??? -> "Z": 49
        # - ??? -> PBG: 53-55
        # - ??? -> Al: 57-58 [NOT USED?]
        #   - Just hardwire to "--"
        out.write(f"{_name(p):14s}{p.loc} {_upp(p)}  {_base(p)}"
                  f" {_notes(p):15s} {_zone(p)}  {_pbg(p)} --\n")


def read_csv(infile, reader) -> Sequence[PlanetData]:
    result: Sequence[PlanetData] = []
    for row in reader:
        data = PlanetData(
            row["Planet"],
            row["Hex"],
            row["Trade Class"],
            row["Chara."],
            int(row["Population"]),
            row["Tech. Age"],
            [row["World Tag 1"], row["World Tag 1"]],
        )
        
        if data.name[0] != '-' and data.loc[0] != '-':
            result.append(data)
    return result


def read_json(jsondata) -> Sequence[PlanetData]:
    result: Sequence[PlanetData] = []
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
                p["world_tags"],
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

    planets: Sequence[PlanetData]

    with args.inputfile as infile:
        if args.json:
            jsondata = json.load(infile)
            planets = read_json(jsondata)
        else:
            dialect = csv.Sniffer().sniff(infile.read(1024))
            infile.seek(0)
            reader = csv.DictReader(infile, dialect=dialect)
            planets = read_csv(infile, reader)

    # TODO: open `out` with encoding="cp1252" or "windows-1252"
    with args.outputfile as outfile:
        write_genie(outfile, planets)    


if __name__ == '__main__':
    main()
