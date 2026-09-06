﻿# 🤖 Automação RPA – Extração de Dados Demográficos (SIDRA / IBGE)

Este projeto consiste em uma solução de automação RPA (*Robotic Process Automation*) desenvolvida em Python com Playwright. O objetivo é navegar pela interface pública do portal **SIDRA/IBGE**, localizar a **Tabela 1209** (População por grupos de idade), aplicar filtros específicos para a população de **60 anos ou mais** por **Unidades da Federação (UF)** e realizar o download dos dados em formato **CSV (BR)**.

## 📁 Estrutura do Projeto

```text
.
├── data/
│   ├── raw/                         # CSV original baixado
│   └── processed/                   # Resultado tratado em Markdown
├── src/sidra_rpa/
│   ├── main.py                      # Coordenação do fluxo
│   ├── config.py                    # Configurações e caminhos
│   ├── automation/                  # Browser, navegação, filtros e download
│   └── processing/                  # Tratamento do CSV
├── pyproject.toml                   # Pacote e dependências
└── README.md                        # Documentação do projeto
```

## ⚙️ Pré-requisitos e Instalação

### 1. Requisitos do Sistema

- **Python**: versão 3.8 ou superior.
- **Chromium**: instalado pelo Playwright.

### 2. Instalação das Dependências

Na raiz do projeto, instale os pacotes necessários:

```bash
python -m pip install -e .
python -m playwright install chromium
```

## 🚀 Como Executar

A automação é executada pela linha de comando.

### Modo Headless

Executa em segundo plano, sem exibir o navegador:

```bash
sidra-rpa
```

### Modo Headed

Exibe o navegador durante a execução:

```bash
sidra-rpa --headed
```

Após uma execução bem-sucedida, o CSV será salvo em `data/raw/populacao_60mais_1209.csv` e o tratamento será executado automaticamente. O resultado formatado será salvo em `data/processed/populacao_60mais_1209.md`. Os caminhos são calculados a partir da raiz do projeto, independentemente do diretório atual do terminal.

## 🎯 Requisitos Cumpridos

- [x] **Navegação estritamente pela interface**: a automação inicia na *Home* (`https://sidra.ibge.gov.br/`) e navega pelos menus até a tabela.
- [x] **Zero acesso direto ou API REST**: não são feitas chamadas de API nem é acessada diretamente a URL da tabela.
- [x] **Sem hacks de DOM**: não utiliza `evaluate()`, `querySelector()` nem alteração manual de elementos no HTML.
- [x] **Filtros aplicados**:
	- Remoção da seleção global `Total`.
	- Seleção dos grupos etários `60 a 69 anos` e `70 anos ou mais`.
	- Seleção de `Unidade da Federação` na árvore territorial.
- [x] **Download configurado**: a modal é processada para selecionar o formato `CSV (BR)` e iniciar a transferência.
- [x] **Destino dos dados**: arquivo salvo em `data/raw/populacao_60mais_1209.csv`.

## 🛠️ Estratégia Adotada e Arquitetura do Script

A arquitetura foi dividida para manter o entry point simples e concentrar cada responsabilidade em um módulo:

- `sidra_rpa.main`: coordena a automação e o processamento.
- `sidra_rpa.config`: centraliza URL, timeout, filtros de idade e caminhos.
- `sidra_rpa.automation`: separa browser, navegação, filtros e download.
- `sidra_rpa.processing.csv_processor`: lê o CSV e gera a saída Markdown.

A estratégia foi desenhada para garantir estabilidade, resiliência e simulação fiel do uso humano.

### 1. Navegação Baseada em Texto Visível

O script usa `get_by_text()` para localizar os menus e opções que o usuário vê. Nos pontos em que o portal expõe controles específicos, ele usa seletores CSS direcionados, como o campo `select[name='formato-arquivo']` e o link `a#opcao-downloads.btn-green-sucess`.

**Motivo:** o texto visível torna a navegação mais próxima da ação humana, enquanto os seletores CSS específicos são usados apenas nos controles do formulário de download que precisam ser identificados com precisão.

### 2. Fallbacks Para Controles Dinâmicos

O helper `first_visible()` recebe uma sequência de locators e retorna o primeiro elemento que realmente esteja visível. Os controles tentam ser encontrados nesta ordem:

1. Role e nome acessível, quando o SIDRA expõe essa informação.
2. Texto visível, quando a ação é baseada em um rótulo da interface.
3. Seletor estrutural específico, como fallback para controles que não possuem nome acessível.

Essa estratégia mantém o locator acessível como primeira opção sem depender exclusivamente de uma hipótese sobre a árvore de acessibilidade do portal. O fallback estrutural continua isolado nos helpers da automação.

### 3. Tratamento de Carregamentos Assíncronos e Instabilidades

