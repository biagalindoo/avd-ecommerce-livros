from avd_project.etl import run_etl


if __name__ == "__main__":
    output_path = run_etl()
    print(f"Dados processados salvos em: {output_path}")
