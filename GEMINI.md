# EAMTA (Emotion-Adaptive Music Therapy AI)

## Project Overview
The **Emotion-Adaptive Music Therapy AI (EAMTA)** is an intelligent, multi-modal system designed to provide personalized music therapy. It continuously monitors a user's emotional state through four distinct input modalities:
*   **Facial Expressions:** Analyzed via webcam.
*   **Voice Acoustics:** Extracts features like pitch, tempo, and RMS energy.
*   **Text NLP:** Uses keyword and DistilRoBERTa models to analyze user speech/text input.
*   **Contactless rPPG (Remote Photoplethysmography):** Analyzes subtle skin color changes in the webcam feed to estimate heart rate (BPM) and stress-induced arousal.

The core of EAMTA is its **Fusion Engine**, which employs an **Upper Confidence Bound (UCB) Bandit Reinforcement Learning** algorithm to dynamically adjust the weighting of these four input modalities based on user feedback. The application follows the clinical **ISO Principle** to generate or recommend therapy music by transitioning the user through Match, Guide, and Target phases.

## Architecture
The system employs a decoupled, client-server architecture:
*   **Backend:** A Python 3.11 **Flask** application serving REST APIs. It handles hardware integrations (OpenCV, librosa), heavy ML processing (Transformers), biometric extraction (Scipy for rPPG), and dynamic state fusion.
*   **Frontend:** A modern **React.js** single-page application built with `react-scripts`. It provides a highly interactive dashboard featuring real-time biometric stats (`LiveStats`), a continuous Valence-Arousal emotion plot (`react-chartjs-2`), session control interfaces, and an embedded streaming music player (YouTube/Spotify integrations).

## Building and Running

### Prerequisites
*   Node.js (for the frontend)
*   Python 3.11+ (for the backend)
*   A working webcam and microphone for full multimodal analysis.

### Running the Backend
The backend utilizes a Python virtual environment.
```bash
# From the project root, activate the virtual environment
source venv/bin/activate

# Start the Flask server
python backend/app.py
```
The backend server typically runs on `http://127.0.0.1:5001`.

### Running the Frontend
The frontend uses standard React tooling.
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies (if not already installed)
npm install

# Start the React development server
npm start
```
The frontend dashboard will be available at `http://localhost:3000`.

## Development Conventions
*   **Mock Mode:** The backend supports a `MOCK_MODE` (often controlled via the `EAMTA_MOCK` environment variable). When enabled, hardware loops generate synthetic data, allowing the UI to be developed and tested without requiring a constant active camera or microphone feed.
*   **Component Structure:** Frontend UI components are logically isolated within `frontend/src/components/` (e.g., `SessionControls.jsx`, `MusicDashboard.jsx`, `EmotionChart.jsx`).
*   **State Management:** The frontend polls the backend `/api/session/status` endpoint periodically to maintain synchronization with the AI's internal state and biometric readings.
*   **API Interactions:** All communication between the React frontend and Flask backend goes through RESTful endpoints under the `/api/` prefix defined in `backend/app.py` and referenced via `API_BASE_URL` in the frontend.