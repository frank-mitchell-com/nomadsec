#!/usr/bin/env python3

import itertools
import json
import random
import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

# `pip install namemaker`
import namemaker

# maximum retries to find a unique star name
MAX_RETRIES: int = 1_000_000

# default number of chars for star names
DEFAULT_MAX_NAME_LENGTH: int = 14

# coordinates are always f"{width:0d}{height:0d}"
DEFAULT_SECTOR_HEIGHT: int = 10
DEFAULT_SECTOR_WIDTH: int = 8

# MINIMUM_DENSITY <= density < MAXIMUM_DENSITY
DEFAULT_DENSITY: int = 3
MAXIMUM_DENSITY: int = 6
MINIMUM_DENSITY: int = 1


@dataclass
class StarHex:
    width: int
    height: int
    name: str


def sector(height: int, width: int, density: int) -> Sequence[StarHex]:
    # Generate a number of stars proportional to density
    result: list[StarHex] = []
    for w, h in itertools.product(range(1, width + 1), range(1, height + 1)):
        if random.randint(MINIMUM_DENSITY, MAXIMUM_DENSITY) <= density:
            result.append(StarHex(w, h, ""))
    return result


def trim_name(name: str, length: int) -> str:
    return name if len(name) < length - 1 else name[:length-1] + '.'


def main() -> None:
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Generate a sector for the _FTL: Nomad_ RPG"
    )
    parser.add_argument(
        "-n", "--namelist",
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
    stars: Sequence[StarHex] = sector(args.height, args.width, args.density)

    for star in stars:
        # generate a name for the star / planet
        star.name = trim_name(names.make_name(), args.length)

        # randomly generate other stuff?

    # TODO: Customize format:
    #    - Default format, i.e. what's below.
    #    - Custom _Nomad_ format (TBD)
    #    - Traveller format: see <https://travellermap.com/doc/fileformats>;
    #      need to generate or fake UPPs etc.

    # Print out the list of stars
    print(f"# width={args.width} height={args.height} density={args.density}")
    print(f"# stars={len(stars)}")
    print(f"#{'Star':{args.length-1}s}Hex")
    print(f"#{'-'*(args.length-2)} ----")
    for s in stars:
        print(f"{s.name:{args.length}s}{s.width:02d}{s.height:02d}")


if __name__ == "__main__":
    main()
