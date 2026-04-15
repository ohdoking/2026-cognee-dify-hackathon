import os

from dotenv import load_dotenv

load_dotenv()

DIFY_API_KEY = os.environ.get("DIFY_API_KEY")
DIFY_BASE_URL = os.environ.get("DIFY_URL", "https://api.dify.ai/v1").rstrip("/")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
COGNEE_API_KEY = os.environ.get("COGNEE_API_KEY")
COGNEE_BASE_URL = (os.environ.get("BASE_URL") or "").rstrip("/")
COGNEE_DATASET_NAME = os.environ.get("COGNEE_DATASET_NAME", "Project_Aurora_Knowledge")
GEMMA_BASE_URL = os.environ.get("GEMMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
GEMMA_MODEL = os.environ.get("GEMMA_MODEL", "gemma4")
