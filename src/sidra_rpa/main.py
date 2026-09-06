import argparse
import logging
import sys

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from sidra_rpa.automation.browser import create_page
from sidra_rpa.automation.downloader import SidraDownloader
from sidra_rpa.automation.filters import SidraFilters
from sidra_rpa.automation.navigation import SidraNavigator
from sidra_rpa.config import PROCESSED_MARKDOWN_PATH, RAW_CSV_PATH
from sidra_rpa.processing.csv_processor import process_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Automação SIDRA Tabela 1209")
    parser.add_argument("--headed", action="store_true", help="Executa com interface gráfica")
    args = parser.parse_args()

    try:
        with create_page(headless=not args.headed) as page:
            SidraNavigator(page).open_table()
            SidraFilters(page).apply()
            csv_path = SidraDownloader(page).download_csv(RAW_CSV_PATH)

        logging.info("RPA concluído. Iniciando tratamento do CSV...")
        processed_path = process_csv(csv_path, PROCESSED_MARKDOWN_PATH)
        logging.info("Arquivo tratado salvo em: %s", processed_path)
        return 0
    except PlaywrightTimeoutError as error:
        logging.error("Timeout durante execução: %s", error)
        return 1
    except Exception as error:
        logging.exception("Erro ao executar automação: %s", error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
