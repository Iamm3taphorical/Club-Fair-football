"""
Gesture Recognition Engine — MediaPipe Tasks API (v0.10+)
Uses the new `mediapipe.tasks` interface instead of the deprecated `mp.solutions`.
"""
import math
import os
from typing import Optional

_CV_DISABLED = os.getenv("FOOTBALLVERSE_DISABLE_CV", "").lower() in {"1", "true", "yes"}
_CV_IMPORT_ERROR = ""

try:
    if _CV_DISABLED:
        raise RuntimeError("FOOTBALLVERSE_DISABLE_CV is enabled")
    import cv2
    import numpy as np
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
    _CV_AVAILABLE = True
except Exception as exc:  # Optional integration for laptops without CV deps.
    cv2 = None
    np = None
    mp = None
    mp_python = None
    mp_vision = None
    _CV_AVAILABLE = False
    _CV_IMPORT_ERROR = str(exc)

# ─── Download the hand landmark model if not present ─────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")

def _ensure_model():
    if not _CV_AVAILABLE:
        return
    if not os.path.exists(MODEL_PATH):
        import urllib.request
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        print(f"[cv_engine] Downloading hand landmarker model to {MODEL_PATH} …")
        urllib.request.urlretrieve(url, MODEL_PATH)
        print("[cv_engine] Model downloaded.")

_ensure_model()

# ─── Build the detector ───────────────────────────────────────────────────────
if _CV_AVAILABLE:
    try:
        _base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
        _hand_options = mp_vision.HandLandmarkerOptions(
            base_options=_base_options,
            num_hands=1,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        _detector = mp_vision.HandLandmarker.create_from_options(_hand_options)
        NormalizedLandmark = mp.tasks.components.containers.NormalizedLandmark
    except Exception as exc:
        _detector = None
        NormalizedLandmark = object
        _CV_AVAILABLE = False
        _CV_IMPORT_ERROR = str(exc)
else:
    _detector = None
    NormalizedLandmark = object


def cv_runtime_status() -> dict:
    if _CV_DISABLED:
        return {
            "available": False,
            "status": "cv_disabled",
            "detail": "Gesture recognition is disabled by FOOTBALLVERSE_DISABLE_CV.",
        }
    if not _CV_AVAILABLE or _detector is None:
        return {
            "available": False,
            "status": "cv_unavailable",
            "detail": f"Gesture recognition needs numpy, opencv-python, and mediapipe. {_CV_IMPORT_ERROR}".strip(),
        }
    return {
        "available": True,
        "status": "ready",
        "detail": "Gesture recognition ready.",
    }


class GestureRecognizer:
    def __init__(self):
        self.last_gesture: Optional[str] = None
        self.cooldown_frames: int = 0
        self.fist_frames: int = 0
        self.gesture_buffer: list = []
        self.buffer_size: int = 3

    # ─── Public API ──────────────────────────────────────────────────────────

    def status(self) -> dict:
        return cv_runtime_status()

    def process_frame(self, frame_bytes: bytes) -> dict:
        if not _CV_AVAILABLE or _detector is None:
            status = self.status()
            return {
                "gesture": None,
                "status": status["status"],
                "detail": status["detail"],
            }

        np_arr = np.frombuffer(frame_bytes, np.uint8)
        img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return {"error": "Invalid frame data"}

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        result = _detector.detect(mp_image)

        gesture: Optional[str] = None
        confidence: float = 0.0
        curve: float = 0.0

        if result.hand_landmarks:
            lm = result.hand_landmarks[0]          # first hand
            gesture, confidence = self._classify(lm)
            curve = self._calc_curve(lm)

        # Temporal smoothing buffer
        self.gesture_buffer.append(gesture)
        if len(self.gesture_buffer) > self.buffer_size:
            self.gesture_buffer.pop(0)
        smoothed = self._smooth()

        # Power meter (fist hold)
        if smoothed == "Fist":
            self.fist_frames += 1
            power = min(1.0, self.fist_frames / 30.0)
            return {"gesture": "Charging", "confidence": confidence, "power": power, "curve": curve}
        else:
            if self.last_gesture == "Fist" and self.fist_frames > 0:
                final_power = min(1.0, self.fist_frames / 30.0)
                self.fist_frames = 0
                self.cooldown_frames = 15
                self.last_gesture = "Power Shot"
                return {"gesture": "Power Shot", "confidence": 1.0, "power": final_power, "curve": curve}
            self.fist_frames = 0

        # Cooldown gate
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
            return {"gesture": None, "status": "cooldown"}

        if smoothed and smoothed != self.last_gesture and confidence >= 0.6:
            self.last_gesture = smoothed
            self.cooldown_frames = 15
            return {"gesture": smoothed, "confidence": confidence, "power": 0.5, "curve": curve}

        self.last_gesture = smoothed
        return {"gesture": None}

    # ─── Internal helpers ─────────────────────────────────────────────────────

    def _smooth(self) -> Optional[str]:
        valid = [g for g in self.gesture_buffer if g]
        if not valid:
            return None
        return max(set(valid), key=valid.count)

    def _calc_curve(self, lm: list) -> float:
        wrist = lm[0]
        mid_mcp = lm[9]
        dx = mid_mcp.x - wrist.x
        dy = mid_mcp.y - wrist.y
        angle = math.degrees(math.atan2(dy, dx)) + 90
        return max(-1.0, min(1.0, angle / 45.0))

    @staticmethod
    def _dist(a, b) -> float:
        return math.hypot(a.x - b.x, a.y - b.y)

    @staticmethod
    def _joint_angle(a, b, c) -> float:
        bax = a.x - b.x
        bay = a.y - b.y
        bcx = c.x - b.x
        bcy = c.y - b.y
        denominator = math.hypot(bax, bay) * math.hypot(bcx, bcy)
        if denominator == 0:
            return 0.0
        cosine = max(-1.0, min(1.0, (bax * bcx + bay * bcy) / denominator))
        return math.degrees(math.acos(cosine))

    def _finger_extended(self, lm: list, tip: int, pip: int, mcp: int, palm_scale: float) -> bool:
        angle = self._joint_angle(lm[tip], lm[pip], lm[mcp])
        length = self._dist(lm[tip], lm[mcp])
        return angle > 145 and length > palm_scale * 0.55

    def _classify(self, lm: list):
        # Finger tip / pip / mcp indices
        # Index=8/6/5, Middle=12/10/9, Ring=16/14/13, Pinky=20/18/17, Thumb tip=4
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        mcps = [5,  9, 13, 17]
        palm_scale = max(0.01, self._dist(lm[0], lm[9]))

        # Pinch — thumb tip close to index tip. Check this before pointing so a
        # clean pinch is not swallowed by an extended index finger.
        pinch_dist = self._dist(lm[4], lm[8])
        pinch_threshold = max(0.045, min(0.085, palm_scale * 0.55))
        if pinch_dist < pinch_threshold:
            return "Pinch", 0.92

        extended = [self._finger_extended(lm, tips[i], pips[i], mcps[i], palm_scale) for i in range(4)]
        only_index = extended[0] and not any(extended[1:])
        all_closed = not any(extended)

        # Fist
        if all_closed:
            return "Fist", 0.90

        if only_index:
            dx = lm[8].x - lm[5].x
            dy = lm[8].y - lm[5].y
            if abs(dx) >= abs(dy):
                return ("Point Right", 0.86) if dx > 0 else ("Point Left", 0.86)
            return ("Point Down", 0.86) if dy > 0 else ("Point Up", 0.88)

        return None, 0.0
