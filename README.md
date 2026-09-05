﻿# 🤖 Automação RPA – Extração de Dados Demográficos (SIDRA / IBGE)

Este projeto consiste em uma solução de automação RPA (*Robotic Process Automation*) desenvolvida em Python com Playwright. O objetivo é navegar pela interface pública do portal **SIDRA/IBGE**, localizar a **Tabela 1209** (População por grupos de idade), aplicar filtros específicos para a população de **60 anos ou mais** por **Unidades da Federação (UF)** e realizar o download dos dados em formato **CSV (BR)**.

## 📁 Estrutura do Projeto

```text
.
├── dados/
│   └── populacao_60mais_1209.csv   # Arquivo CSV gerado pela automação
├── main.py                         # Script principal de automação
├── README.md                       # Documentação do projeto
└── requirements.txt                # Dependências do projeto
```

## ⚙️ Pré-requisitos e Instalação

### 1. Requisitos do Sistema

- **Python**: versão 3.8 ou superior.
- **Chromium**: instalado pelo Playwright.

### 2. Instalação das Dependências

Na raiz do projeto, instale os pacotes necessários:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 🚀 Como Executar

A automação é executada pela linha de comando.

### Modo Headless

Executa em segundo plano, sem exibir o navegador:

```bash
python main.py
```

### Modo Headed

Exibe o navegador durante a execução:

```bash
python main.py --headed
```

Após uma execução bem-sucedida, o arquivo será salvo em `dados/populacao_60mais_1209.csv`. O caminho é calculado a partir da localização do `main.py`, independentemente do diretório atual do terminal.

## 🎯 Requisitos Cumpridos

- [x] **Navegação estritamente pela interface**: a automação inicia na *Home* (`https://sidra.ibge.gov.br/`) e navega pelos menus até a tabela.
- [x] **Zero acesso direto ou API REST**: não são feitas chamadas de API nem é acessada diretamente a URL da tabela.
- [x] **Sem hacks de DOM**: não utiliza `evaluate()`, `querySelector()` nem alteração manual de elementos no HTML.
- [x] **Filtros aplicados**:
	- Remoção da seleção global `Total`.
	- Seleção dos grupos etários `60 a 69 anos` e `70 anos ou mais`.
	- Seleção de `Unidade da Federação` na árvore territorial.
- [x] **Download configurado**: a modal é processada para selecionar o formato `CSV (BR)` e iniciar a transferência.
- [x] **Destino dos dados**: arquivo salvo em `dados/populacao_60mais_1209.csv`.

## 🛠️ Estratégia Adotada e Arquitetura do Script

A estratégia foi desenhada para garantir estabilidade, resiliência e simulação fiel do uso humano.

### 1. Navegação Baseada em Intenção e Atributos Acessíveis

O script utiliza seletores baseados em texto visível e papéis de acessibilidade, como `get_by_text()` e `get_by_role()`, em vez de depender de seletores CSS frágeis.

**Motivo:** textos e papéis interativos tendem a permanecer estáveis mesmo quando o CSS do portal é atualizado.

### 2. Tratamento de Carregamentos Assíncronos e Instabilidades

O portal SIDRA utiliza carregamentos assíncronos ao expandir nós da árvore e alternar opções.

**Motivo:** o script usa esperas explícitas baseadas na visibilidade dos elementos e no estado `domcontentloaded`, reduzindo problemas de *race condition*.

### 3. Interação com a Árvore de Recorte Territorial (JSTree)

Para selecionar as Unidades da Federação, o script localiza o nó `Unidade da Federação` e interage com a caixa de seleção associada, usando os elementos disponíveis na interface.

**Motivo:** a seleção do nó territorial evita depender de seletores visuais frágeis e permite que a própria árvore controle as opções relacionadas.

### 4. Captura Nativa do Download via Evento

O download é gerenciado pelo evento `page.expect_download` do Playwright.

**Motivo:** isso captura a transferência iniciada pela página e permite salvar o arquivo no caminho configurado, independentemente do nome temporário atribuído pelo navegador.

## 🛑 Desafios Encontrados e Soluções

| Desafio encontrado | Causa | Solução aplicada |
| --- | --- | --- |
| Componentes dinâmicos da interface (JSTree) | A árvore territorial utiliza elementos gráficos customizados, como `.jstree-checkbox`. | O script localiza o nó `Unidade da Federação` e interage com o checkbox associado ou com o elemento da própria interface. |
| Modal dinâmica de download | Ao clicar no botão inicial de download, uma modal `#modal-downloads` é renderizada para escolha do formato. | O script restringe a busca ao elemento `#modal-downloads`, seleciona `CSV (BR)` e aciona a confirmação. |
| Tempo de resposta oscilante do SIDRA | O servidor do IBGE pode apresentar lentidão em requisições de tabelas censitárias. | O script usa timeout global de `45.000 ms` e tratamento de exceções específicas. |

## 📄 Saída Gerada

O arquivo final contém os dados baixados da Tabela 1209 no formato CSV (BR):

```text
dados/populacao_60mais_1209.csv
```
