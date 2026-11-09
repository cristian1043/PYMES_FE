import os
from dotenv import load_dotenv

load_dotenv()

is_prod = (
    os.getenv("FLASK_ENV", "").lower() == "production"
    or os.getenv("APP_ENV", "").lower() == "production"
)
secret_key = os.getenv("SECRET_KEY")
if is_prod and (not secret_key or secret_key == "frontend-secret"):
    raise RuntimeError("SECRET_KEY segura es obligatoria en producción para PYMES_FE.")


class Config:
    SECRET_KEY = secret_key or "frontend-secret-dev-key-2026"
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000/api")
    PORTAL_CLIENTES_URL = os.getenv("PORTAL_CLIENTES_URL", "http://127.0.0.1:5002")


config = {
    "default": Config,
    "development": Config,
    "production": Config,
}
