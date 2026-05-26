import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from avd_project.analysis import run_analysis


if __name__ == "__main__":
    outputs = run_analysis()
    for name, path in outputs.items():
        print(f"{name}: {path}")
