#!/usr/bin/env python3

import argparse
import csv
import re

TRADE_CLASS_COL: int = 3
CHARACTERISTIC_COL: int = 4
POPULATION_COL: int = 5
TECHNOLOGY_AGE_COL: int = 6


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
    row[col] = row[col].replace("_", "")
    row[col] = row[col].replace("K", "000")
    row[col] = row[col].replace("M", "000000")
    row[col] = row[col].replace("B", "000000000")
    row[col] = row[col].replace("T", "000000000000")


def unabbrev(row: list[str], col: int, abbrevs: dict[str, str]) -> None:
    if row[col] in abbrevs:
        row[col] = abbrevs[row[col]]


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
            cels: list[str] = re.split(r"\s*[|,]\s*", line.rstrip())
            if not cels[1][0] == '-' and not cels[1] == "Planet":
                unabbrev(cels, TRADE_CLASS_COL, TRADE_CLASS_ABBREVS)
                unabbrev(cels, CHARACTERISTIC_COL, CHARACTERISTIC_ABBREVS)
                unabbrev(cels, TECHNOLOGY_AGE_COL, TECHNOLOGY_AGE_ABBREVS)
                unabbrev_pop(cels, POPULATION_COL)
                csvdata.append(cels[1:])

    with args.outputfile as outfile:
        writer = csv.writer(outfile)
        writer.writerow(HEADER)
        for row in csvdata:
            writer.writerow(row)


if __name__ == "__main__":
    main()
