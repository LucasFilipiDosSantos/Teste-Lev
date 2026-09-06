import logging

from playwright.sync_api import Page

from sidra_rpa.automation.helpers import first_visible
from sidra_rpa.config import AGE_FILTERS

logger = logging.getLogger(__name__)


class SidraFilters:
    def __init__(self, page: Page):
        self.page = page

    def apply(self) -> None:
        self._select_age_groups()
        self._select_federative_units()

    def _select_age_groups(self) -> None:
        logger.info("Aplicando filtros de idade...")
        for age_filter in AGE_FILTERS:
            checkbox = first_visible(
                (
                    self.page.get_by_role("checkbox", name=age_filter, exact=True),
                    self.page.get_by_text(age_filter, exact=True),
                )
            )
            checkbox.scroll_into_view_if_needed()
            checkbox.click()

    def _select_federative_units(self) -> None:
        logger.info("Selecionando Unidades da Federação...")
        uf_label = first_visible(
            (self.page.get_by_text("Unidade da Federação", exact=False),)
        )
        uf_label.scroll_into_view_if_needed()
        parent = uf_label.locator("xpath=..")
        toggle_button = first_visible(
            (
                self.page.get_by_role(
                    "checkbox",
                    name="Unidade da Federação",
                    exact=True,
                ),
                parent.locator("button.sidra-toggle"),
            )
        )

        try:
            toggle_button.click()
            logger.info("Todas as UFs foram selecionadas com sucesso.")
        except Exception:
            logger.exception("Erro ao selecionar Unidades da Federação")
            raise
