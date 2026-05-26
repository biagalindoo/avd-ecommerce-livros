from avd_project.scraping import scrape_books_to_csv


if __name__ == "__main__":
    output_path = scrape_books_to_csv()
    print(f"Dados brutos salvos em: {output_path}")
