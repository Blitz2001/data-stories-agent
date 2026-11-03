"""2D renderer: matplotlib frames piped to ffmpeg. Fast on any laptop (~40 s per 10 s clip)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

import brand as B
from render_3d import write_music
from story import build_story, load_population

OUT = Path(__file__).parent / "out"

for f in (Path(__file__).parent / "fonts").glob("*.otf"):
    font_manager.fontManager.addfont(str(f))
plt.rcParams["font.family"] = ["Inter", "DejaVu Sans"]


def main(fps: int = 30):
    story = build_story(load_population())
    countries, labels = story["countries"], story["labels"]
    final = [story["series"][c][-1] for c in countries]
    xmax = float(np.ceil(abs(min(final)) / 5) * 5) + 5
    fig = plt.figure(figsize=(B.W / 100, B.H / 100), dpi=100, facecolor=B.SURFACE)

    def draw(t):
        fig.clf()
        year = B.year_at(t, story["start"], story["end"])
        fig.text(0.07, 0.915, B.CHANNEL, color=B.MUTED, fontsize=26, weight="bold")
        fig.text(0.93, 0.915, f"{int(round(year))}", ha="right", fontsize=34, weight="bold",
                 color=B.ACCENT if t >= B.RACE_END else B.TEXT_2)
        fig.text(0.07, 0.855, story["title"], color=B.TEXT, fontsize=64, weight="bold")
        fig.text(0.07, 0.825, story["subtitle"], color=B.TEXT_2, fontsize=24)

        ax = fig.add_axes([0.30, 0.30, 0.62, 0.48], facecolor=B.SURFACE)
        vals = B.values_at(story["series"], year, story["start"]) if t >= B.HOOK_END else None
        payoff = B.ease((t - B.RACE_END) / 0.8)
        ypos = np.arange(len(countries))[::-1]
        for i, (y, c, lbl) in enumerate(zip(ypos, countries, labels)):
            lost = max(-vals[c], 0) if vals else 0
            col = B.ACCENT if (i == 0 and payoff > 0.5) else B.BAR
            ax.barh(y, lost, height=0.72, color=col, edgecolor=B.SURFACE, linewidth=2)
            ax.text(-0.6, y, lbl, ha="right", va="center", color=B.TEXT, fontsize=27)
            if vals:
                ax.text(lost + 0.6, y, f"−{lost:.0f}%", ha="left", va="center", color=B.TEXT_2, fontsize=25)
        ax.set_xlim(0, xmax); ax.set_ylim(-0.6, len(countries) - 0.4)
        for s in ax.spines.values():
            s.set_visible(False)
        ticks = list(range(0, int(xmax), 10))
        ax.set_yticks([]); ax.set_xticks(ticks)
        ax.set_xticklabels([f"−{v}%" if v else "0" for v in ticks])
        ax.tick_params(axis="x", colors=B.MUTED, labelsize=20, length=0)
        ax.grid(axis="x", color=B.GRID, linewidth=1); ax.set_axisbelow(True)

        if t < B.HOOK_END + 0.4:
            a = 1 - B.ease((t - B.HOOK_END + 0.1) / 0.5)
            fig.patches.append(plt.Rectangle((0, 0.28), 1, 0.52, transform=fig.transFigure,
                                             color=B.SURFACE, alpha=0.88 * a, zorder=5))
            fig.text(0.5, 0.56, f"{story['start']} → {story['end']}", ha="center", color=B.TEXT_2,
                     fontsize=40, alpha=a, zorder=6)
            fig.text(0.5, 0.49, "Who got smaller?", ha="center", color=B.TEXT, fontsize=78,
                     weight="bold", alpha=a * B.ease(t / 0.5), zorder=6)
        if t >= B.RACE_END:
            a = B.ease((t - B.RACE_END) / 0.6)
            shown = story["lead_change"] * B.ease((t - B.RACE_END) / 1.0)
            fig.text(0.07, 0.205, f"{shown:.1f}%".replace("-", "−"), color=B.ACCENT,
                     fontsize=120, weight="bold", alpha=a)
            fig.text(0.07, 0.17, f"{story['lead']}: {story['pop_start']/1e6:.2f}M → "
                     f"{story['pop_end']/1e6:.2f}M people", color=B.TEXT, fontsize=30, alpha=a)
        for c0, c1, text in B.captions(story):
            if c0 <= t < c1:
                a = B.ease((t - c0) / 0.25)
                fig.text(0.5, 0.115, text, ha="center", va="center", color=B.TEXT, fontsize=36,
                         weight="bold", alpha=a, linespacing=1.3,
                         bbox=dict(boxstyle="round,pad=0.5", fc="#000000", ec="none", alpha=0.55 * a))
        fig.text(0.07, 0.045, f"Source: {story['source_name']}", color=B.MUTED, fontsize=19)

    OUT.mkdir(exist_ok=True)
    music = OUT / "music_2d.wav"
    write_music(music, B.SECONDS)
    video = OUT / "test_clip_2d.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                           "-s", f"{B.W}x{B.H}", "-r", str(fps), "-i", "-", "-i", str(music),
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac",
                           "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(video)],
                          stdin=subprocess.PIPE)
    for i in range(fps * B.SECONDS):
        draw(i / fps)
        fig.canvas.draw()
        ff.stdin.write(fig.canvas.buffer_rgba().tobytes())
    ff.stdin.close(); ff.wait()
    print("wrote", video)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
