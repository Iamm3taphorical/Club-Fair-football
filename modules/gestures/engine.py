from __future__ import annotations


GESTURE_TO_SHOT = {
    "Point Left": "Left Corner",
    "Point Right": "Right Corner",
    "Point Up": "Top Corner",
    "Point Down": "Low Shot",
    "Pinch": "Panenka",
    "Fist": "Power Shot",
}


def map_gesture_to_shot(gesture_name: str) -> str:
    return GESTURE_TO_SHOT.get(gesture_name, "Left Corner")


def supported_gestures() -> list[str]:
    return list(GESTURE_TO_SHOT)


def cv_status() -> dict[str, str]:
    """
    Computer Vision (CV) Integration Status.
    
    CURRENT: Web-based controls via Streamlit UI
    FUTURE: MediaPipe hand gesture recognition for camera-based input
    
    Status (v1.0):
    - Hand gesture recognition: Not yet implemented
    - Recommended next steps: Add MediaPipe integration for production v2.0
    """
    return {
        "Hand Gesture Recognition": "Planned for v2.0 (currently web UI controls)",
        "Webcam Input": "Planned for v2.0",
        "Browser-Based Gameplay": "Active via Streamlit controls (current)",
        "Implementation Note": "See README for upgrade path to gesture-based input",
    }

