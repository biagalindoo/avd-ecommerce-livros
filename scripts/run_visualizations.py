from avd_project.visualization import run_visualizations


if __name__ == "__main__":
    outputs = run_visualizations()
    for name, path in outputs.items():
        print(f"{name}: {path}")
