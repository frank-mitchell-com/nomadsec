#!/usr/bin/env python3

# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import time

from nomadsec import nomad_dice

NUM_TRIALS = 1_000_000

CHISQ_TOLERANCE = 0.05  # maybe? any stats experts here?

EXPECT_1D: dict[int, float] = {
    1: 1 / 6,
    2: 1 / 6,
    3: 1 / 6,
    4: 1 / 6,
    5: 1 / 6,
    6: 1 / 6,
}

EXPECT_2D: dict[int, float] = {
    2: 1 / 36,
    3: 2 / 36,
    4: 3 / 36,
    5: 4 / 36,
    6: 5 / 36,
    7: 6 / 36,
    8: 5 / 36,
    9: 4 / 36,
    10: 3 / 36,
    11: 2 / 36,
    12: 1 / 36,
}

EXPECT_2D_P_1D: dict[int, float] = {
    2: 0.00462962962963,
    3: 0.01388888888888,
    4: 0.0324074074074,
    5: 0.05555555555556,
    6: 0.087962962963,
    7: 0.125,
    8: 0.157497497497,
    9: 1 / 6,
    10: 0.157407407407,
    11: 0.125,
    12: 0.0740740740741,
}

EXPECT_2D_M_1D: dict[int, float] = {
    12: 0.00462962962963,
    11: 0.01388888888888,
    10: 0.0324074074074,
    9: 0.05555555555556,
    8: 0.087962962963,
    7: 0.125,
    6: 0.157497497497,
    5: 1 / 6,
    4: 0.157407407407,
    3: 0.125,
    2: 0.0740740740741,
}

EXPECT_2D_P_2D: dict[int, float] = {
    2: 0.000771604938272,
    3: 0.00308641975309,
    4: 0.0115740740741,
    5: 0.0246912580247,
    6: 0.0501543209877,
    7: 1 / 12,
    8: 0.1319444444444,
    9: 0.172839406173,
    10: 0.2012888888889,
    11: 0.188271604938,
    12: 0.1219444444444,
}


def init_histogram(start: int = 2, end: int = 2) -> dict[int, float]:
    return {x: 0.0 for x in range(start, end + 1)}


def test_dice(title: str, expect: dict[int, float], nkeep: int, nbonus: int) -> None:
    start_time: float = time.time()

    print(f"=== {title} ===")
    histogram: dict[int, float] = init_histogram(nkeep, nkeep * 6)
    for _ in range(NUM_TRIALS):
        result = nomad_dice(nkeep, nbonus)
        histogram[result] += 1

    print("Roll\tActual Prob.\tExpected\tChi**2")
    chisqtotal: float = 0
    for x in range(nkeep, nkeep * 6 + 1):
        actual = histogram[x] / NUM_TRIALS
        chisq = ((actual - expect[x]) / expect[x]) ** 2
        chisqtotal += chisq
        print(f"{x:2d}\t{actual:.8f}\t{expect[x]:.8f}\t{chisq:.10f}")
    print(f"{'':2s}\t{'':10s}\t{'TOTAL':10s}\t{chisqtotal:.10f}")

    end_time: float = time.time()

    elapsed_time: float = end_time - start_time

    if chisqtotal < CHISQ_TOLERANCE:
        print(f"OK ({elapsed_time:.3f} s)")
    else:
        print(f"FAIL ({elapsed_time:.3f} s)")
    print("================")


def main() -> None:
    test_dice("1D", EXPECT_1D, 1, 0)
    test_dice("2D", EXPECT_2D, 2, 0)
    test_dice("2D+1D", EXPECT_2D_P_1D, 2, +1)
    test_dice("2D-1D", EXPECT_2D_M_1D, 2, -1)
    test_dice("2D+2D", EXPECT_2D_P_2D, 2, +2)


if __name__ == "__main__":
    main()
