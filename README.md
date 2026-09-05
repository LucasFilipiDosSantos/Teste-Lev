# Desafio RPA � SIDRA/IBGE tabela 1209

Automa��o em Python com Playwright que inicia em `https://sidra.ibge.gov.br/`, percorre a interface de Pesquisas at� o Censo Demogr�fico/S�ries Temporais e abre a tabela 1209 por meio do link exibido na p�gina. N�o h� URL da tabela, API REST, requisi��o HTTP de dados ou `page.evaluate` no c�digo.

## Requisitos

- Python 3.10 ou superior
- Google Chrome/Chromium (instalado automaticamente pelo Playwright)

## Execu��o

No PowerShell, na raiz do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
python main.py --headed
```

Para rodar sem mostrar o navegador:

```powershell
python main.py
```

Ao t�rmino, o arquivo ser� salvo em `dados/populacao_60mais_1209.csv`. A pasta � criada automaticamente. O CSV n�o � versionado, pois � uma sa�da reproduz�vel da automa��o.

## Estrat�gia adotada

1. Abre exclusivamente a p�gina inicial do SIDRA.
2. Navega por `Pesquisas` ? `Popula��o` ? `Censo Demogr�fico` ? `S�ries Temporais`.
3. Localiza o link da tabela 1209 na lista apresentada pela interface e o aciona ap�s rolar at� ele.
4. Configura `Grupo de idade: 60 anos ou mais`, `N�vel Territorial: Unidades da Federa��o` e o per�odo mais recente exibido.
5. Aciona o download CSV pelo menu da pr�pria p�gina e valida se o arquivo foi gravado e n�o est� vazio.

Os seletores priorizam pap�is acess�veis, nomes vis�veis e rela��o com o r�tulo da dimens�o. H� esperas expl�citas, timeout de 45 segundos e mensagens de erro para indisponibilidade ou altera��es da interface. Use `--headed` na primeira execu��o: ele facilita auditar o caminho RPA e identificar mudan�as na UI do SIDRA.

## Observa��o sobre o ambiente atual

Este reposit�rio cont�m o gerador do CSV, mas o arquivo n�o � pr�-preenchido: ele deve ser gerado pela execu��o real do Playwright, como pede o desafio. Neste ambiente de edi��o n�o h� Python/Node ou navegador automatiz�vel instalados para realizar esse download sem simular o resultado.
