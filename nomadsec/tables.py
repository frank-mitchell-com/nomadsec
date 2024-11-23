"""
Routines to generate random planetary parameters.
"""

import random
import string
from dataclasses import dataclass

from .common import (
    Characteristic,
    NomadDice,
    Settlement,
    TechAge,
    TradeClass,
)


####################### DICE #################################


def nomad_dice(nkeep: int = 2, nadv: int = 0, nsides: int = 6, low: int = 1) -> int:
    """
    Roll `nkeep` + abs(`nadv`) `nsides`-sided dice;
    if nadv is negative, keep the `nkeep`
    lowest, else keep the `nkeep` highest.
    """

    def one_die():
        return random.randint(low, nsides + low - 1)

    if nkeep == 1 and nadv == 0:
        return one_die()

    ntotal: int = nkeep + abs(nadv)
    rolls: list[int] = [one_die() for _ in range(ntotal)]
    rolls.sort()
    return sum(rolls[:nkeep]) if nadv < 0 else sum(rolls[-nkeep:])


####################### TABLES ################################

# All tables copied from the XD6 SRD.


SETTLEMENT_TYPES: list[Settlement] = list(Settlement)


SETTLEMENT_TYPE_NAMES: dict[str, Settlement] = {
    s.name.lower(): s for s in SETTLEMENT_TYPES
}


TRADE_CLASS_TYPES: list[TradeClass] = list(TradeClass)


TRADE_CLASS_TO_ABBREVS: dict[TradeClass, str] = {
    TradeClass.AGRICULTURAL: "Ag",
    TradeClass.GARDEN: "Ga",
    TradeClass.INDUSTRIAL: "In",
    TradeClass.NON_AGRICULTURAL: "Na",
    TradeClass.NON_INDUSTRIAL: "Ni",
    TradeClass.POOR: "Po",
    TradeClass.RESOURCE: "Re",
    TradeClass.RICH: "Ri",
}


TRADE_CLASS_SETTLED: dict[int, TradeClass] = {
    2: TradeClass.GARDEN,
    3: TradeClass.RESOURCE,
    4: TradeClass.POOR,
    5: TradeClass.POOR,
    6: TradeClass.NON_AGRICULTURAL,
    7: TradeClass.NON_INDUSTRIAL,
    8: TradeClass.AGRICULTURAL,
    9: TradeClass.AGRICULTURAL,
    10: TradeClass.RICH,
    11: TradeClass.RICH,
    12: TradeClass.INDUSTRIAL,
}


TRADE_CLASS_UNEXPLORED: dict[int, TradeClass] = {
    2: TradeClass.POOR,
    3: TradeClass.GARDEN,
    4: TradeClass.GARDEN,
    5: TradeClass.GARDEN,
    6: TradeClass.RESOURCE,
    7: TradeClass.RESOURCE,
    8: TradeClass.POOR,
    9: TradeClass.POOR,
    10: TradeClass.POOR,
    11: TradeClass.POOR,
    12: TradeClass.POOR,
}


CHARACTERISTICS_TO_ABBREVS: dict[Characteristic, str] = {
    Characteristic.ASTEROID: "As",
    Characteristic.CORROSIVE: "Co",
    Characteristic.DESERT: "De",
    Characteristic.ICEBALL: "Ic",
    Characteristic.INERT: "In",
    Characteristic.MARGINAL: "Ma",
    Characteristic.OCEAN: "Oc",
    Characteristic.PRIME: "Pr",
    Characteristic.PRIMORDIAL: "Pl",
    Characteristic.ROCKBALL: "Ro",
    Characteristic.TAINTED: "Ta",
}


