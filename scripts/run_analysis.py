from avd_project.analysis import run_analysis


if __name__ == "__main__":
    outputs = run_analysis()
    for name, path in outputs.items():
        print(f"{name}: {path}")
