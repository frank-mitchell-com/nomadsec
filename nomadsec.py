#!/usr/bin/env python3

import itertools
import json
import random
from collections.abc import Collection, Sequence
from dataclasses import dataclass

MAX_NAME_LENGTH: int = 14

DEFAULT_SYLLABLE_MINIMUM: int = 1
DEFAULT_SYLLABLE_MAXIMUM: int = 4
DEFAULT_SYLLABLE_INITIAL: Sequence[str] = "bcdfghjklmnpqrstvwxyz"
DEFAULT_SYLLABLE_VOWELS: Sequence[str] = "aeiou"
DEFAULT_SYLLABLE_FINAL: Sequence[str] = DEFAULT_SYLLABLE_INITIAL

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

    def __str__(self):
        return f"{self.name:14s}{self.width:02d}{self.height:02d}"


def sector(height: int, width: int, density: int) -> Collection[StarHex]:
    # Generate a number of stars proportional to density
    result: list[StarHex] = []
    for w, h in itertools.product(range(1, width + 1), range(1, height + 1)):
        print(f"Considering {w},{h}")
        if random.randint(MINIMUM_DENSITY, MAXIMUM_DENSITY) <= density:
            print(f"Appending star at {w},{h}")
            result.append(StarHex(w, h, ""))
    print(result)
    return result


def name(
    min_syllables: int,
    max_syllables: int,
    initial: Sequence[str],
    vowels: Sequence[str],
    final: Sequence[str],
) -> str:
    name_seq: list[str] = []
    nsyllables: int = random.randint(min_syllables, max_syllables)
    for i in range(nsyllables):
        name_seq.append(random.choice(initial or [""]))
        name_seq.append(random.choice(vowels or [""]))
        name_seq.append(random.choice(final or [""]))
    result = "".join(name_seq).capitalize()
    if len(result) > MAX_NAME_LENGTH - 1:
        return result[: MAX_NAME_LENGTH - 1] + "."
    else:
        return result


def main() -> None:
    sector_width: int = DEFAULT_SECTOR_WIDTH
    sector_height: int = DEFAULT_SECTOR_HEIGHT
    density: int = DEFAULT_DENSITY

    # generate a map of unnamed stars
    stars: Collection[StarHex] = sector(sector_height, sector_width, density)

    for star in stars:
        # generate a name for the star / planet
        n: str = name(
            DEFAULT_SYLLABLE_MINIMUM,
            DEFAULT_SYLLABLE_MAXIMUM,
            DEFAULT_SYLLABLE_INITIAL,
            DEFAULT_SYLLABLE_VOWELS,
            DEFAULT_SYLLABLE_FINAL,
        )
        star.name = n
        # randomly generate other stuff?

    # 4. Print out the map in the requested format:
    #    - Traveller format: see <https://travellermap.com/doc/fileformats>

    print(stars)

    for s in stars:
        print(str(s))


if __name__ == "__main__":
    main()
