# Identity Matching

FootballVerse AI supports two identity modes in the V3 backend.

## Current Runtime Behavior

The identity scan endpoint always returns a football DNA profile. It uses:

- personality/playstyle answers,
- deterministic DNA similarity,
- webcam face-detection status,
- optional DeepFace matching metadata.

If the DeepFace index is unavailable, the response is marked:

```json
{
  "scan": {
    "status": "adapter_fallback",
    "matching_method": "personality/DNA similarity fallback",
    "fallback_reason": "Football face embedding index has not been generated yet."
  }
}
```

The UI displays this as an adapter fallback instead of presenting it as a confirmed face match.

## Real DeepFace + Kaggle Path

Dataset:

```text
https://www.kaggle.com/datasets/alessandrasala79/football-players-and-staff-faces-dataset
```

Default dataset path:

```text
datasets/faces
```

Override with:

```bash
export FOOTBALLVERSE_FACE_DATASET_PATH=/absolute/path/to/football-faces
```

Default embedding index path:

```text
datasets/faces/footballverse_face_index.json
```

Override with:

```bash
export FOOTBALLVERSE_FACE_INDEX_PATH=/absolute/path/to/footballverse_face_index.json
```

Index format:

```json
{
  "players": [
    {
      "name": "Lionel Messi",
      "primary_match": "Messi",
      "embedding": [0.01, -0.23, 0.44]
    }
  ]
}
```

Supported `primary_match` values in the current DNA engine:

```text
Messi
Ronaldo
De Bruyne
Neymar
Kante
```

Confidence threshold:

```bash
export FOOTBALLVERSE_FACE_CONFIDENCE_THRESHOLD=0.60
```

When the submitted webcam frame, DeepFace dependency, and index are all available, the backend compares the submitted face embedding against the index using cosine distance. A match is accepted only when:

```text
1 - cosine_distance >= FOOTBALLVERSE_FACE_CONFIDENCE_THRESHOLD
```

If the best candidate is below threshold, the endpoint returns a provisional DNA/personality fallback and includes the best face candidate metadata for debugging.

## Status Endpoint

Use this endpoint to confirm whether the real face path is ready:

```text
GET /api/v3/identity/config
```

It returns dataset path, index path, DeepFace availability, model name, and threshold.
