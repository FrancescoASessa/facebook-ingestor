import time

from app.performance import Timer


def test_timer_lap_positive():
    t = Timer()
    time.sleep(0.01)
    elapsed = t.lap()

    assert elapsed > 0


def test_timer_lap_returns_float():
    t = Timer()
    elapsed = t.lap()

    assert isinstance(elapsed, float)


def test_timer_lap_monotonic():
    t = Timer()

    first = t.lap()
    time.sleep(0.01)
    second = t.lap()

    assert second > first


def test_timer_initial_lap_small():
    t = Timer()
    elapsed = t.lap()

    assert 0 <= elapsed < 0.1
