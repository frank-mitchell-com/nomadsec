#!/usr/bin/env python3

import csv
import json
from collections.abc import Iterable
from typing import Any

from .common import Planet, StarHex, StarSystem
from .sector import SectorBounds
from .sector import collect_star_systems
from .tables import (
    chara_abbrev,
    chara_str,
    population_abbrev,
    tech_age_abbrev,
    tech_age_str,
    trade_class_abbrev,
    trade_class_str,
)


def max_name_length(planets: Iterable[Planet]) -> int:
    length: int = 0
    for p in planets:
        length = max(length, len(p.name), len(p.star.name))
    return length


def write_as_xsv(outfile, planets: Iterable[Planet], sep: str = ",") -> None:
    writer = csv.writer(
        outfile, delimiter=sep, quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    writer.writerow(
        [
            "Planet",
            "Hex",
            "Trade Class",
            "Chara.",
            "Population",
            "Tech. Age",
            "World Tag 1",
            "World Tag 2",
        ]
    )
    for p in planets:
        writer.writerow(
            [
                p.name,
                p.hexcode,
                trade_class_str(p.trade_class),
                chara_str(p.chara),
                str(p.population),
                tech_age_str(p.tech_age),
                p.world_tag_1,
                p.world_tag_2,
            ]
        )


def write_as_text(outfile, planets: Iterable[Planet]) -> None:
    length: int = max_name_length(planets)

    outfile.write(
        f"|{'Planet':{length}s}|Hex |Trade Class     |Chara.    "
        "|    Population|Tech. Age         |World Tags\n"
    )
    outfile.write(
        f"|{'-'*(length)}|----|----------------|----------"
        "|-------------:|------------------|------------------------------\n"
    )
    for p in planets:
        outfile.write(
            f"|{p.name:{length}s}"
            f"|{p.hexcode}"
            f"|{trade_class_str(p.trade_class):16s}"
            f"|{chara_str(p.chara):10s}"
            f"|{p.population:14_d}"
            f"|{tech_age_str(p.tech_age):18s}"
            f"|{p.world_tag_1}, {p.world_tag_2}\n"
        )


def write_as_short_text(outfile, planets: Iterable[Planet]) -> None:
    length: int = max_name_length(planets)

    outfile.write(f"|{'Planet':{length}s}|Hex |TC|Ch|    Population|TA|World Tags\n")
    outfile.write(
        f"|{'-'*(length)}|----|--|--|-----:|--|------------------------------\n"
    )
    for p in planets:
        outfile.write(
            f"|{p.name:{length}s}"
            f"|{p.hexcode}"
            f"|{trade_class_abbrev(p.trade_class):2s}"
            f"|{chara_abbrev(p.chara):2s}"
            f"|{population_abbrev(p.population):6s}"
            f"|{tech_age_abbrev(p.tech_age):2s}"
            f"|{p.world_tag_1}, {p.world_tag_2}\n"
        )


class StarPlanetEncoder(json.JSONEncoder):
    def default(self, o) -> dict[str, Any]:
        if isinstance(o, Planet):
            p: Planet = o
            return {
                "name": p.name,
                "hex": p.hexcode,
                "trade_class": trade_class_str(p.trade_class),
                "characteristic": chara_str(p.chara),
                "population": p.population,
                "technology_age": tech_age_str(p.tech_age),
                "world_tags": [p.world_tag_1, p.world_tag_2],
            }
        if isinstance(o, StarHex):
            s: StarHex = o
            return {
                "name": s.name,
                "hex": s.hexcode,
            }
        if isinstance(o, StarSystem):
            ss: StarSystem = o
            return {
                "star": ss.star,
                "planets": ss.planets,
            }
        return json.JSONEncoder.default(self, o)


def write_as_json(
    outfile,
    bounds: SectorBounds,
    planets: Iterable[Planet],
    stars: Iterable[StarHex] | None = None,
) -> None:
    systems: list[StarSystem] = collect_star_systems(planets, stars)
    obj: dict = {
        "x": bounds.x,
        "y": bounds.y,
        "width": bounds.width,
        "height": bounds.height,
        "planets": planets,
        "systems": systems,
    }
    json.dump(obj, outfile, cls=StarPlanetEncoder, indent=4)
