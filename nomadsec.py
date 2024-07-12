#!/usr/bin/env python3

import itertools
import json
import random
import sys
import argparse
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Protocol

MAX_NAME_LENGTH: int = 14

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
    def __init__(self, jsonsrc: dict):
        assert "min_syllables" in jsonsrc
        assert "max_syllables" in jsonsrc
        assert "initial" in jsonsrc
        assert "vowels" in jsonsrc

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
        if len(result) > MAX_NAME_LENGTH - 1:
            return result[: MAX_NAME_LENGTH - 1] + "."
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

    def __str__(self):
        return f"{self.name:14s}{self.width:02d}{self.height:02d}"


def sector(height: int, width: int, density: int) -> Collection[StarHex]:
    # Generate a number of stars proportional to density
    result: list[StarHex] = []
    for w, h in itertools.product(range(1, width + 1), range(1, height + 1)):
        if random.randint(MINIMUM_DENSITY, MAXIMUM_DENSITY) <= density:
            result.append(StarHex(w, h, ""))
    return result


def main() -> None:
    sector_width: int = DEFAULT_SECTOR_WIDTH
    sector_height: int = DEFAULT_SECTOR_HEIGHT
    density: int = DEFAULT_DENSITY

    namesrc: NameSource = None

    with open(sys.argv[1]) as jsonfile:
        namesrc = NameGenerator(SimpleNameSource(json.load(jsonfile)))

    # generate a map of unnamed stars
    stars: Collection[StarHex] = sector(sector_height, sector_width, density)

    for star in stars:
        # generate a name for the star / planet
        star.name = namesrc.name()
        # randomly generate other stuff?

    # 4. Print out the map in the requested format:
    #    - Traveller format: see <https://travellermap.com/doc/fileformats>

    for s in stars:
        print(str(s))


if __name__ == "__main__":
    main()
