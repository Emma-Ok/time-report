from .config import parse_args
from .runner import run
from .weekly import weekly_summary

def main() -> None:
    cmd, cfg = parse_args()
    if cmd == "run":
        run(cfg)
    else:
        weekly_summary(cfg)

if __name__ == "__main__":
    main()