O portal SIDRA utiliza carregamentos assíncronos ao expandir nós da árvore e alternar opções.

**Motivo:** o script usa esperas explícitas baseadas na visibilidade dos elementos e no estado `domcontentloaded`, reduzindo problemas de *race condition*.

### 4. Interação com a Árvore de Recorte Territorial

Para selecionar as Unidades da Federação, o script localiza o nó `Unidade da Federação` e interage com a caixa de seleção associada, usando os elementos disponíveis na interface.

**Motivo:** a seleção do nó territorial evita depender de seletores visuais frágeis e permite que a própria árvore controle as opções relacionadas.

### 5. Captura Nativa do Download via Evento

O download é gerenciado pelo evento `page.expect_download` do Playwright.

**Motivo:** isso captura a transferência iniciada pela página e permite salvar o arquivo no caminho configurado, independentemente do nome temporário atribuído pelo navegador.

## 🛑 Desafios Encontrados e Soluções

| Desafio encontrado | Causa | Solução aplicada |
| --- | --- | --- |
| Componentes dinâmicos da interface | O controle territorial é encontrado a partir do texto `Unidade da Federação` e do botão `button.sidra-toggle` localizado no elemento pai. | O script aguarda o texto e o botão ficarem visíveis, rola até o controle e clica nele. |
| Modal dinâmica de download | Ao clicar no botão inicial de Download, os controles de formato e confirmação são renderizados pela página. | O script aguarda o campo de formato, seleciona `CSV (BR)`, aguarda o link de confirmação e captura a transferência com `page.expect_download()`. |
| Tempo de resposta oscilante do SIDRA | O servidor do IBGE pode apresentar lentidão em requisições de tabelas censitárias. | O script usa timeout global de `45.000 ms` e tratamento de exceções específicas. |

## 📄 Saída Gerada

O arquivo final contém os dados baixados da Tabela 1209 no formato CSV (BR):

```text
data/raw/populacao_60mais_1209.csv
```

## 📚 Leitura Literal do Código

Esta seção explica o que cada parte dos arquivos faz, na ordem em que o programa é carregado e executado.

### Arquivo `sidra_rpa/config.py`

Este arquivo contém somente configurações. Ele não abre o navegador, não acessa o SIDRA e não executa funções.

#### `from pathlib import Path`

BASE_URL = "https://sidra.ibge.gov.br/"
```

Define a página inicial que o Playwright abrirá. O fluxo começa nessa página e não começa diretamente na URL da tabela.

#### `FILE_PATH`

```python
FILE_PATH = Path(__file__).resolve().parent / "dados" / "populacao_60mais_1209.csv"
```

- `__file__` representa o arquivo Python que está sendo executado.
- `.resolve()` transforma esse caminho em um caminho absoluto.
- `.parents[2]` localiza a raiz do projeto a partir do pacote.
- `/ "data"` entra na pasta de dados.
- `/ "populacao_60mais_1209.csv"` define o nome do arquivo final.

O resultado é que o CSV não depende da pasta atual do terminal. A saída fica em `data/raw/populacao_60mais_1209.csv`.

#### `DEFAULT_TIMEOUT`

```python
DEFAULT_TIMEOUT = 45_000
```


É uma tupla com os três textos que serão clicados na dimensão de idade. A ordem é intencional: primeiro remove `Total`, depois seleciona as duas faixas de idade.

### Módulos `sidra_rpa.automation`

Esses módulos contêm a automação Playwright. O ponto de entrada da aplicação é `sidra_rpa.main`.

#### Imports

- `from __future__ import annotations`: permite tratar anotações de tipo de forma mais flexível.
- `import logging`: fornece o logger usado para registrar o progresso e os erros.
- `from pathlib import Path`: permite tipar e manipular o caminho do arquivo de saída.
- `Locator` e `Page`: representam elementos localizados e páginas do Playwright.
- `PlaywrightTimeoutError`: representa falhas de tempo limite do Playwright.
- `sync_playwright`: inicia a API síncrona do Playwright.
- Os módulos recebem configurações de `sidra_rpa.config`.

#### `logger = logging.getLogger(__name__)`

Cria um logger cujo nome corresponde ao módulo atual. O `logging.basicConfig()` é configurado pelo entry point, mas este módulo pode registrar mensagens sem criar uma segunda configuração global.

#### `wait_visible(locator)`

```python
def wait_visible(locator: Locator) -> Locator:
	locator.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
	return locator
