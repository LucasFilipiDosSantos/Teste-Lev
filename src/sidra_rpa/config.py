from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

BASE_URL = "https://sidra.ibge.gov.br/"
DEFAULT_TIMEOUT = 45_000

AGE_FILTERS = ("Total", "60 a 69 anos", "70 anos ou mais")
RAW_CSV_PATH = DATA_DIR / "raw" / "populacao_60mais_1209.csv"
PROCESSED_MARKDOWN_PATH = DATA_DIR / "processed" / "populacao_60mais_1209.md"
