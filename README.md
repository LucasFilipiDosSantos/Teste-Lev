﻿# Automação RPA – Extração de Dados do SIDRA/IBGE

Este projeto automatiza a navegação na interface pública do SIDRA/IBGE para extrair dados da Tabela 1209, referente à população de 60 anos ou mais, filtrando as faixas etárias e as Unidades da Federação (UF), e salvando o resultado em CSV e em formato tratado em Markdown.

## Passo a passo de execução

1. Acesse a raiz do projeto:

```bash
cd /home/lucas/DesafioLev
```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Instale o pacote e as dependências do projeto:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

4. Instale o navegador do Playwright:

```bash
python -m playwright install chromium
```

5. Execute a automação:

Modo headless (sem abrir a interface gráfica):

```bash
sidra-rpa
```

Modo com navegador visível:

```bash
sidra-rpa --headed
```

6. O fluxo realiza automaticamente:
   - abertura do SIDRA;
   - navegação até a tabela 1209;
   - aplicação dos filtros de idade e UF;
   - download do CSV em BR;
   - processamento do arquivo para gerar a versão em Markdown.

7. Arquivos gerados:

```text
./dados/populacao_60mais_1209.csv
./dados/processed/populacao_60mais_1209.md
```

> O CSV sem tratamento é salvo em `./dados/populacao_60mais_1209.csv`. O CSV processado fica em `./dados/processed/populacao_60mais_1209.md`. Os caminhos são definidos nos arquivos Python do projeto, especialmente em `src/sidra_rpa/config.py`, e a pasta é criada automaticamente durante a execução.

## Dependências necessárias

- Python >= 3.9
- pip
- Playwright >= 1.48
- Chromium para Playwright
- setuptools (para empacotamento do projeto)

A dependência principal da automação é o pacote `playwright`, responsável pela navegação, interações com a interface e captura do download.

## Estratégia adotada

A solução foi estruturada em módulos para separar responsabilidades:

- `sidra_rpa.main`: ponto de entrada da aplicação;
- `sidra_rpa.config`: URLs, caminhos e filtros fixos;
- `sidra_rpa.automation`: navegação, filtros, browser e download;
- `sidra_rpa.processing.csv_processor`: transforma o CSV em texto formatado em Markdown.

A estratégia principal foi:

- usar a interface do SIDRA como um usuário real, sem chamar endpoints de API;
- localizar elementos por texto visível e por seletores estáveis quando necessário;
- aguardar a visibilidade de controles antes de interagir;
- aplicar filtros explícitos para remover a opção `Total` e manter as faixas etárias relevantes;
- capturar o download com `page.expect_download()` para salvar o arquivo em local controlado;
- processar o CSV depois das etapas de automação para gerar um relatório mais legível.

## Principais desafios encontrados

1. Interface dinâmica do SIDRA
   - Muitos elementos são carregados de forma assíncrona.
   - Solução: uso de esperas explícitas por visibilidade e interação controlada.

2. Modal e fluxo de download
   - O painel de download só aparece após clique em ação específica.
   - Solução: aguardar o campo de formato, selecionar `CSV (BR)` e capturar o arquivo com `expect_download()`.

3. Lentidão e instabilidade da página
   - O portal pode responder mais lentamente em momentos de alta carga.
   - Solução: timeouts configurados e tratamento de exceções para falhas do tipo `PlaywrightTimeoutError`.

4. Seleção de árvore territorial e filtros de idade
   - A interface tem elementos de árvore e controles dependentes de estado.
   - Solução: navegação por texto visível e interações em sequência sobre os nós relevantes.

## Estrutura do projeto

```text
.
├── dados/
│   ├── populacao_60mais_1209.csv
│   └── processed/
│       └── populacao_60mais_1209.md
├── src/
│   └── sidra_rpa/
├── pyproject.toml
├── README.md
└── .venv/
```

O CSV bruto segue o caminho:

```text
./dados/populacao_60mais_1209.csv
```

E o CSV processado fica em:

```text
./dados/processed/populacao_60mais_1209.md
```

## Observações finais

- A automação foi pensada para seguir o fluxo real de uso do SIDRA, sem “hack” no DOM;
- O projeto é útil para consultas repetitivas na Tabela 1209, reduzindo a necessidade de manipulação manual de dados em planilhas;
- O resultado final é uma extração automatizada, organizada e pronta para uso em relatórios ou análises.
