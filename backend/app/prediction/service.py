"""ML model inference and prediction history services."""

import json
import logging
import numpy as np
from PIL import Image
from datetime import datetime, timezone
from io import BytesIO

from ..config import get_settings
from ..database import get_db
from ..knowledge.service import get_insights, assess_risk
from ..storage import save_user_image

logger = logging.getLogger(__name__)

# Module-level model cache (loaded once at startup)
_model = None
_inv_map = None


def load_model():
    """Load the TensorFlow model and class mapping. Called once at startup."""
    global _model, _inv_map
    settings = get_settings()

    import os
    if not os.path.exists(settings.MODEL_PATH):
        logger.warning(f"Model file not found: {settings.MODEL_PATH}")
        return False
    if not os.path.exists(settings.CLASS_MAP_PATH):
        logger.warning(f"Class map not found: {settings.CLASS_MAP_PATH}")
        return False

    try:
        from tensorflow.keras.models import load_model as keras_load
        with open(settings.CLASS_MAP_PATH, "r") as f:
            class_indices = json.load(f)
        _inv_map = {int(v): k for k, v in class_indices.items()}
        _model = keras_load(settings.MODEL_PATH, compile=False)
        logger.info(f"Model loaded: {len(_inv_map)} classes — {list(_inv_map.values())}")
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False


def is_model_loaded() -> bool:
    return _model is not None and _inv_map is not None


def get_class_names() -> list[str]:
    if _inv_map is None:
        return []
    return list(_inv_map.values())


def predict_image(image_bytes: bytes) -> dict:
    """Run inference on image bytes. Returns prediction dict."""
    if not is_model_loaded():
        raise RuntimeError("Model not loaded")

    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)

    pred = _model.predict(arr, verbose=0)
    cls_id = int(np.argmax(pred))
    confidence = float(np.max(pred))
    predicted_class = _inv_map.get(cls_id, "unknown")

    # Build per-class probability map
    all_probs = {_inv_map[i]: round(float(pred[0][i]), 6) for i in range(len(pred[0]))}

    return {
        "prediction": predicted_class,
        "confidence": round(confidence, 6),
        "all_probabilities": all_probs,
    }


def save_prediction(
    username: str,
    filename: str,
    result: dict,
    image_bytes: bytes | None = None,
) -> int:
    """Save a prediction to the history table. Returns the prediction ID."""
    image_path = None
    if image_bytes:
        image_path = save_user_image(username, image_bytes, filename)

    risk = assess_risk(result["prediction"], result["confidence"])

    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO predictions
               (username, filename, predicted_class, confidence, all_probabilities,
                image_path, risk_level, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                username,
                filename,
                result["prediction"],
                result["confidence"],
                json.dumps(result["all_probabilities"]),
                image_path,
                risk["level"],
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def build_prediction_response(
    prediction_id: int,
    filename: str,
    result: dict,
    has_image: bool,
) -> dict:
    """Assemble API response with insights."""
    insights = get_insights(
        result["prediction"],
        result["confidence"],
        result["all_probabilities"],
    )
    return {
        "id": prediction_id,
        "file": filename,
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "all_probabilities": result["all_probabilities"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "image_url": f"/api/predictions/{prediction_id}/image" if has_image else None,
        "risk_level": insights["risk"]["level"],
        "insights": insights,
    }


def get_prediction_by_id(username: str, prediction_id: int) -> dict | None:
    """Fetch a single prediction owned by the user."""
    with get_db() as conn:
        row = conn.execute(
            """SELECT id, filename, predicted_class, confidence, all_probabilities,
                      image_path, risk_level, created_at
               FROM predictions
               WHERE id = ? AND username = ?""",
            (prediction_id, username),
        ).fetchone()

    if not row:
        return None

    all_probs = json.loads(row["all_probabilities"]) if row["all_probabilities"] else {}
    insights = get_insights(row["predicted_class"], row["confidence"], all_probs)

    return {
        "id": row["id"],
        "filename": row["filename"],
        "predicted_class": row["predicted_class"],
        "confidence": row["confidence"],
        "all_probabilities": all_probs,
        "created_at": row["created_at"],
        "image_path": row["image_path"],
        "image_url": f"/api/predictions/{row['id']}/image" if row["image_path"] else None,
        "risk_level": row["risk_level"] or insights["risk"]["level"],
        "insights": insights,
    }


def get_prediction_image_path(username: str, prediction_id: int) -> str | None:
    """Return stored image relative path if user owns the prediction."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT image_path FROM predictions WHERE id = ? AND username = ?",
            (prediction_id, username),
        ).fetchone()
    if row and row["image_path"]:
        return row["image_path"]
    return None


def get_prediction_history(username: str, page: int = 1, per_page: int = 20) -> dict:
    """Get paginated prediction history for a user."""
    offset = (page - 1) * per_page

    with get_db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM predictions WHERE username = ?", (username,)
        ).fetchone()[0]

        rows = conn.execute(
            """SELECT id, filename, predicted_class, confidence, created_at,
                      image_path, risk_level
               FROM predictions
               WHERE username = ?
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?""",
            (username, per_page, offset),
        ).fetchall()

    predictions = [
        {
            "id": row["id"],
            "filename": row["filename"],
            "predicted_class": row["predicted_class"],
            "confidence": row["confidence"],
            "created_at": row["created_at"],
            "image_url": f"/api/predictions/{row['id']}/image" if row["image_path"] else None,
            "risk_level": row["risk_level"],
        }
        for row in rows
    ]

    return {
        "predictions": predictions,
        "total": total,
        "page": page,
        "per_page": per_page,
    }