CHARACTERISTICS: dict[TradeClass, list[Characteristic]] = {
    TradeClass.AGRICULTURAL: [
        Characteristic.PRIME,
        Characteristic.PRIME,
        Characteristic.TAINTED,
        Characteristic.TAINTED,
        Characteristic.MARGINAL,
        Characteristic.OCEAN,
    ],
    TradeClass.GARDEN: [
        Characteristic.PRIME,
        Characteristic.TAINTED,
        Characteristic.MARGINAL,
        Characteristic.OCEAN,
        Characteristic.DESERT,
        Characteristic.PRIMORDIAL,
    ],
    TradeClass.INDUSTRIAL: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.MARGINAL,
        Characteristic.TAINTED,
        Characteristic.TAINTED,
        Characteristic.ICEBALL,
    ],
    TradeClass.NON_AGRICULTURAL: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.ICEBALL,
        Characteristic.MARGINAL,
        Characteristic.TAINTED,
        Characteristic.INERT,
    ],
    TradeClass.NON_INDUSTRIAL: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.ROCKBALL,
        Characteristic.MARGINAL,
        Characteristic.TAINTED,
        Characteristic.INERT,
    ],
    TradeClass.POOR: [
        Characteristic.ROCKBALL,
        Characteristic.ROCKBALL,
        Characteristic.ICEBALL,
        Characteristic.ASTEROID,
        Characteristic.INERT,
        Characteristic.CORROSIVE,
    ],
    TradeClass.RESOURCE: [
        Characteristic.ASTEROID,
        Characteristic.ROCKBALL,
        Characteristic.ICEBALL,
        Characteristic.MARGINAL,
        Characteristic.INERT,
        Characteristic.CORROSIVE,
    ],
    TradeClass.RICH: [
        Characteristic.PRIME,
        Characteristic.PRIME,
        Characteristic.TAINTED,
        Characteristic.TAINTED,
        Characteristic.MARGINAL,
        Characteristic.OCEAN,
    ],
}


@dataclass(frozen=True, slots=True)
class PopulationSpec:
    ndice: int
    modifier: int
    multiplier: int


POPULATION: dict[TradeClass, PopulationSpec] = {
    TradeClass.AGRICULTURAL: PopulationSpec(1, 0, 50_000_000),
    TradeClass.GARDEN: PopulationSpec(0, 0, 0),
    TradeClass.INDUSTRIAL: PopulationSpec(2, 0, 500_000_000),
    TradeClass.NON_AGRICULTURAL: PopulationSpec(1, 0, 200_000_000),
    TradeClass.NON_INDUSTRIAL: PopulationSpec(2, 0, 50_000),
    TradeClass.POOR: PopulationSpec(2, -8, 500),  # none if unexplored
    TradeClass.RESOURCE: PopulationSpec(0, 0, 0),
    TradeClass.RICH: PopulationSpec(4, 0, 100_000_000),
}


TECHNOLOGY_AGES: list[TechAge] = list(TechAge)


TECHNOLOGY_AGES_ABBREVS: dict[str, TechAge] = {
    "ep": TechAge.EARLY_PRIMITIVE,
    "lp": TechAge.LATE_PRIMITIVE,
    "em": TechAge.EARLY_MECHANICAL,
    "lm": TechAge.LATE_MECHANICAL,
    "ea": TechAge.EARLY_ATOMIC,
    "la": TechAge.LATE_ATOMIC,
    "es": TechAge.EARLY_SPACE,
    "ls": TechAge.LATE_SPACE,
    "ei": TechAge.EARLY_INTERSTELLAR,
    "li": TechAge.LATE_INTERSTELLAR,
    "eg": TechAge.EARLY_GALACTIC,
    "lg": TechAge.LATE_GALACTIC,
}


TECHNOLOGY_AGES_TO_ABBREVS: dict[TechAge, str] = {
    TechAge.NO_TECHNOLOGY: "NT",
    TechAge.EARLY_PRIMITIVE: "EP",
    TechAge.LATE_PRIMITIVE: "LP",
    TechAge.EARLY_MECHANICAL: "EM",
    TechAge.LATE_MECHANICAL: "LM",
    TechAge.EARLY_ATOMIC: "EA",
    TechAge.LATE_ATOMIC: "LA",
    TechAge.EARLY_SPACE: "ES",
    TechAge.LATE_SPACE: "LS",
    TechAge.EARLY_INTERSTELLAR: "EI",
    TechAge.LATE_INTERSTELLAR: "LI",
    TechAge.EARLY_GALACTIC: "EG",
    TechAge.LATE_GALACTIC: "LG",
    TechAge.COSMIC: "C",
}


