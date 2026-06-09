import os
from types import SimpleNamespace

os.environ.setdefault("FOOTBALLVERSE_DISABLE_CV", "1")

from backend.cv_engine import GestureRecognizer


def point(x: float, y: float):
    return SimpleNamespace(x=x, y=y)


def base_landmarks():
    lm = [point(0.5, 0.75) for _ in range(21)]
    lm[0] = point(0.5, 0.8)
    lm[4] = point(0.2, 0.75)

    lm[5] = point(0.5, 0.55)
    lm[6] = point(0.5, 0.56)
    lm[8] = point(0.5, 0.57)

    for mcp, pip, tip, x in ((9, 10, 12, 0.46), (13, 14, 16, 0.54), (17, 18, 20, 0.6)):
        lm[mcp] = point(x, 0.56)
        lm[pip] = point(x, 0.57)
        lm[tip] = point(x, 0.58)
    return lm


def set_index(lm, tip_x: float, tip_y: float, pip_x: float, pip_y: float):
    lm[5] = point(0.5, 0.55)
    lm[6] = point(pip_x, pip_y)
    lm[8] = point(tip_x, tip_y)


def set_extended_finger(lm, mcp: int, pip: int, tip: int, x: float):
    lm[mcp] = point(x, 0.56)
    lm[pip] = point(x, 0.36)
    lm[tip] = point(x, 0.16)


def classify(lm):
    return GestureRecognizer()._classify(lm)[0]


def test_classifies_index_direction_by_vector():
    cases = [
        ((0.18, 0.55, 0.34, 0.55), "Point Left"),
        ((0.82, 0.55, 0.66, 0.55), "Point Right"),
        ((0.5, 0.16, 0.5, 0.35), "Point Up"),
        ((0.5, 0.9, 0.5, 0.73), "Point Down"),
    ]

    for (tip_x, tip_y, pip_x, pip_y), expected in cases:
        lm = base_landmarks()
        set_index(lm, tip_x, tip_y, pip_x, pip_y)
        assert classify(lm) == expected


def test_open_hand_is_not_a_pointing_gesture():
    lm = base_landmarks()
    set_index(lm, 0.5, 0.16, 0.5, 0.35)
    set_extended_finger(lm, 9, 10, 12, 0.46)
    set_extended_finger(lm, 13, 14, 16, 0.54)
    set_extended_finger(lm, 17, 18, 20, 0.6)

    assert classify(lm) is None


def test_pinch_takes_priority_over_pointing():
    lm = base_landmarks()
    set_index(lm, 0.5, 0.16, 0.5, 0.35)
    lm[4] = point(0.51, 0.17)

    assert classify(lm) == "Pinch"