```

Esta função recebe um locator, espera até que ele esteja visível e devolve o mesmo locator. Ela concentra a espera explícita usada pelo restante do código.

Se o elemento não ficar visível em até 45 segundos, o Playwright lança `PlaywrightTimeoutError`.

#### `first_visible(locators)`

Esta função recebe vários locators candidatos. Para cada locator, ela verifica suas ocorrências e espera até 1 segundo para cada ocorrência ficar visível. Assim que encontra uma ocorrência visível, retorna esse elemento.

Se nenhum candidato ficar visível, lança `RuntimeError` com a mensagem `Nenhum controle visível foi encontrado.`. A espera curta é intencional: essa função serve para escolher entre fallbacks que já devem estar presentes, enquanto transições de página usam `wait_visible()` com o timeout completo.

#### `wait_and_click(page, text, exact=True)`

Esta função recebe a página, um texto e uma indicação de correspondência exata.

1. `page.get_by_text(text, exact=exact)` procura elementos pelo texto visível.
2. `.first` escolhe a primeira ocorrência.
3. `wait_visible(...)` aguarda essa ocorrência aparecer.
4. `scroll_into_view_if_needed()` rola a página somente se necessário.
5. `.click()` simula o clique do usuário.
6. A função retorna o locator clicado.

Quando `exact=False`, o texto pode aparecer dentro de um texto maior. Isso é usado em nomes como `Censo Demográfico`, `Séries Temporais` e `1209`.

#### `navigate_to_table(page)`

Esta função abre o SIDRA e percorre a interface até a tabela 1209.

1. Registra `Acessando SIDRA...` no log.
2. Executa `page.goto(BASE_URL, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)`.
3. Aguarda o DOM inicial ser carregado, respeitando o limite de 45 segundos.
4. Clica em `Pesquisas`.
5. Clica em `População`.
6. Clica em `Censo Demográfico`, permitindo correspondência parcial.
7. Clica em `Séries Temporais`, permitindo correspondência parcial.
8. Tenta localizar e clicar em `1209`.
9. Se a busca da tabela atingir o timeout, converte o erro em `RuntimeError` com a mensagem `Não foi possível localizar a tabela 1209`.
10. Depois do clique, aguarda o texto `60 a 69 anos` aparecer. Esse texto funciona como evidência de que a tela da tabela foi carregada.

Essa função não acessa a URL direta da tabela. Ela usa a URL inicial e cliques na interface.

#### `select_filters(page)`

Esta função aplica os filtros de idade e território.

1. Registra `Aplicando filtros de idade...`.
2. Percorre a tupla `AGE_FILTERS` com um `for`.
3. Para cada faixa, tenta primeiro `get_by_role("checkbox", name=..., exact=True)`.
4. Se não encontrar um checkbox acessível visível, tenta `get_by_text(..., exact=True)`.
5. Rola até o controle e clica nele.
6. O primeiro clique é em `Total`.
7. O segundo clique é em `60 a 69 anos`.
8. O terceiro clique é em `70 anos ou mais`.
9. Registra `Selecionando Unidades da Federação...`.
10. Localiza o texto `Unidade da Federação` com correspondência parcial.
11. Rola até o texto, se necessário.
12. Sobe um nível na árvore com `uf_label.locator("xpath=..")` para obter o elemento pai.
13. Tenta um checkbox acessível chamado `Unidade da Federação`.
14. Se esse checkbox não estiver disponível, tenta `button.sidra-toggle` dentro do elemento pai.
15. Clica no controle encontrado para selecionar as Unidades da Federação.
16. Registra sucesso no log.

Se o clique territorial gerar qualquer exceção, `logger.exception()` registra a mensagem junto com o traceback e `raise` relança o mesmo erro. A execução não continua fingindo que o filtro foi aplicado.

O código atual não percorre manualmente uma lista de 27 estados e não valida individualmente cada estado. Ele aciona o controle territorial disponível na própria interface.

#### `download_file(page, target_path)`

Esta função abre o fluxo de download, escolhe o formato e salva o arquivo.

1. `target_path.parent.mkdir(parents=True, exist_ok=True)` cria a pasta de saída se ela ainda não existir.
2. Registra `Abrindo janela de download...`.
3. Usa `wait_and_click(page, "Download")` para abrir a área de download.
4. Tenta localizar primeiro um `combobox` acessível.
5. Se não encontrar um `combobox`, usa `form#download-form select[name='formato-arquivo']`.
6. Aguarda o campo de seleção ficar visível.
7. Executa `select_option("br.csv")`, usando a API oficial do Playwright para selecionar a opção do elemento HTML `<select>`.
8. Lê o valor com `input_value()`.
9. Se o valor não for exatamente `br.csv`, lança `RuntimeError`.
10. Tenta localizar um link ou botão acessível com nome `Download`.
11. Se não encontrar esses controles, usa `a#opcao-downloads.btn-green-sucess`.
12. Aguarda o controle ficar visível.
13. Abre `page.expect_download(...)` antes do clique. Isso prepara o Playwright para capturar o evento de download.
14. Clica no link de confirmação.
15. Obtém o download capturado em `download_info.value`.
16. Salva o arquivo no caminho recebido em `target_path`.
17. Verifica se o arquivo existe e se seu tamanho é maior que zero.
18. Se o arquivo não existir ou estiver vazio, lança `RuntimeError`.
19. Registra o caminho final no log.

