#!/usr/bin/env python3
"""Assemble final video: encode scenes, concat, build voice track + soft pad, SRT."""
import json, math, os, subprocess, wave
import numpy as np
from multiprocessing import Pool

BASE = os.path.expanduser("~/YouTube/CuriousCortex/video1")
FPS = 12
SR = 44100
LEAD = 0.45   # silence before voice in each scene

scenes = json.load(open(f"{BASE}/scenes.json"))
durations = json.load(open(f"{BASE}/voice/durations.json"))

def scene_dur(sid): return max(durations[sid] + 1.0, 4.0)
def n_frames(sid): return int(round(scene_dur(sid) * FPS))

# ---------- 1. encode each scene ----------
def encode(scene):
    sid = scene["id"]
    n = n_frames(sid)
    out = f"{BASE}/scenes/{sid}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", f"{BASE}/frames/{sid}/%04d.png",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS), out], check=True)
    return sid

print("encoding scenes...")
with Pool(8) as p:
    for sid in p.map(encode, scenes):
        print(" ", sid, "done")

# ---------- 2. concat ----------
with open(f"{BASE}/concat.txt", "w") as f:
    for s in scenes:
        f.write(f"file '{BASE}/scenes/{s['id']}.mp4'\n")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
    "-i", f"{BASE}/concat.txt", "-c", "copy", f"{BASE}/exports/video1_silent.mp4"], check=True)
print("concat done")

# ---------- 3. audio: voice timeline + soft pad ----------
def decode_mp3(path):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", path,
        "-f", "wav", "-acodec", "pcm_s16le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0

starts, t = [], 0.0
for s in scenes:
    starts.append(t)
    t += scene_dur(s["id"])
total = t + 0.6
track = np.zeros(int(total * SR))
for s, st in zip(scenes, starts):
    seg = decode_mp3(f"{BASE}/voice/{s['id']}.mp3")
    i = int((st + LEAD) * SR)
    track[i:i+len(seg)] += seg

# soft ambient pad: slow chord progression, very low volume
def note(f): return np.sin(2*np.pi*f*np.arange(int(SR*2.4))/SR) * np.exp(-np.arange(int(SR*2.4))/(SR*1.8))
chords = [(220.0, 277.2, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7), (164.8, 207.7, 246.9)]
pad = np.zeros(int(total * SR))
pos, ci = 0.0, 0
while pos < total:
    seg = sum(note(f) for f in chords[ci % 4]) / 3
    i = int(pos * SR)
    end = min(i + len(seg), len(pad))
    pad[i:end] += seg[:end - i]
    pos += 2.2; ci += 1

mix = track + pad * 0.045
mix = np.clip(mix / max(1.0, np.abs(track).max()) * 0.92, -1, 1)
stereo = np.repeat((mix * 32767).astype(np.int16)[:, None], 2, axis=1)

with wave.open(f"{BASE}/master_audio.wav", "w") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(stereo.tobytes())

# ---------- 4. mux ----------
subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
    "-i", f"{BASE}/exports/video1_silent.mp4", "-i", f"{BASE}/master_audio.wav",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest",
    f"{BASE}/exports/video1_final.mp4"], check=True)
print("final video done")

# ---------- 5. SRT ----------
def fmt(sec):
    h, rem = divmod(sec, 3600); m, s2 = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s2):02d},{int((s2%1)*1000):03d}"
with open(f"{BASE}/exports/video1.srt", "w") as f:
    for i, (s, st) in enumerate(zip(scenes, starts), 1):
        d = scene_dur(s["id"])
        f.write(f"{i}\n{fmt(st+0.3)} --> {fmt(st+d-0.2)}\n{s['caption']}\n\n")
print("srt done | total:", round(total, 1), "s")
