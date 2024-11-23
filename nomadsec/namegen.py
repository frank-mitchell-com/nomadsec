"""
Generates random names based on a grammar specified in a JSON file.
"""

import itertools
import json
import os.path
import pkgutil
import random
from collections.abc import Mapping, Sequence


DEFAULT_NUMBER_OF_NAMES = 100

_GRAMMAR_DIR = "grammars"

# maximum retries to find a unique star name
MAX_RETRIES: int = 1_000_000


def _has_elements(d: Mapping, key: str) -> bool:
    return key in d and d[key]


def _load_grammar_file(filename: str) -> Mapping:
    grammar: Mapping
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert isinstance(data, Mapping)
        grammar = data
    return grammar


def _load_grammar(grammar_name: str) -> Mapping:
    if os.path.exists(grammar_name):
        return _load_grammar_file(grammar_name)

    if os.path.exists(grammar_name + ".json"):
        return _load_grammar_file(grammar_name + ".json")

    rcname = f"{_GRAMMAR_DIR}/{grammar_name}"
    if not grammar_name.endswith(".json"):
        rcname = rcname + ".json"
    data: bytes | None = pkgutil.get_data(__name__, rcname)
    if data:
        return json.loads(data)
    return {}


class GrammarNameSet:
    def __init__(self, grammar_name: str):
        grammar: Mapping = _load_grammar(grammar_name)

        assert "min_syllables" in grammar
        assert "max_syllables" in grammar
        assert "initial" in grammar
        assert "vowels" in grammar

        self._max: int
        self._min: int
        self._initial: Sequence[str]
        self._medial: Sequence[str]
        self._final: Sequence[str]
        self._vowels: Sequence[str]
        self._pastnames: set[str] = set()

        # TODO: Verify types from `grammar`
        self._min = grammar["min_syllables"]
        self._max = grammar["max_syllables"]
        self._vowels = grammar["vowels"]
        self._initial = grammar["initial"]
        if _has_elements(grammar, "final"):
            self._final = grammar["final"]
        else:
            self._final = [""]
        if _has_elements(grammar, "medial"):
            self._medial = grammar["medial"]
        else:
            self._medial = [
                "".join(x) for x in itertools.product(self._final, self._initial)
            ]

    def _internal_make_name(self) -> str:
        nsyllables: int = random.randint(self._min, self._max)

        name_seq: list[str] = [
            random.choice(self._initial),
            random.choice(self._vowels),
        ]
        for _ in range(1, nsyllables):
            name_seq.extend((random.choice(self._medial), random.choice(self._vowels)))
        name_seq.append(random.choice(self._final))

        return "".join(name_seq).capitalize()

    def make_name(self) -> str:
        count: int = 0
        newname: str = self._internal_make_name()
        while newname and newname in self._pastnames and count < MAX_RETRIES:
            newname = self._internal_make_name()
            count += 1
        self._pastnames.add(newname)
        return newname

    def add_to_history(self, name_s) -> None:
        self._pastnames.add(name_s)
