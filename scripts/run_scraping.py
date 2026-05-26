import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from avd_project.scraping import scrape_books_to_csv


if __name__ == "__main__":
    output_path = scrape_books_to_csv()
    print(f"Dados brutos salvos em: {output_path}")
