"""Tests de metrics.py : on vérifie les règles de notation sur des cas dont on connaît la réponse."""

import numpy as np

from orunmila.metrics import brier_score, log_loss, max_drawdown, result_to_index, roi


def test_result_to_index():
    assert list(result_to_index(["H", "D", "A"])) == [0, 1, 2]


def test_log_loss_uniform_is_ln3():
    probs = np.full((4, 3), 1 / 3)
    assert np.isclose(log_loss(probs, [0, 1, 2, 0]), np.log(3))


def test_log_loss_perfect_prediction_is_zero():
    probs = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    assert log_loss(probs, [0, 2]) < 1e-9


def test_log_loss_penalizes_confident_mistakes():
    good = np.array([[0.6, 0.2, 0.2]])
    bad = np.array([[0.05, 0.05, 0.9]])
    assert log_loss(bad, [0]) > log_loss(good, [0])


def test_brier_uniform():
    probs = np.full((3, 3), 1 / 3)
    assert np.isclose(brier_score(probs, [0, 1, 2]), 6 / 9)


def test_roi():
    # profits +1, -1, -1, +2 avec 4 mises de 1 -> +1 au total -> ROI 25 %
    assert np.isclose(roi([1, -1, -1, 2], [1, 1, 1, 1]), 0.25)


def test_roi_without_bets_is_nan():
    assert np.isnan(roi([], []))


def test_max_drawdown():
    # cumul : 1, 2, 1, 0, -1, 1  -> sommet à 2, creux à -1 -> chute de 3
    assert np.isclose(max_drawdown([1, 1, -1, -1, -1, 2]), 3.0)
