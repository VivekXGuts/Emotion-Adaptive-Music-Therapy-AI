import numpy as np
import time
import os
from dataclasses import dataclass, field
from typing import Optional, List

try:
    from midiutil import MIDIFile
    MIDIUTIL_AVAILABLE = True
except ImportError:
    MIDIUTIL_AVAILABLE = False

SCALES = {
    "major":            [0, 2, 4, 5, 7, 9, 11],
    "minor":            [0, 2, 3, 5, 7, 8, 10],
    "dorian":           [0, 2, 3, 5, 7, 9, 10],
    "phrygian":         [0, 1, 3, 5, 7, 8, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
}

INSTRUMENTS = {
    "piano": 0, "strings": 48, "flute": 73,
    "guitar": 25, "ambient_pad": 88, "vibraphone": 11,
}

THERAPEUTIC_TARGETS = {
    "angry":    (0.3, -0.3, "calm"),
    "anxious":  (0.4, -0.5, "relaxed"),
    "tense":    (0.3, -0.4, "neutral"),
    "stressed": (0.4, -0.6, "content"),
    "sad":      (0.5,  0.1, "content"),
    "depressed":(0.4,  0.2, "neutral"),
    "fatigued": (0.3,  0.3, "alert"),
    "neutral":  (0.5, -0.3, "relaxed"),
    "happy":    (0.7, -0.2, "content"),
    "elated":   (0.6, -0.3, "content"),
    "alert":    (0.4, -0.2, "relaxed"),
    "content":  (0.6, -0.4, "calm"),
    "relaxed":  (0.6, -0.5, "calm"),
    "calm":     (0.6, -0.6, "calm"),
}

EMOTION_LINKS = {
    "anxious": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DWZqd5JICZI0u", "youtube": "https://www.youtube.com/watch?v=5qap5aO4i9A"},
    "stressed": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DWZqd5JICZI0u", "youtube": "https://www.youtube.com/watch?v=5qap5aO4i9A"},
    "tense": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DWZqd5JICZI0u", "youtube": "https://www.youtube.com/watch?v=5qap5aO4i9A"},
    "angry": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX1s9knjP51Oa", "youtube": "https://www.youtube.com/watch?v=HuFSne7D2u8"},
    "sad": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0", "youtube": "https://www.youtube.com/watch?v=7u8_umT737I"},
    "depressed": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0", "youtube": "https://www.youtube.com/watch?v=7u8_umT737I"},
    "fatigued": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX0b1hHYQtJso", "youtube": "https://www.youtube.com/watch?v=0Asv9e0eP8c"},
    "neutral": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX8Uebhn9wzrS", "youtube": "https://www.youtube.com/watch?v=jfKfPfyJRdk"},
    "alert": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX8Uebhn9wzrS", "youtube": "https://www.youtube.com/watch?v=jfKfPfyJRdk"},
    "happy": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC", "youtube": "https://www.youtube.com/watch?v=ZbZSe6N_BXs"},
    "elated": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC", "youtube": "https://www.youtube.com/watch?v=ZbZSe6N_BXs"},
    "content": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX889U0q85ZsJ", "youtube": "https://www.youtube.com/watch?v=S0Q4gqBUs7c"},
    "relaxed": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX889U0q85ZsJ", "youtube": "https://www.youtube.com/watch?v=S0Q4gqBUs7c"},
    "calm": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX889U0q85ZsJ", "youtube": "https://www.youtube.com/watch?v=S0Q4gqBUs7c"},
}

@dataclass
class MusicParameters:
    tempo_bpm: float
    scale: str
    root_note: int
    instrument: str
    velocity: int
    note_duration: float
    rhythm_complexity: float
    octave_range: int
    phase: str
    label: str = ""
    links: dict = field(default_factory=dict)

@dataclass
class TherapySession:
    user_id: str
    start_time: float = field(default_factory=time.time)
    current_emotion: str = "neutral"
    target_emotion: str = "calm"
    phase: str = "match"
    guide_start_time: Optional[float] = None
    guide_duration_s: float = 120.0

class MusicTherapyEngine:
    def __init__(self, output_dir="music_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._session: Optional[TherapySession] = None

    def va_to_music_params(self, v, a, phase="match", label="neutral"):
        v = float(np.clip(v, -1, 1))
        a = float(np.clip(a, -1, 1))

        tempo = round(45 + (a + 1.0) / 2.0 * 115, 1)
        tempo = float(np.clip(tempo, 45, 160))

        if v >= 0.4:
            scale = "major" if a > -0.3 else "pentatonic_major"
        elif v >= 0.0:
            scale = "dorian"
        elif v >= -0.4:
            scale = "minor"
        else:
            scale = "phrygian" if a > 0.3 else "pentatonic_minor"

        if v >= 0.3 and a >= 0.3:     instrument = "guitar"
        elif v >= 0.3 and a < 0.0:    instrument = "flute"
        elif v < 0.0 and a >= 0.3:    instrument = "strings"
        elif v < 0.0 and a < -0.3:    instrument = "ambient_pad"
        else:                          instrument = "piano"

        velocity = int(np.clip(40 + (a + 1.0) / 2.0 * 60, 20, 110))
        if phase == "guide":    velocity = max(20, int(velocity * 0.85))
        elif phase == "target": velocity = max(20, int(velocity * 0.70))

        note_duration = round(1.0 + (1.0 - (a + 1.0) / 2.0) * 1.5, 2)
        rhythm_complexity = round((a + 1.0) / 2.0 * 0.7, 2)
        octave_range = 1 if a < -0.3 else (2 if a < 0.5 else 3)
        
        emotion_key = label.split('_')[0].lower()
        links = EMOTION_LINKS.get(emotion_key, EMOTION_LINKS["neutral"])

        return MusicParameters(tempo, scale, 60, instrument,
                               velocity, note_duration,
                               rhythm_complexity, octave_range, phase, label, links)

    def interpolate_params(self, start, end, t):
        t = float(np.clip(t, 0, 1))
        ts = t * t * (3 - 2 * t)
        def lerp(a, b): return a + ts * (b - a)

        current_label = start.label if ts < 0.5 else end.label
        emotion_key = current_label.split('_')[0].lower()
        links = EMOTION_LINKS.get(emotion_key, EMOTION_LINKS["neutral"])

        return MusicParameters(
            tempo_bpm=round(lerp(start.tempo_bpm, end.tempo_bpm), 1),
            scale=start.scale if ts < 0.5 else end.scale,
            root_note=start.root_note,
            instrument=start.instrument if ts < 0.5 else end.instrument,
            velocity=int(lerp(start.velocity, end.velocity)),
            note_duration=round(lerp(start.note_duration, end.note_duration), 2),
            rhythm_complexity=round(lerp(start.rhythm_complexity, end.rhythm_complexity), 2),
            octave_range=int(round(lerp(start.octave_range, end.octave_range))),
            phase="guide", label=f"guide_{ts:.2f}",
            links=links
        )

    def start_session(self, user_id, current_emotion, guide_duration_s=120.0):
        target_info = THERAPEUTIC_TARGETS.get(current_emotion, (0.5, -0.4, "relaxed"))
        self._session = TherapySession(
            user_id=user_id, current_emotion=current_emotion,
            target_emotion=target_info[2], guide_duration_s=guide_duration_s
        )
        print(f"[therapy] Session: {current_emotion} → {target_info[2]}")
        return self._session

    def get_current_params(self, v, a, label):
        if self._session is None:
            self.start_session("default", label)
        session = self._session
        now = time.time()

        if session.phase == "match":
            if now - session.start_time > 15.0:
                session.phase = "guide"
                session.guide_start_time = now
            return self.va_to_music_params(v, a, "match", label)

        if session.phase == "guide":
            t = min(1.0, (now - session.guide_start_time) / session.guide_duration_s)
            tv, ta, _ = THERAPEUTIC_TARGETS.get(session.current_emotion, (0.5, -0.4, "relaxed"))
            start_p = self.va_to_music_params(v, a, "match", label)
            end_p   = self.va_to_music_params(tv, ta, "target", session.target_emotion)
            if t >= 1.0:
                session.phase = "target"
            return self.interpolate_params(start_p, end_p, t)

        tv, ta, _ = THERAPEUTIC_TARGETS.get(session.current_emotion, (0.5, -0.4, "relaxed"))
        return self.va_to_music_params(tv, ta, "target", session.target_emotion)

    def generate_midi(self, params, beats=16, filename=None):
        if not MIDIUTIL_AVAILABLE:
            return None
        if filename is None:
            filename = os.path.join(self.output_dir, f"segment_{int(time.time())}.mid")
        scale = SCALES.get(params.scale, SCALES["major"])
        midi = MIDIFile(1)
        midi.addTempo(0, 0, params.tempo_bpm)
        midi.addProgramChange(0, 0, 0, INSTRUMENTS.get(params.instrument, 0))
        beat = 0.0
        np.random.seed(int(params.tempo_bpm))
        probs = np.ones(len(scale))
        probs[0] *= 3.0
        if len(scale) > 4: probs[4] *= 2.0
        probs /= probs.sum()
        for _ in range(beats):
            if np.random.random() < 0.15:
                beat += params.note_duration
                continue
            degree = int(np.random.choice(len(scale), p=probs))
            octave = np.random.randint(0, params.octave_range) * 12
            note = params.root_note + scale[degree] + octave
            midi.addNote(0, 0, int(note), beat, params.note_duration, params.velocity)
            beat += params.note_duration
        with open(filename, "wb") as f:
            midi.writeFile(f)
        return filename

if __name__ == "__main__":
    engine = MusicTherapyEngine(output_dir="/tmp/eamta_music")
    engine.start_session("test", "anxious")
    for v, a, label in [(-0.4, 0.7, "anxious"), (0.0, 0.2, "tense"), (0.5, -0.4, "relaxed")]:
        p = engine.get_current_params(v, a, label)
        print(f"  {label:10s} | {p.phase:6s} | BPM:{p.tempo_bpm:5.1f} | "
              f"Scale:{p.scale:16s} | Inst:{p.instrument}")