import base64
import importlib.util
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List


DATASET_URL = "https://www.kaggle.com/datasets/alessandrasala79/football-players-and-staff-faces-dataset"
KNOWN_MATCH_ALIASES = {
    "lionel messi": "Messi",
    "messi": "Messi",
    "cristiano ronaldo": "Ronaldo",
    "ronaldo": "Ronaldo",
    "kevin de bruyne": "De Bruyne",
    "de bruyne": "De Bruyne",
    "neymar": "Neymar",
    "neymar jr": "Neymar",
    "n'golo kante": "Kante",
    "ngolo kante": "Kante",
    "kante": "Kante",
}


class FaceIdentityMatcher:
    """Optional DeepFace/Kaggle adapter with explicit fallback metadata."""

    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        default_dataset = project_root / "datasets" / "faces"
        self.dataset_path = Path(os.getenv("FOOTBALLVERSE_FACE_DATASET_PATH", str(default_dataset))).expanduser()
        self.index_path = Path(
            os.getenv(
                "FOOTBALLVERSE_FACE_INDEX_PATH",
                str(self.dataset_path / "footballverse_face_index.json"),
            )
        ).expanduser()
        self.model_name = os.getenv("FOOTBALLVERSE_DEEPFACE_MODEL", "Facenet512")
        self.confidence_threshold = float(os.getenv("FOOTBALLVERSE_FACE_CONFIDENCE_THRESHOLD", "0.60"))

    def status(self) -> Dict[str, Any]:
        return {
            "dataset_url": DATASET_URL,
            "dataset_path": str(self.dataset_path),
            "dataset_present": self.dataset_path.exists(),
            "index_path": str(self.index_path),
            "index_present": self.index_path.exists(),
            "embedding_model": self.model_name,
            "deepface_available": importlib.util.find_spec("deepface") is not None,
            "confidence_threshold": self.confidence_threshold,
            "index_format": {
                "players": [
                    {
                        "name": "Lionel Messi",
                        "primary_match": "Messi",
                        "embedding": ["float", "..."],
                    }
                ]
            },
        }

    def match(self, payload: Dict[str, Any], base_profile: Dict[str, Any]) -> Dict[str, Any]:
        status = self.status()
        base_match = base_profile.get("primary_match") or "Messi"
        face_image = payload.get("face_image_base64")
        face_detected = bool(payload.get("face_detected", False))

        fallback = {
            **status,
            "status": "adapter_fallback",
            "face_detected": face_detected,
            "primary_match": base_match,
            "display_name": base_profile.get("name_match") or base_profile.get("display_name") or base_match,
            "confidence_score": base_profile.get("confidence_score", 0),
            "matching_method": "personality/DNA similarity fallback",
            "fallback_reason": self._fallback_reason(status, face_image),
            "identity_basis": "personality signal plus deterministic football DNA similarity",
        }

        if not face_image or not status["deepface_available"] or not status["index_present"]:
            return fallback

        try:
            query_embedding = self._embedding_from_base64(face_image)
            candidates = self._load_index()
            best = self._best_candidate(query_embedding, candidates)
        except Exception as exc:
            return {**fallback, "fallback_reason": f"DeepFace matching failed: {exc}"}

        if not best:
            return {**fallback, "fallback_reason": "Embedding index has no usable players."}

        confidence = max(0.0, min(1.0, 1.0 - best["distance"]))
        primary_match = self._normalize_match(best)
        if confidence < self.confidence_threshold or not primary_match:
            return {
                **fallback,
                "fallback_reason": "Best face match was below the configured confidence threshold.",
                "best_face_candidate": best.get("name"),
                "face_confidence": round(confidence * 100),
            }

        return {
            **status,
            "status": "deepface_confirmed",
            "face_detected": True,
            "primary_match": primary_match,
            "display_name": best.get("name") or primary_match,
            "confidence_score": round(confidence * 100),
            "matching_method": "DeepFace embedding cosine similarity against Kaggle face index",
            "face_confidence": round(confidence * 100),
            "best_face_candidate": best.get("name") or primary_match,
            "identity_basis": "DeepFace face embedding plus personality signal",
        }

    def _fallback_reason(self, status: Dict[str, Any], face_image: str | None) -> str:
        if not face_image:
            return "No face frame was submitted to the backend."
        if not status["deepface_available"]:
            return "DeepFace is not installed in this environment."
        if not status["dataset_present"]:
            return "Kaggle football face dataset path is not present."
        if not status["index_present"]:
            return "Football face embedding index has not been generated yet."
        return "Face adapter fallback is active."

    def _embedding_from_base64(self, image_data: str) -> List[float]:
        from deepface import DeepFace

        encoded = image_data.split(",", 1)[-1]
        image_bytes = base64.b64decode(encoded)
        try:
            import cv2
            import numpy as np
        except Exception as exc:
            raise RuntimeError("cv2 and numpy are required to decode submitted face frames") from exc

        np_image = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
        if frame is None:
            raise RuntimeError("Submitted face frame could not be decoded")

        representations = DeepFace.represent(
            img_path=frame,
            model_name=self.model_name,
            enforce_detection=False,
        )
        if not representations:
            raise RuntimeError("DeepFace did not return an embedding")
        embedding = representations[0].get("embedding")
        if not isinstance(embedding, list):
            raise RuntimeError("DeepFace embedding format was not recognized")
        return [float(value) for value in embedding]

    def _load_index(self) -> List[Dict[str, Any]]:
        with self.index_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        candidates = data.get("players", data if isinstance(data, list) else [])
        if not isinstance(candidates, list):
            return []
        return [candidate for candidate in candidates if isinstance(candidate, dict)]

    def _best_candidate(self, query_embedding: List[float], candidates: Iterable[Dict[str, Any]]) -> Dict[str, Any] | None:
        best: Dict[str, Any] | None = None
        for candidate in candidates:
            embedding = candidate.get("embedding")
            if not isinstance(embedding, list):
                continue
            distance = self._cosine_distance(query_embedding, [float(value) for value in embedding])
            if best is None or distance < best["distance"]:
                best = {**candidate, "distance": distance}
        return best

    def _normalize_match(self, candidate: Dict[str, Any]) -> str | None:
        explicit = candidate.get("primary_match")
        if explicit in {"Messi", "Ronaldo", "De Bruyne", "Neymar", "Kante"}:
            return explicit
        name = str(candidate.get("name") or candidate.get("label") or "").strip().lower()
        return KNOWN_MATCH_ALIASES.get(name)

    def _cosine_distance(self, left: List[float], right: List[float]) -> float:
        if len(left) != len(right) or not left:
            raise RuntimeError("Embedding dimensions do not match")
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if not left_norm or not right_norm:
            return 1.0
        return 1.0 - (dot / (left_norm * right_norm))
