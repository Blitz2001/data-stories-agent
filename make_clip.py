"""One command for everything.

    python make_clip.py                      # 2D clip (fast, any laptop)
    python make_clip.py --style 3d           # 3D clip, draft quality
    python make_clip.py --style 3d --quality final --engine eevee
    python make_clip.py --style 3d --quality final --engine cycles-gpu   # best, NVIDIA
    python make_clip.py --check              # only verify the numbers
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main():
    ap = argparse.ArgumentParser(description="Data Stories clip maker")
    ap.add_argument("--style", choices=["2d", "3d"], default="2d")
    ap.add_argument("--quality", choices=["draft", "preview", "final"], default="draft")
    ap.add_argument("--engine", choices=["auto", "eevee", "cycles-gpu", "cycles-cpu"], default="auto")
    ap.add_argument("--check", action="store_true", help="verify the data story and exit")
    a = ap.parse_args()

    data = HERE / "data" / "owid-co2-data.csv"
    if not data.exists():
        print("Downloading dataset from Our World in Data (GitHub)...")
        data.parent.mkdir(exist_ok=True)
        import urllib.request
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv", data)

    py = sys.executable
    if a.check:
        cmd = [py, "story.py"]
    elif a.style == "2d":
        cmd = [py, "render_2d.py"]
    else:
        cmd = [py, "render_3d.py", "--quality", a.quality, "--engine", a.engine]
    sys.exit(subprocess.call(cmd, cwd=HERE))


if __name__ == "__main__":
    main()
