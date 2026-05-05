import sys
import os
import time
import threading
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))

from inputs.facial import FacialEmotionDetector
from inputs.rppg import RPPGDetector
from inputs.text_nlp import TextEmotionDetector
from inputs.voice import VoiceEmotionDetector
from fusion.fusion_engine import FusionEngine, ModalityReading
from music.therapy_engine import MusicTherapyEngine

app = Flask(__name__)
CORS(app)

MOCK_MODE = os.environ.get("EAMTA_MOCK", "false").lower() == "true"
START_HARDWARE = os.environ.get("EAMTA_START_HARDWARE", "false").lower() == "true"

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    np = None
    CV2_AVAILABLE = False

facial  = FacialEmotionDetector(mock_mode=MOCK_MODE)
rppg    = RPPGDetector(fps=30, mock_mode=MOCK_MODE)
text    = TextEmotionDetector(use_transformer=False)
voice   = VoiceEmotionDetector(mock_mode=MOCK_MODE)
fusion  = FusionEngine(user_id="default", models_dir="models")
therapy = MusicTherapyEngine(output_dir="music_output")

_state = {
    "active": False,
    "user_id": None,
    "start_time": None,
    "latest_fused": None,
    "latest_music": None,
}
_lock = threading.Lock()

def _update_fusion():
    fused = fusion.fuse()
    _state["latest_fused"] = {
        "valence": fused.valence,
        "arousal": fused.arousal,
        "emotion_label": fused.emotion_label,
        "quadrant": fused.quadrant,
        "confidence": fused.confidence,
        "modality_contributions": fused.modality_contributions,
        "weights_used": fused.weights_used,
    }
    if _state["active"]:
        p = therapy.get_current_params(
            fused.valence, fused.arousal, fused.emotion_label)
        _state["latest_music"] = {
            "tempo_bpm": p.tempo_bpm,
            "scale": p.scale,
            "instrument": p.instrument,
            "velocity": p.velocity,
            "phase": p.phase,
            "label": p.label,
            "links": p.links,
        }

def _decode_image(data_url):
    if not data_url or not CV2_AVAILABLE:
        return None
    try:
        _, encoded = data_url.split(",", 1) if "," in data_url else ("", data_url)
        image_bytes = base64.b64decode(encoded)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    except Exception as exc:
        print(f"[facial decode error] {exc}")
        return None

def _hardware_loop():
    if MOCK_MODE:
        while True:
            try:
                result = rppg.process_frame()
                if result.get("bpm"):
                    with _lock:
                        fusion.add_reading(ModalityReading(
                            "rppg", result["valence"],
                            result["arousal"], 0.75))
            except Exception as e:
                print(f"[rppg mock] {e}")
            time.sleep(1)

    if not CV2_AVAILABLE:
        print("[EAMTA] OpenCV not installed; hardware loop disabled.")
        return

    print("[EAMTA] Requesting webcam access...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[EAMTA Error] Could not open webcam. Check camera permissions.")
        return

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
        
        # 1. Process rPPG (Heart Rate) every frame
        try:
            rppg.add_frame(frame)
            if frame_count % 30 == 0:  # Calculate BPM every 1 second
                bpm_result = rppg.compute_and_get_result()
                if bpm_result:
                    with _lock:
                        fusion.add_reading(ModalityReading(
                            "rppg", bpm_result["valence"], bpm_result["arousal"], 0.75))
        except Exception as e:
            print(f"[rppg error] {e}")

        # 2. Process Facial Emotion every ~2 seconds (60 frames)
        if frame_count % 60 == 0:
            try:
                if _state["active"]:
                    face_result = facial.analyze_frame(frame)
                    with _lock:
                        fusion.add_reading(ModalityReading(
                            "facial", face_result["valence"], face_result["arousal"], 0.85))
                        _update_fusion()
            except Exception as e:
                print(f"[facial error] {e}")

        frame_count += 1
        time.sleep(1/30.0)

if START_HARDWARE:
    threading.Thread(target=_hardware_loop, daemon=True).start()

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "mock_mode": MOCK_MODE})

@app.route("/api/analyze/text", methods=["POST"])
def analyze_text():
    data = request.get_json() or {}
    text_input = data.get("text", "").strip()
    if not text_input:
        return jsonify({"error": "No text provided"}), 400
    result = text.analyze_text(text_input)
    with _lock:
        fusion.add_reading(ModalityReading(
            "text", result["valence"], result["arousal"], 1.0))
        _update_fusion()
    return jsonify({
        "text_result": result,
        "fused_state": _state["latest_fused"],
        "music_params": _state["latest_music"],
    })

@app.route("/api/analyze/facial", methods=["POST"])
def analyze_facial():
    data = request.get_json(silent=True) or {}
    frame = _decode_image(data.get("image"))
    result = facial.analyze_frame(frame) if frame is not None else facial.run_once()
    with _lock:
        fusion.add_reading(ModalityReading(
            "facial", result["valence"], result["arousal"], 0.85))
        _update_fusion()
    return jsonify({
        "facial_result": result,
        "fused_state": _state["latest_fused"],
    })

@app.route("/api/analyze/rppg")
def get_rppg():
    return jsonify(rppg.process_frame())

@app.route("/api/session/start", methods=["POST"])
def start_session():
    data = request.get_json() or {}
    user_id = data.get("user_id", "default")
    emotion = data.get("initial_emotion", "neutral")
    with _lock:
        _state["active"] = True
        _state["user_id"] = user_id
        _state["start_time"] = time.time()
        fusion.user_id = user_id
    session = therapy.start_session(user_id, emotion)
    return jsonify({
        "status": "started",
        "user_id": user_id,
        "initial_emotion": emotion,
        "target_emotion": session.target_emotion,
    })

@app.route("/api/session/status")
def session_status():
    with _lock:
        return jsonify({
            "session": {
                "active": _state["active"],
                "user_id": _state["user_id"],
                "elapsed_s": round(time.time() - _state["start_time"], 1)
                             if _state["start_time"] else 0,
            },
            "emotion": _state["latest_fused"],
            "music":   _state["latest_music"],
            "weights": fusion.current_weights(),
        })

@app.route("/api/session/feedback", methods=["POST"])
def session_feedback():
    data = request.get_json() or {}
    rating = int(data.get("rating", 3))
    reward = (rating - 1) / 4.0
    with _lock:
        fusion.apply_session_reward(reward)
        _state["active"] = False
        _state["latest_music"] = None
    return jsonify({
        "status": "feedback_received",
        "reward": reward,
        "updated_weights": fusion.current_weights(),
    })

@app.route("/api/music/params")
def music_params():
    with _lock:
        return jsonify(_state.get("latest_music") or {})

if __name__ == "__main__":
    if not START_HARDWARE:
        threading.Thread(target=_hardware_loop, daemon=True).start()
    print(f"\n[EAMTA] Starting server - mock_mode={MOCK_MODE}")
    print("[EAMTA] Open http://localhost:5001/api/health to verify\n")
    app.run(debug=True, port=5001, threaded=True)
