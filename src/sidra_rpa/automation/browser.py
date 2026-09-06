from collections.abc import Iterator
from contextlib import contextmanager

from playwright.sync_api import Page, sync_playwright

from sidra_rpa.config import DEFAULT_TIMEOUT


@contextmanager
def create_page(headless: bool) -> Iterator[Page]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(accept_downloads=True, locale="pt-BR")
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT)

        try:
            yield page
        finally:
            context.close()
            browser.close()
