# OCR deployment notes

## Windows
- Install Tesseract OCR and set `TESSERACT_CMD` if it is not on PATH.
- Install backend dependencies from `backend/requirements.txt`.
- Default primary engine is PaddleOCR on CPU, with Tesseract fallback.

## Docker/Linux
- Install system libs required by Pillow / Paddle runtime.
- Ensure `tesseract` binary is available if fallback is required.
- Keep `OCR_ENABLE_GPU=false` for CPU images.
- Switch to GPU by providing a GPU-capable Paddle runtime and setting `OCR_ENABLE_GPU=true`.

## Recommended env
- `OCR_PRIMARY_ENGINE=paddle`
- `OCR_FALLBACK_ENGINE=tesseract`
- `OCR_ENABLE_GPU=false`
- `OCR_LANG=ch`
- `OCR_PADDLE_USE_ANGLE_CLS=true`
- `OCR_PADDLE_DET_LIMIT_SIDE_LEN=1920`
- `TESSERACT_LANG=chi_sim+eng`
- `TESSERACT_CONFIG=--oem 1 --psm 4`