TECHNOLOGY_AGES_TABLE: dict[int, TechAge] = {
    2: TechAge.EARLY_PRIMITIVE,
    3: TechAge.LATE_PRIMITIVE,
    4: TechAge.LATE_MECHANICAL,
    5: TechAge.LATE_ATOMIC,
    6: TechAge.EARLY_SPACE,
    7: TechAge.LATE_SPACE,
    8: TechAge.EARLY_INTERSTELLAR,
    9: TechAge.LATE_INTERSTELLAR,
    10: TechAge.EARLY_INTERSTELLAR,  # (sic)
    11: TechAge.EARLY_GALACTIC,
    12: TechAge.LATE_GALACTIC,
}


TECHNOLOGY_AGES_OFFSET_TABLE: dict[int, int] = {
    2: -2,
    3: -1,
    4: -1,
    5: -1,
    6: +0,
    7: +0,
    8: +0,
    9: +0,
    10: +1,
    11: +1,
    12: +2,
}


WORLD_TAG_TABLE_1: list[list[str]] = [
    [
        "Alien Ruins",
        "Ancient Ruins",
        "Battleground",
        "Capitalist",
        "Caste System",
        "Civil War",
    ],
    [
        "Corporate",
        "Declining Population",
        "Desert",
        "Feral World",
        "Forbidden Tech",
        "Glaciers",
    ],
    [
        "Historical Culture",
        "Honorable",
        "Impending Doom",
        "Liberal",
        "Mercenaries",
        "Misandry/Misogyny",
    ],
    [
        "Multiple Species",
        "Nomads",
        "Peaceful",
        "Police State",
        "Psionics",
        "Radioactive",
    ],
    [
        "Restrictive Laws",
        "Robots",
        "Segregated",
        "Separate Cultures",
        "Superstitious",
        "Terraforming",
    ],
    [
        "Trade Hub",
        "Underground Cities",
        "Unusual Tech",
        "Utopia",
        "Xeno-archeology",
        "Xenophobia",
    ],
]


WORLD_TAG_TABLE_2: list[list[str]] = [
    [
        "Altered Humanity",
        "Athenian Democracy",
        "Beautiful",
        "Captive Government",
        "Charismatic Dictator",
        "Cold War",
    ],
    [
        "Cyborgs",
        "Democracy",
        "Eugenics",
        "Feudal",
        "Freak Weather",
        "Gladiators",
    ],
    [
        "Holy War",
        "Hostile Space",
        "Jungle World",
        "Megafauna",
        "Minimal Laws",
        "Multiple Govs.",
    ],
    [
        "Night/Day",
        "Oceans",
        "Pleasure World",
        "Primitives",
        "Quarantined",
        "Religious",
    ],
    [
        "Rigid Culture",
        "Salvage Economy",
        "Seismic Instability",
        "Slavery",
        "Taboo Custom",
        "Theocracy",
    ],
    [
        "Transhuman",
        "Unusual Custom",
        "Unusual Weather",
        "Warlords",
        "Xenophiles",
        "Zombies",
    ],
]

####################### TABLE LOOKUPS #############################


def settlement_name_list() -> list[str]:
    return list(SETTLEMENT_TYPE_NAMES)


def str_to_settlement(name: str | None) -> Settlement | None:
    return SETTLEMENT_TYPE_NAMES.get(name.lower()) if name else None


def settlement_str(settlement: Settlement | None) -> str:
    assert not settlement or settlement in SETTLEMENT_TYPES
    if not settlement:
        return ""
    return settlement.name.capitalize()


def trade_class(settle: Settlement | None, roll: NomadDice = nomad_dice) -> TradeClass:
    assert not settle or settle in SETTLEMENT_TYPES
    assert roll

    result: int
    if settle == Settlement.UNEXPLORED:
        result = roll(2)
        return TRADE_CLASS_UNEXPLORED[result]
    if settle == Settlement.CORE:
        result = roll(2, +2)
    elif settle == Settlement.FRONTIER:
        result = roll(2, -1)
    elif settle == Settlement.CONFLICT:
        result = roll(2, +1)
    else:
        result = roll(2)
    return TRADE_CLASS_SETTLED[result]


