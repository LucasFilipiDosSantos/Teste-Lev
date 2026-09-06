from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from playwright.sync_api import (
    Locator,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

from sidra_config import AGE_FILTERS, BASE_URL, DEFAULT_TIMEOUT, FILE_PATH

logger = logging.getLogger(__name__)


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


def navigate_to_table(page: Page) -> None:
    logger.info("Acessando SIDRA...")
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)

    logger.info("Navegando nos menus até a tabela 1209...")
    wait_and_click(page, "Pesquisas")
    wait_and_click(page, "População")
    wait_and_click(page, "Censo Demográfico", exact=False)
    wait_and_click(page, "Séries Temporais", exact=False)

    try:
        wait_and_click(page, "1209", exact=False)
    except PlaywrightTimeoutError as error:
        raise RuntimeError("Não foi possível localizar a tabela 1209") from error

    wait_visible(page.get_by_text("60 a 69 anos", exact=True).first)


def select_filters(page: Page) -> None:
    logger.info("Aplicando filtros de idade...")
    for age_filter in AGE_FILTERS:
        checkbox = first_visible(
            (
                page.get_by_role("checkbox", name=age_filter, exact=True),
                page.get_by_text(age_filter, exact=True),
            )
        )
        checkbox.scroll_into_view_if_needed()
        checkbox.click()

    logger.info("Selecionando Unidades da Federação...")
    uf_label = first_visible(
        (page.get_by_text("Unidade da Federação", exact=False),)
    )
    uf_label.scroll_into_view_if_needed()
    parent = uf_label.locator("xpath=..")
    toggle_button = first_visible(
        (
            page.get_by_role(
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


def download_file(page: Page, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Abrindo janela de download...")
    wait_and_click(page, "Download")

    logger.info("Definindo formato CSV (BR)...")
    formato_select = first_visible(
        (
            page.get_by_role("combobox"),
            page.locator("form#download-form select[name='formato-arquivo']"),
        )
    )
    formato_select.select_option("br.csv")

    if formato_select.input_value() != "br.csv":
        raise RuntimeError("O formato CSV (BR) não foi selecionado.")

    logger.info("Baixando arquivo...")
    download_button = first_visible(
        (
            page.get_by_role("link", name="Download", exact=True),
            page.get_by_role("button", name="Download", exact=True),
            page.locator("a#opcao-downloads.btn-green-sucess"),
        )
    )

    with page.expect_download(timeout=DEFAULT_TIMEOUT) as download_info:
        download_button.click()

    download_info.value.save_as(target_path)

    if not target_path.exists() or target_path.stat().st_size == 0:
        raise RuntimeError("Download falhou: arquivo não foi gerado ou está zerado.")

    logger.info("Sucesso! Arquivo salvo em: %s", target_path)


def run(headless: bool) -> Path:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(accept_downloads=True, locale="pt-BR")
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT)

        try:
            navigate_to_table(page)
            select_filters(page)
            download_file(page, FILE_PATH)
            return FILE_PATH
        finally:
            context.close()
            browser.close()
