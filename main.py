from pathlib import Path
import sys

# Support both development checkout and PyInstaller frozen execution
if getattr(sys, "frozen", False):
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
else:
    base_dir = Path(__file__).parent

src_dir = base_dir / "src"
if src_dir.exists() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from tws_name_changer.app import run

if __name__ == "__main__":
    raise SystemExit(run())
