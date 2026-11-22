"""Assert API-layer agreement on the IEEE 13 snapshot through the three wrappers."""
import subprocess
import sys
from pathlib import Path


if __name__ == "__main__":
    tool = Path(__file__).resolve().parents[2] / "tools" / "compare_interfaces.py"
    subprocess.run([sys.executable, "-B", str(tool), "--fixture", "ieee13"], check=True)
