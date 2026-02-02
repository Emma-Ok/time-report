import os
import tempfile
import unittest

from worklog.storage import append_jsonl, read_jsonl
from worklog.domain import Entry


class TestStorage(unittest.TestCase):
    def test_append_and_read_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.jsonl")
            entry = Entry(
                date="2026-02-02",
                start="2026-02-02T12:00:00-05:00",
                end="2026-02-02T13:00:00-05:00",
                minutes=60,
                activity="reunion",
                tags="azure-devops",
            )
            append_jsonl(path, entry)
            entries = read_jsonl(path)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].activity, "reunion")

    def test_read_jsonl_skips_invalid_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.jsonl")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{bad json}\n")
                f.write("{}\n")
            entries = read_jsonl(path)
            self.assertEqual(entries, [])


if __name__ == "__main__":
    unittest.main()
