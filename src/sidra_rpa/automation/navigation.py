import logging

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from sidra_rpa.automation.helpers import wait_and_click, wait_visible
from sidra_rpa.config import BASE_URL, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class SidraNavigator:
    def __init__(self, page: Page):
        self.page = page

    def open_table(self) -> None:
        logger.info("Acessando SIDRA...")
        self.page.goto(
            BASE_URL,
            wait_until="domcontentloaded",
            timeout=DEFAULT_TIMEOUT,
        )

        logger.info("Navegando nos menus até a tabela 1209...")
        wait_and_click(self.page, "Pesquisas")
        wait_and_click(self.page, "População")
        wait_and_click(self.page, "Censo Demográfico", exact=False)
        wait_and_click(self.page, "Séries Temporais", exact=False)

        try:
            wait_and_click(self.page, "1209", exact=False)
        except PlaywrightTimeoutError as error:
            raise RuntimeError("Não foi possível localizar a tabela 1209") from error

        wait_visible(self.page.get_by_text("60 a 69 anos", exact=True).first)
