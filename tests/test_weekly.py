import os
import tempfile
import unittest
from datetime import date

from worklog.weekly import _write_weekly_md
from worklog.domain import Entry


class TestWeekly(unittest.TestCase):
    def test_write_weekly_md_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "summary.md")
            entries = [
                Entry(
                    date="2026-02-02",
                    start="2026-02-02T12:00:00-05:00",
                    end="2026-02-02T13:00:00-05:00",
                    minutes=60,
                    activity="dev",
                    tags="azure-devops",
                )
            ]
            _write_weekly_md(out_path, "2026-W05", date(2026, 2, 2), date(2026, 2, 8), entries, False)
            self.assertTrue(os.path.exists(out_path))


if __name__ == "__main__":
    unittest.main()
