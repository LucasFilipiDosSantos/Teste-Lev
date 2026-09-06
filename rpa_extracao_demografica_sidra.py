from __future__ import annotations

import argparse
import logging
import sys
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from sidra_automation import run
from tratamento_csv import process_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def main() -> int:
    parser = argparse.ArgumentParser(description="Automação SIDRA Tabela 1209")
    parser.add_argument("--headed", action="store_true", help="Executa com interface gráfica")
    args = parser.parse_args()

    try:
        csv_file = run(headless=not args.headed)
        logging.info("RPA concluído. Iniciando tratamento do CSV...")
        treated_file = process_csv(csv_file)
        logging.info("Arquivo tratado salvo em: %s", treated_file)
        return 0
    except PlaywrightTimeoutError as error:
        logging.error("Timeout durante execução: %s", error)
        return 1
    except Exception as error:
        logging.exception("Erro ao executar automação: %s", error)
        return 1


if __name__ == "__main__":
    sys.exit(main())