#!/usr/bin/env python3

import itertools
import json
import random
import argparse
from collections.abc import Sequence
from typing import Protocol

DEFAULT_NUMBER_OF_NAMES = 100

# maximum retries to find a unique star name
MAX_RETRIES: int = 1_000_000


class NameSource(Protocol):
    def name(self) -> str: ...


class SimpleNameSource:
    def __init__(self, jsonsrc: dict):
        assert "min_syllables" in jsonsrc
        assert "max_syllables" in jsonsrc
        assert "initial" in jsonsrc
        assert "vowels" in jsonsrc

        self._max: int
        self._min: int
        self._initial: Sequence[str]
        self._medial: Sequence[str]
        self._final: Sequence[str]
        self._vowels: Sequence[str]

        # TODO: Verify types from `jsonsrc`
        self._min = jsonsrc["min_syllables"]
        self._max = jsonsrc["max_syllables"]
        self._vowels = jsonsrc["vowels"]
        self._initial = jsonsrc["initial"]
        if "final" not in jsonsrc or not jsonsrc["final"]:
            self._final = [""]
        else:
            self._final = jsonsrc["final"]
        if "medial" not in jsonsrc or not jsonsrc["medial"]:
            self._medial = [
                "".join(x) for x in itertools.product(self._final, self._initial)
            ]
        else:
            self._medial = jsonsrc["medial"]

    def name(self) -> str:
        name_seq: list[str] = []
        nsyllables: int = random.randint(self._min, self._max)

        name_seq.append(random.choice(self._initial))
        name_seq.append(random.choice(self._vowels))
        for _ in range(1, nsyllables):
            name_seq.append(random.choice(self._medial))
            name_seq.append(random.choice(self._vowels))
        name_seq.append(random.choice(self._final))

        return "".join(name_seq).capitalize()


class NameUniquifier:
    def __init__(self, source: NameSource) -> None:
        self._source = source
        self._pastnames: set[str] = set()

    def name(self) -> str:
        count: int = 0
        newname: str = self._source.name()
        while newname and newname in self._pastnames and count < MAX_RETRIES:
            newname = self._source.name()
            count += 1
        self._pastnames.add(newname)
        return newname


def main() -> None:
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Generate a list of names based on a grammar"
    )
    parser.add_argument(
        "namefile",
        help="JSON file specifying random name generator",
        type=argparse.FileType(mode="r", encoding="UTF-8"),
    )
    parser.add_argument(
        "-n",
        "--number",
        help="number of names to generate",
        default=DEFAULT_NUMBER_OF_NAMES,
        type=int,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output file",
        default="-",
        type=argparse.FileType(mode="w", encoding="UTF-8"),
    )
    args = parser.parse_args()

    namesrc: NameSource

    with args.namefile as jsonfile:
        namesrc = NameUniquifier(SimpleNameSource(json.load(jsonfile)))

    with args.output as outfile:
        for _ in range(args.number):
            outfile.write(f"{namesrc.name()}\n")


if __name__ == "__main__":
    main()
