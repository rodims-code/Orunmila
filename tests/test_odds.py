"""Tests de odds.py : on vérifie que la conversion cotes -> probabilités est juste."""

import numpy as np

from orunmila.odds import overround, remove_margin


def test_margin_is_computed():
    # cotes 2,0 / 3,0 / 3,0 -> 50 % + 33,3 % + 33,3 % = 116,7 %, soit 16,7 % de marge
    margin = overround([2.0], [3.0], [3.0])
    assert np.isclose(margin[0], 1 / 6)


def test_remove_margin_sums_to_one():
    probs = remove_margin([2.0, 1.5], [3.0, 4.0], [3.0, 7.0])
    assert np.allclose(probs.sum(axis=1), 1.0)


def test_remove_margin_known_values():
    probs = remove_margin([2.0], [3.0], [3.0])
    expected = np.array([0.5, 1 / 3, 1 / 3]) / (1 + 1 / 6)
    assert np.allclose(probs[0], expected)
