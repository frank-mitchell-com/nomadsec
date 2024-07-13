#!/usr/bin/env python3

import itertools
import json
import random
import sys
import argparse
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Protocol

DEFAULT_MAX_NAME_LENGTH: int = 14

# coordinates are always f"{width:0d}{height:0d}"
DEFAULT_SECTOR_HEIGHT: int = 10
DEFAULT_SECTOR_WIDTH: int = 8

# MINIMUM_DENSITY <= density < MAXIMUM_DENSITY
DEFAULT_DENSITY: int = 3
MAXIMUM_DENSITY: int = 6
MINIMUM_DENSITY: int = 1


class NameSource(Protocol):
    def name(self) -> str:
        ...

class SimpleNameSource:
    def __init__(self, jsonsrc: dict, length=DEFAULT_MAX_NAME_LENGTH):
        assert "min_syllables" in jsonsrc
        assert "max_syllables" in jsonsrc
        assert "initial" in jsonsrc
        assert "vowels" in jsonsrc

        self._length = length
        self._min = jsonsrc["min_syllables"]
        self._max = jsonsrc["max_syllables"]
        self._vowels = jsonsrc["vowels"]
        self._initial = jsonsrc["initial"]
        if "final" not in jsonsrc or not jsonsrc["final"]:
            self._final = [""]
        else:
            self._final = jsonsrc["final"]
        if "medial" not in jsonsrc:
            self._medial = ["".join(x) for x in itertools.product(self._final, self._initial)]
        else:
            self._medial = jsonsrc["medial"]


    def name(self) -> str:
        name_seq: list[str] = []
        nsyllables: int = random.randint(self._min, self._max)

        name_seq.append(random.choice(self._initial))
        name_seq.append(random.choice(self._vowels))
        for i in range(1, nsyllables):
            name_seq.append(random.choice(self._medial))
            name_seq.append(random.choice(self._vowels))
        name_seq.append(random.choice(self._final))

        result = "".join(name_seq).capitalize()
        if len(result) > self._length - 1:
            return result[:self._length - 1] + "."
        else:
            return result


class NameGenerator:
    def __init__(self, source: NameSource) -> None:
        self._source = source
        self._pastnames = set()

    def name(self) -> str:
        newname: str = self._source.name()
        while newname and newname in self._pastnames:
            newname = self._source.name()
        self._pastnames.add(newname)
        return newname


@dataclass
class StarHex:
    width: int
    height: int
    name: str


def sector(height: int, width: int, density: int) -> Collection[StarHex]:
    # Generate a number of stars proportional to density
    result: list[StarHex] = []
    for w, h in itertools.product(range(1, width + 1), range(1, height + 1)):
        if random.randint(MINIMUM_DENSITY, MAXIMUM_DENSITY) <= density:
            result.append(StarHex(w, h, ""))
    return result


def main() -> None:
    # Parse arguments
    parser = argparse.ArgumentParser(
            description="Generate a sector for the _FTL: Nomad_ RPG")
    parser.add_argument("namefile",
                        help="JSON file specifying random name generator",
                        type=argparse.FileType(mode="r", encoding="ASCII"))
    parser.add_argument("-x", "--width",
                        help="number of hexes/parsecs across",
                        default=DEFAULT_SECTOR_WIDTH,
                        type=int)
    parser.add_argument("-y", "--height",
                        help="number of hexes/parsecs down",
                        default=DEFAULT_SECTOR_HEIGHT,
                        type=int)
    parser.add_argument("-d", "--density", 
                        help="density of stars (n in 6)",
                        default=DEFAULT_DENSITY,
                        type=int,
                        choices=range(MINIMUM_DENSITY, MAXIMUM_DENSITY))
    parser.add_argument("-l", "--length", 
                        help="maximum length of star names",
                        default=DEFAULT_MAX_NAME_LENGTH,
                        type=int)
    args = parser.parse_args()

    # Record parameters
    rseed = random.getstate()

    namesrc: NameSource = None

    with args.namefile as jsonfile:
        namesrc = NameGenerator(SimpleNameSource(json.load(jsonfile), length=args.length))

    # generate a map of unnamed stars
    stars: Collection[StarHex] = sector(args.height, args.width, args.density)

    for star in stars:
        # generate a name for the star / planet
        star.name = namesrc.name()
        # randomly generate other stuff?

    # 4. Print out the map in the requested format:
    #    - Traveller format: see <https://travellermap.com/doc/fileformats>

    # print(f"# {rseed=}")
    print(f"# width={args.width} height={args.height} density={args.density}")
    print(f"# stars={len(stars)}")
    for s in stars:
        print(f"{s.name:{args.length}s}{s.width:02d}{s.height:02d}")


if __name__ == "__main__":
    main()
