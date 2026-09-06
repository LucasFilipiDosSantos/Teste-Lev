import logging
from pathlib import Path

from playwright.sync_api import Page

from sidra_rpa.automation.helpers import first_visible, wait_and_click
from sidra_rpa.config import DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class SidraDownloader:
    def __init__(self, page: Page):
        self.page = page

    def download_csv(self, target_path: Path) -> Path:
        target_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Abrindo janela de download...")
        wait_and_click(self.page, "Download")

        logger.info("Definindo formato CSV (BR)...")
        formato_select = first_visible(
            (
                self.page.get_by_role("combobox"),
                self.page.locator(
                    "form#download-form select[name='formato-arquivo']"
                ),
            )
        )
        formato_select.select_option("br.csv")

        if formato_select.input_value() != "br.csv":
            raise RuntimeError("O formato CSV (BR) não foi selecionado.")

        logger.info("Baixando arquivo...")
        download_button = first_visible(
            (
                self.page.get_by_role("link", name="Download", exact=True),
                self.page.get_by_role("button", name="Download", exact=True),
                self.page.locator("a#opcao-downloads.btn-green-sucess"),
            )
        )

        with self.page.expect_download(timeout=DEFAULT_TIMEOUT) as download_info:
            download_button.click()

        download_info.value.save_as(target_path)

        if not target_path.exists() or target_path.stat().st_size == 0:
            raise RuntimeError("Download falhou: arquivo não foi gerado ou está zerado.")

        logger.info("Sucesso! Arquivo salvo em: %s", target_path)
        return target_path
