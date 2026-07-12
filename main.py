from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
MIN_SUPPORTED_VERSION = (3, 11)
MAX_SUPPORTED_VERSION = (3, 13)

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from app import ChessApplication


def main() -> None:
    if sys.version_info < MIN_SUPPORTED_VERSION or sys.version_info[:2] > MAX_SUPPORTED_VERSION:
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        raise RuntimeError(
            "This project supports Python 3.11 through 3.13 for the pygame GUI. "
            f"Detected Python {version}. Please create the virtual environment with Python 3.11, 3.12, or 3.13."
        )
    ChessApplication().run()


if __name__ == "__main__":
    main()
