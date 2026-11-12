#!/usr/bin/env python3
"""Video 1 scene definitions: narration + captions + visual element specs."""
import json, os

V1 = [
  dict(id="s01",
       narration="Try to remember being two years old. A birthday. A face. One single moment. Nothing, right? That's not your fault. Your brain deleted those memories on purpose.",
       caption="AGE 2: BLANK",
       elements=[
         dict(kind="frame", cx=0.30, cy=0.42, s=0.20, t0=0.05, color="pink"),   # empty photo frame
         dict(kind="qm", cx=0.30, cy=0.42, s=0.09, t0=0.20, color="yellow"),    # ? inside frame
         dict(kind="sparkle", cx=0.48, cy=0.20, s=0.03, t0=0.35, color="teal"),
         dict(kind="caption", text="AGE 2: BLANK", t0=0.45, color="white"),
       ]),
  dict(id="s02",
       narration="It even has a name — infantile amnesia — and it happens to almost every human on Earth.",
       caption="INFANTILE AMNESIA",
       elements=[
         dict(kind="brain", cx=0.30, cy=0.38, s=0.15, t0=0.05, color="pink"),
         dict(kind="label", text="INFANTILE AMNESIA", t0=0.35, color="white"),
         dict(kind="sparkle", cx=0.62, cy=0.30, s=0.03, t0=0.50, color="yellow"),
       ]),
  dict(id="s03",
       narration="Here's the strange part: babies remember just fine. A newborn can pick out their mother's voice within days of being born.",
       caption="BABIES REMEMBER",
       elements=[
         dict(kind="baby", cx=0.32, cy=0.46, s=0.16, t0=0.05, color="teal"),
         dict(kind="waves", cx=0.32, cy=0.46, s=0.30, t0=0.30, color="yellow"),
         dict(kind="caption", text="BABIES REMEMBER", t0=0.45, color="white"),
       ]),
  dict(id="s04",
       narration="In one famous experiment, babies learned that kicking their foot moves a mobile hanging above them — and they remembered the trick for days.",
       caption="THE MOBILE TRICK",
       elements=[
         dict(kind="mobile", cx=0.55, cy=0.0, s=0.30, t0=0.05, color="pink"),
         dict(kind="baby", cx=0.28, cy=0.58, s=0.17, t0=0.25, color="teal"),
         dict(kind="arrow", x0=0.42, y0=0.72, x1=0.28, y1=0.58, t0=0.45, color="yellow"),
         dict(kind="caption", text="THE MOBILE TRICK", t0=0.55, color="white"),
       ]),
  dict(id="s05",
       narration="So the memories are in there. The problem isn't saving them. It's finding them later.",
       caption="SAVED, NOT SEARCHABLE",
       elements=[
         dict(kind="brain", cx=0.30, cy=0.38, s=0.15, t0=0.05, color="pink"),
         dict(kind="cabinet", cx=0.62, cy=0.52, s=0.18, t0=0.30, color="teal"),
         dict(kind="caption", text="SAVED, NOT SEARCHABLE", t0=0.50, color="white"),
       ]),
  dict(id="s06",
       narration="Because your hippocampus — the brain's memory hard drive — is still under construction until around age four.",
       caption="HIPPOCAMPUS",
       elements=[
         dict(kind="seahorse", cx=0.33, cy=0.44, s=0.26, t0=0.05, color="pink"),
         dict(kind="label", text="HIPPOCAMPUS — MEMORY'S HARD DRIVE", t0=0.40, color="yellow"),
       ]),
  dict(id="s07",
       narration="It's flooding with new neurons, and every wave of new cells literally rewires the circuits where your earliest memories are stored.",
       caption="NEW NEURONS REWIRE",
       elements=[
         dict(kind="neurons", cx=0.50, cy=0.45, s=0.38, t0=0.05, color="pink"),
         dict(kind="caption", text="NEW NEURONS REWIRE", t0=0.55, color="teal"),
       ]),
  dict(id="s08",
       narration="On top of that, before age three you have no language — and language is the index that lets you look a memory up. No words, no search bar.",
       caption="NO WORDS = NO SEARCH BAR",
       elements=[
         dict(kind="bubble", cx=0.35, cy=0.40, s=0.26, t0=0.05, color="teal"),
         dict(kind="caption", text="NO WORDS = NO SEARCH BAR", t0=0.40, color="white"),
       ]),
  dict(id="s09",
       narration="Some of it survives as pure feeling: a warm glow when you're held, a spike of fear at the doctor's office. The story is gone; the emotion stayed.",
       caption="FEELINGS SURVIVE",
       elements=[
         dict(kind="heart", cx=0.33, cy=0.42, s=0.17, t0=0.05, color="pink"),
         dict(kind="bolt", cx=0.60, cy=0.40, s=0.13, t0=0.30, color="yellow"),
         dict(kind="caption", text="FEELINGS SURVIVE", t0=0.50, color="white"),
       ]),
  dict(id="s10",
       narration="So no — your brain isn't broken. It threw away the scaffolding so it could build the tower. Everything you can remember right now… you can thank the demolition for that.",
       caption="THE SCAFFOLD HAD TO GO",
       elements=[
         dict(kind="tower", cx=0.35, cy=0.42, s=0.24, t0=0.05, color="pink"),
         dict(kind="caption", text="THE SCAFFOLD HAD TO GO", t0=0.50, color="white"),
         dict(kind="sparkle", cx=0.68, cy=0.25, s=0.04, t0=0.70, color="yellow"),
       ]),
]

out = os.path.expanduser("~/YouTube/CuriousCortex/video1")
json.dump(V1, open(f"{out}/scenes.json", "w"), indent=1)
total_words = sum(len(s["narration"].split()) for s in V1)
print(f"scenes: {len(V1)}, narration words: {total_words} (~{total_words/150*60:.0f}s)")
