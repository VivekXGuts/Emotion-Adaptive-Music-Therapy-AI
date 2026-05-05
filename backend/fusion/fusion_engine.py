import numpy as np
import json
import os
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
from datetime import datetime

@dataclass
class ModalityReading:
    source: str
    valence: float
    arousal: float
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class FusedEmotionState:
    valence: float
    arousal: float
    emotion_label: str
    quadrant: str
    modality_contributions: dict
    weights_used: dict
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

def va_to_label(v, a):
    if v >= 0 and a >= 0:
        quadrant = "excited"
        label = "elated" if v > 0.5 and a > 0.5 else "happy" if v > 0.3 else "alert"
    elif v < 0 and a >= 0:
        quadrant = "stressed"
        label = "angry" if a > 0.6 and v < -0.4 else "anxious" if a > 0.4 else "tense"
    elif v < 0 and a < 0:
        quadrant = "sad"
        label = "depressed" if v < -0.5 else "fatigued" if a < -0.5 else "sad"
    else:
        quadrant = "calm"
        label = "content" if v > 0.5 else "relaxed" if v > 0.2 else "neutral"
    return label, quadrant

class UCBWeightAdapter:
    MODALITIES = ["facial", "voice", "text", "rppg"]

    def __init__(self, initial_weights=None):
        self.counts  = {m: 0   for m in self.MODALITIES}
        self.rewards = {m: 0.0 for m in self.MODALITIES}
        self.total_steps = 0
        self._base = initial_weights or {
            "facial": 0.30, "voice": 0.30,
            "text":   0.20, "rppg":  0.20,
        }

    def get_weights(self):
        if self.total_steps < len(self.MODALITIES):
            return dict(self._base)
        ucb = {}
        for m in self.MODALITIES:
            n = self.counts[m]
            if n == 0:
                ucb[m] = float("inf")
            else:
                ucb[m] = self.rewards[m]/n + 0.5*np.sqrt(2*np.log(self.total_steps)/n)
        scores = np.array([min(ucb[m], 10) for m in self.MODALITIES])
        exp_s  = np.exp(scores - scores.max())
        weights = exp_s / exp_s.sum()
        return {m: round(float(w), 4) for m, w in zip(self.MODALITIES, weights)}

    def update(self, dominant, reward):
        if dominant in self.counts:
            self.counts[dominant]  += 1
            self.rewards[dominant] += float(np.clip(reward, 0, 1))
        self.total_steps += 1

    def to_dict(self):
        return {"counts": self.counts, "rewards": self.rewards,
                "total_steps": self.total_steps, "base": self._base}

    @classmethod
    def from_dict(cls, d):
        a = cls(initial_weights=d.get("base"))
        a.counts      = d.get("counts", {m: 0   for m in cls.MODALITIES})
        a.rewards     = d.get("rewards",{m: 0.0 for m in cls.MODALITIES})
        a.total_steps = d.get("total_steps", 0)
        return a

class FusionEngine:
    SMOOTHING_WINDOW = 10

    def __init__(self, user_id="default", models_dir="models"):
        self.user_id    = user_id
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        self.ucb = self._load_ucb()
        self._current_readings: Dict[str, ModalityReading] = {}
        self._va_history: List[Tuple[float, float]] = []
        self._label_history: List[str] = []
        self._current_stable_label: str = "neutral"
        self._session_dominant: Optional[str] = None

    def _profile_path(self):
        return os.path.join(self.models_dir, f"{self.user_id}_ucb.json")

    def _load_ucb(self):
        path = self._profile_path()
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return UCBWeightAdapter.from_dict(json.load(f))
            except:
                pass
        return UCBWeightAdapter()

    def save_profile(self):
        with open(self._profile_path(), "w") as f:
            json.dump(self.ucb.to_dict(), f, indent=2)

    def add_reading(self, reading: ModalityReading):
        self._current_readings[reading.source] = reading

    def clear_readings(self):
        self._current_readings = {}

    def fuse(self) -> FusedEmotionState:
        if not self._current_readings:
            return FusedEmotionState(0.0, 0.0, self._current_stable_label, "calm", {}, {}, 0.0)

        weights = self.ucb.get_weights()
        eff_w, total = {}, 0.0
        for mod, reading in self._current_readings.items():
            w = weights.get(mod, 0.0) * reading.confidence
            eff_w[mod] = w
            total += w
        if total == 0:
            total = 1.0

        rv, ra, contributions = 0.0, 0.0, {}
        for mod, reading in self._current_readings.items():
            w = eff_w.get(mod, 0.0) / total
            rv += w * reading.valence
            ra += w * reading.arousal
            contributions[mod] = round(w, 4)

        if contributions:
            self._session_dominant = max(contributions, key=contributions.get)

        self._va_history.append((rv, ra))
        if len(self._va_history) > self.SMOOTHING_WINDOW:
            self._va_history.pop(0)

        alpha = 0.4
        sv, sa = rv, ra
        for pv, pa in reversed(self._va_history[:-1]):
            sv = alpha * sv + (1 - alpha) * pv
            sa = alpha * sa + (1 - alpha) * pa

        fv = round(float(np.clip(sv, -1, 1)), 4)
        fa = round(float(np.clip(sa, -1, 1)), 4)
        confidence = round(min(1.0, total / sum(weights.values())), 4)
        
        # Stability buffer for labels
        new_label, quadrant = va_to_label(fv, fa)
        self._label_history.append(new_label)
        if len(self._label_history) > 3:
            self._label_history.pop(0)
            
        if len(self._label_history) == 3 and all(l == self._label_history[0] for l in self._label_history):
            self._current_stable_label = self._label_history[0]

        return FusedEmotionState(fv, fa, self._current_stable_label, quadrant,
                                 contributions,
                                 {m: round(w, 4) for m, w in weights.items()},
                                 confidence)

    def apply_session_reward(self, reward):
        if self._session_dominant:
            self.ucb.update(self._session_dominant, reward)
        self.save_profile()

    def current_weights(self):
        return self.ucb.get_weights()

if __name__ == "__main__":
    engine = FusionEngine(user_id="test", models_dir="/tmp/eamta_models")
    engine.add_reading(ModalityReading("facial", -0.4,  0.6, 0.85))
    engine.add_reading(ModalityReading("voice",  -0.3,  0.7, 0.90))
    engine.add_reading(ModalityReading("text",   -0.5,  0.5, 1.00))
    engine.add_reading(ModalityReading("rppg",   -0.2,  0.8, 0.75))
    state = engine.fuse()
    print(f"Emotion : {state.emotion_label}")
    print(f"Valence : {state.valence}  Arousal: {state.arousal}")
    print(f"Weights : {state.weights_used}")