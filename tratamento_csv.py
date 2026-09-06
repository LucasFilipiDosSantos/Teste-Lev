from __future__ import annotations

import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "dados" / "populacao_60mais_1209.csv"
OUTPUT_FILE = BASE_DIR / "dados" / "populacao_60mais_1209_tratado.md"


def read_csv_sections(csv_file: Path) -> tuple[list[str], list[list[str]], list[list[str]]]:
	with csv_file.open("r", encoding="utf-8-sig", newline="") as file:
		rows = list(csv.reader(file, delimiter=";"))

	source_index = next(
		index for index, row in enumerate(rows) if row and row[0].startswith("Fonte:")
	)
	table_rows = rows[4:source_index]
	metadata = [row[0] for row in rows[:2] if row]
	metadata.append(f"Ano: {rows[3][1]}")
	footer = rows[source_index:]
	return metadata, table_rows, footer


def markdown_row(values: list[str]) -> str:
	escaped_values = [value.replace("|", "\\|").replace("\n", "<br>") for value in values]
	return "| " + " | ".join(escaped_values) + " |"


def build_markdown(
	metadata: list[str],
	table_rows: list[list[str]],
	footer: list[list[str]],
) -> str:
	header = table_rows[0]
	data_rows = table_rows[1:]
	source = footer[0][0]
	notes_start = next(
		index for index, row in enumerate(footer) if row and row[0] == "Notas"
	)
	legend_start = next(
		index for index, row in enumerate(footer) if row and row[0] == "Legenda"
	)

	lines = [
		f"# {metadata[0]}",
		"",
		metadata[1],
		metadata[2],
		"",
		"## Estados e Brasil",
		"",
	]
	lines.append(markdown_row(header))
	lines.append(markdown_row(["---"] * len(header)))
	lines.extend(markdown_row(row) for row in data_rows)
	lines.extend(["", f"**{source}**", "", "## Notas", ""])

	for row in footer[notes_start + 1 : legend_start]:
		if row and row[0]:
			lines.append(f"- {row[0]}")

	lines.extend(["", "## Legenda", "", markdown_row(footer[legend_start + 1])])
	lines.append(markdown_row(["---", "---"]))
	lines.extend(markdown_row(row) for row in footer[legend_start + 2 :] if row)
	return "\n".join(lines) + "\n"


def process_csv(
	input_file: Path = INPUT_FILE,
	output_file: Path = OUTPUT_FILE,
) -> Path:
	metadata, table_rows, footer = read_csv_sections(input_file)
	output_file.write_text(
		build_markdown(metadata, table_rows, footer),
		encoding="utf-8",
	)
	return output_file


def main() -> None:
	output_file = process_csv()
	print(f"Arquivo tratado salvo em: {output_file}")


if __name__ == "__main__":
	main()
