from typing import cast
import logging
import os

from .config import parse_args, RunConfig, SummaryConfig
from .runner import run
from .weekly import weekly_summary


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
    cmd, cfg = parse_args()
    base_dir = cfg.base_dir if hasattr(cfg, "base_dir") else os.getcwd()
    _setup_logging(base_dir)

    if cmd == "run":
        run(cast(RunConfig, cfg))
        return

    weekly_summary(cast(SummaryConfig, cfg))


if __name__ == "__main__":
    main()
