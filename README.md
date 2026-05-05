# Emotion-Adaptive Music Therapy AI

React and Flask prototype for emotion-adaptive music therapy sessions.

## Local Development

Start the backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set EAMTA_MOCK=true
python app.py
```

Start the frontend in another terminal:

```bash
cd frontend
npm ci
npm start
```

The frontend uses `http://127.0.0.1:5001/api` by default. For a deployed backend, set `REACT_APP_API_BASE_URL` before building the frontend.

## Vercel

This repository deploys the React frontend to Vercel. The Flask backend uses local camera/audio hardware and should be run locally or hosted separately as an API service.
