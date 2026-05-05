import numpy as np
from typing import Optional

try:
    from fer import FER
    FER_AVAILABLE = True
except ImportError:
    FER_AVAILABLE = False

EMOTION_VA_MAP = {
    "angry":     (-0.70,  0.85),
    "disgust":   (-0.60,  0.40),
    "fear":      (-0.65,  0.80),
    "happy":     ( 0.85,  0.60),
    "sad":       (-0.70, -0.50),
    "surprise":  ( 0.10,  0.75),
    "neutral":   ( 0.00,  0.00),
}

class FacialEmotionDetector:
    def __init__(self, mock_mode=False):
        self.mock_mode = mock_mode or not FER_AVAILABLE
        if not self.mock_mode:
            self.detector = FER(mtcnn=False)

    def analyze_frame(self, frame):
        if self.mock_mode:
            return self._mock_result()
        try:
            result = self.detector.detect_emotions(frame)
            if not result:
                return self._neutral()
            emotions = result[0]["emotions"]
            valence, arousal = self._compute_va(emotions)
            dominant = max(emotions, key=emotions.get)
            return {"valence": valence, "arousal": arousal,
                    "dominant_emotion": dominant, "source": "facial"}
        except Exception:
            return self._neutral()

    def _compute_va(self, scores):
        v, a, total = 0.0, 0.0, 0.0
        for emotion, score in scores.items():
            if emotion in EMOTION_VA_MAP:
                ev, ea = EMOTION_VA_MAP[emotion]
                v += score * ev
                a += score * ea
                total += score
        if total > 0:
            v /= total
            a /= total
        return round(float(v), 4), round(float(a), 4)

    def _neutral(self):
        return {"valence": 0.0, "arousal": 0.0,
                "dominant_emotion": "neutral", "source": "facial"}

    def _mock_result(self):
        import random
        emotion = random.choice(list(EMOTION_VA_MAP.keys()))
        v, a = EMOTION_VA_MAP[emotion]
        return {"valence": round(v + random.gauss(0, 0.05), 4),
                "arousal": round(a + random.gauss(0, 0.05), 4),
                "dominant_emotion": emotion, "source": "facial"}

    def run_once(self):
        return self._mock_result() if self.mock_mode else self._neutral()

if __name__ == "__main__":
    d = FacialEmotionDetector(mock_mode=True)
    print(d.run_once())