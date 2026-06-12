from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://curedesk:curedesk@localhost:5432/curedesk"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    cors_origins: str = "http://localhost:3000,exp://localhost:8081"
    # e.g. redis://localhost:6379 — empty means in-process memory (single worker only)
    rate_limit_storage_uri: str = ""
    firebase_service_account_json: str = ""
    sentry_dsn: str = ""
    artifacts_dir: str = "models/artifacts"
    max_upload_bytes: int = 5 * 1024 * 1024
    ocr_timeout_seconds: int = 30
    ocr_use_gpu: str = "auto"  # auto | true | false
    ocr_engine: str = "easyocr"  # easyocr | paddle | ensemble
    # Pre-load heavy models (OCR reader, embedding model) in a background
    # thread at startup so the first request doesn't pay the cold-start cost.
    warmup_enabled: bool = True
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    @property
    def ocr_gpu_enabled(self) -> bool:
        v = self.ocr_use_gpu.strip().lower()
        if v in ("1", "true", "yes"):
            return True
        if v in ("0", "false", "no"):
            return False
        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
