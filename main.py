from __future__ import annotations

import argparse
import sys
from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

BASE_URL = "https://sidra.ibge.gov.br/"
FILE_PATH = Path(__file__).resolve().parent / "dados" / "populacao_60mais_1209.csv"
DEFAULT_TIMEOUT = 45000


def wait_and_click(page: Page, text: str, exact: bool = True) -> None:
    element = page.get_by_text(text, exact=exact).first
    element.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    element.scroll_into_view_if_needed()
    element.click()


def navigate_to_table(page: Page) -> None:
    print("Acessando SIDRA...")
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)

    print("Navegando nos menus até a tabela 1209...")
    wait_and_click(page, "Pesquisas")
    wait_and_click(page, "População")
    wait_and_click(page, "Censo Demográfico", exact=False)
    wait_and_click(page, "Séries Temporais", exact=False)

    try:
        wait_and_click(page, "1209", exact=False)
    except PlaywrightTimeoutError:
        raise RuntimeError("Não foi possível localizar a tabela 1209")

    page.get_by_text("60 a 69 anos").first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)


def select_filters(page: Page) -> None:
    print("Aplicando filtros de idade...")
    wait_and_click(page, "Total")
    wait_and_click(page, "60 a 69 anos")
    wait_and_click(page, "70 anos ou mais")

    print("Selecionando Unidades da Federação...")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)

    uf_label = page.get_by_text("Unidade da Federação", exact=False).first
    uf_label.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    uf_label.scroll_into_view_if_needed()

    parent = uf_label.locator("xpath=..")
    toggle_button = parent.locator("button.sidra-toggle").first

    try:
        toggle_button.click()
        print("Todas as UFs foram selecionadas com sucesso.")
    except Exception as e:
        print(f"Não consegui clicar no botão de Unidades da Federação: {e}")


def download_file(page: Page, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)

    print("Abrindo janela de download...")
    wait_and_click(page, "Download")

    print("Definindo formato CSV (BR)...")
    formato_select = page.locator("form#download-form select[name='formato-arquivo']").first
    formato_select.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    formato_select.select_option("br.csv")

    print("Baixando arquivo...")
    # O botão de download é um link <a id="opcao-downloads">
    with page.expect_download(timeout=DEFAULT_TIMEOUT) as download_info:
        page.locator("a#opcao-downloads.btn-green-sucess").click()

    download = download_info.value
    download.save_as(target_path)

    if not target_path.exists() or target_path.stat().st_size == 0:
        raise RuntimeError("Download falhou: arquivo não foi gerado ou está zerado.")

    print(f"Sucesso! Arquivo salvo em: {target_path}")


def run(headless: bool) -> Path:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Automação SIDRA Tabela 1209")
    parser.add_argument("--headed", action="store_true", help="Executa com interface gráfica")
    args = parser.parse_args()

    try:
        run(headless=not args.headed)
        return 0
    except PlaywrightTimeoutError as e:
        print(f"Timeout durante execução: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Erro ao executar automação: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
