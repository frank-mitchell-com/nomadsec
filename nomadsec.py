#!/usr/bin/env python3

import itertools
import json
import random
from collections.abc import Collection, Sequence

DEFAULT_SYLLABLE_MINIMUM: int = 1
DEFAULT_SYLLABLE_MAXIMUM: int = 5
DEFAULT_SYLLABLE_INITIAL: Sequence[str] = "bcdfghjklmnpqrstvwxyz"
DEFAULT_SYLLABLE_VOWELS: Sequence[str] = "aeiou"
DEFAULT_SYLLABLE_FINAL: Sequence[str] = DEFAULT_SYLLABLE_INITIAL

DEFAULT_ZONE_HEIGHT: int = 1
DEFAULT_ZONE_WIDTH: int = 1

# coordinates are always f"{width:0d}{height:0d}"
DEFAULT_SECTOR_HEIGHT: int = 10
DEFAULT_SECTOR_WIDTH:  int = 8

# MINIMUM_DENSITY <= density < MAXIMUM_DENSITY
DEFAULT_DENSITY: int = 3
MAXIMUM_DENSITY: int = 6
MINIMUM_DENSITY: int = 1

Coordinate = tuple[int, int] # width, height

def sector(height: int, width: int, density: int) -> Collection[Coordinate]:
    # Generate a number of coordinates proportional to density
    return [x for x in itertools.product(range(1, height+1), range(1, width+1))
            if random.randint(MINIMUM_DENSITY, MAXIMUM_DENSITY) <= density]

def name(min_syllables: int, 
                    max_syllables: int, 
                    initial: Sequence[str], 
                    vowels: Sequence[str], 
                    final: Sequence[str]) -> str:
    name_seq: list[str] = []
    nsyllables: int = random.randint(min_syllables, max_syllables)
    for i in range(nsyllables):
        name_seq.append(random.choice(initial or ['']))
        name_seq.append(random.choice(vowels or ['']))
        name_seq.append(random.choice(final or ['']))
    return ''.join(name_seq).capitalize()

def main() -> None:
    stars: list[tuple[Coordinate, Coordinate, str]] = []

    zone_width: int = DEFAULT_ZONE_WIDTH
    zone_height: int = DEFAULT_ZONE_HEIGHT
    sector_width: int = DEFAULT_SECTOR_WIDTH
    sector_height: int = DEFAULT_SECTOR_HEIGHT
    density: int = DEFAULT_DENSITY

    # generate a list of zones
    for zone in itertools.product(range(zone_height), range(zone_width)):
        # generate a map of unnamed stars
        for star in sector(sector_height, sector_width, density):
            # generate a name for the star / planet
            n: str = name(
                    DEFAULT_SYLLABLE_MINIMUM,
                    DEFAULT_SYLLABLE_MAXIMUM,
                    DEFAULT_SYLLABLE_INITIAL,
                    DEFAULT_SYLLABLE_VOWELS,
                    DEFAULT_SYLLABLE_FINAL)
            # randomly generate other stuff?
            stars.append((zone, star, n))

    # 4. Print out the map in the requested format:
    #    - My format (planet-name, hex, zone, star-name)
    #    - Traveller format: see <https://travellermap.com/doc/fileformats>

    print(stars)


if __name__ == "__main__":
    main()
