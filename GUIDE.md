# Data Stories – how to use it, and how to get the best videos for free

## 1. What you have now

```
data-stories-agent/
├── make_clip.py      ← the one command you run
├── story.py          ← data step: loads the dataset, computes the story, VERIFIES every number
├── brand.py          ← colours, fonts, timing (hook / race / payoff) – edit this to restyle
├── render_2d.py      ← flat animated chart (matplotlib) – fast, ~1 min on any laptop
├── render_3d.py      ← 3D chart (Blender) + crisp text overlay – the "premium" look
├── fonts/            ← Inter font (free, SIL Open Font License), bundled
├── data/             ← dataset (downloaded automatically on first run)
└── out/              ← finished videos, story.json, preview stills
```

The data step and both renderers share **one verified story** (`out/story.json`).
That means the 2D and 3D versions always show the same, checked numbers.
If the data ever changes so a sentence like "almost 1 in 3" stops being true,
the build **fails** instead of publishing a wrong claim.

## 2. Setup on your laptop (Windows, RTX 3050)

1. Install **Python 3.13** from python.org (tick "Add to PATH").
   *bpy 5.2 (Blender as a Python module) only works with Python 3.13.*
2. Install ffmpeg:

   ```bash
   winget install Gyan.FFmpeg
   ```

3. Update your NVIDIA driver (GeForce Experience or nvidia.com).
4. In the project folder:

   ```bash
   python -m venv .venv
   ```

   ```bash
   .venv\Scripts\activate
   ```

   ```bash
   pip install -r requirements.txt
   ```

## 3. Commands

| What | Command | Time on RTX 3050 laptop (estimate) |
|---|---|---|
| Check the numbers only | `python make_clip.py --check` | 2 s |
| 2D clip | `python make_clip.py` | ~1 min |
| 3D quick look | `python make_clip.py --style 3d --quality draft` | ~1 min |
| 3D good | `python make_clip.py --style 3d --quality final --engine eevee` | ~5–10 min |
| 3D best (ray-traced) | `python make_clip.py --style 3d --quality final --engine cycles-gpu` | ~15–30 min |

`--engine auto` (the default) picks EEVEE when it finds a GPU and falls back to
CPU otherwise, so the same command works on any machine. The times above are
estimates; the script prints real seconds-per-frame and an ETA while it runs.
Only on CPU (no GPU) is 3D slow: ~20 s per frame at full size.

Workflow tip: always do `draft` first, look at the stills, then render `final` once.

## 4. 2D vs 3D – which to use

| | 2D (matplotlib) | 3D (Blender) |
|---|---|---|
| Look | clean, data-journalism | depth, lighting, camera moves – feels "produced" |
| Render time | ~1 min | ~5–30 min on your GPU |
| Best for | daily Shorts, quick topics, Fiverr drafts | your best 1–2 videos a week, channel trailer, thumbnails |
| Risk | can look like every other chart channel | can be slow; too much motion hurts readability |

**Recommendation:** use 3D for the main video of the week and its thumbnail, and 2D for quick extras.
Use the 3D still at the payoff moment (`out/3d_still_9.5s.png`) as your thumbnail base.
It already looks premium.

## 5. How to get the best output for free

**Voice has the biggest impact.**
- Record it yourself on your phone in a quiet room, holding the phone 15–20 cm away. Clean it with **Audacity** (free): Noise Reduction → Compressor → Normalize to −1 dB.
  A real human voice gets better retention, and it clearly counts as original work for monetization.
- If you'd rather not use your voice, **Kokoro TTS** (free, open model) sounds very good and runs fast on your GPU.
  **Piper** is lighter but sounds more robotic.

**Hook (first 2 seconds).**
- Ask a question or make a surprising claim with a number: "Moldova lost 1 in 3 people. Here's who else is shrinking."
- Show movement in the very first frame; never open on a static title card.

**Pacing.**
- Shorts: 30–45 s. One idea, one chart, one payoff number.
- Cut anything that doesn't move the story forward. Rewatches matter more than length.

**Captions.** They're burned in, which matters because most people watch Shorts muted. Keep them to ≤ 7 words per line.

**Credibility.** The source is always on screen and in the description. This builds trust and protects monetization.

**Free tools worth having.**
- **Blender**: for 3D beyond this script, e.g. globes and maps. Use the same scene files.
- **DaVinci Resolve (free)**: for manual touch-ups or longer videos.
- **Audacity**: voice clean-up.
- **Our World in Data, World Bank, UN data, Kaggle**: free data sources.
- Music: keep using the code-generated bed, or YouTube Audio Library tracks (free, safe on YouTube).

**What to avoid.**
- Stock AI faces or AI-generated "realistic" footage: this triggers the disclosure requirement and the slop filters.
- Re-using the same template with only the numbers swapped every day. Vary the chart type (bars, lines, maps, globe) and the angle of the story.
- Health, finance and legal advice topics.

## 6. Ideas to improve next (in order)

1. **Voice + word-timed captions**: Kokoro TTS or your own recording, with captions synced word by word (whisper.cpp runs free on your GPU).
2. **More 3D scenes**: a rotating globe with countries rising as columns, a 3D line "ribbon" over time, and a population pyramid.
3. **16:9 version** of the same story for long-form videos (same `story.json`, different camera framing).
4. **Topic agent (Gemini free tier)** that proposes 5 verifiable questions per week.
5. **Review dashboard (Streamlit)**: watch, edit the script, approve, then upload as private.
6. **Similarity check** so no two videos are too alike, which keeps you safe from the "repetitive content" rule.

## 7. Restyling

Everything visual lives in `brand.py`:
- `BAR`, `ACCENT`, `SURFACE` …: colours (keep the accent for the single most important number).
- `HOOK_END`, `RACE_END`, `SECONDS`: timing of the three acts.
- `CHANNEL`: the name shown at the top.

In `render_3d.py`:
- `UNIT` (bar length per 1 %) and `ROW` (bar spacing) change the chart's proportions.
- The camera path is in `pose()`.
