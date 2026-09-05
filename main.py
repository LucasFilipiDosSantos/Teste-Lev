"""
RPA para baixar a tabela 1209 do SIDRA pela interface web.

O script sempre inicia na página inicial do SIDRA.
A tabela não é acessada por URL, API, requisições HTTP ou manipulação direta do DOM.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

from playwright.sync_api import (
    Browser,
    Locator,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)


SIDRA_HOME = "https://sidra.ibge.gov.br/"
OUTPUT_FILE = Path("dados") / "populacao_60mais_1209.csv"
TIMEOUT_MS = 45_000


def first_visible(locators: Iterable[Locator]) -> Locator:
    """Retorna o primeiro locator visível."""
    for locator in locators:
        for index in range(locator.count()):
            candidate = locator.nth(index)

            try:
                candidate.wait_for(
                    state="visible",
                    timeout=3_000,
                )
                return candidate
            except PlaywrightTimeoutError:
                continue

    raise RuntimeError(
        "Nenhum dos controles esperados ficou visível."
    )


def click_text(
    page: Page,
    text: str,
    *,
    exact: bool = True,
) -> None:
    """Clica em um texto visível, priorizando links e botões."""

    escaped = re.escape(text)

    pattern = re.compile(
        rf"^{escaped}$" if exact else escaped,
        re.IGNORECASE,
    )

    target = first_visible(
        (
            page.get_by_role("link", name=pattern),
            page.get_by_role("button", name=pattern),
            page.get_by_text(pattern),
        )
    )

    target.scroll_into_view_if_needed()
    target.click()


def wait_for_navigation_or_content(page: Page) -> None:
    """Aguarda o carregamento da página/conteúdo."""

    page.wait_for_load_state("domcontentloaded")
    page.locator("body").wait_for(
        state="visible",
        timeout=TIMEOUT_MS,
    )


def navigate_to_table_1209(page: Page) -> None:
    """
    Navega até a tabela 1209 exclusivamente pela interface do SIDRA.
    """

    page.goto(
        SIDRA_HOME,
        wait_until="domcontentloaded",
    )

    page.set_default_timeout(TIMEOUT_MS)

    print("  - Abrindo Pesquisas")
    click_text(page, "Pesquisas")

    print("  - Abrindo População")
    click_text(page, "População")

    print("  - Abrindo Censo Demográfico")
    click_text(
        page,
        "Censo Demográfico",
        exact=False,
    )

    wait_for_navigation_or_content(page)

    print("  - Abrindo Séries Temporais")
    click_text(
        page,
        "Séries Temporais",
        exact=False,
    )

    wait_for_navigation_or_content(page)

    print("  - Localizando a tabela 1209")

    table_link = first_visible(
        (
            page.get_by_role(
                "link",
                name=re.compile(r"^1209$", re.IGNORECASE),
            ),
            page.get_by_role(
                "link",
                name=re.compile(
                    r"1209.*População",
                    re.IGNORECASE,
                ),
            ),
            page.get_by_role(
                "link",
                name=re.compile(
                    r"População.*grupos de idade",
                    re.IGNORECASE,
                ),
            ),
        )
    )

    table_link.scroll_into_view_if_needed()
    table_link.click()

    wait_for_navigation_or_content(page)

    page.get_by_text(
        "60 a 69 anos",
        exact=True,
    ).wait_for(
        state="visible",
        timeout=TIMEOUT_MS,
    )


def choose_in_dimension(
    page: Page,
    dimension: str,
    value: str,
) -> None:
    """Seleciona uma opção de uma dimensão do SIDRA."""

    label = first_visible(
        (
            page.get_by_text(
                re.compile(
                    rf"^{re.escape(dimension)}$",
                    re.IGNORECASE,
                )
            ),
            page.get_by_text(
                re.compile(
                    re.escape(dimension),
                    re.IGNORECASE,
                )
            ),
        )
    )

    label.scroll_into_view_if_needed()

    select = label.locator(
        "xpath=following::select[1]"
    )

    try:
        select.wait_for(
            state="visible",
            timeout=1_500,
        )

        options = select.locator("option")

        for index in range(options.count()):
            option = options.nth(index)

            if re.fullmatch(
                re.escape(value),
                option.inner_text().strip(),
                re.IGNORECASE,
            ):
                option_value = option.get_attribute("value")

                if option_value is None:
                    raise RuntimeError(
                        f"A opção '{value}' não possui valor."
                    )

                select.select_option(
                    value=option_value
                )
                return

        raise RuntimeError(
            f"A opção '{value}' não foi encontrada "
            f"em '{dimension}'."
        )

    except PlaywrightTimeoutError:
        pass

    trigger = label.locator(
        "xpath=following::*"
        "[self::button or "
        "@role='combobox' or "
        "@aria-haspopup='listbox'][1]"
    )

    try:
        trigger.wait_for(
            state="visible",
            timeout=1_500,
        )
        trigger.click()

    except PlaywrightTimeoutError:
        label.click()

    option = first_visible(
        (
            page.get_by_role(
                "option",
                name=re.compile(
                    rf"^{re.escape(value)}$",
                    re.IGNORECASE,
                ),
            ),
            page.get_by_role(
                "checkbox",
                name=re.compile(
                    rf"^{re.escape(value)}$",
                    re.IGNORECASE,
                ),
            ),
            page.get_by_text(
                re.compile(
                    rf"^{re.escape(value)}$",
                    re.IGNORECASE,
                )
            ),
        )
    )

    option.click()

    for confirmation in (
        "Aplicar",
        "Selecionar",
        "OK",
    ):
        try:
            page.get_by_role(
                "button",
                name=re.compile(
                    rf"^{re.escape(confirmation)}$",
                    re.IGNORECASE,
                ),
            ).click(timeout=1_000)

            break

        except PlaywrightTimeoutError:
            continue


def configure_table(page: Page) -> None:
    """
    Configura:
    - 60 a 69 anos
    - 70 anos ou mais
    - 27 Unidades da Federação
    - Brasil desmarcado
    - Grandes Regiões não selecionadas
    - Ano 2022
    """

    print("  - Removendo Total")

    total = first_visible(
        (
            page.get_by_text(
                "Total",
                exact=True,
            ),
        )
    )

    total.click()

    print("  - Selecionando 60 a 69 anos")
    click_text(
        page,
        "60 a 69 anos",
    )

    print("  - Selecionando 70 anos ou mais")
    click_text(
        page,
        "70 anos ou mais",
    )

    print("  - Abrindo Unidade da Federação")

    click_text(
        page,
        "Unidade da Federação",
        exact=False,
    )

    federative_units = (
        "11. Rondônia",
        "12. Acre",
        "13. Amazonas",
        "14. Roraima",
        "15. Pará",
        "16. Amapá",
        "17. Tocantins",
        "21. Maranhão",
        "22. Piauí",
        "23. Ceará",
        "24. Rio Grande do Norte",
        "25. Paraíba",
        "26. Pernambuco",
        "27. Alagoas",
        "28. Sergipe",
        "29. Bahia",
        "31. Minas Gerais",
        "32. Espírito Santo",
        "33. Rio de Janeiro",
        "35. São Paulo",
        "41. Paraná",
        "42. Santa Catarina",
        "43. Rio Grande do Sul",
        "50. Mato Grosso do Sul",
        "51. Mato Grosso",
        "52. Goiás",
        "53. Distrito Federal",
    )

    for unit in federative_units:
        print(f"    - UF: {unit}")

        click_text(
            page,
            unit,
        )

    print("  - Verificando seleção territorial")

    # Brasil deve ficar desmarcado.
    # O SIDRA pode retirar Brasil automaticamente após
    # a seleção das 27 UFs. Caso continue selecionado,
    # desmarca explicitamente.

    brazil = page.get_by_text(
        re.compile(
            r"^Brasil(?:\s*\[\d+/\d+\])?$",
            re.IGNORECASE,
        )
    )

    for index in range(brazil.count()):
        candidate = brazil.nth(index)

        try:
            if not candidate.is_visible():
                continue

            candidate.click()
            print("  - Brasil desmarcado")
            break

        except Exception:
            continue

    # Não clicamos em Grandes Regiões.
    # Portanto, ela permanece desmarcada.

    # As 27 UFs devem resultar na seleção:
    #
    # Unidade da Federação [27/27]
    #
    # com o ano 2022.
    #
    # O ano 2022 já é disponibilizado/selecionado pela interface.

    print("  - Visualizando tabela")

    click_text(
        page,
        "Visualizar",
        exact=False,
    )

    wait_for_navigation_or_content(page)


def download_csv(
    page: Page,
    destination: Path,
) -> None:
    """
    Executa o fluxo:

    Download
        ↓
    CSV (BR)
        ↓
    Download
        ↓
    arquivo CSV
    """

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("  - Clicando em Download")

    open_download = first_visible(
        (
            page.get_by_role(
                "button",
                name=re.compile(
                    r"^Download$",
                    re.IGNORECASE,
                ),
            ),
            page.get_by_role(
                "link",
                name=re.compile(
                    r"^Download$",
                    re.IGNORECASE,
                ),
            ),
        )
    )

    open_download.click()

    print("  - Selecionando CSV (BR)")

    csv_br = first_visible(
        (
            page.get_by_role(
                "option",
                name=re.compile(
                    r"^CSV\s*\(BR\)$",
                    re.IGNORECASE,
                ),
            ),
            page.get_by_role(
                "radio",
                name=re.compile(
                    r"^CSV\s*\(BR\)$",
                    re.IGNORECASE,
                ),
            ),
            page.get_by_text(
                re.compile(
                    r"^CSV\s*\(BR\)$",
                    re.IGNORECASE,
                )
            ),
        )
    )

    csv_br.click()

    print("  - Clicando em Download novamente")

    final_download = first_visible(
        (
            page.get_by_role(
                "button",
                name=re.compile(
                    r"^Download$",
                    re.IGNORECASE,
                ),
            ),
            page.get_by_role(
                "link",
                name=re.compile(
                    r"^Download$",
                    re.IGNORECASE,
                ),
            ),
        )
    )

    with page.expect_download(
        timeout=TIMEOUT_MS
    ) as download_info:

        final_download.click()

    download = download_info.value

    download.save_as(destination)

    if not destination.exists():
        raise RuntimeError(
            "O arquivo CSV não foi criado."
        )

    if destination.stat().st_size == 0:
        raise RuntimeError(
            "O CSV foi criado, mas está vazio."
        )

    print(
        f"  - Download concluído: {destination}"
    )


def run(headless: bool) -> Path:

    with sync_playwright() as playwright:

        browser: Browser = playwright.chromium.launch(
            headless=headless
        )

        context = browser.new_context(
            accept_downloads=True,
            locale="pt-BR",
        )

        page = context.new_page()

        try:

            print(
                "1/3 Navegando até a tabela 1209..."
            )

            navigate_to_table_1209(page)

            print(
                "2/3 Configurando idade, UFs e ano..."
            )

            configure_table(page)

            print(
                "3/3 Baixando o CSV..."
            )

            download_csv(
                page,
                OUTPUT_FILE,
            )

            return OUTPUT_FILE

        finally:

            context.close()
            browser.close()


def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Baixa a população de 60+ "
            "da tabela 1209 do SIDRA."
        )
    )

    parser.add_argument(
        "--headed",
        action="store_true",
        help=(
            "Exibe o navegador para "
            "acompanhar a automação."
        ),
    )

    args = parser.parse_args()

    try:

        output = run(
            headless=not args.headed
        )

    except PlaywrightTimeoutError as error:

        print(
            f"Tempo esgotado ao aguardar o SIDRA: {error}",
            file=sys.stderr,
        )

        return 1

    except Exception as error:

        print(
            f"Falha na automação: {error}",
            file=sys.stderr,
        )

        return 1

    print(
        f"CSV salvo em: {output}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())