#!/usr/bin/env python3

import argparse
import csv
import re

POPULATION_COL: int = 5

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
            cels[POPULATION_COL] = cels[POPULATION_COL].replace("_", "")
            if not cels[1][0] == '-' and not cels[1] == "Planet":
                csvdata.append(cels[1:])

    with args.outputfile as outfile:
        writer = csv.writer(outfile)
        writer.writerow(HEADER)
        for row in csvdata:
            writer.writerow(row)


if __name__ == "__main__":
    main()
