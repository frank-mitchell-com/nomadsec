#!/usr/bin/env python3
"""
Main program for the command-line version.
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#    "namemaker"
# ]
# ///

import argparse
import sys

from namemaker import make_name_set  # type: ignore

from .common import (
    DEFAULT_DENSITY,
    DEFAULT_SECTOR_HEIGHT,
    DEFAULT_SECTOR_WIDTH,
    DEFAULT_SECTOR_X,
    DEFAULT_SECTOR_Y,
    MAXIMUM_DENSITY,
    MINIMUM_DENSITY,
    NameSet,
    SectorBounds,
)
from .namegen import GrammarNameSet
from .sector import sector
from .tables import (
    settlement_name_list,
    str_to_settlement,
    str_to_tech_age,
    tech_age_abbrev_list,
)
from .output import (
    write_as_json,
    write_as_short_text,
    write_as_text,
    write_as_xsv,
)


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
        prog="nomadsec",
        description="Generate a sector for the _FTL: Nomad_ RPG"
    )
    nsgroup = parser.add_mutually_exclusive_group()
    nsgroup.add_argument(
        "-n",
        "--namelist",
        help="text file providing example names",
        default="Greek mythology.txt",
    )
    nsgroup.add_argument(
        "-g",
        "--grammar",
        help="JSON file describing a grammar for names",
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
        default=DEFAULT_SECTOR_X,
        type=int,
    )
    parser.add_argument(
        "-Y",
        "--start-height",
        help="first index down",
        default=DEFAULT_SECTOR_Y,
        type=int,
    )
    parser.add_argument(
        "-d",
        "--density",
        help=f"density of stars (n in {MAXIMUM_DENSITY})",
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
        choices=settlement_name_list(),
    )
    parser.add_argument(
        "-t",
        "--tech",
        help="technology age of sector",
        type=str,
        choices=tech_age_abbrev_list(),
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
    nameset: NameSet

    if args.grammar:
        nameset = GrammarNameSet(args.grammar)
    else:
        nameset = make_name_set(args.namelist)

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
