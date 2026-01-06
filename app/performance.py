"""Performance timing utilities."""

import time


class Timer:
    """Simple wall-clock timer utility.

    This class is used to measure elapsed time between events,
    typically for logging and performance monitoring purposes.
    """

    def __init__(self) -> None:
        """Initialize the timer starting from the current time."""
        self.start = time.perf_counter()

    def lap(self) -> float:
        """Return the elapsed time since timer initialization.

        Returns:
            float: Elapsed time in seconds.
        """
        return time.perf_counter() - self.start
