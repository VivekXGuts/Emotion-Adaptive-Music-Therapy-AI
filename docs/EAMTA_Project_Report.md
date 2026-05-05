# Project Report: Emotion-Adaptive Music Therapy AI (EAMTA)

**Subject:** AI Essentials (4th Semester)  
**Student Name:** Arya Ghosh  
**Device:** Mac M4 (Apple Silicon)  
**Date:** April 1, 2026  

---

## 1. Abstract
The **Emotion-Adaptive Music Therapy AI (EAMTA)** is an intelligent, multi-modal system designed to provide personalized music therapy by continuously monitoring a user's emotional state through facial expressions, voice, text, and contactless heart rate detection (rPPG). The system employs a unique **UCB (Upper Confidence Bound) Bandit** reinforcement learning algorithm to fuse these modalities and generates real-time MIDI music based on the **ISO Principle** of clinical music therapy.

## 2. Problem Statement
Most existing music therapy applications rely on static, pre-tagged playlists and single-modality emotion detection (usually just text or labels). These systems fail to:
1. Capture the continuous spectrum of human emotion.
2. Adapt to individual differences in emotional expression.
3. Provide a feedback loop that improves the therapy over time.

## 3. System Architecture & Methodology
EAMTA is built using a **Modular AI Architecture**:

### 3.1 Input Modalities
*   **Facial Module (`facial.py`):** Uses the `FER` library to extract 7 discrete emotions, mapped to a 2D **Valence-Arousal (V-A) Vector**.
*   **rPPG Module (`rppg.py`):** A contactless heart rate detector that analyzes subtle skin color changes in the webcam feed using the **CHROM (Chrominance-based)** algorithm to estimate BPM and stress-induced arousal.
*   **Voice Module (`voice.py`):** Uses `librosa` for acoustic feature extraction (RMS energy, pitch tracking, and tempo) to estimate emotional energy.
*   **Text NLP Module (`text_nlp.py`):** Employs a keyword-based lexicon and a pre-trained **DistilRoBERTa** model to analyze the valence of user input.

### 3.2 The Fusion Engine (Patent-Worthy Core)
Instead of simple voting, EAMTA uses a **Weighted Weighted Ensemble**. The weights for each modality (Facial, Voice, Text, rPPG) are dynamically adjusted using a **Reinforcement Learning (RL)** loop. If a user reports "feeling better" after a session, the system "rewards" the modalities that were most confident during that session, personalizing the detection for the user.

### 3.3 Music Therapy Engine
The system follows the **ISO Principle**:
1.  **Match Phase:** AI generates music that matches the user's current emotional state (e.g., fast tempo, minor key for anxiety).
2.  **Guide Phase:** AI gradually shifts musical parameters (tempo, scale, instrument) toward a "Target" therapeutic state.
3.  **Target Phase:** Music stabilizes at a relaxing, high-valence state (e.g., 60 BPM, Major scale, Flute).

## 4. Implementation Details
*   **Backend:** Python 3.11 (Flask)
*   **Frontend:** React.js (Chart.js for V-A Plot, Lucide-React for UI)
*   **ML Libraries:** Scipy (signal processing), Numpy (vector fusion), Transformers (NLP).
*   **Hardware:** Optimized for **Mac M4** using Python 3.11 universal2 builds.

## 5. Patent Novelty Claims
1.  **Contactless Multi-modal Fusion:** First system to fuse facial/voice with **contactless rPPG** for a continuous emotion vector.
2.  **Adaptive UCB Weighting:** A self-correcting fusion mechanism that learns which sensor is most accurate for a specific user over time.
3.  **Real-time ISO MIDI Generation:** Dynamic parameterization of music therapy principles rather than static file playback.

## 6. Conclusion
EAMTA demonstrates the potential of AI in digital health. By combining cutting-edge computer vision (rPPG) with reinforcement learning, it provides a truly personalized therapeutic experience that evolves with the user.

---
*End of Report*
