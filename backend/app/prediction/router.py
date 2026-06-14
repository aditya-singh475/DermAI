"""Prediction API routes — upload images and get history."""

import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from ..models import PredictionResponse, PredictionHistoryResponse, ErrorResponse
from ..auth.dependencies import get_current_user
from ..storage import resolve_image_path
from .service import (
    predict_image,
    save_prediction,
    build_prediction_response,
    get_prediction_history,
    get_prediction_by_id,
    get_prediction_image_path,
    is_model_loaded,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg"}


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def predict(
    file: UploadFile = File(...),
    user: str = Depends(get_current_user),
):
    """Upload a skin image and get AI classification with health insights."""
    if not is_model_loaded():
        raise HTTPException(status_code=503, detail="ML model is not loaded. Contact administrator.")

    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Allowed: JPG, JPEG, PNG",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    try:
        result = predict_image(contents)
        filename = file.filename or "unknown.jpg"
        prediction_id = save_prediction(user, filename, result, image_bytes=contents)
        response = build_prediction_response(prediction_id, filename, result, has_image=True)

        logger.info(
            f"Prediction: user={user} file={filename} "
            f"class={result['prediction']} conf={result['confidence']:.4f} "
            f"risk={response['risk_level']}"
        )

        return PredictionResponse(**response)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")


@router.get("/history", response_model=PredictionHistoryResponse)
async def history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: str = Depends(get_current_user),
):
    """Get paginated prediction history for the current user."""
    result = get_prediction_history(user, page=page, per_page=per_page)
    return PredictionHistoryResponse(**result)


@router.get("/{prediction_id}")
async def get_prediction(
    prediction_id: int,
    user: str = Depends(get_current_user),
):
    """Get a single prediction with full insights."""
    record = get_prediction_by_id(user, prediction_id)
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return record


@router.get("/{prediction_id}/image")
async def get_prediction_image(
    prediction_id: int,
    user: str = Depends(get_current_user),
):
    """Serve the stored image for a prediction."""
    relative_path = get_prediction_image_path(user, prediction_id)
    if not relative_path:
        raise HTTPException(status_code=404, detail="Image not found")

    full_path = resolve_image_path(relative_path)
    if not full_path:
        raise HTTPException(status_code=404, detail="Image file missing on server")

    media = "image/png" if full_path.suffix == ".png" else "image/jpeg"
    return FileResponse(full_path, media_type=media)
