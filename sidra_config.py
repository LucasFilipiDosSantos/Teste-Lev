from pathlib import Path

BASE_URL = "https://sidra.ibge.gov.br/"
FILE_PATH = Path(__file__).resolve().parent / "dados" / "populacao_60mais_1209.csv"
DEFAULT_TIMEOUT = 45_000
AGE_FILTERS = ("Total", "60 a 69 anos", "70 anos ou mais")
