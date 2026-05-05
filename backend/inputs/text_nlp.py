import numpy as np
import re

try:
    from transformers import pipeline as hf_pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

EMOTION_VA_MAP = {
    "anger":    (-0.70,  0.85),
    "disgust":  (-0.60,  0.40),
    "fear":     (-0.65,  0.80),
    "joy":      ( 0.85,  0.60),
    "neutral":  ( 0.00,  0.00),
    "sadness":  (-0.70, -0.50),
    "surprise": ( 0.10,  0.75),
}

KEYWORD_LEXICON = {
    "anger":   ["angry", "furious", "rage", "mad", "irritated", "hate"],
    "disgust": ["disgusting", "gross", "revolting", "nasty", "repulsed"],
    "fear":    ["scared", "afraid", "terrified", "anxious", "nervous", "worried"],
    "joy":     ["happy", "joyful", "excited", "great", "wonderful", "love", "amazing"],
    "sadness": ["sad", "depressed", "unhappy", "cry", "miserable", "hopeless", "lonely"],
    "surprise":["surprised", "shocked", "unexpected", "wow", "astonished"],
    "neutral": ["okay", "fine", "alright", "normal", "nothing"],
}

class TextEmotionDetector:
    def __init__(self, mock_mode=False, use_transformer=False):
        self.mock_mode = mock_mode
        self.use_transformer = use_transformer and TRANSFORMERS_AVAILABLE
        self._model = None
        if self.use_transformer and not mock_mode:
            self._load_model()

    def _load_model(self):
        try:
            print("[text] Loading emotion model...")
            self._model = hf_pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True, device=-1
            )
            print("[text] Model ready.")
        except Exception as e:
            print(f"[text] Model load failed: {e} — using keywords.")
            self._model = None

    def _keyword_inference(self, text):
        tokens = set(re.findall(r"\b\w+\b", text.lower()))
        scores = {e: sum(1 for kw in kws if kw in tokens)
                  for e, kws in KEYWORD_LEXICON.items()}
        total = sum(scores.values())
        if total == 0:
            return {e: (1.0 if e == "neutral" else 0.0) for e in EMOTION_VA_MAP}
        return {e: scores[e] / total for e in scores}

    def _scores_to_va(self, scores):
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

    def analyze_text(self, text):
        if self.mock_mode:
            return self._mock_result()
        if not text or not text.strip():
            return {"valence": 0.0, "arousal": 0.0,
                    "dominant_emotion": "neutral", "source": "text"}
        if self.use_transformer and self._model:
            results = self._model(text[:512])
            results = results[0] if isinstance(results[0], list) else results
            scores = {r["label"].lower(): r["score"] for r in results}
        else:
            scores = self._keyword_inference(text)
        dominant = max(scores, key=scores.get)
        valence, arousal = self._scores_to_va(scores)
        return {"valence": valence, "arousal": arousal,
                "dominant_emotion": dominant,
                "scores": {k: round(v, 4) for k, v in scores.items()},
                "source": "text"}

    def _mock_result(self):
        import random
        emotion = random.choice(list(EMOTION_VA_MAP.keys()))
        v, a = EMOTION_VA_MAP[emotion]
        return {"valence": round(v, 4), "arousal": round(a, 4),
                "dominant_emotion": emotion, "source": "text"}

if __name__ == "__main__":
    d = TextEmotionDetector(use_transformer=False)
    tests = ["I feel amazing today!", "I am so angry", "feeling sad and lonely"]
    for t in tests:
        print(f"'{t}' → {d.analyze_text(t)}")