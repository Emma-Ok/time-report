from typing import cast

from .config import parse_args, RunConfig, SummaryConfig
from .runner import run
from .weekly import weekly_summary


def main() -> None:
    cmd, cfg = parse_args()

    if cmd == "run":
        run(cast(RunConfig, cfg))
        return

    weekly_summary(cast(SummaryConfig, cfg))


if __name__ == "__main__":
    main()