O código não escolhe um nome temporário do navegador. Ele sempre salva a transferência no caminho definido por `FILE_PATH`.

#### `run(headless)`

Esta é a função que coordena a execução completa do Playwright.

1. `sync_playwright()` inicia o Playwright síncrono.
2. `chromium.launch(headless=headless)` abre o Chromium. Quando `headless=True`, o navegador não aparece; quando `False`, aparece na tela.
3. `browser.new_context(accept_downloads=True, locale="pt-BR")` cria um contexto isolado, permite downloads e define o idioma/localidade como português do Brasil.
9. Retorna o caminho do arquivo.
10. O bloco `finally` fecha o contexto e o navegador mesmo se alguma etapa falhar.

O fechamento no `finally` evita deixar processos do Chromium abertos após sucesso ou erro.

Este é o entry point, ou seja, o arquivo que deve ser executado pelo usuário.

#### Imports

- `argparse` interpreta argumentos como `--headed`.
- `logging` exibe mensagens de execução e erro.
- `sys` permite encerrar o processo com um código numérico.
- `PlaywrightTimeoutError` identifica timeouts de forma específica.
- `main` importa os componentes especializados de `sidra_rpa.automation`.

#### `logging.basicConfig(...)`

Configura o logging global:

- `level=logging.INFO` exibe mensagens informativas, avisos e erros.
- `format="%(asctime)s - %(levelname)s - %(message)s"` mostra horário, nível e mensagem.

#### `main()`

1. Cria um `ArgumentParser` com a descrição da automação.
2. Registra o argumento opcional `--headed`.
3. Analisa os argumentos recebidos pelo terminal.
4. Chama `run(headless=not args.headed)`.
5. Sem `--headed`, `args.headed` é falso e `headless` fica verdadeiro.
6. Com `--headed`, `args.headed` é verdadeiro e `headless` fica falso.
7. Em caso de sucesso, retorna `0`.
8. Se ocorrer `PlaywrightTimeoutError`, registra o timeout e retorna `1`.
9. Se ocorrer qualquer outra exceção, `logging.exception()` registra mensagem e traceback e retorna `1`.

#### `if __name__ == "__main__"`

O arquivo possui uma única dependência:

```text
playwright>=1.48,<2
```

Isso permite versões do Playwright a partir da `1.48`, mas menores que a versão `2`. O intervalo evita instalar automaticamente uma versão principal incompatível.

O projeto não utiliza `WebDriverWait`, porque essa é uma API do Selenium. No Playwright, `wait_for()` e as esperas automáticas dos locators cumprem esse papel.

Não existe `time.sleep()` nem `page.wait_for_timeout()` no código atual. Também não existe espera fixa baseada apenas em passagem de tempo.

## ❌ O que o projeto não faz

- Não usa API REST para obter os dados.
- Não acessa diretamente a URL interna da tabela.
- Não usa `page.evaluate()`.
- Não usa `querySelector()`.
- Não altera manualmente o DOM.
- Não usa Selenium ou `WebDriverWait`.
- Não mantém o navegador aberto depois que o fluxo termina.
- Não cria o CSV artificialmente; o arquivo vem do download capturado pelo Playwright.
- Não adiciona automaticamente arquivos ao Git.

## 🔁 Fluxo Completo em Uma Visão

```text
CLI
 |
 v
sidra_rpa.main
 |
 v
sidra_rpa.main
 |
 +--> abre Chromium e cria contexto pt-BR
 |
 +--> abre https://sidra.ibge.gov.br/
 |
 +--> Pesquisas > População > Censo Demográfico > Séries Temporais
 |
 +--> abre a tabela 1209
 |
 +--> clica em Total, 60 a 69 anos e 70 anos ou mais
 |
 +--> seleciona Unidade da Federação
 |
 +--> abre Download e escolhe br.csv
 |
 +--> captura o download e salva em data/raw/populacao_60mais_1209.csv
 |
 +--> valida o arquivo e fecha o navegador
```

## 🧪 Validações Locais

Antes de executar o site real, é possível validar a sintaxe e a CLI:

```bash
PYTHONPATH=src python -m compileall -q src
PYTHONPATH=src python -m sidra_rpa.main --help
```

Esses comandos verificam que os módulos compilam e que o entry point consegue carregar os argumentos. Eles não navegam no SIDRA nem baixam o CSV.
