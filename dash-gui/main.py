"""Entry point. Run with: python main.py"""
import os
import sys
from pathlib import Path

# Static widget — the software scene-graph renders identically and avoids the
# GPU backend failing when launched early at startup. Overridable via the env.
os.environ.setdefault("QT_QUICK_BACKEND", "software")

# Make the `src` layout importable without an install step.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
# Make shared project-root packages (e.g. utils) importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from investment_widget.app import Application  # noqa: E402


def main() -> int:
    return Application().run()


if __name__ == "__main__":
    sys.exit(main())
