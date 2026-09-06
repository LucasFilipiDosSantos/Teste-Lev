from collections.abc import Iterable

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from sidra_rpa.config import DEFAULT_TIMEOUT


def wait_visible(locator: Locator) -> Locator:
    locator.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    return locator


def first_visible(locators: Iterable[Locator]) -> Locator:
    for locator in locators:
        for index in range(locator.count()):
            candidate = locator.nth(index)
            try:
                candidate.wait_for(state="visible", timeout=1_000)
                return candidate
            except PlaywrightTimeoutError:
                continue

    raise RuntimeError("Nenhum controle visível foi encontrado.")


def wait_and_click(page: Page, text: str, exact: bool = True) -> Locator:
    element = wait_visible(page.get_by_text(text, exact=exact).first)
    element.scroll_into_view_if_needed()
    element.click()
    return element
