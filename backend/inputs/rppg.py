import numpy as np
from collections import deque
from typing import Optional

try:
    from scipy.signal import butter, filtfilt
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

FPS_DEFAULT = 30
WINDOW_SECONDS = 10
BPM_MIN = 42
BPM_MAX = 180
RESTING_BPM = 70

class RPPGDetector:
    def __init__(self, fps=FPS_DEFAULT, mock_mode=False):
        self.fps = fps
        self.mock_mode = mock_mode
        self.window_size = fps * WINDOW_SECONDS
        self.rgb_buffer = deque(maxlen=self.window_size)

    def _chrom_algorithm(self, rgb):
        rgb_norm = rgb / (rgb.mean(axis=0) + 1e-6)
        Xs = 3 * rgb_norm[:, 0] - 2 * rgb_norm[:, 1]
        Ys = 1.5 * rgb_norm[:, 0] + rgb_norm[:, 1] - 1.5 * rgb_norm[:, 2]
        alpha = Xs.std() / (Ys.std() + 1e-6)
        return Xs - alpha * Ys

    def _bandpass(self, signal):
        if not SCIPY_AVAILABLE:
            return signal - np.mean(signal)
        nyq = self.fps / 2.0
        low = max(0.01, (BPM_MIN / 60.0) / nyq)
        high = min(0.99, (BPM_MAX / 60.0) / nyq)
        b, a = butter(3, [low, high], btype='band')
        return filtfilt(b, a, signal)

    def _fft_bpm(self, signal):
        freqs = np.fft.rfftfreq(len(signal), d=1.0 / self.fps)
        mags = np.abs(np.fft.rfft(signal * np.hanning(len(signal))))
        mask = (freqs >= BPM_MIN / 60.0) & (freqs <= BPM_MAX / 60.0)
        if not mask.any():
            return RESTING_BPM
        return float(freqs[mask][np.argmax(mags[mask])]) * 60.0

    def compute_bpm(self):
        if len(self.rgb_buffer) < self.window_size // 2:
            return None
        rgb = np.array(list(self.rgb_buffer), dtype=np.float64)
        return round(self._fft_bpm(self._bandpass(self._chrom_algorithm(rgb))), 1)

    def bpm_to_stress(self, bpm):
        delta = (bpm - RESTING_BPM) / 40.0
        arousal = float(np.tanh(delta))
        valence = float(np.tanh(-delta * 0.5))
        if bpm < 65:     label = "very_calm"
        elif bpm < 80:   label = "calm"
        elif bpm < 95:   label = "neutral"
        elif bpm < 110:  label = "elevated"
        else:            label = "stressed"
        return {"bpm": round(bpm, 1), "stress_label": label,
                "arousal": round(arousal, 4), "valence": round(valence, 4),
                "source": "rppg"}

    def add_frame(self, frame):
        # Crop to center forehead region roughly
        h, w = frame.shape[:2]
        crop = frame[int(h*0.2):int(h*0.4), int(w*0.4):int(w*0.6)]
        # Extract mean RGB values
        rgb_mean = crop.mean(axis=(0, 1))
        self.rgb_buffer.append(rgb_mean)

    def compute_and_get_result(self):
        bpm = self.compute_bpm()
        if bpm:
            return self.bpm_to_stress(bpm)
        return None

    def process_frame(self):
        # Kept for backward compatibility with mock mode
        return self._mock_result()

    def _mock_result(self):
        import random
        bpm = max(BPM_MIN, min(BPM_MAX, random.gauss(75, 15)))
        return self.bpm_to_stress(bpm)

if __name__ == "__main__":
    d = RPPGDetector(mock_mode=True)
    for i in range(3):
        print(d.process_frame())
