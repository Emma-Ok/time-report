import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from worklog.clock import parse_hhmm, is_work_time, next_work_start, WorkWindow


class TestClock(unittest.TestCase):
    def test_parse_hhmm_valid(self) -> None:
        self.assertEqual(parse_hhmm("07:30"), (7, 30))

    def test_parse_hhmm_invalid(self) -> None:
        with self.assertRaises(ValueError):
            parse_hhmm("25:00")

    def test_is_work_time(self) -> None:
        tz = ZoneInfo("America/Bogota")
        w = WorkWindow(7, 0, 17, 0)
        dt = datetime(2026, 2, 2, 9, 0, tzinfo=tz)  # Monday
        self.assertTrue(is_work_time(dt, w))

    def test_next_work_start_weekend(self) -> None:
        tz = ZoneInfo("America/Bogota")
        w = WorkWindow(7, 0, 17, 0)
        dt = datetime(2026, 2, 7, 10, 0, tzinfo=tz)  # Saturday
        nxt = next_work_start(dt, w)
        self.assertEqual(nxt.weekday(), 0)
        self.assertEqual(nxt.hour, 7)
        self.assertEqual(nxt.minute, 0)


if __name__ == "__main__":
    unittest.main()