def trade_class_str(trade: TradeClass | None) -> str:
    assert not trade or trade in TRADE_CLASS_TYPES
    if not trade:
        return ""
    return string.capwords(trade.name.replace("_", " ")).replace(" ", "-")


def trade_class_abbrev(trade: TradeClass | None) -> str:
    assert not trade or trade in TRADE_CLASS_TYPES
    return TRADE_CLASS_TO_ABBREVS[trade] if trade else ""


def characteristic(tc: TradeClass, roll: NomadDice = nomad_dice) -> Characteristic:
    assert tc in CHARACTERISTICS
    return CHARACTERISTICS[tc][roll(1) - 1]


def chara_str(c: Characteristic | None) -> str:
    return c.name.capitalize() if c else ""


def chara_abbrev(c: Characteristic | None) -> str:
    return CHARACTERISTICS_TO_ABBREVS[c] if c else ""


def population(
    tc: TradeClass, settle: Settlement | None, roll: NomadDice = nomad_dice
) -> int:
    assert tc in TRADE_CLASS_TYPES
    assert not settle or settle in SETTLEMENT_TYPES
    assert roll

    if tc == TradeClass.POOR and settle == Settlement.UNEXPLORED:
        return 0
    assert tc in POPULATION
    popspec: PopulationSpec = POPULATION[tc]
    pop: int = (roll(popspec.ndice) + popspec.modifier) * popspec.multiplier
    return max(pop, 0)


def population_abbrev(pop: int) -> str:
    # sourcery skip: assign-if-exp, reintroduce-else
    if pop == 0:
        return f"{pop:6d}"
    if pop % 1_000_000_000 == 0:
        return f"{pop//1_000_000_000:5d}B"
    if pop % 1_000_000 == 0:
        return f"{pop//1_000_000:5d}M"
    if pop % 1_000 == 0:
        return f"{pop//1_000:5d}K"
    return f"{pop:6d}"


def tech_age_random(roll: NomadDice = nomad_dice) -> TechAge:
    assert roll
    return TECHNOLOGY_AGES_TABLE[roll(2)]


def tech_age_offset(age: TechAge, roll: NomadDice = nomad_dice) -> TechAge:
    assert age in TECHNOLOGY_AGES
    assert roll

    offset: int = TECHNOLOGY_AGES_OFFSET_TABLE[roll(2)]
    index: int = age.value
    if index + offset < TechAge.EARLY_PRIMITIVE.value:
        return TechAge.EARLY_PRIMITIVE
    if index + offset > TechAge.LATE_GALACTIC.value:
        return TechAge.LATE_GALACTIC
    return TECHNOLOGY_AGES[index + offset]


def tech_age(
    pop: int, avg_age: TechAge | None = None, roll: NomadDice = nomad_dice
) -> TechAge:
    assert not avg_age or avg_age in TECHNOLOGY_AGES
    assert roll
    if pop == 0:
        return TechAge.NO_TECHNOLOGY
    return tech_age_offset(avg_age, roll) if avg_age else tech_age_random(roll)


def tech_age_str(age: TechAge | None) -> str:
    return string.capwords(age.name.replace("_", " ")) if age else ""


def tech_age_abbrev_list() -> list[str]:
    return list(TECHNOLOGY_AGES_ABBREVS)


def tech_age_abbrev(age: TechAge | None) -> str:
    return TECHNOLOGY_AGES_TO_ABBREVS.get(age, "") if age else ""


def str_to_tech_age(agestr: str | None) -> TechAge | None:
    return TECHNOLOGY_AGES_ABBREVS.get(agestr) if agestr else None


def world_tag(index: int = 1, roll: NomadDice = nomad_dice) -> str:
    assert roll
    if index % 2 == 1:
        return WORLD_TAG_TABLE_1[roll(1) - 1][roll(1) - 1]
    return WORLD_TAG_TABLE_2[roll(1) - 1][roll(1) - 1]
