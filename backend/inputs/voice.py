import numpy as np
from typing import Optional
import time

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

EMOTION_VA_MAP = {
    "angry":    (-0.70,  0.85),
    "calm":     ( 0.50, -0.60),
    "fearful":  (-0.65,  0.80),
    "happy":    ( 0.85,  0.60),
    "neutral":  ( 0.00,  0.00),
    "sad":      (-0.70, -0.50),
    "surprised":( 0.10,  0.75),
}

class VoiceEmotionDetector:
    def __init__(self, mock_mode=False):
        self.mock_mode = mock_mode or not LIBROSA_AVAILABLE
        # Smoothing state to prevent "cracking" or jittery readings
        self.last_valence = 0.0
        self.last_arousal = 0.0
        self.alpha = 0.3  # Smoothing factor (0.3 = 30% new, 70% old)

    def analyze_audio(self, audio=None):
        if self.mock_mode:
            res = self._mock_result()
            return self._apply_smoothing(res)
            
        try:
            import sounddevice as sd
            SAMPLE_RATE = 16000
            if audio is None:
                # Reduced recording time to 2s for more frequent, smoother updates
                duration = 2.0 
                audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                               channels=1, dtype="float32")
                sd.wait()
                audio = audio.flatten()
            
            res = self._acoustic_to_result(audio, SAMPLE_RATE)
            return self._apply_smoothing(res)
        except Exception as e:
            print(f"[voice] Error: {e}")
            return self._apply_smoothing(self._mock_result())

    def _apply_smoothing(self, result):
        """Smoothes the V-A readings to prevent sudden jumps (cracking)."""
        v = result["valence"]
        a = result["arousal"]
        
        # Exponential moving average
        smoothed_v = (self.alpha * v) + (1.0 - self.alpha) * self.last_valence
        smoothed_a = (self.alpha * a) + (1.0 - self.alpha) * self.last_arousal
        
        self.last_valence = smoothed_v
        self.last_arousal = smoothed_a
        
        return {
            "valence": round(float(smoothed_v), 4),
            "arousal": round(float(smoothed_a), 4),
            "source": "voice"
        }

    def _acoustic_to_result(self, audio, sr):
        if len(audio) == 0:
            return {"valence": 0.0, "arousal": 0.0, "source": "voice"}
            
        energy = float(librosa.feature.rms(y=audio).mean())
        pitches, mags = librosa.piptrack(y=audio, sr=sr)
        pitch_vals = pitches[mags > mags.mean()]
        pitch_vals = pitch_vals[pitch_vals > 0]
        pitch_mean = float(pitch_vals.mean()) if len(pitch_vals) > 0 else 0.0
        
        # Handle beat tracking more robustly
        try:
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            tempo = float(tempo) if np.isscalar(tempo) else float(tempo[0])
        except:
            tempo = 120.0

        # Refined acoustic mapping for smoother response
        arousal = float(np.tanh(energy / 0.05) * 0.5 +
                        np.tanh((pitch_mean - 150) / 100) * 0.3 +
                        np.tanh((tempo - 120) / 80) * 0.2)
        
        # Valence is harder from acoustics; using pitch stability proxy
        valence = float(np.tanh((pitch_mean - 120) / 100) * 0.4) 
        
        return {
            "valence": round(float(np.clip(valence, -1, 1)), 4),
            "arousal": round(float(np.clip(arousal, -1, 1)), 4),
            "source": "voice"
        }

    def _mock_result(self):
        import random
        # Pick a base emotion
        v, a = random.choice(list(EMOTION_VA_MAP.values()))
        # Add very small noise for "live" feel without cracking
        noise = lambda: random.gauss(0, 0.02)
        return {
            "valence": round(float(np.clip(v + noise(), -1, 1)), 4),
            "arousal": round(float(np.clip(a + noise(), -1, 1)), 4),
            "source": "voice"
        }

    def run_once(self):
        return self.analyze_audio()

if __name__ == "__main__":
    d = VoiceEmotionDetector(mock_mode=True)
    for i in range(5):
        print(d.run_once())
        time.sleep(0.5)
