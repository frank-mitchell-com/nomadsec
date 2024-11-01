#!/usr/bin/env python3

# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import argparse
import csv
import re

TRADE_CLASS_COL: int = 3
CHARACTERISTIC_COL: int = 4
POPULATION_COL: int = 5
TECHNOLOGY_AGE_COL: int = 6
WORLD_TAGS_COL: int = 7


HEADER: list[str] = [
    "Planet",
    "Hex",
    "Trade Class",
    "Chara.",
    "Population",
    "Tech. Age",
    "World Tag 1",
    "World Tag 2",
]


TRADE_CLASS_ABBREVS: dict[str, str] = {
    "Ag": "Agricultural",
    "Ga": "Garden",
    "In": "Industrial",
    "Na": "Non-Agricultural",
    "Ni": "Non-Industrial",
    "Po": "Poor",
    "Re": "Resource",
    "Ri": "Rich",
}


CHARACTERISTIC_ABBREVS: dict[str, str] = {
    "As": "Asteroid",
    "Co": "Corrosive",
    "De": "Desert",
    "Ic": "Iceball",
    "In": "Inert",
    "Ma": "Marginal",
    "Oc": "Ocean",
    "Pr": "Prime",
    "Pl": "Primordial",
    "Ro": "Rockball",
    "Ta": "Tainted",
}


TECHNOLOGY_AGE_ABBREVS: dict[str, str] = {
    "NT": "No Technology",
    "EP": "Early Primitive",
    "LP": "Late Primitive",
    "EM": "Early Mechanical",
    "LM": "Late Mechanical",
    "EA": "Early Atomic",
    "LA": "Late Atomic",
    "ES": "Early Space",
    "LS": "Late Space",
    "EI": "Early Interstellar",
    "LI": "Late Interstellar",
    "EG": "Early Galactic",
    "LG": "Late Galactic",
}


def unabbrev_pop(row: list[str], col: int) -> None:
    pop: str = row[col]
    pop = (
        pop.replace("_", "")
        .replace(",", "")
        .replace("K", "000")
        .replace("M", "000000")
        .replace("B", "000000000")
    )
    row[col] = str(int(pop))


def unabbrev(row: list[str], col: int, abbrevs: dict[str, str]) -> None:
    if row[col] in abbrevs:
        row[col] = abbrevs[row[col]]


def split_tags(row: list[str], col) -> None:
    row[col : col + 1] = re.split(r"\s*,\s*", row[col])


def convert_to_csv_format(cels: list[str], csvdata: list[list[str]]):
    unabbrev(cels, TRADE_CLASS_COL, TRADE_CLASS_ABBREVS)
    unabbrev(cels, CHARACTERISTIC_COL, CHARACTERISTIC_ABBREVS)
    unabbrev(cels, TECHNOLOGY_AGE_COL, TECHNOLOGY_AGE_ABBREVS)
    unabbrev_pop(cels, POPULATION_COL)
    split_tags(cels, WORLD_TAGS_COL)
    csvdata.append(cels[1:])


def main() -> None:
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Parse `nomadsec.py` plain text data into a CSV"
    )
    parser.add_argument(
        "inputfile",
        help="file containing `nomadsec.py` default text",
        type=argparse.FileType(mode="r", encoding="UTF-8"),
    )
    parser.add_argument(
        "outputfile",
        help="file to contain CSV data",
        type=argparse.FileType(mode="w", encoding="UTF-8"),
    )
    args = parser.parse_args()

    csvdata: list[list[str]] = []

    with args.inputfile as infile:
        for line in infile.readlines():
            cels: list[str] = re.split(r"\s*\|\s*", line.rstrip())
            if cels[1][0] != "-" and cels[1] != "Planet":
                convert_to_csv_format(cels, csvdata)
    with args.outputfile as outfile:
        writer = csv.writer(outfile)
        writer.writerow(HEADER)
        for row in csvdata:
            writer.writerow(row)


if __name__ == "__main__":
    main()
