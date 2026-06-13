"""
Gesture Recognition Engine — MediaPipe Tasks API (v0.10+)
Uses the new `mediapipe.tasks` interface instead of the deprecated `mp.solutions`.
"""
import math
import os
import itertools
from collections import deque, Counter
from types import SimpleNamespace
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
    try:
        import tensorflow as tf
    except ImportError:
        tf = None
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
PH_MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "point_history_classifier", "point_history_classifier.tflite")
KP_MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "keypoint_classifier", "keypoint_classifier.tflite")
KP_LABELS_PATH = os.path.join(os.path.dirname(__file__), "model", "keypoint_classifier", "keypoint_classifier_label.csv")

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
        
        # Load keypoint classifier (kinivi trained model)
        self.kp_interpreter = None
        self.kp_labels: list = []
        if _CV_AVAILABLE:
            try:
                self.kp_interpreter = tf.lite.Interpreter(model_path=KP_MODEL_PATH, num_threads=1)
                self.kp_interpreter.allocate_tensors()
                self.kp_input_details = self.kp_interpreter.get_input_details()
                self.kp_output_details = self.kp_interpreter.get_output_details()
                import csv
                with open(KP_LABELS_PATH, encoding='utf-8-sig') as f:
                    self.kp_labels = [row[0] for row in csv.reader(f) if row]
                print(f"[cv_engine] Keypoint classifier loaded. Labels: {self.kp_labels}")
            except Exception as exc:
                print(f"[cv_engine] Keypoint classifier failed to load: {exc}")
                self.kp_interpreter = None
        
        if _CV_AVAILABLE:
            try:
                self.ph_interpreter = tf.lite.Interpreter(model_path=PH_MODEL_PATH, num_threads=1)
                self.ph_interpreter.allocate_tensors()
                self.ph_input_details = self.ph_interpreter.get_input_details()
                self.ph_output_details = self.ph_interpreter.get_output_details()
            except Exception:
                self.ph_interpreter = None
        else:
            self.ph_interpreter = None

        self.point_history = deque(maxlen=16)
        self.finger_gesture_history = deque(maxlen=16)

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
        pointer: Optional[dict] = None
        debug: Optional[dict] = None

        if result.hand_landmarks:
            raw_lm = result.hand_landmarks[0]
            # The browser displays the front camera mirrored. Convert raw
            # MediaPipe landmarks into display-space once, then use that same
            # coordinate system for pointer tracking and gesture direction.
            lm = [SimpleNamespace(x=1.0 - point.x, y=point.y, z=getattr(point, "z", 0.0)) for point in raw_lm]
            gesture, confidence = self._classify(lm, img_bgr)
            curve = self._calc_curve(lm)
            pointer = {"x": lm[8].x, "y": lm[8].y}
            
            # Point history tracking
            self.point_history.append([lm[8].x, lm[8].y])
            
            # Point history classification
            finger_gesture_id = 0
            if len(self.point_history) == 16 and getattr(self, 'ph_interpreter', None) is not None:
                pre_processed_history = self._pre_process_point_history(self.point_history)
                input_tensor_index = self.ph_input_details[0]['index']
                self.ph_interpreter.set_tensor(input_tensor_index, np.array([pre_processed_history], dtype=np.float32))
                self.ph_interpreter.invoke()
                output_tensor_index = self.ph_output_details[0]['index']
                ph_result = self.ph_interpreter.get_tensor(output_tensor_index)
                finger_gesture_id = np.argmax(np.squeeze(ph_result))
                if np.squeeze(ph_result)[finger_gesture_id] < 0.5:
                    finger_gesture_id = 0

            self.finger_gesture_history.append(finger_gesture_id)
            most_common_fg_id = Counter(self.finger_gesture_history).most_common()
            # Only override with Flick when:
            # 1) The most common dynamic gesture is 'Move' (class 3)
            # 2) It has a strong majority (>=10 of 16 frames)
            # 3) The static gesture is not already a strong directional point
            strong_static = gesture in ("Point Left", "Point Right", "Point Up", "Point Down", "Fist", "Pinch")
            if (most_common_fg_id
                and most_common_fg_id[0][0] == 3
                and most_common_fg_id[0][1] >= 10
                and not strong_static):
                gesture = "Flick"
                confidence = 0.90
                # Clear history after emitting so it doesn't stick
                self.finger_gesture_history.clear()
            
            debug = {
                "landmarks": [
                    {"x": point.x, "y": point.y, "z": getattr(point, "z", 0.0)}
                    for point in lm
                ],
                "raw_landmarks": [
                    {"x": point.x, "y": point.y, "z": getattr(point, "z", 0.0)}
                    for point in raw_lm
                ],
                "gesture": gesture,
                "confidence": confidence,
                "palm_scale": self._dist(lm[0], lm[9]),
            }
        else:
            self.point_history.append([0.0, 0.0])

        # Temporal smoothing buffer
        self.gesture_buffer.append(gesture)
        if len(self.gesture_buffer) > self.buffer_size:
            self.gesture_buffer.pop(0)
        smoothed = self._smooth()

        # Power meter (fist hold)
        if smoothed == "Fist":
            self.fist_frames += 1
            power = min(1.0, self.fist_frames / 30.0)
            self.last_gesture = "Charging"
            return {"gesture": "Charging", "confidence": confidence, "power": power, "curve": curve, "pointer": pointer, "debug": debug}
        else:
            if self.last_gesture in ("Fist", "Charging") and self.fist_frames > 0:
                final_power = min(1.0, self.fist_frames / 30.0)
                self.fist_frames = 0
                self.cooldown_frames = 5
                self.last_gesture = "Fist Released"
                return {"gesture": "Fist Released", "confidence": 1.0, "power": final_power, "curve": curve, "pointer": pointer, "debug": debug}
            self.fist_frames = 0

        # Cooldown gate
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
            return {"gesture": None, "status": "cooldown", "pointer": pointer, "debug": debug}

        if smoothed and smoothed != self.last_gesture and confidence >= 0.6:
            self.last_gesture = smoothed
            self.cooldown_frames = 5
            return {"gesture": smoothed, "confidence": confidence, "power": 0.5, "curve": curve, "pointer": pointer, "debug": debug}

        self.last_gesture = smoothed
        return {"gesture": None, "pointer": pointer, "debug": debug}

    # ─── Internal helpers ─────────────────────────────────────────────────────

    def _pre_process_point_history(self, point_history):
        temp_point_history = list(point_history)
        base_x, base_y = 0.0, 0.0
        for index, point in enumerate(temp_point_history):
            if index == 0:
                base_x, base_y = point[0], point[1]
            temp_point_history[index] = [point[0] - base_x, point[1] - base_y]
        return list(itertools.chain.from_iterable(temp_point_history))

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
        return angle > 130 and length > palm_scale * 0.45

    def _finger_curled(self, lm: list, tip: int, pip: int, mcp: int, palm_scale: float) -> bool:
        # A closed fist can put tips near the MCP, lower than the PIP joint, or
        # tucked toward the wrist depending on camera angle. Use all three cues.
        tip_to_mcp = self._dist(lm[tip], lm[mcp])
        tip_to_wrist = self._dist(lm[tip], lm[0])
        return (
            tip_to_mcp < palm_scale * 0.92
            or lm[tip].y > lm[pip].y - 0.015
            or tip_to_wrist < palm_scale * 1.05
        )

    def _classify(self, lm: list, img_bgr=None):
        """Classify gesture using the trained kinivi keypoint model, falling
        back to geometric heuristics if the model isn't loaded."""
        palm_scale = max(0.01, self._dist(lm[0], lm[9]))

        # ── Try trained model first ──────────────────────────────────────
        if self.kp_interpreter is not None and img_bgr is not None:
            try:
                h, w = img_bgr.shape[:2]
                # Build pixel landmark list (same as kinivi calc_landmark_list)
                landmark_list = []
                for point in lm:
                    lx = min(int(point.x * w), w - 1)
                    ly = min(int(point.y * h), h - 1)
                    landmark_list.append([lx, ly])

                # Preprocess (kinivi pre_process_landmark)
                processed = self._pre_process_landmark(landmark_list)

                # Run inference
                idx = self.kp_input_details[0]['index']
                self.kp_interpreter.set_tensor(idx, np.array([processed], dtype=np.float32))
                self.kp_interpreter.invoke()
                out_idx = self.kp_output_details[0]['index']
                kp_result = self.kp_interpreter.get_tensor(out_idx)
                scores = np.squeeze(kp_result)
                class_id = int(np.argmax(scores))
                class_conf = float(scores[class_id])

                if class_conf > 0.5 and class_id < len(self.kp_labels):
                    label = self.kp_labels[class_id]  # Open, Close, Pointer, OK

                    if label == "Close":
                        return "Fist", class_conf
                    elif label == "OK":
                        # OK gesture — not used in game
                        return None, 0.0
                    elif label == "Pointer":
                        # Use the index finger direction to determine which way
                        dx = lm[8].x - lm[5].x
                        dy = lm[8].y - lm[5].y
                        if abs(dx) >= abs(dy):
                            return ("Point Right", class_conf) if dx > 0 else ("Point Left", class_conf)
                        return ("Point Down", class_conf) if dy > 0 else ("Point Up", class_conf)
                    elif label == "Open":
                        # Open palm — no shot gesture
                        return None, 0.0
            except Exception:
                pass  # Fall through to heuristic

        # ── Heuristic fallback ───────────────────────────────────────────
        # Finger tip / pip / mcp indices
        # Index=8/6/5, Middle=12/10/9, Ring=16/14/13, Pinky=20/18/17, Thumb tip=4
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        mcps = [5,  9, 13, 17]

        extended = [self._finger_extended(lm, tips[i], pips[i], mcps[i], palm_scale) for i in range(4)]
        curled = [self._finger_curled(lm, tips[i], pips[i], mcps[i], palm_scale) for i in range(4)]

        only_index = extended[0] and not any(extended[1:])

        thumb_to_index = self._dist(lm[4], lm[5])
        thumb_to_wrist = self._dist(lm[4], lm[0])
        thumb_curled = thumb_to_index < palm_scale * 1.18 or thumb_to_wrist < palm_scale * 1.2
        all_closed = sum(curled) >= 3 and not any(extended) and thumb_curled

        if all_closed:
            return "Fist", 0.80

        if only_index:
            dx = lm[8].x - lm[5].x
            dy = lm[8].y - lm[5].y
            if abs(dx) >= abs(dy):
                return ("Point Right", 0.76) if dx > 0 else ("Point Left", 0.76)
            return ("Point Down", 0.76) if dy > 0 else ("Point Up", 0.78)

        return None, 0.0

    @staticmethod
    def _pre_process_landmark(landmark_list: list) -> list:
        """Kinivi preprocessing: relative coords from wrist, flatten, normalize."""
        import copy
        temp = copy.deepcopy(landmark_list)
        base_x, base_y = 0, 0
        for i, point in enumerate(temp):
            if i == 0:
                base_x, base_y = point[0], point[1]
            temp[i][0] = temp[i][0] - base_x
            temp[i][1] = temp[i][1] - base_y
        flat = list(itertools.chain.from_iterable(temp))
        max_val = max(list(map(abs, flat)))
        if max_val == 0:
            return flat
        return [v / max_val for v in flat]
