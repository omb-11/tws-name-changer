from pathlib import Path
import sys

# Allows `python main.py` from a source checkout without an editable install.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tws_name_changer.app import run

if __name__ == "__main__":
    raise SystemExit(run())

