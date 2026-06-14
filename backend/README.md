Quick start for backend (FastAPI)

1. Create a Python environment and install dependencies:

   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r backend\requirements.txt

2. Ensure model files exist at: model\models\skin_model.h5 and class_indices.json

3. Run the server:

   uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

4. Use the static frontend at http://localhost:8000/ or use /docs for API docs.

Notes:
- Update SECRET_KEY in backend/auth.py before deploying.
- Creating a user: POST /register?username=demo&password=pass
- Get token via /token (OAuth2 password grant) and use it in Authorization: Bearer <token>
