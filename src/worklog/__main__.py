import logging
import os
import sys

from .cli import app


def _setup_logging(base_dir: str) -> None:
    root = logging.getLogger()
    if root.handlers:
        return
    try:
        os.makedirs(base_dir, exist_ok=True)
    except Exception:
        base_dir = os.getcwd()
    log_path = os.path.join(base_dir, "worklog.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main() -> None:
    base_dir = "logs"
    args = sys.argv[1:]
    if "--base-dir" in args:
        idx = args.index("--base-dir")
        if idx + 1 < len(args):
            base_dir = args[idx + 1]

    _setup_logging(base_dir)
    app()


if __name__ == "__main__":
    main()
