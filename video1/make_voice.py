#!/usr/bin/env python3
"""Generate per-scene voiceover with edge-tts and measure durations."""
import asyncio, json, os, subprocess
from edge_tts import Communicate

BASE = os.path.expanduser("~/YouTube/CuriousCortex/video1")
VOICE = "en-US-AndrewNeural"   # deep documentary male
scenes = json.load(open(f"{BASE}/scenes.json"))

async def gen(scene, attempts=4):
    mp3 = f"{BASE}/voice/{scene['id']}.mp3"
    import time as _t
    for i in range(attempts):
        try:
            c = Communicate(scene["narration"], VOICE, rate="-4%")
            await c.save(mp3)
            if os.path.getsize(mp3) > 2000:   # sanity: non-empty audio
                break
        except Exception as e:
            print(f"  {scene['id']} attempt {i+1} failed: {e.__class__.__name__}, retrying...")
            await asyncio.sleep(2 + i * 3)
    else:
        raise RuntimeError(f"voice failed for {scene['id']}")
    # duration via ffprobe
    dur = float(subprocess.check_output([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", mp3]).strip())
    return scene["id"], dur

async def main():
    durations = {}
    for s in scenes:
        sid, dur = await gen(s)
        durations[sid] = round(dur, 2)
        print(f"{sid}: {dur:.1f}s")
    total = sum(durations.values())
    print(f"TOTAL voice: {total:.1f}s (~{total/60:.1f} min)")
    json.dump(durations, open(f"{BASE}/voice/durations.json", "w"), indent=1)

asyncio.run(main())
